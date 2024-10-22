import asyncio
import time
from logging import getLogger
from time import time

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont
from pyrogram import enums, filters
from pyrogram.types import ChatMemberUpdated

from VIPMUSIC import app
from VIPMUSIC.utils.database import get_assistant
from pymongo import MongoClient
from config import MONGO_DB_URI

# Define a dictionary to track the last message timestamp for each user
user_last_message_time = {}
user_command_count = {}
# Define the threshold for command spamming (e.g., 20 commands within 60 seconds)
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

LOGGER = getLogger(__name__)

class temp:
    ME = None
    CURRENT = 2
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None


# Database setup for welcome status
awelcomedb = MongoClient(MONGO_DB_URI)
astatus_db = awelcomedb.awelcome_status_db.status

async def get_awelcome_status(chat_id):
    status = astatus_db.find_one({"chat_id": chat_id})
    if status:
        return status.get("welcome", "on")
    return "on"

async def set_awelcome_status(chat_id, state):
    astatus_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": state}},
        upsert=True
    )

# Command to toggle welcome message
@app.on_message(filters.command("awelcome") & ~filters.private)
async def auto_state(_, message):
    user_id = message.from_user.id
    current_time = time()

    last_message_time = user_last_message_time.get(user_id, 0)
    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(
                f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**"
            )
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    usage = "**ᴜsᴀɢᴇ:**\n**⦿ /awelcome [on|off]**"
    if len(message.command) == 1:
        return await message.reply_text(usage)

    chat_id = message.chat.id
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        state = message.text.split(None, 1)[1].strip().lower()
        current_status = await get_awelcome_status(chat_id)

        if state == "off":
            if current_status == "off":
                await message.reply_text("** ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ!**")
            else:
                await set_awelcome_status(chat_id, "off")
                await message.reply_text(f"**ᴅɪsᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ** {message.chat.title} **ʙʏ ᴀssɪsᴛᴀɴᴛ**")
        elif state == "on":
            if current_status == "on":
                await message.reply_text("**ᴇɴᴀʙʟᴇᴅ ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ!**")
            else:
                await set_awelcome_status(chat_id, "on")
                await message.reply_text(f"**ᴇɴᴀʙʟᴇᴅ ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ** {message.chat.title}")
        else:
            await message.reply_text(usage)
    else:
        await message.reply("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ!**")

# Auto-welcome message for new members
@app.on_chat_member_updated(filters.group, group=5)
async def greet_new_members(_, member: ChatMemberUpdated):
    userbot = await get_assistant(member.chat.id)
    try:
        chat_id = member.chat.id
        welcome_status = await get_awelcome_status(chat_id)
        if welcome_status == "off":
            return

        user = member.new_chat_member.user

        if member.new_chat_member and not member.old_chat_member:
            welcome_text = f"{user.mention}, ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ?"
            await userbot.send_message(chat_id, text=welcome_text)

    except Exception as e:
        return
