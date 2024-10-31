import requests
from MukeshAPI import api
from pyrogram import filters
from pyrogram.enums import ChatAction
from VIPMUSIC import app


@app.on_message(filters.command(["gemini"]))
async def gemini_handler(client, message):
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)
    if (
        message.text.startswith(f"/gemini@{app.username}")
        and len(message.text.split(" ", 1)) > 1
    ):
        user_input = message.text.split(" ", 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        if len(message.command) > 1:
            user_input = " ".join(message.command[1:])
        else:
            await message.reply_text("ᴇxᴀᴍᴘʟᴇ :- `/gemini who is lord ram`")
            return

    try:
        response = api.gemini(user_input)
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        x = response["results"]
        if x:
            await message.reply_text(x, quote=True)
        else:
            await message.reply_text("sᴏʀʀʏ sɪʀ! ᴘʟᴇᴀsᴇ Tʀʏ ᴀɢᴀɪɴ")
    except requests.exceptions.RequestException as e:
        pass



@app.on_message(filters.group, group=50)
async def chatbot_handler(client, message):
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)
    if message.text and any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
        return

    if (message.reply_to_message and message.reply_to_message.from_user.id == app.id) or (app.username in message.text):
        try:
            user_input = f"""
                text:- ({message.text})
                text me message hai uske liye Ekdam chatty aur chhota reply do jitna chhota se chhota reply me kam ho jaye utna hi chota reply do agar jyada bada reply dena ho to maximum 1 line ka dena barna kosis krna chhota sa chhota reply ho aur purane jaise reply mat dena new reply lagna chahiye aur reply mazedar aur simple ho. Jis language mein yeh text hai, usi language mein reply karo. Agar sirf emoji hai toh bas usi se related emoji bhejo. Dhyaan rahe tum ek ladki ho toh reply bhi ladki ke jaise masti bhara ho.
                Bas reply hi likh ke do, kuch extra nahi aur jitna fast ho sake utna fast reply do!
                """
            response = api.gemini(user_input)
            await app.send_chat_action(message.chat.id, ChatAction.TYPING)
            x = response["results"]
            if x:
                await message.reply_text(x, quote=True)
            else:
                await message.reply_text("sᴏʀʀʏ sɪʀ! ᴘʟᴇᴀsᴇ Tʀʏ ᴀɢᴀɪɴ")
        except requests.exceptions.RequestException as e:
            pass
