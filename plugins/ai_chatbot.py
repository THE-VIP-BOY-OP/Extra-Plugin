import requests
import random
import re
from MukeshAPI import api
from pyrogram import filters
from pyrogram.enums import ChatAction
from VIPMUSIC import app

# List of random emojis for reactions
EMOJI_LIST = ["😃", "😂", "👍", "🔥", "😎", "🤔", "😍", "😅", "🤖", "🎉", "💯", "🕊️"]

# Function to send a random emoji reaction
async def react_with_random_emoji(client, message):
    emoji = random.choice(EMOJI_LIST)
    await app.send_reaction(message.chat.id, message.id, emoji)

# Function to convert text to small caps
def to_small_caps(text):
    small_caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ',
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ',
        'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ'
    }
    return ''.join(small_caps.get(char, char) for char in text.lower())

# Function to determine if the response contains a link
def contains_link(text):
    return bool(re.search(r'http[s]?://', text))

# Function to format the response based on content
def format_response(text):
    if contains_link(text):
        return text
    else:
        return to_small_caps(text)

# Handler for direct messages (DMs)
@app.on_message(filters.private & ~filters.service)
async def gemini_dm_handler(client, message):
    await react_with_random_emoji(client, message)
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    user_input = message.text

    try:
        response = api.gemini(user_input)
        x = response["results"]
        if x:
            formatted_response = format_response(x)
            await message.reply_text(formatted_response, quote=True)
        else:
            await message.reply_text(to_small_caps("sᴏʀʀʏ sɪʀ! ᴘʟᴇᴀsᴇ Tʀʏ ᴀɢᴀɪɴ"), quote=True)
    except requests.exceptions.RequestException as e:
        pass

# Handler for group chats when replying to the bot's message or mentioning the bot
@app.on_message(filters.group)
async def gemini_group_handler(client, message):
    bot_username = (await app.get_me()).username

    # Check if the message is a reply to the bot's message or mentions the bot's username
    if (message.reply_to_message and message.reply_to_message.from_user.id == (await app.get_me()).id) or f"@{bot_username}" in message.text:
        await react_with_random_emoji(client, message)
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)

        user_input = message.text

        try:
            response = api.gemini(user_input)
            x = response["results"]
            if x:
                formatted_response = format_response(x)
                await message.reply_text(formatted_response, quote=True)
            else:
                await message.reply_text(to_small_caps("sᴏʀʀʏ sɪʀ! ᴘʟᴇᴀsᴇ Tʀʏ ᴀɢᴀɪɴ"), quote=True)
        except requests.exceptions.RequestException as e:
            pass
