from pyrogram import filters
from pyrogram.enums import ChatAction
from TheApi import api

from VIPMUSIC import app
from config import BANNED_USERS


@app.on_message(filters.command(["detect", "aidetect", "asklang"]) & ~BANNED_USERS)
async def chatgpt_chat_lang(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("**Provide any text after command or reply to any message**")
            
        return

    if message.reply_to_message and message.reply_to_message.text:
        user_text = message.reply_to_message.text
    else:
        user_text = " ".join(message.command[1:])

    user_input = f"""
    Sentences :- {user_text}
    Ye sentence kon sa language me hai mujhe bas ush sentencess ka lang name aur lang code aur ush sentences ka ek se do line me ek mast sa chatbot ki tarah attractive mast sa reply usi lang me likh ke do aur aisa reply dena ki ush sentence se related ho aur padh ke maja aa jaye, aur man kre bat krne ka ok aur agar emoji ho sentences me to tum bhi aisa emoji use krna ki padhne bala banda khus ho jaye aur agar koi sentence gusse bhare mile to reply emotional bala dena with emotional emoji, aise format me do :- 
   
    Lang : -
    Code :-
    Reply :- 

    Bas lang name aur lang code aur reply likh ke do uske alava kuch nhi
    """

    # Send typing action and get the response from API
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    results = api.chatgpt(user_input)
    await message.reply_text(results)


@app.on_message(filters.command(["chatgpt", "ai", "ask"]) & ~BANNED_USERS)
async def chatgpt_chat(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            "Example:\n\n`/ai write simple website code using html css, js?`"
        )
        return

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    results = api.chatgpt(user_input)
    await message.reply_text(results)


__MODULE__ = "CʜᴀᴛGᴘᴛ"
__HELP__ = """
/advice - ɢᴇᴛ ʀᴀɴᴅᴏᴍ ᴀᴅᴠɪᴄᴇ ʙʏ ʙᴏᴛ
/ai [ǫᴜᴇʀʏ] - ᴀsᴋ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴡɪᴛʜ ᴄʜᴀᴛɢᴘᴛ's ᴀɪ
/gemini [ǫᴜᴇʀʏ] - ᴀsᴋ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴡɪᴛʜ ɢᴏᴏɢʟᴇ's ɢᴇᴍɪɴɪ ᴀɪ
/bard [ǫᴜᴇʀʏ] -ᴀsᴋ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴡɪᴛʜ ɢᴏᴏɢʟᴇ's ʙᴀʀᴅ ᴀɪ"""
