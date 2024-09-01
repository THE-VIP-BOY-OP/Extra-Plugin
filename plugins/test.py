from pyrogram import Client, filters
from VIPMUSIC.utils.database import get_assistant
# Create a Pyrogram Client
from VIPMUSIC import app
# Define the command handler
@app.on_message(filters.command("chats"))
async def get_user_ids(client, message):
    userbot = await get_assistant(message.chat.id)
    async for dialog in userbot.get_dialogs():
        user_id = dialog.chat.id
        chat_name = dialog.chat.title or dialog.chat.first_name
        await message.reply_text(f"Chat Name: {chat_name}\nUser ID: {user_id}")

# Start the client
