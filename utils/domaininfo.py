import requests
from dns import resolver
from pyrogram import Client, filters
from utils.misc import modules_help, prefix
from utils.scripts import import_library

whois = import_library("whois", "python-whois")


def get_domain_hosting_info(domain_name):
    """Get domain hosting information."""
    try:
        domain_info = whois.whois(domain_name)
        return domain_info
    except whois.parser.PywhoisError as e:
        print(f"Error: {e}")
        return None


def get_dns_records(domain_name):
    """Get DNS records for the given domain."""
    records = {}
    try:
        # A Record (IP address)
        a_record = resolver.resolve(domain_name, "A")
        records["A"] = [str(ip) for ip in a_record]
    except Exception as e:
        records["A"] = f"Failed to retrieve A record: {e}"

    try:
        # MX Record (Mail servers)
        mx_record = resolver.resolve(domain_name, "MX")
        records["MX"] = [str(mx) for mx in mx_record]
    except Exception as e:
        records["MX"] = f"Failed to retrieve MX record: {e}"

    return records


def get_ip_geolocation(ip):
    """Get IP geolocation information."""
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        return response.json()
    except Exception as e:
        print(f"Failed to get IP geolocation: {e}")
        return None


@Client.on_message(filters.command("domaininfo", prefix) & filters.me)
async def get_domain_info(_, message):
    if len(message.command) > 1:
        domain_name = message.text.split(f"{prefix}domain ", 1)[1]
        await message.edit_text("<b>Processing...</b>")
        domain_info = get_domain_hosting_info(domain_name)
        dns_records = get_dns_records(domain_name)

        if domain_info:
            # Get the first IP address (if A record exists) for geolocation
            ip_address = (
                dns_records["A"][0]
                if "A" in dns_records and isinstance(dns_records["A"], list)
                else None
            )
            ip_geolocation = get_ip_geolocation(ip_address) if ip_address else None
            creation_date = (
                domain_info.creation_date[0]
                if isinstance(domain_info.creation_date, list)
                else domain_info.creation_date
            )
            expiration_date = (
                domain_info.expiration_date[0]
                if isinstance(domain_info.expiration_date, list)
                else domain_info.expiration_date
            )
            updated_date = (
                domain_info.updated_date[0]
                if isinstance(domain_info.updated_date, list)
                else domain_info.updated_date
            )

            response = (
                f"<b>Domain Information:</b>\n"
                f"<b>Domain Name:</b> {domain_info.domain_name}\n"
                f"<b>Registrar:</b> {domain_info.registrar}\n"
                f"<b>Creation Date:</b> {creation_date}\n"
                f"<b>Expiration Date:</b> {expiration_date}\n"
                f"<b>Updated Date:</b> {updated_date}\n"
                f"<b>Nameservers:</b> {', '.join(domain_info.name_servers) if domain_info.name_servers else 'N/A'}\n"
                f"<b>Status:</b> {', '.join([s.split()[0] if isinstance(s, str) else s for s in domain_info.status]) if domain_info.status else 'N/A'}\n"
                f"<b>Registrant:</b> {domain_info.registrant_name if hasattr(domain_info, 'registrant_name') else 'N/A'}\n"
                f"<b>Registrant Country:</b> {domain_info.registrant_country if hasattr(domain_info, 'registrant_country') else 'N/A'}\n"
                f"\n<b>DNS Records</b>\n"
                f"<b>A Record:</b> {', '.join(dns_records['A']) if isinstance(dns_records['A'], list) else dns_records['A']}\n"
                f"<b>MX Record:</b> {', '.join(dns_records['MX']) if isinstance(dns_records['MX'], list) else dns_records['MX']}\n"
            )

            if ip_geolocation:
                response += (
                    f"\n<b>IP Geolocation</b>\n"
                    f"<b>IP:</b> {ip_address}\n"
                    f"<b>City:</b> {ip_geolocation.get('city', 'N/A')}\n"
                    f"<b>Region:</b> {ip_geolocation.get('region', 'N/A')}\n"
                    f"<b>Country:</b> {ip_geolocation.get('country', 'N/A')}\n"
                    f"<b>Location:</b> {ip_geolocation.get('loc', 'N/A')}\n"
                    f"<b>ISP:</b> {ip_geolocation.get('org', 'N/A')}\n"
                )
        else:
            response = "Failed to retrieve domain hosting information."

        return await message.edit_text(response)
    return await message.edit_text("Please provide a domain name")


modules_help["domaininfo"] = {"domain [url]": "Get Domain Info"}
