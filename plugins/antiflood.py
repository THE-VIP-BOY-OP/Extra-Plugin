from VIPMUSIC import app
from VIPMUSIC.core.mongo import mongodb
from pyrogram import filters
from pyrogram.types import Message
from datetime import timedelta, datetime

# MongoDB collection to store flood settings
antiflood_collection = mongodb['antiflood_settings']

# Default action if not set
DEFAULT_FLOOD_ACTION = "mute"

# Helper functions to fetch and update settings from the database

def get_chat_flood_settings(chat_id):
    settings = antiflood_collection.find_one({"chat_id": chat_id})
    if not settings:
        return {
            "flood_limit": 0,
            "flood_timer": 0,
            "flood_action": DEFAULT_FLOOD_ACTION,
            "delete_flood": False
        }
    return settings

def update_chat_flood_settings(chat_id, update_data):
    antiflood_collection.update_one({"chat_id": chat_id}, {"$set": update_data}, upsert=True)

# Command: /flood - Get the current antiflood settings
@app.on_message(filters.command("flood") & filters.user(admin=True))
async def get_flood_settings(client, message: Message):
    chat_id = message.chat.id
    settings = get_chat_flood_settings(chat_id)
    await message.reply(
        f"Flood Limit: {settings['flood_limit']}\n"
        f"Flood Timer: {settings['flood_timer']} seconds\n"
        f"Flood Action: {settings['flood_action']}\n"
        f"Delete Flood Messages: {settings['delete_flood']}"
    )

# Command: /setflood <number/off/no> - Set the number of consecutive messages to trigger antiflood
@app.on_message(filters.command("setflood") & filters.user(admin=True))
async def set_flood_limit(client, message: Message):
    chat_id = message.chat.id
    command_args = message.command[1:]
    
    if len(command_args) == 0:
        await message.reply("Please provide a flood limit or 'off'.")
        return
    
    flood_limit = command_args[0].lower()
    
    if flood_limit in ["off", "no", "0"]:
        update_chat_flood_settings(chat_id, {"flood_limit": 0})
        await message.reply("Antiflood has been disabled.")
    else:
        try:
            flood_limit = int(flood_limit)
            update_chat_flood_settings(chat_id, {"flood_limit": flood_limit})
            await message.reply(f"Flood limit set to {flood_limit} consecutive messages.")
        except ValueError:
            await message.reply("Invalid flood limit. Please provide a valid number or 'off'.")

# Command: /setfloodtimer <count> <duration> - Set the number of messages and time required for timed antiflood
@app.on_message(filters.command("setfloodtimer") & filters.user(admin=True))
async def set_flood_timer(client, message: Message):
    chat_id = message.chat.id
    command_args = message.command[1:]
    
    if len(command_args) == 0 or command_args[0].lower() in ["off", "no"]:
        update_chat_flood_settings(chat_id, {"flood_timer": 0})
        await message.reply("Timed antiflood has been disabled.")
        return

    if len(command_args) != 2:
        await message.reply("Please provide both count and duration in seconds.")
        return
    
    try:
        count = int(command_args[0])
        duration = int(command_args[1].replace('s', ''))
        update_chat_flood_settings(chat_id, {"flood_timer": duration, "flood_limit": count})
        await message.reply(f"Flood timer set to {count} messages in {duration} seconds.")
    except ValueError:
        await message.reply("Invalid timer settings. Please provide a valid number.")

# Command: /floodmode <action> - Choose action for users exceeding the flood limit
@app.on_message(filters.command("floodmode") & filters.user(admin=True))
async def set_flood_mode(client, message: Message):
    chat_id = message.chat.id
    command_args = message.command[1:]
    
    if len(command_args) == 0:
        await message.reply("Please provide a valid action (ban/mute/kick/tban/tmute).")
        return
    
    action = command_args[0].lower()
    if action not in ["ban", "mute", "kick", "tban", "tmute"]:
        await message.reply("Invalid action. Please choose from ban/mute/kick/tban/tmute.")
        return
    
    update_chat_flood_settings(chat_id, {"flood_action": action})
    await message.reply(f"Flood action set to {action}.")

# Command: /clearflood <yes/no> - Whether to delete flood messages
@app.on_message(filters.command("clearflood") & filters.user(admin=True))
async def set_flood_clear(client, message: Message):
    chat_id = message.chat.id
    command_args = message.command[1:]
    
    if len(command_args) == 0 or command_args[0].lower() not in ["yes", "no", "on", "off"]:
        await message.reply("Please choose either 'yes' or 'no'.")
        return
    
    delete_flood = command_args[0].lower() in ["yes", "on"]
    update_chat_flood_settings(chat_id, {"delete_flood": delete_flood})
    await message.reply(f"Delete flood messages set to {delete_flood}.")

# Flood detection logic
flood_count = {}

@app.on_message(filters.group)
async def flood_detector(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    settings = get_chat_flood_settings(chat_id)
    
    if settings['flood_limit'] == 0:
        return  # Antiflood is disabled
    
    # Track message frequency per user
    if chat_id not in flood_count:
        flood_count[chat_id] = {}
    
    user_flood_data = flood_count[chat_id].get(user_id, {"count": 0, "first_message_time": datetime.now()})
    
    if (datetime.now() - user_flood_data['first_message_time']).seconds > settings['flood_timer']:
        # Reset count if flood_timer exceeded
        user_flood_data = {"count": 1, "first_message_time": datetime.now()}
    else:
        user_flood_data['count'] += 1
    
    flood_count[chat_id][user_id] = user_flood_data

    if user_flood_data['count'] > settings['flood_limit']:
        # Take action when the flood limit is exceeded
        action = settings['flood_action']
        await take_flood_action(client, message, action)
        
        if settings['delete_flood']:
            await message.delete()

# Action function: ban, mute, kick, tban, tmute
async def take_flood_action(client, message, action):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if action == "ban":
        await client.kick_chat_member(chat_id, user_id)
    elif action == "mute":
        await client.restrict_chat_member(chat_id, user_id, permissions=[])
    elif action == "kick":
        await client.kick_chat_member(chat_id, user_id)
        await client.unban_chat_member(chat_id, user_id)
    elif action == "tban":
        await client.kick_chat_member(chat_id, user_id, until_date=datetime.now() + timedelta(days=3))
    elif action == "tmute":
        await client.restrict_chat_member(chat_id, user_id, permissions=[], until_date=datetime.now() + timedelta(days=3))

    await message.reply(f"User {message.from_user.first_name} was {action}ed for flooding.")
