from pyrogram import Client, filters

# Create a Pyrogram Client
from VIPMUSIC import app
# Define the command handler
@app.on_message(filters.command("chats"))
async def get_user_ids(client, message):
    async for dialog in client.get_dialogs():
        user_id = dialog.chat.id
        chat_name = dialog.chat.title or dialog.chat.first_name
        await message.reply_text(f"Chat Name: {chat_name}\nUser ID: {user_id}")

# Start the client
