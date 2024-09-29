import whois
import dns.resolver
import requests
from pyrogram import Client, filters
from utils.misc import modules_help, prefix

def get_domain_hosting_info(domain_name):
    try:
        domain_info = whois.whois(domain_name)
        return domain_info
    except whois.parser.PywhoisError as e:
        print(f"Error: {e}")
        return None

def get_dns_records(domain_name):
    records = {}
    try:
        # A Record (IP address)
        a_record = dns.resolver.resolve(domain_name, 'A')
        records['A'] = [str(ip) for ip in a_record]
    except Exception as e:
        records['A'] = f"Failed to retrieve A record: {e}"
        
    try:
        # MX Record (Mail servers)
        mx_record = dns.resolver.resolve(domain_name, 'MX')
        records['MX'] = [str(mx) for mx in mx_record]
    except Exception as e:
        records['MX'] = f"Failed to retrieve MX record: {e}"
        
    return records

def get_ip_geolocation(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        return response.json()
    except Exception as e:
        print(f"Failed to get IP geolocation: {e}")
        return None

@Client.on_message(filters.command("domain", prefix) & filters.me)
async def get_domain_info(client, message):
    if len(message.command) > 1:
        domain_name = message.text.split("/domain ", 1)[1]
        domain_info = get_domain_hosting_info(domain_name)
        dns_records = get_dns_records(domain_name)
        
        if domain_info:
            # Get the first IP address (if A record exists) for geolocation
            ip_address = dns_records['A'][0] if 'A' in dns_records and isinstance(dns_records['A'], list) else None
            ip_geolocation = get_ip_geolocation(ip_address) if ip_address else None

            response = (
                f"Domain Name: {domain_info.domain_name}\n"
                f"Registrar: {domain_info.registrar}\n"
                f"Creation Date: {domain_info.creation_date}\n"
                f"Expiration Date: {domain_info.expiration_date}\n"
                f"Updated Date: {domain_info.updated_date}\n"
                f"Nameservers: {', '.join(domain_info.name_servers) if domain_info.name_servers else 'N/A'}\n"
                f"Status: {', '.join(domain_info.status) if domain_info.status else 'N/A'}\n"
                f"Registrant: {domain_info.registrant_name if hasattr(domain_info, 'registrant_name') else 'N/A'}\n"
                f"Registrant Country: {domain_info.registrant_country if hasattr(domain_info, 'registrant_country') else 'N/A'}\n"
                f"\n-- DNS Records --\n"
                f"A Record: {', '.join(dns_records['A']) if isinstance(dns_records['A'], list) else dns_records['A']}\n"
                f"MX Record: {', '.join(dns_records['MX']) if isinstance(dns_records['MX'], list) else dns_records['MX']}\n"
            )

            if ip_geolocation:
                response += (
                    f"\n-- IP Geolocation --\n"
                    f"IP: {ip_address}\n"
                    f"City: {ip_geolocation.get('city', 'N/A')}\n"
                    f"Region: {ip_geolocation.get('region', 'N/A')}\n"
                    f"Country: {ip_geolocation.get('country', 'N/A')}\n"
                    f"Location: {ip_geolocation.get('loc', 'N/A')}\n"
                    f"ISP: {ip_geolocation.get('org', 'N/A')}\n"
                )
        else:
            response = "Failed to retrieve domain hosting information."

        await message.reply(response)
    else:
        await message.reply("Please provide a domain name after the .domain Google.com .")


modules_help["domain"] = {
    "domain [url]": "domain google.com"
}
