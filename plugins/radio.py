from strings import get_string
import logging
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, InviteRequestSent, UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from config import BANNED_USERS, adminlist
from VIPMUSIC import app
from VIPMUSIC.misc import SUDOERS
from VIPMUSIC.utils.database import get_assistant, get_cmode, get_lang, get_playmode, get_playtype
from VIPMUSIC.utils.logger import play_logs
from VIPMUSIC.utils.stream.stream import stream

RADIO_STATION = {
    "air bilaspur": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio110/playlist.m3u8",
    "air raipur": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio118/playlist.m3u8",
    "capital fm": "http://media-ice.musicradio.com/CapitalMP3?.mp3&listening-from-radio-garden=1616312105154",
    "english": "https://hls-01-regions.emgsound.ru/11_msk/playlist.m3u8",
    "mirchi": "http://peridot.streamguys.com:7150/Mirchi",
    "radio today": "http://stream.zenolive.com/8wv4d8g4344tv",
    "youtube": "https://www.youtube.com/live/eu191hR_LEc?si=T-9QYD548jd0Mogp",
    "zee news": "https://www.youtube.com/live/TPcmrPrygDc?si=hiHBkIidgurQAd1P",
    "aaj tak": "https://www.youtube.com/live/Nq2wYlWFucg?si=usY4UYiSBInKA0S1",
}

@app.on_message(
    filters.command(["radioplayforce", "radio", "cradio"]) & filters.group & ~BANNED_USERS
)
async def radio(client, message: Message):
    msg = await message.reply_text("please wait a moment...")

    # Ensure Assistant is in chat
    try:
        userbot = await get_assistant(message.chat.id)
        get = await app.get_chat_member(message.chat.id, userbot.id)
    except ChatAdminRequired:
        return await msg.edit_text(
            f"I don't have permissions to invite users for inviting {userbot.mention} assistant."
        )
    if get.status == ChatMemberStatus.BANNED:
        return await msg.edit_text(
            text=f"{userbot.mention} assistant is banned in this chat.\nPlease unban the assistant and try again."
        )

    await msg.delete()

    # Create buttons in a triangular shape
    buttons = []
    row_count = 3
    row = []
    
    for idx, (name, url) in enumerate(RADIO_STATION.items(), 1):
        row.append(InlineKeyboardButton(text=str(idx), callback_data=f"radio_{name}"))
        if len(row) == row_count:  # If the row has enough buttons for the current row
            buttons.append(row)
            row_count -= 1  # Decrease the number of buttons in the next row
            row = []
        if row_count == 0:
            break

    if row:  # Append any remaining buttons
        buttons.append(row)

    # Send message with buttons
    await message.reply_text(
        "please click below button to play radio channel.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(r"radio_(.*)"))
async def radio_callback(client, callback_query):
    station_name = callback_query.data.split("_")[1]
    RADIO_URL = RADIO_STATION.get(station_name)
    
    if not RADIO_URL:
        await callback_query.answer("Station not found!", show_alert=True)
        return
    
    message = callback_query.message
    user_id = callback_query.from_user.id
    chat_id = message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)
    
    playmode = await get_playmode(chat_id)
    playty = await get_playtype(chat_id)
    
    if playty != "Everyone" and user_id not in SUDOERS:
        admins = adminlist.get(chat_id)
        if not admins or user_id not in admins:
            return await message.reply_text(_["play_4"])
    
    try:
        await stream(
            _,
            message,
            user_id,
            RADIO_URL,
            chat_id,
            callback_query.from_user.mention,
            chat_id,
            streamtype="index",
        )
        await play_logs(message, streamtype="Radio")
    except Exception as e:
        err_msg = f"Error occurred: {type(e).__name__}"
        await message.edit_text(err_msg)
