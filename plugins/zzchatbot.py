import random
from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient
from pyrogram import Client
from pyrogram import filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from config import MONGO_DB_URI as MONGO_URL
from VIPMUSIC import app

# MongoDB connection
chatdb = MongoClient(MONGO_URL)
status_db = chatdb["ChatBotStatusDb"]["StatusCollection"]  # Make sure to reference a collection
chatai = chatdb["Word"]["WordDb"]  # Existing collection for replies



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

@app.on_callback_query(filters.regex("enable_chatbot|disable_chatbot"))
async def callback_handler(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    action = callback_query.data

    if action == "enable_chatbot":
        status_db.update_one(
            {"chat_id": chat_id},
            {"$set": {"status": "enabled"}},
            upsert=True
        )
        await callback_query.answer("Chatbot has been enabled!")
    elif action == "disable_chatbot":
        status_db.update_one(
            {"chat_id": chat_id},
            {"$set": {"status": "disabled"}},
            upsert=True
        )
        await callback_query.answer("Chatbot has been disabled!")

    await callback_query.message.edit_text(
        f"ᴄʜᴀᴛ: {callback_query.message.chat.title}\n**ᴄʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ {'ᴇɴᴀʙʟᴇᴅ' if action == 'enable_chatbot' else 'ᴅɪsᴀʙʟᴇᴅ'}.**"
    )

@app.on_message((filters.text | filters.sticker | filters.photo | filters.video) & filters.group)
async def chatbot_response(client: Client, message: Message):
    # Check if the message is a command
    if message.text and message.text.startswith(("/", "!", "?", "@")):
        return

    # Check chatbot status (Ensure status_db is a collection, not a database)
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
    elif reply_message.photo:
        is_chat = chatai.find_one({"word": original_message.text, "text": reply_message.photo.file_id, "check": "photo"})
        if not is_chat:
            chatai.insert_one({
                "word": original_message.text,
                "text": reply_message.photo.file_id,
                "check": "photo"
            })
    elif reply_message.video:
        is_chat = chatai.find_one({"word": original_message.text, "text": reply_message.video.file_id, "check": "video"})
        if not is_chat:
            chatai.insert_one({
                "word": original_message.text,
                "text": reply_message.video.file_id,
                "check": "video"
            })
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

async def get_reply(word: str):
    is_chat = list(chatai.find({"word": word}))
    k = chatai.find_one({"word": word})

    if not k:
        is_chat = list(chatai.find())

    K = [x["text"] for x in is_chat]

    if K:
        hey = random.choice(K)
        return chatai.find_one({"text": hey})
    return None
