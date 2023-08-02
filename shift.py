import asyncio
from pyrogram import filters
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply, text
from pyrogram.errors import RPCError

@Client.on_message(filters.command("shift", prefix) & filters.me)
async def shift(client, message):
    lol = await edit_or_reply(message, "Processing please wait")
    x = get_text(message)
    x=x.replace(" ","")
    try:
       fromchat, tochat, limit, reverse = x.split("|")
       if reverse == "reverse":
           reverse = True
       else:
           reverse = False
    except:
        try:
           fromchat, tochat, limit = x.split("|")
           reverse = False
        except:
            await lol.edit("Check command syntax")
    try:
        fromchat =int(fromchat)
    except:
        if not (fromchat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    try:
        tochat = int(tochat)
    except:
        if not (tochat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return

    a =0    
    if limit == "None" or limit == "none":
        try:
            async for message in client.iter_history(fromchat, reverse=reverse):
              try:
                await message.copy(tochat)
                a=a+1
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass              
            
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return
    else:
        try:
            limit = int(limit)
        except:
            lol.edit("Enter a vailed limit")
            return
        try:
            async for message in client.iter_history(fromchat, limit = limit,reverse=reverse):
              try:
                await message.copy(tochat)

                a=a+1
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass   
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return

@Client.on_message(filters.command("mediashift", prefix) & filters.me)
async def mediashift(client, message):
    lol = await edit_or_reply(message, "Processing please wait")
    x = get_text(message)
    try:
       fromchat, tochat , cap, limit, reverse = x.split("|")
       if reverse == "reverse":
           reverse = True
    except:
        try:
           fromchat, tochat,cap  ,limit = x.split("|")
           reverse = False
        except:
            await lol.edit("Check command syntax")
    fromchat = fromchat.replace(" ","")
    tochat = tochat.replace(" ","")
    try:
        fromchat =int(fromchat)
    except:
        if not (fromchat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    try:
        tochat = int(tochat)
    except:
        if not (tochat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    a =0
    if limit == "None" or limit == "none":
        try:
            async for message in client.iter_history(fromchat, reverse=reverse):
              try:
                if message.video or message.document:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat)
                  
                  a=a+1              
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass            
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return
    else:
        try:
            limit = int(limit)
        except:
            lol.edit("Enter a vailed limit")
            return
        try:
            async for message in client.iter_history(fromchat, limit = limit,reverse=reverse):
              try:
                if message.video or message.document:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat)
                  a=a+1     
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass     
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return
        

@Client.on_message(filters.command("audioshift", prefix) & filters.me)
async def audioshift(client, message):
    lol = await edit_or_reply(message, "Processing please wait")
    x = get_text(message)
    try:
       fromchat, tochat , cap, limit, reverse = x.split("|")
       if reverse == "reverse":
           reverse = True
    except:
        try:
           fromchat, tochat,cap , limit = x.split("|")
           reverse = False
        except:
            await lol.edit("Check command syntax")
    fromchat = fromchat.replace(" ","")
    tochat = tochat.replace(" ","")
    try:
        fromchat =int(fromchat)
    except:
        if not (fromchat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    try:
        tochat = int(tochat)
    except:
        if not (tochat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    a =0    
    if limit == "None" or limit == "none":
        try:
            async for message in client.iter_history(fromchat, reverse=reverse):
              try:
                if message.audio or message.voice:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat)
                  a=a+1     
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass             
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return

    else:
        try:
            limit = int(limit)
        except:
            lol.edit("Enter a vailed limit")
            return
        try:
            async for message in client.iter_history(fromchat, limit = limit,reverse=reverse):
              try:
                if message.audio or message.voice:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat) 
              except Exception as e:
                await lol.edit(e)
                return
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")

        except RPCError as i:
            await lol.edit(i)
            return
        
@Client.on_message(filters.command("videoshift", prefix) & filters.me)
async def videoshift(client, message):
    lol = await edit_or_reply(message, "Processing please wait")
    x = get_text(message)
    try:
       fromchat, tochat , cap, limit, reverse = x.split("|")
       if reverse == "reverse":
           reverse = True
    except:
        try:
           fromchat, tochat,cap , limit = x.split("|")
           reverse = False
        except:
            await lol.edit("Check command syntax")
    fromchat = fromchat.replace(" ","")
    tochat = tochat.replace(" ","")
    try:
        fromchat =int(fromchat)
    except:
        if not (fromchat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    try:
        tochat = int(tochat)
    except:
        if not (tochat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    a =0    
    if limit == "None" or limit == "none":
        try:
            async for message in client.iter_history(fromchat, reverse=reverse):
              try:
                if message.video:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat) 
                  a=a+1     
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass   
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return

    else:
        try:
            limit = int(limit)
        except:
            lol.edit("Enter a vailed limit")
            return
        try:
            async for message in client.iter_history(fromchat, limit = limit,reverse=reverse):
              try:
                if message.video:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat) 
                  a=a+1     
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass   
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")   
        except RPCError as i:
            await lol.edit(i)
            return
        
@Client.on_message(filters.command("imageshift", prefix) & filters.me)
async def imageshift(client, message):
    lol = await edit_or_reply(message, "Processing please wait")
    x = get_text(message)
    try:
       fromchat, tochat , cap, limit, reverse = x.split("|")
       if reverse == "reverse":
           reverse = True
    except:
        try:
           fromchat, tochat,cap , limit = x.split("|")
           reverse = False
        except:
            await lol.edit("Check command syntax")
    fromchat = fromchat.replace(" ","")
    tochat = tochat.replace(" ","")
    try:
        fromchat =int(fromchat)
    except:
        if not (fromchat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    try:
        tochat = int(tochat)
    except:
        if not (tochat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    a =0    
    if limit == "None" or limit == "none":
        try:
            async for message in client.iter_history(fromchat, reverse=reverse):
              try:
                if message.photo:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat) 
                  a=a+1     
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass   
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return

    else:
        try:
            limit = int(limit)
        except:
            lol.edit("Enter a vailed limit")
            return
        try:
            
            async for message in client.iter_history(fromchat, limit = limit,reverse=reverse):
              try:
                if message.photo:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat) 
                  a=a+1     
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass   
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return


@Client.on_message(filters.command("docshift", prefix) & filters.me)
async def docshift(client, message):
    lol = await edit_or_reply(message, "Processing please wait")
    x = get_text(message)
    try:
       fromchat, tochat , cap, limit, reverse = x.split("|")
       if reverse == "reverse":
           reverse = True
    except:
        try:
           fromchat, tochat,cap , limit = x.split("|")
           reverse = False
        except:
            await lol.edit("Check command syntax")
    fromchat = fromchat.replace(" ","")
    tochat = tochat.replace(" ","")
    try:
        fromchat =int(fromchat)
    except:
        if not (fromchat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    try:
        tochat = int(tochat)
    except:
        if not (tochat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    a =0    
    if limit == "None" or limit == "none":
        try:
            async for message in client.iter_history(fromchat, reverse=reverse):
              try:
                if message.document:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat) 
                  a=a+1     
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass   
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return
    else:
        try:
            limit = int(limit)
        except:
            lol.edit("Enter a vailed limit")
            return
        try:
            async for message in client.iter_history(fromchat, limit = limit,reverse=reverse):
              try:
                if message.document:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat) 
                  a=a+1     
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass   
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return
        
@Client.on_message(filters.command("msgshift", prefix) & filters.me)
async def msgshift(client, message):
    lol = await edit_or_reply(message, "Processing please wait")
    x = get_text(message)
    x=x.replace(" ","")
    try:
       fromchat, tochat , cap, limit, reverse = x.split("|")
       if reverse == "reverse":
           reverse = True
    except:
        try:
           fromchat, tochat,cap , limit = x.split("|")
           reverse = False
        except:
            await lol.edit("Check command syntax")
    try:
        fromchat =int(fromchat)
    except:
        if not (fromchat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    try:
        tochat = int(tochat)
    except:
        if not (tochat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    a =0    
    if limit == "None" or limit == "none":
        try:
            async for message in client.iter_history(fromchat, reverse=reverse):
              try:
                if message.text:
                  await message.copy(tochat) 
                  a=a+1     
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass   
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return
        
    else:
        try:
            limit = int(limit)
        except:
            lol.edit("Enter a vailed limit")
            return
        try:
            async for message in client.iter_history(fromchat, limit = limit,reverse=reverse):
              try:
                if message.document:
                  if cap != "None" or cap != "none":
                    await message.copy(tochat, caption= cap)
                  else:
                    await message.copy(tochat) 
                  a=a+1     
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass   
              await asyncio.sleep(1)
            await lol.edit(f"Successfully shifted {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return


@Client.on_message(filters.command("forshift", prefix) & filters.me)
async def forshift(client, message):
    lol = await edit_or_reply(message, "Processing please wait")
    x = get_text(message)
    x=x.replace(" ","")
    try:
       fromchat, tochat, limit, reverse = x.split("|")
       if reverse == "reverse":
           reverse = True
       else:
           reverse = False
    except:
        try:
           fromchat, tochat, limit = x.split("|")
           reverse = False
        except:
            await lol.edit("Check command syntax")
    try:
        fromchat =int(fromchat)
    except:
        if not (fromchat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    try:
        tochat = int(tochat)
    except:
        if not (tochat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return

    a =0    
    if limit == "None" or limit == "none":
        try:
            async for message in client.iter_history(fromchat, reverse=reverse):
              try:
                await message.forward(tochat)
                a=a+1
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass              
            
              await asyncio.sleep(1)
            await lol.edit(f"Successfully forwarded {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return
    else:
        try:
            limit = int(limit)
        except:
            lol.edit("Enter a vailed limit")
            return
        try:
            async for message in client.iter_history(fromchat, limit = limit,reverse=reverse):
              try:
                await message.forward(tochat)

                a=a+1
              except Exception as e:
                await lol.edit(e)
                pass
              except RPCError as i:
                await lol.edit(i)
                pass   
              await asyncio.sleep(1)
            await lol.edit(f"Successfully forwarded {a} messages from {fromchat} to {tochat}")
        except RPCError as i:
            await lol.edit(i)
            return




@Client.on_message(filters.command("dmshift", prefix) & filters.me)
async def dmshift(client, message):
    lol = await edit_or_reply(message, "Processing please wait")
    x = get_text(message)
    x=x.replace(" ","")

    if not message.reply_to_message:
        await lol.edit("reply to any message to deliver")
    reply = message.reply_to_message
    try:
        x =int(x)
    except:
        if not (x.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    try:
        await reply.copy(x)    
    except RPCError as i:
        await lol.edit(i)
        return
    await lol.edit(f"Message Delivered to {x}")

modules_help["shift"] = {
        "shift": "Steal all from one chat to other chat \n .shift fromchat | to chat | limit none for no limits\nNote: | is essential",
        "example": "{prefix}shift @moonuserbot | @moonub_chat | 100",
        "dmshift": "forward a message to someone without forward tag",
        "example": "{prefix}dmshift @qbtaumai",
        "forshift": "forward all from one chat to other chat \n .forshift fromchat | to chat | limit none for no limits\nNote: | is essential",
        "example": "{prefix}forshift @moonuserbot | @moonub_chat | 100",
        "msgshift": "Steal all text messages from one chat to other chat \n .msgshift fromchat | to chat | limit non for unlimited\nNote: | is essential",
        "example": "{prefix}msgshift @moonuserbot | @moonub_chat | 100",
        "docshift": "Steal all documents from one chat to other chat \n .docshift fromchat | to chat | If caption or None for not | limit\nNote: | is essential",
        "example": "{prefix}docshift @moonuserbot | @moonub_chat | I stole this file | 100",
        "imageshift": "Steal all photos from one chat to other chat \n .imageshift fromchat | to chat | If caption or None for not | limit\nNote: | is essential",
        "example": "{prefix}imageshift @moonuserbot | @moonub_chat | I stole this file | 100",
        "videoshift": "Steal all video from one chat to other chat \n .videoshift fromchat | to chat | If caption or None for not | limit none for no limit\nNote: | is essential",
        "example": "{prefix}videoshift @moonuserbot | @moonub_chat | I stole this file | 100",
        "audioshift": "Steal all audio from one chat to other chat \n .audioshift fromchat | to chat | If caption or None for not | limit\nNote: | is essential",
        "example": "{prefix}audioshift @moonuserbot | @moonub_chat | I stole this file | 100",
        "mediashift": "Steal all media from one chat to other chat \n .mediashift fromchat | to chat | If caption or None for not | limit\nNote: | is essential",
        "example": "{prefix}mediashift @moonuserbot | @moonub_chat | I stole this file | 100",
    }
