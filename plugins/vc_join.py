from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import Update, UserJoined, UserLeft
from pytgcalls.types.enums import UpdateType
from VIPMUSIC.core.mongo import mongodb  # MongoDB connection
from VIPMUSIC import app

# Function to check if monitoring is enabled for a group
def is_monitoring_enabled(chat_id):
    status = mongodb.vc_monitoring.find_one({"chat_id": chat_id})
    return status and status["status"] == "on"

# Event to monitor VC join/leave
@pytgcalls.on_update()
async def vc_participant_update(client, update: Update):
    chat_id = update.chat_id
    if is_monitoring_enabled(chat_id):  # Only proceed if monitoring is enabled for this group
        if update.update_type == UpdateType.PARTICIPANT_JOINED and isinstance(update, UserJoined):
            user_id = update.user_id
            mention = f"[User](tg://user?id={user_id})"
            await app.send_message(chat_id, f"{mention} ne VC join kiya. User ID: {user_id}")

        elif update.update_type == UpdateType.PARTICIPANT_LEFT and isinstance(update, UserLeft):
            user_id = update.user_id
            mention = f"[User](tg://user?id={user_id})"
            await app.send_message(chat_id, f"{mention} ne VC leave kiya. User ID: {user_id}")

# Command to start VC monitoring and update status in database
@app.on_message(filters.command("checkvc on") & filters.group)
async def start_vc_monitor(client: Client, message: Message):
    chat_id = message.chat.id
    mongodb.vc_monitoring.update_one(
        {"chat_id": chat_id},
        {"$set": {"status": "on"}},
        upsert=True
    )
    await pytgcalls.start(chat_id)
    await message.reply("VC monitoring started. Ab jo bhi VC join ya leave karega, uska update yaha milega.")

# Command to stop VC monitoring and update status in database
@app.on_message(filters.command("checkvcoff") & filters.group)
async def stop_vc_monitor(client: Client, message: Message):
    chat_id = message.chat.id
    mongodb.vc_monitoring.update_one(
        {"chat_id": chat_id},
        {"$set": {"status": "off"}}
    )
    await pytgcalls.leave_group_call(chat_id)
    await message.reply("VC monitoring stopped.")

