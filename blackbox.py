import uuid
import re

from aiohttp import ClientSession, FormData

from pyrogram import Client, filters

from utils.misc import modules_help, prefix


def id_generator() -> str:
    return str(uuid.uuid4())


@Client.on_message(filters.command(["bboxai", "blackbox"], prefix) & filters.me)
async def blackbox(client, message):
    m = message
    msg = await m.edit_text("🔍")

    if len(m.text.split()) == 1:
        return await msg.edit_text(
            "Type some query buddy 🐼\n"
            f"{prefix}blackbox text with reply to the photo or just text"
        )
    else:
        try:
            session = ClientSession()
            prompt = m.text.split(maxsplit=1)[1]
            user_id = id_generator()
            image = None

            if m.reply_to_message and (
                m.reply_to_message.photo
                or (m.reply_to_message.sticker and not m.reply_to_message.sticker.is_video)
            ):
                file_name = f"blackbox_{m.chat.id}.jpeg"
                file_path = await m.reply_to_message.download(file_name=file_name)
                with open(file_path, "rb") as file:
                    image = file.read()

            if image:
                data = FormData()
                data.add_field("fileName", file_name)
                data.add_field("userId", user_id)
                data.add_field(
                    "image", image, filename=file_name, content_type="image/jpeg"
                )
                api_url = "https://www.blackbox.ai/api/upload"
                try:
                    async with session.post(api_url, data=data) as response:
                        response_json = await response.json()
                except Exception as e:
                    return await msg.edit(f"❌ Error: {str(e)}")

                messages = [
                    {
                        "role": "user",
                        "content": response_json["response"] + "\n#\n" + prompt,
                    }
                ]
                data = {
                    "messages": messages,
                    "user_id": user_id,
                    "codeModelMode": True,
                    "agentMode": {},
                    "trendingAgentMode": {},
                }
                headers = {"Content-Type": "application/json"}
                url = "https://www.blackbox.ai/api/chat"
                try:
                    async with session.post(url, headers=headers, json=data) as response:
                        response_text = await response.text()
                except Exception as e:
                    return await msg.edit(f"❌ Error: {str(e)}")

                cleaned_response_text = re.sub(
                    r"^\$?@?\$?v=undefined-rv\d+@?\$?|\$?@?\$?v=v\d+\.\d+-rv\d+@?\$?",
                    "",
                    response_text,
                )
                text = cleaned_response_text.strip()[2:]
                if "$~~~$" in text:
                    text = re.sub(r"\$~~~\$.*?\$~~~\$", "", text, flags=re.DOTALL)
                rdata = {"reply": text}

                return await msg.edit_text(text=rdata["reply"])
            else:
                reply = m.reply_to_message
                if reply and reply.text:
                    prompt = f"Old conversation:\n{reply.text}\n\nQuestion:\n{prompt}"
                messages = [{"role": "user", "content": prompt}]
                data = {
                    "messages": messages,
                    "user_id": user_id,
                    "codeModelMode": True,
                    "agentMode": {},
                    "trendingAgentMode": {},
                }
                headers = {"Content-Type": "application/json"}
                url = "https://www.blackbox.ai/api/chat"
                try:
                    async with session.post(url, headers=headers, json=data) as response:
                        response_text = await response.text()
                except Exception as e:
                    return await msg.edit(f"❌ Error: {str(e)}")

                cleaned_response_text = re.sub(
                    r"^\$?@?\$?v=undefined-rv\d+@?\$?|\$?@?\$?v=v\d+\.\d+-rv\d+@?\$?",
                    "",
                    response_text,
                )
                text = cleaned_response_text.strip()[2:]
                if "$~~~$" in text:
                    text = re.sub(r"\$~~~\$.*?\$~~~\$", "", text, flags=re.DOTALL)
                rdata = {"reply": text}

                return await msg.edit_text(text=rdata["reply"])
        except Exception as e:
            return await msg.edit(f"�� Error: {str(e)}")
        finally:
            await session.close()


modules_help["blackbox"] = {
    "blackbox [query]*": "Ask anything to Blackbox",
    "bbox [query]*": "Ask anything to Blackbox",
}
