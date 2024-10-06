import random
from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient
from pyrogram import Client
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from config import MONGO_DB_URI as MONGO_URL
from VIPMUSIC import app
# MongoDB connection
chatdb = MongoClient(MONGO_URL)
status_db = chatdb["ChatBotStatusDb"]  # New collection for storing chatbot status
chatai = chatdb["Word"]["WordDb"]  # Existing collection for replies

# Inline keyboard for enabling/disabling chatbot
CHATBOT_ON = [
    [
        InlineKeyboardButton(text="ᴇɴᴀʙʟᴇ", callback_data="enable_chatbot"),
        InlineKeyboardButton(text="ᴅɪsᴀʙʟᴇ", callback_data="disable_chatbot"),
    ],
]

@app.on_message(filters.command("chatbot") & filters.group)
async def chaton(client: Client, message: Message):
    await message.reply_text(
        f"ᴄʜᴀᴛ: {message.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )

# Callback query handler for enabling/disabling the chatbot
@app.on_callback_query(filters.regex("enable_chatbot|disable_chatbot"))
async def callback_handler(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    action = callback_query.data

    if action == "enable_chatbot":
        # Save status to the database
        status_db.update_one(
            {"chat_id": chat_id},
            {"$set": {"status": "enabled"}},
            upsert=True
        )
        await callback_query.answer("Chatbot has been enabled!")
    elif action == "disable_chatbot":
        # Save status to the database
        status_db.update_one(
            {"chat_id": chat_id},
            {"$set": {"status": "disabled"}},
            upsert=True
        )
        await callback_query.answer("Chatbot has been disabled!")

    # Optionally, you can edit the message to reflect the status change
    await callback_query.message.edit_text(
        f"ᴄʜᴀᴛ: {callback_query.message.chat.title}\n**ᴄʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ {'ᴇɴᴀʙʟᴇᴅ' if action == 'enable_chatbot' else 'ᴅɪsᴀʙʟᴇᴅ'}.**"
    )

# Message handler for text, sticker, photo, and video messages
@app.on_message((filters.text | filters.sticker | filters.photo | filters.video) & filters.group)
async def chatbot_response(client: Client, message: Message):
    # Ignore bot commands
    if message.text.startswith(("!", "/", "?", "@", "#")):
        return

    # Check chatbot status
    chat_status = status_db.find_one({"chat_id": message.chat.id})
    if chat_status and chat_status.get("status") == "disabled":
        return  # Do not respond if the chatbot is disabled

    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    if message.reply_to_message:
        # Save the reply in the database
        await save_reply(message.reply_to_message, message)

    # Get a reply from the database
    reply_data = await get_reply(message.text)

    if reply_data:
        if reply_data['check'] == 'sticker':
            await message.reply_sticker(reply_data['text'])
        elif reply_data['check'] == 'photo':
            await message.reply_photo(reply_data['text'])
        elif reply_data['check'] == 'video':
            await message.reply_video(reply_data['text'])
        else:
            await message.reply_text(reply_data['text'])
    else:
        await message.reply_text("I don't have a reply for this message yet!")

# Function to save a reply in the database
async def save_reply(original_message: Message, reply_message: Message):
    if reply_message.sticker:
        is_chat = chatai.find_one(
            {
                "word": original_message.text,
                "text": reply_message.sticker.file_id,
                "check": "sticker",
                "id": reply_message.sticker.file_unique_id,
            }
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.sticker.file_id,
                    "check": "sticker",
                    "id": reply_message.sticker.file_unique_id,
                }
            )
    elif reply_message.text:
        is_chat = chatai.find_one(
            {"word": original_message.text, "text": reply_message.text}
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.text,
                    "check": "none",
                }
            )

# Function to retrieve a reply from the database
async def get_reply(word: str):
    is_chat = chatai.find({"word": word})
    k = chatai.find_one({"word": word})

    # If no exact match is found, return random replies
    if not k:
        is_chat = chatai.find()
    
    K = [x["text"] for x in is_chat]

    if K:
        hey = random.choice(K)
        return chatai.find_one({"text": hey})
    return None
