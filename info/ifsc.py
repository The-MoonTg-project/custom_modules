from pyrogram import Client, filters
import requests
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

API_BASE_URL = "https://ifsc.razorpay.com/"


@Client.on_message(filters.command("ifsc", prefix) & filters.me)
async def fetch_ifsc_details(_, message):
    try:
        ifsc_code = message.text.split(" ")[1]
        response = requests.get(f"{API_BASE_URL}{ifsc_code}")
        response.raise_for_status()
        data = response.json()

        if "IFSC" in data:
            details = [
                f"<b>Bank:</b> <code>{data.get('BANK', 'N/A')}</code>",
                f"<b>Bank Code:</b> <code>{data.get('BANKCODE', 'N/A')}</code>",
                f"<b>IFSC:</b> <code>{data.get('IFSC', 'N/A')}</code> | <b>MICR:</b> <code>{data.get('MICR', 'N/A')}</code>",
                f"<b>State:</b> <code>{data.get('STATE', 'N/A')}</code>",
                f"<b>District:</b> <code>{data.get('DISTRICT', 'N/A')}</code>",
                f"<b>City:</b> <code>{data.get('CITY', 'N/A')}</code>",
                f"<b>Branch:</b> <code>{data.get('BRANCH', 'N/A')}</code>",
                f"<b>Address:</b> <code>{data.get('ADDRESS', 'N/A')}</code>",
                f"<b>Contact:</b> <code>{data.get('CONTACT', 'N/A')}</code>",
                f"<b>UPI:</b> <code>{data.get('UPI', 'N/A')}</code> | <b>ISO3166:</b> <code>{data.get('ISO3166', 'N/A')}</code>",
                f"<b>NEFT:</b> <code>{data.get('NEFT', 'N/A')}</code> | <b>IMPS:</b> <code>{data.get('IMPS', 'N/A')}</code>",
                f"<b>RTGS:</b> <code>{data.get('RTGS', 'N/A')}</code> | <b>Swift:</b> <code>{data.get('SWIFT', 'N/A')}</code>",
            ]
            info = "<b>Detailed Info</b>:\n\n" + "\n".join(details)

            await message.edit_text(info)
        else:
            await message.edit_text("Invalid IFSC Code 😕")
    except requests.exceptions.RequestException:
        await message.edit_text("Please provide valid IFSC Code")
    except IndexError:
        await message.edit_text("Please provide an IFSC Code")


modules_help["ifsc"] = {"ifsc [ifsc code]": "Get the IFSC code with full details"}
