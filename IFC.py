from pyrogram import Client, filters
import requests as req

API_URL = 'https://ifsc.razorpay.com/'

@Client.on_message(filters.command('ifsc'))
async def ifsc(client, message):
    try:
        ifsc_code = message.text.split(' ')[1]
        response = req.get(API_URL + ifsc_code)
        json_data = response.json()

        if 'IFSC' in json_data:  # Check if the 'IFSC' key exists in the response
            info = "Detailed Info\n...................\n\n"
            info += f"Bank: {json_data.get('BANK', 'N/A')}\n"
            info += f"Bank Code: {json_data.get('BANKCODE', 'N/A')}\n"
            info += f"IFSC: {json_data.get('IFSC', 'N/A')}\n"
            info += f"MICR: {json_data.get('MICR', 'N/A')}\n"
            info += f"State: {json_data.get('STATE', 'N/A')}\n"
            info += f"District: {json_data.get('DISTRICT', 'N/A')}\n"
            info += f"City: {json_data.get('CITY', 'N/A')}\n"
            info += f"Branch: {json_data.get('BRANCH', 'N/A')}\n"
            info += f"Address: {json_data.get('ADDRESS', 'N/A')}\n"
            info += f"Contact: {json_data.get('CONTACT', 'N/A')}\n"
            info += f"UPI: {json_data.get('UPI', 'N/A')}\n"
            info += f"ISO3166: {json_data.get('ISO3166', 'N/A')}\n"
            info += f"NEFT: {json_data.get('NEFT', 'N/A')}\n"
            info += f"IMPS: {json_data.get('IMPS', 'N/A')}\n"
            info += f"RTGS: {json_data.get('RTGS', 'N/A')}\n"
            info += f"Swift: {json_data.get('SWIFT', 'N/A')}\n"

            await message.reply(info)
        else:
            await message.reply("Invalid IFSC Code 😕")
    except Exception as e:
        await message.reply("Invalid IFSC Code 😕")
      
