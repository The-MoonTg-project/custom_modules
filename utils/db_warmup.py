# Moon-Userbot - Database Warmup Module
# Keeps MongoDB, Supabase, Postgres, Redis, and HTTP database endpoints active
# to prevent deactivation / auto-pausing due to prolonged offline usage or inactivity.

import asyncio
from contextlib import suppress
import html
import re
import socket
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import aiohttp
from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from utils import modules_help, prefix
from utils.db import db
from utils.scripts import import_library


def mask_uri(uri: str) -> str:
    """
    Masks credentials (passwords, tokens, keys) in database URIs and URLs
    to prevent accidental leakage in chat outputs.
    """
    if not uri:
        return ""
    # Mask user:password@
    masked = re.sub(r"(://[^:]+:)([^@]+)(@)", r"\1****\3", uri)
    # Mask URL parameters containing secrets
    masked = re.sub(
        r"((?:key|pass|password|secret|token|apikey)=)[^&]+",
        r"\1****",
        masked,
        flags=re.IGNORECASE,
    )
    return masked


def detect_db_type(uri: str) -> str:
    """
    Auto-detects database/service type from connection URI scheme or hostname.
    """
    uri_lower = uri.lower()
    if uri_lower.startswith(("mongodb://", "mongodb+srv://")):
        return "mongodb"
    elif uri_lower.startswith(("postgresql://", "postgres://", "supabase://")):
        return "postgres"
    elif uri_lower.startswith(("redis://", "rediss://")):
        return "redis"
    elif uri_lower.startswith(("http://", "https://")):
        if "supabase" in uri_lower:
            return "supabase"
        return "http"
    elif uri_lower.startswith(("mysql://", "mariadb://")):
        return "mysql"
    return "http"


def auto_generate_alias(db_type: str, existing_dbs: dict) -> str:
    """
    Generates a clean, incremental alias (e.g. mongo_1, postgres_1)
    when a user provides a DB link directly without an alias.
    """
    prefix_map = {
        "mongodb": "mongo",
        "postgres": "postgres",
        "redis": "redis",
        "supabase": "supabase",
        "mysql": "mysql",
        "http": "http",
    }
    base = prefix_map.get(db_type.lower(), "db")
    count = 1
    while f"{base}_{count}" in existing_dbs:
        count += 1
    return f"{base}_{count}"


async def get_ipv4_host(host: str) -> str:
    """Resolves hostname specifically to an IPv4 address to avoid Network Unreachable (Errno 101)."""
    loop = asyncio.get_running_loop()
    try:
        info = await loop.getaddrinfo(host, None, family=socket.AF_INET)
        if info:
            return info[0][4][0]
    except Exception:
        pass
    return host


# --- Rate Limit & FloodWait Helper ---


class TelegramEditThrottler:
    """
    Prevents Telegram rate-limiting and FloodWait errors by enforcing
    a minimum interval between message edits.
    """

    def __init__(self, message: Message, min_interval: float = 1.5):
        self.message = message
        self.min_interval = min_interval
        self.last_edit = 0.0

    async def edit(self, text: str):
        now = time.time()
        if now - self.last_edit < self.min_interval:
            return
        self.last_edit = now
        try:
            await self.message.edit_text(text, parse_mode=enums.ParseMode.HTML)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            with suppress(Exception):
                await self.message.edit_text(text, parse_mode=enums.ParseMode.HTML)
        except Exception:
            pass

    async def final_edit(self, text: str):
        """Applies final edit with FloodWait retry guarantee."""
        try:
            await self.message.edit_text(text, parse_mode=enums.ParseMode.HTML)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            with suppress(Exception):
                await self.message.edit_text(text, parse_mode=enums.ParseMode.HTML)
        except Exception:
            pass


# --- Database Warmup & Ping Drivers ---


async def ping_mongodb(uri: str) -> tuple[bool, float, str]:
    """Pings MongoDB using pymongo (if available) or IPv4 socket fallback."""
    start = time.perf_counter()
    # 1. Try pymongo driver
    try:
        pymongo = import_library("pymongo")

        def _sync_ping():
            client = pymongo.MongoClient(
                uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000
            )
            client.admin.command("ping")
            client.close()

        loop = asyncio.get_running_loop()
        await asyncio.wait_for(loop.run_in_executor(None, _sync_ping), timeout=7.0)
        elapsed = (time.perf_counter() - start) * 1000
        return True, round(elapsed, 2), "Ping command succeeded (pymongo)"
    except Exception as e:
        # 2. Fallback to TCP IPv4 socket connection test
        try:
            parsed = urlparse(uri if "://" in uri else f"mongodb://{uri}")
            host = parsed.hostname or "localhost"
            port = parsed.port or 27017

            # Handle SRV cluster hostnames (e.g. cluster0.xxxx.mongodb.net -> shard host)
            hosts_to_try = [host]
            if "mongodb.net" in host and "shard" not in host:
                prefix = host.split(".")[0]
                domain = ".".join(host.split(".")[1:])
                hosts_to_try.append(f"{prefix}-shard-00-00.{domain}")

            last_err = ""
            for h in hosts_to_try:
                try:
                    ipv4_host = await get_ipv4_host(h)
                    _, writer = await asyncio.wait_for(
                        asyncio.open_connection(ipv4_host, port), timeout=4.0
                    )
                    writer.close()
                    await writer.wait_closed()
                    elapsed = (time.perf_counter() - start) * 1000
                    return (
                        True,
                        round(elapsed, 2),
                        f"Socket connection verified ({ipv4_host}:{port})",
                    )
                except Exception as se:
                    last_err = str(se)

            elapsed = (time.perf_counter() - start) * 1000
            return (
                False,
                round(elapsed, 2),
                mask_uri(f"Connection failed: {str(e)} | Socket: {last_err}"),
            )
        except Exception as se:
            elapsed = (time.perf_counter() - start) * 1000
            return (
                False,
                round(elapsed, 2),
                mask_uri(f"Connection failed: {str(se)}"),
            )


async def ping_postgres(uri: str) -> tuple[bool, float, str]:
    """Pings PostgreSQL / Supabase Postgres using asyncpg, psycopg2, Supabase HTTP REST, or IPv4 socket fallback."""
    start = time.perf_counter()

    # 1. Try asyncpg driver
    try:
        asyncpg = import_library("asyncpg")
        conn_uri = uri.replace("postgres://", "postgresql://", 1)
        conn = await asyncio.wait_for(
            asyncpg.connect(conn_uri, timeout=5.0), timeout=6.0
        )
        await conn.execute("SELECT 1;")
        await conn.close()
        elapsed = (time.perf_counter() - start) * 1000
        return True, round(elapsed, 2), "Query 'SELECT 1;' succeeded (asyncpg)"
    except Exception:
        pass

    # 2. Try psycopg2 driver (module name 'psycopg2', package 'psycopg2-binary')
    try:
        psycopg2 = import_library("psycopg2", "psycopg2-binary")

        def _sync_pg():
            conn = psycopg2.connect(uri, connect_timeout=5)
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            cur.close()
            conn.close()

        loop = asyncio.get_running_loop()
        await asyncio.wait_for(loop.run_in_executor(None, _sync_pg), timeout=7.0)
        elapsed = (time.perf_counter() - start) * 1000
        return True, round(elapsed, 2), "Query 'SELECT 1;' succeeded (psycopg2)"
    except Exception:
        pass

    # 3. If Supabase project URI, try Supabase REST HTTP fallback (wakes up Supabase instances!)
    if "supabase" in uri.lower():
        try:
            parsed = urlparse(uri if "://" in uri else f"postgres://{uri}")
            host = parsed.hostname or ""
            parts = host.split(".")
            project_ref = None
            if "db." in host and len(parts) >= 4:
                project_ref = parts[1]
            elif len(parts) >= 3 and parts[1] == "supabase":
                project_ref = parts[0]

            if project_ref:
                rest_url = f"https://{project_ref}.supabase.co/rest/v1/"
                ok, pms, msg = await ping_http(rest_url)
                if ok or "401" in msg:
                    return True, pms, "Supabase active & kept alive (HTTP traffic verified)"
        except Exception:
            pass

    # 4. Fallback to TCP IPv4 socket connection test
    try:
        parsed = urlparse(uri if "://" in uri else f"postgres://{uri}")
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        ipv4_host = await get_ipv4_host(host)

        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ipv4_host, port), timeout=5.0
        )
        writer.close()
        await writer.wait_closed()
        elapsed = (time.perf_counter() - start) * 1000
        return (
            True,
            round(elapsed, 2),
            f"Socket connection verified ({ipv4_host}:{port})",
        )
    except Exception as se:
        elapsed = (time.perf_counter() - start) * 1000
        return (
            False,
            round(elapsed, 2),
            mask_uri(f"Postgres ping failed. Socket error: {str(se)}"),
        )


async def ping_redis(uri: str) -> tuple[bool, float, str]:
    """Pings Redis / Upstash Redis using redis-py or IPv4 socket fallback."""
    start = time.perf_counter()
    try:
        import_library("redis")
        from redis.asyncio import Redis

        r = Redis.from_url(uri, socket_connect_timeout=5, socket_timeout=5)
        await asyncio.wait_for(r.ping(), timeout=6.0)
        if hasattr(r, "aclose"):
            await r.aclose()
        else:
            await r.close()
        elapsed = (time.perf_counter() - start) * 1000
        return True, round(elapsed, 2), "PING command succeeded (redis-py)"
    except Exception as e:
        # Fallback to TCP IPv4 socket connection test
        try:
            parsed = urlparse(uri if "://" in uri else f"redis://{uri}")
            host = parsed.hostname or "localhost"
            port = parsed.port or 6379
            ipv4_host = await get_ipv4_host(host)

            _, writer = await asyncio.wait_for(
                asyncio.open_connection(ipv4_host, port), timeout=5.0
            )
            writer.close()
            await writer.wait_closed()
            elapsed = (time.perf_counter() - start) * 1000
            return (
                True,
                round(elapsed, 2),
                f"Socket connection verified ({ipv4_host}:{port})",
            )
        except Exception as se:
            elapsed = (time.perf_counter() - start) * 1000
            return (
                False,
                round(elapsed, 2),
                mask_uri(f"Connection failed: {str(e)} | Socket: {str(se)}"),
            )


async def ping_http(uri: str) -> tuple[bool, float, str]:
    """Pings HTTP/REST database endpoints (Supabase REST, Render, Neon, PocketBase, Webhooks)."""
    start = time.perf_counter()
    try:
        headers = {"User-Agent": "Telegram-DB-Warmup/1.0"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                uri, headers=headers, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                elapsed = (time.perf_counter() - start) * 1000
                return (
                    True,
                    round(elapsed, 2),
                    f"HTTP GET {resp.status} {resp.reason}",
                )
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        return False, round(elapsed, 2), mask_uri(f"HTTP request failed: {str(e)}")


async def ping_db(db_type: str, uri: str) -> tuple[bool, float, str]:
    """Routes database ping request to appropriate driver handler."""
    db_type = db_type.lower()
    if db_type in ("mongodb", "mongo"):
        return await ping_mongodb(uri)
    elif db_type in ("postgres", "postgresql", "supabase"):
        return await ping_postgres(uri)
    elif db_type in ("redis", "valkey", "upstash"):
        return await ping_redis(uri)
    elif db_type in ("http", "https", "supabase_rest", "rest", "web"):
        return await ping_http(uri)
    else:
        detected = detect_db_type(uri)
        if detected != "http":
            return await ping_db(detected, uri)
        return await ping_http(uri)


# --- Core Warmup Helpers ---


async def warmup_single_db(alias: str, info: dict) -> dict:
    """Warms up a single database entry and returns updated status dictionary."""
    db_type = info.get("db_type", "auto")
    uri = info.get("uri", "")
    success, ping_ms, msg = await ping_db(db_type, uri)
    now_iso = datetime.now(timezone.utc).isoformat()
    fail_count = info.get("fail_count", 0)

    if success:
        fail_count = 0
    else:
        fail_count += 1

    return {
        "alias": alias,
        "db_type": db_type,
        "uri": uri,
        "success": success,
        "last_status": "OK" if success else f"Failed: {msg[:35]}",
        "last_ping_ms": ping_ms,
        "last_warmup": now_iso,
        "fail_count": fail_count,
        "message": mask_uri(msg),
    }


# --- Background Auto-Warmup Task Loop ---


_auto_warmup_task = None


async def _background_warmup_loop():
    """Background task loop that periodically warms up all saved databases."""
    while True:
        try:
            enabled = db.get("custom.db_warmup", "auto_enabled", False)
            interval_hours = db.get("custom.db_warmup", "auto_interval", 12)
            if enabled:
                dbs = db.get("custom.db_warmup", "databases", default={})
                if dbs:
                    for alias, info in dbs.items():
                        res = await warmup_single_db(alias, info)
                        if alias in dbs:
                            dbs[alias].update(res)
                    db.set("custom.db_warmup", "databases", dbs)
        except Exception:
            pass

        # Check every 1 hour or interval_hours
        await asyncio.sleep(3600 * max(1, db.get("custom.db_warmup", "auto_interval", 12)))


def ensure_background_task():
    """Ensures background loop task is spawned on the active event loop."""
    global _auto_warmup_task
    if _auto_warmup_task is None or _auto_warmup_task.done():
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                _auto_warmup_task = loop.create_task(_background_warmup_loop())
        except RuntimeError:
            pass


# Try initializing background task on module import
ensure_background_task()


# --- Pyrogram Commands ---


@Client.on_message(filters.command(["adddb", "add_db"], prefix) & filters.me)
async def add_db_cmd(_: Client, message: Message):
    """
    Command to add a new database connection for warming up.
    Supports passing connection string directly (e.g. .adddb mongodb+srv://...)
    """
    ensure_background_task()
    args = message.command[1:]
    if not args:
        return await message.edit_text(
            f"<b>Usage:</b>\n"
            f"• <code>{prefix}adddb &lt;uri/url&gt;</code> <i>(Direct connection link)</i>\n"
            f"• <code>{prefix}adddb &lt;alias&gt; &lt;uri/url&gt;</code>\n"
            f"• <code>{prefix}adddb &lt;alias&gt; [db_type] &lt;uri/url&gt;</code>\n\n"
            f"<b>Examples:</b>\n"
            f"• <code>{prefix}adddb mongodb+srv://user:pass@cluster.mongodb.net/test</code>\n"
            f"• <code>{prefix}adddb postgresql://postgres:pass@db.supabase.co:5432/postgres</code>\n"
            f"• <code>{prefix}adddb redis rediss://default:pass@redis.upstash.io:6379</code>",
            parse_mode=enums.ParseMode.HTML,
        )

    dbs = db.get("custom.db_warmup", "databases", default={})

    # Direct URI mode (1 argument or 1st argument contains ://)
    if len(args) == 1 or "://" in args[0] or args[0].startswith("http"):
        uri = args[0]
        db_type = detect_db_type(uri)
        alias = auto_generate_alias(db_type, dbs)
    elif len(args) == 2:
        alias = args[0].lower()
        uri = args[1]
        db_type = detect_db_type(uri)
    else:
        alias = args[0].lower()
        db_type = args[1].lower()
        uri = args[2]

    dbs[alias] = {
        "db_type": db_type,
        "uri": uri,
        "added_at": datetime.now(timezone.utc).isoformat(),
        "last_status": "Never tested",
        "last_ping_ms": 0,
        "last_warmup": "Never",
        "fail_count": 0,
    }
    db.set("custom.db_warmup", "databases", dbs)

    masked = mask_uri(uri)
    await message.edit_text(
        f"✅ <b>Database Added Successfully!</b>\n\n"
        f"<b>Alias:</b> <code>{alias}</code>\n"
        f"<b>Type:</b> <code>{db_type}</code>\n"
        f"<b>URI:</b> <code>{masked}</code>\n\n"
        f"<i>Run <code>{prefix}warmup {alias}</code> to test connection.</i>",
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_message(filters.command(["deldb", "rmdb", "del_db"], prefix) & filters.me)
async def del_db_cmd(_: Client, message: Message):
    """Command to remove a database from the warmup list."""
    ensure_background_task()
    args = message.command[1:]
    if not args:
        return await message.edit_text(
            f"<b>Usage:</b> <code>{prefix}deldb &lt;alias&gt;</code>",
            parse_mode=enums.ParseMode.HTML,
        )

    alias = args[0].lower()
    dbs = db.get("custom.db_warmup", "databases", default={})
    if alias not in dbs:
        return await message.edit_text(
            f"❌ <b>Database with alias <code>{alias}</code> not found!</b>",
            parse_mode=enums.ParseMode.HTML,
        )

    del dbs[alias]
    db.set("custom.db_warmup", "databases", dbs)
    await message.edit_text(
        f"🗑️ <b>Database <code>{alias}</code> deleted successfully!</b>",
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_message(filters.command(["listdb", "dbs", "list_db"], prefix) & filters.me)
async def list_db_cmd(_: Client, message: Message):
    """Command to list all configured database accounts and their status."""
    ensure_background_task()
    dbs = db.get("custom.db_warmup", "databases", default={})
    if not dbs:
        return await message.edit_text(
            f"ℹ️ <b>No database accounts configured yet.</b>\n"
            f"Use <code>{prefix}adddb &lt;uri&gt;</code> to add one.",
            parse_mode=enums.ParseMode.HTML,
        )

    text = f"🗄️ <b>Configured Database Accounts ({len(dbs)}):</b>\n\n"
    for alias, info in dbs.items():
        masked = mask_uri(info.get("uri", ""))
        db_type = info.get("db_type", "unknown")
        status = info.get("last_status", "N/A")
        ping = info.get("last_ping_ms", 0)
        last_time = info.get("last_warmup", "Never")

        if last_time != "Never":
            try:
                dt = datetime.fromisoformat(last_time)
                last_time = dt.strftime("%Y-%m-%d %H:%M UTC")
            except Exception:
                pass

        icon = (
            "🟢"
            if "succeeded" in status.lower()
            or "verified" in status.lower()
            or "active" in status.lower()
            or "ok" in status.lower()
            or status == "OK"
            else ("⚪" if status == "Never tested" else "🔴")
        )

        text += (
            f"{icon} <b>{alias}</b> (<code>{db_type}</code>)\n"
            f"├ <b>URI:</b> <code>{masked}</code>\n"
            f"├ <b>Last Status:</b> {html.escape(str(status))} ({ping} ms)\n"
            f"└ <b>Last Warmup:</b> {last_time}\n\n"
        )

    auto_enabled = db.get("custom.db_warmup", "auto_enabled", False)
    interval = db.get("custom.db_warmup", "auto_interval", 12)
    auto_status = f"ENABLED (every {interval}h)" if auto_enabled else "DISABLED"
    text += f"⚙️ <b>Background Auto Warmup:</b> <code>{auto_status}</code>"

    await message.edit_text(text, parse_mode=enums.ParseMode.HTML)


@Client.on_message(
    filters.command(["warmup", "dbwarmup", "warmup_db"], prefix) & filters.me
)
async def warmup_cmd(_: Client, message: Message):
    """
    Command to trigger immediate warmup on all (or specific) databases.
    Displays live progress bar while respecting Telegram message editing limits.
    """
    ensure_background_task()
    dbs = db.get("custom.db_warmup", "databases", default={})
    if not dbs:
        return await message.edit_text(
            f"ℹ️ <b>No databases added.</b> Use <code>{prefix}adddb &lt;uri&gt;</code> first.",
            parse_mode=enums.ParseMode.HTML,
        )

    args = message.command[1:]
    target_alias = args[0].lower() if args else None

    if target_alias:
        if target_alias not in dbs:
            return await message.edit_text(
                f"❌ <b>Database <code>{target_alias}</code> not found!</b>",
                parse_mode=enums.ParseMode.HTML,
            )
        targets = {target_alias: dbs[target_alias]}
    else:
        targets = dbs

    total_count = len(targets)
    completed_count = 0
    results = {}
    throttler = TelegramEditThrottler(message, min_interval=1.5)

    await message.edit_text(
        f"🔥 <b>Starting Database Warmup (0/{total_count})...</b>",
        parse_mode=enums.ParseMode.HTML,
    )

    # Concurrency semaphore to bound parallel connections
    sem = asyncio.Semaphore(5)

    async def _worker(alias: str, info: dict):
        nonlocal completed_count
        async with sem:
            res = await warmup_single_db(alias, info)
            results[alias] = res
            completed_count += 1

            # Build visual progress indicator
            pct_10 = int((completed_count / total_count) * 10)
            bar = "▓" * pct_10 + "░" * (10 - pct_10)
            pct_full = (completed_count * 100) // total_count

            progress_text = (
                f"🔥 <b>Warming up databases...</b>\n"
                f"<code>[{bar}]</code> {completed_count}/{total_count} ({pct_full}%)\n\n"
                f"⚡ <i>Finished pinging:</i> <code>{alias}</code>"
            )
            await throttler.edit(progress_text)

    tasks = [_worker(alias, info) for alias, info in targets.items()]
    await asyncio.gather(*tasks)

    # Update persistent database records
    for alias, info in results.items():
        if alias in dbs:
            dbs[alias].update(info)
    db.set("custom.db_warmup", "databases", dbs)

    # Build final report summary
    success_cnt = sum(1 for r in results.values() if r["success"])
    fail_cnt = len(results) - success_cnt

    report = (
        f"⚡ <b>Database Warmup Completed!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Total:</b> {len(results)} | 🟢 <b>Success:</b> {success_cnt} | 🔴 <b>Failed:</b> {fail_cnt}\n\n"
    )

    for alias, res in results.items():
        icon = "🟢" if res["success"] else "🔴"
        masked = mask_uri(res.get("uri", ""))
        report += (
            f"{icon} <b>{alias}</b> (<code>{res['db_type']}</code>)\n"
            f"├ <b>Latency:</b> <code>{res['last_ping_ms']} ms</code>\n"
            f"├ <b>Result:</b> <code>{html.escape(res['message'])}</code>\n"
            f"└ <b>URI:</b> <code>{masked}</code>\n\n"
        )

    await throttler.final_edit(report)


@Client.on_message(
    filters.command(["autowarmup", "auto_warmup"], prefix) & filters.me
)
async def auto_warmup_cmd(_: Client, message: Message):
    """Command to configure automatic background periodic warmup."""
    ensure_background_task()
    args = message.command[1:]
    if not args:
        enabled = db.get("custom.db_warmup", "auto_enabled", False)
        interval = db.get("custom.db_warmup", "auto_interval", 12)
        return await message.edit_text(
            f"⚙️ <b>Auto Warmup Settings:</b>\n"
            f"• <b>Status:</b> <code>{'ENABLED' if enabled else 'DISABLED'}</code>\n"
            f"• <b>Interval:</b> <code>{interval} hours</code>\n\n"
            f"<b>Usage:</b>\n"
            f"• <code>{prefix}autowarmup on</code> - Enable background auto-warmup\n"
            f"• <code>{prefix}autowarmup off</code> - Disable background auto-warmup\n"
            f"• <code>{prefix}autowarmup &lt;hours&gt;</code> - Set interval in hours (e.g. 6, 12, 24)",
            parse_mode=enums.ParseMode.HTML,
        )

    arg = args[0].lower()
    if arg in ("on", "true", "enable"):
        db.set("custom.db_warmup", "auto_enabled", True)
        await message.edit_text(
            f"✅ <b>Auto Warmup Enabled!</b> Databases will be automatically kept active in the background.",
            parse_mode=enums.ParseMode.HTML,
        )
    elif arg in ("off", "false", "disable"):
        db.set("custom.db_warmup", "auto_enabled", False)
        await message.edit_text(
            f"🛑 <b>Auto Warmup Disabled.</b>",
            parse_mode=enums.ParseMode.HTML,
        )
    elif arg.isdigit():
        hours = int(arg)
        if hours < 1:
            hours = 1
        db.set("custom.db_warmup", "auto_enabled", True)
        db.set("custom.db_warmup", "auto_interval", hours)
        await message.edit_text(
            f"✅ <b>Auto Warmup set to run every {hours} hour(s) and enabled!</b>",
            parse_mode=enums.ParseMode.HTML,
        )
    else:
        await message.edit_text(
            f"❌ <b>Invalid argument. Use <code>on</code>, <code>off</code>, or an integer (e.g. 12).</b>",
            parse_mode=enums.ParseMode.HTML,
        )


@Client.on_message(
    filters.command(["cleardb", "clear_db"], prefix) & filters.me
)
async def clear_db_cmd(_: Client, message: Message):
    """Command to clear all stored database accounts."""
    ensure_background_task()
    db.set("custom.db_warmup", "databases", {})
    await message.edit_text(
        "🗑️ <b>All database accounts cleared from warmup list.</b>",
        parse_mode=enums.ParseMode.HTML,
    )


# Module Help Registration
modules_help["db_warmup"] = {
    "adddb [link]*": "Add a database link directly (auto-detects type & auto-generates alias mongo_1, postgres_1, etc.).",
    "deldb [alias]*": "Remove a database account from warmup list.",
    "listdb": "List all configured database accounts, their masked URIs, latency, and status.",
    "warmup [alias]": "Send warmup requests to all (or specified) databases with live progress updates.",
    "autowarmup [on/off/hours]": "Configure automated background database warming up interval.",
    "cleardb": "Remove all database entries from the warmup list.",
}
