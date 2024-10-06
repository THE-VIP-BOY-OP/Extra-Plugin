import random
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection setup (refer to your MongoDB setup code)
from VIPMUSIC.core.mongo import mongodb, pymongodb

# Collections to store messages, replies, and group settings
messages_collection = mongodb.message
group_settings_collection = mongodb.group_settings

# Initialize bot
from VIPMUSIC import app 

# Save a message and its replies (supporting text, stickers, photos, and videos)
async def save_reply(original_message, reply_message):
    message_id = original_message.message_id
    user_id = original_message.from_user.id

    # Determine the type of message to save
    if reply_message.text:
        reply_data = {"type": "text", "content": reply_message.text}
    elif reply_message.sticker:
        reply_data = {"type": "sticker", "content": reply_message.sticker.file_id}
    elif reply_message.photo:
        reply_data = {"type": "photo", "content": reply_message.photo.file_id}
    elif reply_message.video:
        reply_data = {"type": "video", "content": reply_message.video.file_id}

    # Check if the message already exists
    message_data = await messages_collection.find_one({"message_id": message_id})

    if message_data:
        # Add the new reply to the existing message
        await messages_collection.update_one(
            {"message_id": message_id},
            {"$push": {"replies": reply_data}}
        )
    else:
        # Save the original message and the reply
        await messages_collection.insert_one({
            "message_id": message_id,
            "user_id": user_id,
            "message_text": original_message.text,
            "replies": [reply_data]
        })

# Retrieve a random reply (supports text, stickers, photos, and videos)
async def get_reply(message):
    message_data = await messages_collection.find_one({"message_text": message.text})

    if message_data and message_data["replies"]:
        # Return a random reply from the saved replies
        return random.choice(message_data["replies"])

    # If no specific replies found, return a random reply from any message
    random_reply = await messages_collection.aggregate([{"$sample": {"size": 1}}]).to_list(length=1)
    if random_reply:
        return random.choice(random_reply[0]["replies"])

    return None

# Check if the chatbot is enabled in the group
async def is_chatbot_enabled(group_id):
    group_status = await group_settings_collection.find_one({"group_id": group_id})
    return group_status is None or group_status.get("enabled", True)

# Send the appropriate reply based on its type
async def send_reply(client, message, reply_data):
    if reply_data["type"] == "text":
        await message.reply_text(reply_data["content"])
    elif reply_data["type"] == "sticker":
        await message.reply_sticker(reply_data["content"])
    elif reply_data["type"] == "photo":
        await message.reply_photo(reply_data["content"])
    elif reply_data["type"] == "video":
        await message.reply_video(reply_data["content"])

# Listener for group messages (supports text, stickers, photos, and videos)
@app.on_message(filters.group & (filters.text | filters.sticker | filters.photo | filters.video))
async def handle_message(client, message):
    # Check if the chatbot is enabled for this group
    if not await is_chatbot_enabled(message.chat.id):
        return  # Do nothing if chatbot is disabled in this group

    # Check if it's a reply to another message
    if message.reply_to_message:
        await save_reply(message.reply_to_message, message)

    # Try to find a reply from the database
    reply = await get_reply(message)

    # If a reply is found, send it
    if reply:
        await send_reply(client, message, reply)
    else:
        await message.reply_text("I don't have a reply for this message yet!")

@app.on_message(filters.command("chatbot", prefixes="/") & filters.group)
async def toggle_chatbot(client, message):
    group_id = message.chat.id

    # Check if the second argument is 'on' or 'off'
    if len(message.command) < 2:
        await message.reply_text("Please specify 'on' or 'off'. Usage: /chatbot [on|off]")
        return

    state = message.command[1].lower()

    if state == "on":
        await group_settings_collection.update_one(
            {"group_id": group_id},
            {"$set": {"enabled": True}},
            upsert=True
        )
        await message.reply_text("Chatbot is now ON in this group!")
    elif state == "off":
        await group_settings_collection.update_one(
            {"group_id": group_id},
            {"$set": {"enabled": False}},
            upsert=True
        )
        await message.reply_text("Chatbot is now OFF in this group!")
    else:
        await message.reply_text("Invalid argument. Please use '/chatbot on' or '/chatbot off'.")
