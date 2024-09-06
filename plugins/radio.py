from strings import get_string
import asyncio
import logging
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from config import BANNED_USERS
from VIPMUSIC import app
from VIPMUSIC.utils.database import get_assistant, get_cmode, get_lang, get_playmode, get_playtype
from VIPMUSIC.utils.logger import play_logs
from VIPMUSIC.utils.stream.stream import stream
from VIPMUSIC.misc import SUDOERS

# Radio Station List
RADIO_STATION = {
    "ᴀɪʀ ʙɪʟᴀsᴘᴜʀ": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio110/playlist.m3u8",
    "ᴀɪʀ ʀᴀɪᴘᴜʀ": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio118/playlist.m3u8",
    "ᴄᴀᴘɪᴛᴀʟ ꜰᴍ": "http://media-ice.musicradio.com/CapitalMP3?.mp3&listening-from-radio-garden=1616312105154",
    "ᴇɴɢʟɪsʜ": "https://hls-01-regions.emgsound.ru/11_msk/playlist.m3u8",
    "ᴍɪʀᴄʜɪ": "http://peridot.streamguys.com:7150/Mirchi",
    "ʀᴀᴅɪᴏ ᴛᴏᴅᴀʏ": "http://stream.zenolive.com/8wv4d8g4344tv",
    "ʏᴏᴜᴛᴜʙᴇ": "https://www.youtube.com/live/eu191hR_LEc?si=T-9QYD548jd0Mogp",
    "ᴢᴇᴇ ɴᴇᴡs": "https://www.youtube.com/live/TPcmrPrygDc?si=hiHBkIidgurQAd1P",
    "ᴀᴀᴊ ᴛᴀᴋ": "https://www.youtube.com/live/Nq2wYlWFucg?si=usY4UYiSBInKA0S1",
}


# Function to create triangular buttons dynamically
def create_triangular_buttons():
    buttons = []
    stations = list(RADIO_STATION.keys())
    row_count = 3  # Number of buttons per row
    
    # Iterate through the stations and create buttons
    while stations:
        button_row = []
        for _ in range(min(row_count, len(stations))):
            station_name = stations.pop(0)
            button_row.append(InlineKeyboardButton(station_name, callback_data=f"radio_station_{station_name}"))
        buttons.append(button_row)
    
    return buttons

@app.on_message(
    filters.command(["radio", "radioplayforce", "cradio"]) & filters.group & ~BANNED_USERS
)
async def radio(client, message: Message):
    msg = await message.reply_text("ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ...")

    try:
        userbot = await get_assistant(message.chat.id)
        get = await app.get_chat_member(message.chat.id, userbot.id)

        if get.status == ChatMemberStatus.BANNED:
            return await msg.edit_text(
                text=f"» {userbot.mention} ᴀssɪsᴛᴀɴᴛ ɪs ʙᴀɴɴᴇᴅ ɪɴ {message.chat.title}.\nᴘʟᴇᴀsᴇ ᴜɴʙᴀɴ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ."
            )
    except UserNotParticipant:
        pass

    # Create triangular buttons for available radio stations
    buttons = create_triangular_buttons()

    # Create a textual list of all channels
    channels_list = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(RADIO_STATION.keys())])

    # Send message with buttons and list of channels
    await message.reply_text(
        f"ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴘʟᴀʏ ᴀ ʀᴀᴅɪᴏ ᴄʜᴀɴɴᴇʟ:\n\n"
        f"ᴄʜᴀɴɴᴇʟ ʟɪsᴛ:\n{channels_list}\n\n"
        f"sᴇʟᴇᴄᴛ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴘʟᴀʏ ᴛʜᴇ ʀᴇsᴘᴇᴄᴛɪᴠᴇ ʀᴀᴅɪᴏ sᴛᴀᴛɪᴏɴ.",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

@app.on_callback_query(filters.regex(r"radio_station_(.*)"))
async def play_radio(client, callback_query):
    station_name = callback_query.data.split("_")[-1]
    RADIO_URL = RADIO_STATION.get(station_name)

    if RADIO_URL:
        await callback_query.message.edit_text("ᴏᴋ ʙᴀʙʏ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ sᴛᴀʀᴛɪɴɢ ʏᴏᴜʀ ʀᴀᴅɪᴏ ɪɴ ᴠᴄ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴠᴄ ᴀɴᴅ ᴇɴᴊᴏʏ😁")
        language = await get_lang(callback_query.message.chat.id)
        _ = get_string(language)
        chat_id = callback_query.message.chat.id
        
        try:
            await stream(
                _,
                callback_query.message,
                callback_query.from_user.id,
                RADIO_URL,
                chat_id,
                callback_query.from_user.mention,
                callback_query.message.chat.id,
                video=None,
                streamtype="index",
            )
        except Exception as e:
            ex_type = type(e).__name__
            err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
            await callback_query.message.edit_text(err)
        await play_logs(callback_query.message, streamtype="Radio")
    else:
        await callback_query.message.edit_text("ɪnᴠᴀʟɪᴅ sᴛᴀᴛɪᴏɴ sᴇʟᴇᴄᴛᴇᴅ!")

__MODULE__ = "Radio"
__HELP__ = """
/radio - ᴛᴏ ᴘʟᴀʏ ʀᴀᴅɪᴏ ɪɴ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.
"""
