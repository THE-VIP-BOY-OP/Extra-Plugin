from pyrogram import filters
from pyrogram.enums import ParseMode

from VIPMUSIC import app


@app.on_message(filters.command("me"))
def ids(_, message):
    reply = message.reply_to_message
    if reply:
        message.reply_text(
            f"ʏᴏᴜʀ ɪᴅ: {message.from_user.id}\n{reply.from_user.first_name}'s ɪᴅ: {reply.from_user.id}\nᴄʜᴀᴛ ɪᴅ: {message.chat.id}"
        )
    else:
        message.reply(f"ʏᴏᴜʀ ɪᴅ: {message.from_user.id}\nᴄʜᴀᴛ ɪᴅ: {message.chat.id}")


####


@app.on_message(filters.command("id"))
async def getid(client, message):
    chat = message.chat
    your_id = message.from_user.id
    message_id = message.id
    reply = message.reply_to_message

    text = f"**[ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message_id}`\n"
    text += f"**[ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** `{your_id}`\n"

    if not message.command:
        message.command = message.text.split()

    if not message.command:
        message.command = message.text.split()

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"**[ᴜsᴇʀ ɪᴅ:](tg://user?id={user_id})** `{user_id}`\n"

        except Exception:
            return await message.reply_text("ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.", quote=True)

    text += f"**[ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat.username})** `{chat.id}`\n\n"

    if (
        not getattr(reply, "empty", True)
        and not message.forward_from_chat
        and not reply.sender_chat
    ):
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** `{reply.id}`\n"
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:](tg://user?id={reply.from_user.id})** `{reply.from_user.id}`\n\n"

    if reply and reply.forward_from_chat:
        text += f"ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, {reply.forward_from_chat.title}, ʜᴀs ᴀɴ ɪᴅ ᴏғ `{reply.forward_from_chat.id}`\n\n"
        print(reply.forward_from_chat)

    if reply and reply.sender_chat:
        text += f"ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ, ɪs `{reply.sender_chat.id}`"
        print(reply.sender_chat)

    await message.reply_text(
        text,
        disable_web_page_preview=True,
        parse_mode=ParseMode.DEFAULT,
    )



@app.on_message(filters.command("audioid") & filters.reply)
async def get_audio_id(client, message):
    if message.reply_to_message.audio or message.reply_to_message.voice:
        audio = message.reply_to_message.audio or message.reply_to_message.voice
        file_id = audio.file_id
        await message.reply_text(f"Audio File ID: `{file_id}`")
    else:
        await message.reply_text("Please reply to an audio or voice message.")

@app.on_message(filters.command("videoid") & filters.reply)
async def get_video_id(client, message):
    if message.reply_to_message.video or message.reply_to_message.video_note:
        video = message.reply_to_message.video or message.reply_to_message.video_note
        file_id = video.file_id
        await message.reply_text(f"Video File ID: `{file_id}`")
    else:
        await message.reply_text("Please reply to a video message.")



__MODULE__ = "Usᴇʀɪᴅ"
__HELP__ = """
## Usᴇʀ ID Cᴏᴍᴍᴀɴᴅs Hᴇᴘ

### 1. /id
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
Gᴇᴛ ʏᴏᴜʀ ᴀɴᴅ ʀᴇᴘɪᴇᴅ ᴜsᴇʀ's IDs ᴀᴏɴɢ ᴡɪᴛʜ ᴄʜᴀᴛ ID.

### 2. /id [ᴜsᴇʀɴᴀᴍᴇ/ID]
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
Gᴇᴛ ᴍᴇssᴀɢᴇ ID, ʏᴏᴜʀ ID, ᴜsᴇʀ's ID (ɪғ ᴘʀᴏᴠɪᴅᴇᴅ), ᴀɴᴅ ᴄʜᴀᴛ ID.

### ᴀᴜᴅɪᴏ ᴀɴᴅ ᴠɪᴅᴇᴏ ɪᴅ ᴄᴏᴍᴍᴀɴᴅs

### 3. /audioid
**ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:**
ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ᴀᴜᴅɪᴏ ᴏʀ ᴠᴏɪᴄᴇ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ `/ᴀᴜᴅɪᴏɪᴅ` ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ᴛʜᴇ ғɪʟᴇ ɪᴅ ᴏғ ᴛʜᴇ ᴀᴜᴅɪᴏ ᴍᴇssᴀɢᴇ.

### 4. /videoid
**ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:**
ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴠɪᴅᴇᴏ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ `/ᴠɪᴅᴇᴏɪᴅ` ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ᴛʜᴇ ғɪʟᴇ ɪᴅ ᴏғ ᴛʜᴇ ᴠɪᴅᴇᴏ ᴍᴇssᴀɢᴇ.
**Usᴀɢᴇ:**
/ɪᴅ [ᴜsᴇʀɴᴀᴍᴇ/ID]

**Dᴇᴛᴀɪs:**
- Rᴇᴛʀɪᴇᴠᴇs ᴛʜᴇ ID ᴏғ ᴛʜᴇ ᴍᴇssᴀɢᴇ, ʏᴏᴜʀ Tᴇᴇɢʀᴀᴍ ID, ᴀɴᴅ ᴛʜᴇ ᴄʜᴀᴛ's ID.
- Iғ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ID ɪs ᴘʀᴏᴠɪᴅᴇᴅ, ᴀsᴏ ʀᴇᴛʀɪᴇᴠᴇs ᴛʜᴇ ID ᴏғ ᴛʜᴇ sᴘᴇᴄɪғɪᴇᴅ ᴜsᴇʀ.
- Aᴅᴅɪᴛɪᴏɴᴀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ sᴜᴄʜ ᴀs ʀᴇᴘɪᴇᴅ ᴍᴇssᴀɢᴇ ID ᴀɴᴅ ᴄʜᴀᴛ ID ɪs ᴘʀᴏᴠɪᴅᴇᴅ ɪғ ᴀᴘᴘɪᴄᴀʙᴇ.

**Exᴀᴍᴘᴇs:**
- `/ɪᴅ ᴜsᴇʀɴᴀᴍᴇ`
- `/ɪᴅ 123456789`
"""
