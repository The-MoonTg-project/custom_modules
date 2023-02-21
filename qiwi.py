from __future__ import annotations

import logging
from datetime import datetime

# from glQiwiApi.qiwi.clients.wallet.types import TransactionType, Transaction
from pyrogram import Client, filters
from pyrogram.types import Message

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix

# from utils.scripts import format_exc
from utils.scripts import import_library, format_exc

# noinspection PyUnresolvedReferences
from utils.db import db

# from glQiwiApi import QiwiWallet, QiwiP2PClient

QiwiApi = import_library("glQiwiApi")
QiwiWallet = QiwiApi.QiwiWallet
QiwiP2PClient = QiwiApi.QiwiP2PClient
TransactionType = QiwiApi.qiwi.clients.wallet.types.TransactionType
Transaction = QiwiApi.qiwi.clients.wallet.types.Transaction


class P2pNotInitializedError(Exception):
    pass


p2p_error = P2pNotInitializedError("Пожалуйста, привяжите p2p токен: .qp2p [token]")


class BasicQiwi:
    def __init__(self, token: str = None, number: str = None, secret_p2p: str = None):
        self.token = token
        self.number = number
        self.secret_p2p = secret_p2p
        self.qiwi = QiwiWallet(api_access_token=self.token, phone_number=self.number)
        if self.secret_p2p:
            try:
                self.p2p = QiwiP2PClient(secret_p2p=self.secret_p2p)
            except Exception as ex:
                self.p2p = None
                logging.warning("Failed to create P2P client: %s", ex)

    async def set_p2p(self, secret_p2p: str):
        self.p2p = QiwiP2PClient(secret_p2p=secret_p2p)
        self.secret_p2p = secret_p2p

    @property
    async def balance(self):
        await self.qiwi.get_list_of_balances()
        return await self.qiwi.get_balance()

    @property
    async def nickname(self):
        return await self.qiwi.get_nickname()

    async def get_history(
        self,
        limit: int = 5,
        trans_type: TransactionType | str = TransactionType.ALL,
        start_date: datetime = None,
        end_date: datetime = None,
        offset: int = 0,
    ):
        result = rsource = await self.qiwi.history(
            rows=limit,
            transaction_type=trans_type,
            start_date=start_date,
            end_date=end_date,
        )
        if offset and len(result) // offset > 0:
            result = []
            for i in range(0, len(result), offset):
                result.append(rsource[i])
        return result

    @staticmethod
    async def trans_to_str(transaction: Transaction):
        x = (
            f"\n<b>Куда:</b> <code>{transaction.to_account}</code>"
            if transaction.to_account
            else ""
        )
        return (
            f"<b>Транзакция:</b> <code>#{transaction.id} ({transaction.type})</code>\n"
            f'<b>Дата:</b> <code>{transaction.date.strftime("%d.%m.%Y %H:%M")}</code>\n'
            f"<b>Сумма:</b> <code>{transaction.total.amount} {transaction.total.currency.symbol_native}</code>"
            + x
        )

    @property
    async def last_trans(self):
        trans = await self.get_history(limit=1)
        if len(trans) == 0:
            return "⛔ Не найдено транзакций."
        return await self.trans_to_str(trans[0])

    async def send_money(
        self, number: str, amount: int | float | str, comment: str = None
    ):
        return await self.qiwi.transfer_money(
            to_phone_number=number, amount=amount, comment=comment
        )

    async def send_card(self, number: str, amount: int | float | str):
        return await self.qiwi.transfer_money_to_card(card_number=number, amount=amount)

    async def create_p2p(
        self, amount: int | float | str, bill_id: str = None, comment: str = None
    ):
        if self.p2p is None:
            raise p2p_error

        return await self.p2p.create_p2p_bill(
            amount=amount, bill_id=bill_id, comment=comment
        )

    async def get_p2p_bill(self, bill_id: str):
        if self.p2p is None:
            raise p2p_error

        bill = await self.p2p.get_bill_by_id(bill_id=bill_id)

        if bill is None:
            return "<b>⛔ Счёт не найден.</b>"

        status = (
            "✅ Оплачен"
            if bill.status == "PAID"
            else "💤 Ожидает оплаты"
            if bill.status == "WAITING"
            else ""
            if bill.status == "EXPIRED"
            else "🚫 Отклонён"
        )

        return (
            f"<b>Платеж</b> <code>#{bill.id}</code>:\n"
            f"<b>Сумма:</b> {bill.amount} руб.\n"
            f"<b>Статус:</b> {status}"
        )

    @property
    async def text(self):
        balance = await self.balance
        nickname = await self.nickname
        return (
            f"<b>📞 Телефон:</b> <code>{self.number}</code>\n"
            f"<b>💰 Баланс:</b> <code>{balance.amount} {balance.currency.symbol_native}</code>\n"
            f"<b>👤 Никнейм:</b> <code>{nickname.nickname} ({'Можно сменить' if nickname.can_change else 'Перманент'})</code>\n\n"
            f"<b>🗒️ Последняя транзакция:</b>\n{await self.last_trans}"
        )

    async def get_limits(self):
        result = await self.qiwi.get_limits()
        text = ""
        for name, limit in result.items():
            text += f"<b>{name}</b>:\n"
            for lim in limit:
                text += f"<b><i>{lim.limit_type}</i></b>: <code>{lim.rest}</code><b>/</b><code>{lim.max_limit}</code>\n"
        return text


class Config:
    qiwis = db.get("lordcodes.qiwi", "token")
    if qiwis:
        qiwi = BasicQiwi(
            token=qiwis,
            number=db.get("lordcodes.qiwi", "number"),
            secret_p2p=db.get("lordcodes.qiwi", "secret_p2p"),
        )
    else:
        qiwi = None


commands = [
    "qiwi",
    "qset",
    "qp2p",
    "qdel",
    "qsend",
    "qcard",
    "qcheck",
    "qhistory",
    "qlimits",
]


# noinspection PyUnusedLocal
@Client.on_message(filters.command(commands, prefix) & filters.me)
async def qiwi_handler(client: Client, message: Message):
    try:
        cmd = message.command[0]
        args = message.command[1:]

        await message.edit("Обрабатываю команду...")

        if cmd == "qset":
            if len(args) < 2:
                return await message.edit(
                    f"<b>Используйте:</b> <code>{prefix}qset [token]* [number]* [p2p]</code>"
                )

            p2p = args[2] if len(args) > 2 else None

            try:
                Config.qiwi = BasicQiwi(token=args[0], number=args[1], secret_p2p=p2p)
            except Exception as ex:
                Config.qiwi = None
                return await message.edit(
                    "<b>Не удалось создать клиент Qiwi:</b>\n" f"{format_exc(ex)}"
                )
            db.set("lordcodes.qiwi", "token", args[0])
            db.set("lordcodes.qiwi", "number", args[1])
            if p2p:
                db.set("lordcodes.qiwi", "secret_p2p", p2p)
            return await message.edit("<b>Настройки qiwi сохранены.</b>")
        elif cmd == "qcheck":
            if len(args) < 2:
                return await message.edit(
                    f"<b>Используйте:</b> <code>{prefix}qcheck [токен]* [номер]*</code>"
                )
            token = args[0]
            number = args[1]
            try:
                client = BasicQiwi(token=token, number=number)
                text = await client.text
                return await message.edit(
                    f"<b>✅ Токен</b> <code>{token}</code> <b>валид.</b>\n\n{text}"
                )
            except Exception as ex:
                return await message.edit(
                    f"<b>⛔ Токен</b> <code>{token}</code> <b>невалид.</b>\n"
                    f"{format_exc(ex)}"
                )

        if Config.qiwi is None:
            return await message.edit(
                "<b>Вы не создали клиент. Введите:</b> "
                f"<code>{prefix}qset [token]* [number]* [p2p]</code>"
            )
        if cmd == "qiwi":
            return await message.edit(await Config.qiwi.text)
        elif cmd == "qp2p":
            if len(args) < 1:
                return await message.edit(
                    f"<b>Используйте:</b> <code>{prefix}qp2p [secret_p2p]*</code>"
                )
            try:
                await Config.qiwi.set_p2p(args[0])
                db.set("lordcodes.qiwi", "secret_p2p", args[0])
            except Exception as ex:
                return await message.edit(
                    "<b>⛔ Не удалось установить p2p secret token.</b>\n"
                    f"{format_exc(ex)}"
                )
        elif cmd == "qdel":
            db.remove("lordcodes.qiwi", "token")
            db.remove("lordcodes.qiwi", "number")
            db.remove("lordcodes.qiwi", "secret_p2p")
            Config.qiwi = None
            return await message.edit("<b>Данные от Qiwi удалены с бд.</b>")

        elif cmd == "qlimits":
            text = (
                f"<b>Лимиты для клиента:</b> <code>{Config.qiwi.number}</code>\n"
                f"{await Config.qiwi.get_limits()}"
            )
            return await message.edit(text)

        elif cmd in ["qsend", "qcard"]:
            if len(args) < 2:
                return await message.edit(
                    f"<b>Используйте:</b> <code>{prefix}qsend [номер]* [сумма]* [коммент]</code>"
                )
            try:
                amount = float(args[1].replace(",", "."))
            except ValueError:
                return await message.edit("<b>Сумма должна быть числом.</b>")
            if amount < 1:
                return await message.edit("<b>Сумма должна быть больше 0.</b>")
            try:
                comment = args[2] if len(args) > 2 else None
                await Config.qiwi.send_money(
                    number=args[0], amount=amount, comment=comment
                ) if cmd == "qsend" else await Config.qiwi.send_card(
                    number=args[0], amount=amount
                )
                await message.edit(
                    f"<b>✅ Отправлено:</b> <code>{amount}</code> <b>на номер</b> <code>{args[0]}</code>"
                )
            except Exception as ex:
                return await message.edit(
                    "<b>Не удалось отправить деньги:</b>\n" f"{format_exc(ex)}"
                )
        elif cmd == "qhistory":
            if len(args) > 0:
                a = args[0].lower()
                typ = (
                    TransactionType.IN
                    if "in" in a
                    else TransactionType.OUT
                    if "out" in a
                    else TransactionType.ALL
                )
            else:
                typ = TransactionType.ALL
            if len(args) > 1:
                try:
                    limit = int(args[1])
                except ValueError:
                    limit = 5
            else:
                limit = 5
            if len(args) > 2:
                try:
                    offset = int(args[2])
                except ValueError:
                    offset = 0
            else:
                offset = 0

            history = await Config.qiwi.get_history(
                limit=limit, offset=offset, trans_type=typ
            )
            text = "\n➖➖➖➖➖➖➖➖➖\n".join(
                [await BasicQiwi.trans_to_str(_i) for _i in history]
            )[:4096]
            return await message.edit(text)
        else:
            return await message.edit(
                f"<b>Используйте:</b> <code>{prefix}help qiwi</code> чтобы узнать команды модуля."
            )
    except Exception as ex:
        return await message.edit(f"<b>Qiwi module:</b>\n{format_exc(ex)}")


modules_help["qiwi"] = {
    "qset [токен]* [номер]* [p2p]": "Установить кошелек Qiwi",
    "qp2p [p2p]*": "Установить p2p secret token Qiwi",
    "qdel": "Удалить кошелёк с бд",
    "qiwi": "Получить информацию о кошельке",
    "qsend [номер]* [сумма]* [коммент]": "Отправить средства на кошелёк",
    "qcard [номер]* [сумма]*": "Отправить средства на карту",
    "qhistory [лимит] [in|out|all] [offset]": "Список транзакций (default 5, all, 0)",
    "qcheck [токен]* [номер]*": "Чекнуть токен на валидность",
    "qlimits": "Чекнуть свой аккаунт на лимиты",
}
