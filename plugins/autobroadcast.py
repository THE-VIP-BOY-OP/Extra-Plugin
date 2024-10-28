import asyncio

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import AUTO_GCAST, AUTO_GCAST_MSG, LOG_GROUP_ID
from VIPMUSIC import app
from VIPMUSIC.utils.database import get_served_chats

# Convert AUTO_GCAST to boolean based on "On" or "Off"
AUTO_GCASTS = AUTO_GCAST.strip().lower() == "on"

START_IMG_URLS = "https://envs.sh/I0U.jpg"

MESSAGE = f"""**๏ ᴛʜɪs ɪs ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘs + ᴄʜᴀɴɴᴇʟs ᴠᴄ. 💌

🎧 ᴘʟᴀʏ + ᴠᴘʟᴀʏ + ᴄᴘʟᴀʏ 🎧

➥ sᴜᴘᴘᴏʀᴛᴇᴅ ᴡᴇʟᴄᴏᴍᴇ - ʟᴇғᴛ ɴᴏᴛɪᴄᴇ, ᴛᴀɢᴀʟʟ, ᴠᴄᴛᴀɢ, ʙᴀɴ - ᴍᴜᴛᴇ, sʜᴀʏʀɪ, ʟᴜʀɪᴄs, sᴏɴɢ - ᴠɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅ, ᴇᴛᴄ... ❤️

🔐ᴜꜱᴇ » [/start](https://t.me/{app.username}?start=help) ᴛᴏ ᴄʜᴇᴄᴋ ʙᴏᴛ

➲ ʙᴏᴛ :** @{app.username}"""

BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "๏ ᴋɪᴅɴᴀᴘ ᴍᴇ ๏",
                url=f"https://t.me/THE_NANCY_ROBOT?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users",
            )
        ]
    ]
)

caption = f"""{AUTO_GCAST_MSG}""" if AUTO_GCAST_MSG else MESSAGE

TEXT = """**ᴀᴜᴛᴏ ɢᴄᴀsᴛ ɪs ᴇɴᴀʙʟᴇᴅ sᴏ ᴀᴜᴛᴏ ɢᴄᴀsᴛ/ʙʀᴏᴀᴅᴄᴀsᴛ ɪs ᴅᴏɪɴɢ ɪɴ ᴀʟʟ ᴄʜᴀᴛs ᴄᴏɴᴛɪɴᴜᴏᴜsʟʏ.**\n**ɪᴛ ᴄᴀɴ ʙᴇ sᴛᴏᴘᴘᴇᴅ ʙʏ ᴘᴜᴛ ᴠᴀʀɪᴀʙʟᴇ [ᴀᴜᴛᴏ_ɢᴄᴀsᴛ = (Off)]**"""


async def send_text_once():
    try:
        await app.send_message(LOG_GROUP_ID, TEXT)
    except Exception as e:
        pass


async def send_message_to_chats():
    try:
        chats = await get_served_chats()

        for chat_info in chats:
            chat_id = chat_info.get("chat_id")
            if isinstance(chat_id, int):  # Check if chat_id is an integer
                try:
                    await app.send_photo(
                        chat_id,
                        photo=START_IMG_URLS,
                        caption=caption,
                        reply_markup=BUTTON,
                    )
                    await asyncio.sleep(
                        20
                    )  # Sleep for 20 seconds between sending messages
                except Exception as e:
                    pass  # Do nothing if an error occurs while sending message
    except Exception as e:
        pass  # Do nothing if an error occurs while fetching served chats


async def continuous_broadcast():
    await send_text_once()  # Send TEXT once when bot starts

    while True:
        if AUTO_GCASTS:
            try:
                await send_message_to_chats()
            except Exception as e:
                pass

        # Wait for 100000 seconds before next broadcast
        await asyncio.sleep(100000)


# Start the continuous broadcast loop if AUTO_GCASTS is True
if AUTO_GCASTS:
    asyncio.create_task(continuous_broadcast())





from pyrogram import filters
from pyrogram.enums import ChatType
from strings import get_string
from VIPMUSIC import app
from VIPMUSIC.utils import VIPbin

from VIPMUSIC.utils.database import get_assistant, get_lang
import asyncio
from os import getenv
from dotenv import load_dotenv
from pyrogram import Client
from dotenv import load_dotenv
import config

from VIPMUSIC.logging import LOGGER
from VIPMUSIC.utils.database import (
    delete_filter,
    get_cmode,
    get_lang,
    is_active_chat,
    is_commanddelete_on,
    is_maintenance,
    is_nonadmin_chat,
    set_loop,
)
from VIPMUSIC.core.call import VIP

from pyrogram import filters
from VIPMUSIC import app
from VIPMUSIC.utils.database import get_assistant
import asyncio

async def continuous_check():
    monitored_chat_id = config.LOG_GROUP_ID  # Replace with your target group chat ID
    prev_members = set()

    while True:
        userbot = await get_assistant(config.LOG_GROUP_ID)
        current_members = set()

        async for m in userbot.get_call_members(monitored_chat_id):
            if not m.is_left:
                current_members.add(m.user.id)

        new_joiners = current_members - prev_members
        leavers = prev_members - current_members

        for user_id in new_joiners:
            user = await app.get_users(user_id)
            await app.send_message(monitored_chat_id, f"{user.mention} has joined the voice chat.")

        for user_id in leavers:
            user = await app.get_users(user_id)
            await app.send_message(monitored_chat_id, f"{user.mention} has left the voice chat.")

        prev_members = current_members
        await asyncio.sleep(1)

if AUTO_GCASTS:
    asyncio.create_task(continuous_check())
