from pyrogram import filters
from TheApi import api

from VIPMUSIC import app
from config import BANNED_USERS


@app.on_message(filters.command(["blackpink"]) & ~BANNED_USERS)
async def chatgpt_chat(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "/blackpink Radhe Radhe "
        )
    a = await message.reply_text("Creating BlackPink for You.....")

    args = " ".join(message.command[1:])

    results = api.blackpink(args)
    await message.reply_photo(results)
    try:
        await a.delete()
    except:
        pass
