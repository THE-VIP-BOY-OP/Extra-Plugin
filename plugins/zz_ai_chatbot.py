import random
import requests
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import MONGO_DB_URI as MONGO_URL
from VIPMUSIC import app as nexichat
from MukeshAPI import api

# Emoji List for Reactions
EMOJI_LIST = [
    "👍", "👎", "❤️", "🔥"
]

# Function to send a random emoji reaction
async def react_with_random_emoji(client, message):
    try:
        emoji = random.choice(EMOJI_LIST)
        await client.send_reaction(message.chat.id, message.id, emoji)
    except Exception as e:
        print(f"Failed to send reaction: {str(e)}")

# Function to get random sticker from the sticker pack of the sticker sent by the user
async def get_random_sticker_from_pack(client, message):
    try:
        if message.sticker and message.sticker.set_name:
            sticker_set = await client.get_sticker_set(message.sticker.set_name)
            random_sticker = random.choice(sticker_set.stickers)
            await client.send_sticker(message.chat.id, random_sticker.file_id, reply_to_message_id=message.id)
    except Exception as e:
        print(f"Failed to send random sticker: {str(e)}")

# Convert text to small caps
def to_small_caps(text):
    small_caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ',
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ',
        'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ'
    }
    words = text.split()
    transformed_words = [''.join(small_caps.get(char, char) for char in word.lower()) for word in words]
    return ' '.join(transformed_words)

# Function to truncate text to a specific word limit
def truncate_text(text, max_words=50):
    words = text.split()
    return ' '.join(words[:max_words]) + "..." if len(words) > max_words else text

# Function to handle the "Read More" button click and edit the message with full text
async def handle_read_more(client, callback_query):
    original_text = callback_query.message.reply_to_message.text
    await callback_query.message.edit_text(
        original_text,
        reply_markup=None  # Remove the "Read More" button after expanding the message
    )

# Add a command handler for button clicks
@nexichat.on_callback_query(filters.regex(r"read_more"))
async def on_read_more_button(client, callback_query):
    await handle_read_more(client, callback_query)

# Function to send AI responses with optional "Read More" button for long messages
async def send_ai_response(client, message, response_text):
    truncated_text = truncate_text(response_text)
    
    # Check if message was truncated (i.e., it was long enough to need "Read More")
    if truncated_text.endswith("..."):
        # If the message was truncated, send it with a "Read More" button
        await message.reply_text(
            truncated_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Read More", callback_data="read_more")]
            ]),
            quote=True
        )
    else:
        # If the message was short enough, send it normally
        await message.reply_text(truncated_text, quote=True)

# Chatbot enable/disable command for group chats
@nexichat.on_message(filters.command(["chatbot"]))
async def chatbot_toggle(client, message):
    chatdb = MongoClient(MONGO_URL)
    chatbot = chatdb["Chatbot"]["ChatbotDb"]
    
    if len(message.command) != 2:
        return await message.reply_text("**Usage:** /chatbot [enable|disable]")
    
    status = message.command[1].lower()
    
    if status == "enable":
        chatbot.update_one({"chat_id": message.chat.id}, {"$set": {"enabled": True}}, upsert=True)
        await message.reply_text("**Chatbot enabled!**")
    
    elif status == "disable":
        chatbot.update_one({"chat_id": message.chat.id}, {"$set": {"enabled": False}}, upsert=True)
        await message.reply_text("**Chatbot disabled!**")
    
    else:
        await message.reply_text("**Usage:** /chatbot [enable|disable]")

# Chatbot handler for text and sticker messages
@nexichat.on_message(filters.text | filters.sticker | filters.group, group=4)
async def chatbot_text(client: Client, message: Message):
    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]
    chatbot = chatdb["Chatbot"]["ChatbotDb"]

    # Check if chatbot is enabled for this chat
    is_chatbot_enabled = chatbot.find_one({"chat_id": message.chat.id})
    
    if is_chatbot_enabled and not is_chatbot_enabled.get("enabled", True):
        return
    
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    if message.text:
        try:
            response = api.gemini(message.text)
            x = response.get("results")
            if x:
                formatted_response = to_small_caps(x)
                await send_ai_response(client, message, formatted_response)
            else:
                await message.reply_text(to_small_caps("sᴏʀʀʏ! ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ"), quote=True)
        except requests.exceptions.RequestException:
            pass
    
    # Handle sticker messages by sending a random sticker from the same sticker pack
    elif message.sticker:
        await get_random_sticker_from_pack(client, message)

# Chatbot handler for private messages
@nexichat.on_message(filters.private & filters.text)
async def chatbot_text_private(client: Client, message: Message):
    chatdb = MongoClient(MONGO_URL)
    processed_messages = chatdb["ProcessedMessages"]

    # Only respond if the message is a reply to one of the bot's messages
    if not message.reply_to_message or message.reply_to_message.from_user.id != client.me.id:
        return
    
    # Check if message has already been processed
    if processed_messages.find_one({"message_id": message.message_id}):
        return

    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    # AI-based replies for private chats
    if message.text:
        try:
            response = api.gemini(message.text)
            x = response.get("results")
            if x:
                formatted_response = to_small_caps(truncate_text(x))
                await message.reply_text(formatted_response, quote=True)
            else:
                await message.reply_text(to_small_caps("sᴏʀʀʏ! ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ"), quote=True)
        except requests.exceptions.RequestException:
            pass
    
    # Mark message as processed
    processed_messages.insert_one({"message_id": message.message_id})
