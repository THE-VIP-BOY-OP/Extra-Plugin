from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from VIPMUSIC import app
from VIPMUSIC.misc import SUDOERS
from config import MONGO_DB_URI

# Connect to MongoDB
client = MongoClient(MONGO_DB_URI)
db = client["forcesub_db"]
forcesub_collection = db["forcesub"]

# Command for group owners and sudoers to set the forcesub channel
@app.on_message(filters.command("forcesub") & filters.group)
async def set_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if the user is the group owner or sudoer
    member = await client.get_chat_member(chat_id, user_id)
    if not (member.status == "creator" or user_id in SUDOERS):
        return await message.reply_text("Only group owners or sudoers can use this command.")

    # Handle disabling forcesub with "off" or "disable"
    if len(message.command) == 2 and message.command[1].lower() in ["off", "disable"]:
        forcesub_collection.delete_one({"chat_id": chat_id})
        return await message.reply_text("Force subscription has been disabled for this group.")

    # Ensure a channel username or ID is provided for enabling forcesub
    if len(message.command) != 2:
        return await message.reply_text("Usage: /forcesub <channel username or ID> or /forcesub off to disable")

    channel = message.command[1]

    try:
        # Check if the bot is an admin in the provided channel
        bot_id = app.id
        bot_member = await client.get_chat_member(channel, bot_id)
        if bot_member.status != "administrator":
            return await message.reply_text("I'm not an admin in this channel. Please make me an admin first.")

        # Save the forcesub data in the database
        forcesub_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"channel": channel}},
            upsert=True
        )

        await message.reply_text(f"Force subscription set to {channel} for this group.")

    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Function to check if a user has joined the forcesub channel
async def check_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Retrieve the forcesub channel for this chat
    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})
    if not forcesub_data:
        return True  # No forcesub set for this group

    channel = forcesub_data["channel"]

    try:
        # Check if the user is a member of the forcesub channel
        user_member = await client.get_chat_member(channel, user_id)
        if user_member.status in ["member", "administrator", "creator"]:
            return True  # User is in the channel
        else:
            raise Exception

    except:
        # If the user is not in the channel, delete the message and send a warning
        await message.delete()
        await message.reply_text(
            f"Hello {message.from_user.mention}, you need to join the [channel]({channel}) to send messages in this group.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel", url=f"https://t.me/{channel}")]
            ]),
            disable_web_page_preview=True
        )
        return False

# Monitor all messages in the group to enforce forcesub
@app.on_message(filters.group)
async def enforce_forcesub(client: Client, message: Message):
    if not await check_forcesub(client, message):
        return 
  
