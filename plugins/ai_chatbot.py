import requests
from MukeshAPI import api
from pyrogram import filters
from pyrogram.enums import ChatAction
from VIPMUSIC import app

# Handler for direct messages (DMs)
@app.on_message(filters.private & ~filters.service)
async def gemini_dm_handler(client, message):
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    user_input = message.text

    try:
        response = api.gemini(user_input)
        x = response["results"]
        if x:
            await message.reply_text(x, quote=True)
        else:
            await message.reply_text("sᴏʀʀʏ sɪʀ! ᴘʟᴇᴀsᴇ Tʀʏ ᴀɢᴀɪɴ")
    except requests.exceptions.RequestException as e:
        pass

# Handler for group chats when replying to the bot's message
@app.on_message(filters.group & filters.reply)
async def gemini_group_reply_handler(client, message):
    if message.reply_to_message.from_user.id == (await app.get_me()).id:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)

        user_input = message.text

        try:
            response = api.gemini(user_input)
            x = response["results"]
            if x:
                await message.reply_text(x, quote=True)
            else:
                await message.reply_text("sᴏʀʀʏ sɪʀ! ᴘʟᴇᴀsᴇ Tʀʏ ᴀɢᴀɪɴ")
        except requests.exceptions.RequestException as e:
            pass
