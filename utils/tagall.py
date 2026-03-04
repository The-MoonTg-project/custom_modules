import asyncio
from typing import List, Optional

from pyrogram import Client, filters, enums
from pyrogram.types import Message, ChatMember
from pyrogram.errors import FloodWait, ChatAdminRequired, UserNotParticipant

from utils.misc import modules_help, prefix


class TaggerBot:
    def __init__(self, batch_size: int = 5, delay: float = 2.0):
        self.batch_size = batch_size
        self.delay = delay
    
    async def get_members_by_role(
        self, 
        client: Client, 
        chat_id: int, 
        admin_only: bool = False,
        max_members: Optional[int] = None
    ) -> List[ChatMember]:
        members = []
        count = 0
        
        try:
            async for member in client.get_chat_members(chat_id):
                if max_members and count >= max_members:
                    break
                    
                if admin_only:
                    if member.status in [
                        enums.ChatMemberStatus.OWNER, 
                        enums.ChatMemberStatus.ADMINISTRATOR
                    ]:
                        members.append(member)
                        count += 1
                else:
                    if not member.user.is_bot and not member.user.is_deleted:
                        members.append(member)
                        count += 1
                        
        except UserNotParticipant:
            print("Bot is not a member of this chat!")
        except Exception as e:
            print(f"Error fetching members: {e}")
            
        return members
    
    async def send_batch_tags(
        self, 
        client: Client, 
        chat_id: int, 
        members: List[ChatMember]
    ) -> bool:
        if not members:
            return False
            
        for i in range(0, len(members), self.batch_size):
            batch = members[i:i + self.batch_size]
            tags = []
            
            for member in batch:
                if member.user.username:
                    tags.append(f"@{member.user.username}")
                else:
                    tags.append(member.user.mention)
            
            if tags:
                message_text = "\n".join(tags)
                try:
                    await client.send_message(
                        chat_id, 
                        text=message_text, 
                        parse_mode=enums.ParseMode.HTML
                    )
                    
                    if i + self.batch_size < len(members):
                        await asyncio.sleep(self.delay)
                        
                except FloodWait as e:
                    await asyncio.sleep(e.value + 1)
                    continue
                except Exception as e:
                    print(f"Error sending batch {i//self.batch_size + 1}: {e}")
                    continue
                    
        return True


tagger = TaggerBot(batch_size=5, delay=2.0)


@Client.on_message(filters.command("tagall", prefix) & filters.me)
async def tagall(client: Client, message: Message):
    await message.delete()
    
    if message.chat.type == enums.ChatType.PRIVATE:
        await client.send_message(
            message.chat.id, 
            "❌ This command only works in groups and supergroups!"
        )
        return
    
    status_msg = await client.send_message(
        message.chat.id, 
        "🔄 Fetching member list..."
    )
    
    try:
        members = await tagger.get_members_by_role(
            client, 
            message.chat.id, 
            admin_only=False,
            max_members=200
        )
        
        if not members:
            await status_msg.edit("❌ No active members found!")
            return
            
        await status_msg.edit(f"🏷 Starting to tag {len(members)} members...")
        
        success = await tagger.send_batch_tags(client, message.chat.id, members)
        
        if success:
            await status_msg.edit(f"✅ Successfully tagged {len(members)} members!")
        else:
            await status_msg.edit("❌ Error tagging members!")
            
    except ChatAdminRequired:
        await status_msg.edit("❌ I need to be a group admin to execute this command!")
    except Exception as e:
        await status_msg.edit(f"❌ Command execution error: {str(e)}")


@Client.on_message(filters.command("tagadmins", prefix) & filters.me)
async def tagadmins(client: Client, message: Message):
    await message.delete()
    
    if message.chat.type == enums.ChatType.PRIVATE:
        await client.send_message(
            message.chat.id, 
            "❌ This command only works in groups and supergroups!"
        )
        return
    
    status_msg = await client.send_message(
        message.chat.id, 
        "🔄 Fetching admin list..."
    )
    
    try:
        admins = await tagger.get_members_by_role(
            client, 
            message.chat.id, 
            admin_only=True
        )
        
        if not admins:
            await status_msg.edit("❌ No admins found!")
            return
            
        await status_msg.edit(f"🏷 Starting to tag {len(admins)} admins...")
        
        success = await tagger.send_batch_tags(client, message.chat.id, admins)
        
        if success:
            await status_msg.edit(f"✅ Successfully tagged {len(admins)} admins!")
        else:
            await status_msg.edit("❌ Error tagging admins!")
            
    except ChatAdminRequired:
        await status_msg.edit("❌ I need to be a group admin to execute this command!")
    except Exception as e:
        await status_msg.edit(f"❌ Command execution error: {str(e)}")


@Client.on_message(filters.command("tagstop", prefix) & filters.me)
async def tagstop(client: Client, message: Message):
    await message.delete()
    await client.send_message(
        message.chat.id,
        "⚠️ To stop the operation, restart the bot or wait for it to finish"
    )


modules_help["tagall"] = {
    "tagall": "Tag all active group members (max 200)",
    "tagadmins": "Tag only admins and group owner", 
    "tagstop": "Instructions to stop tagging operation"
}
