import asyncio
import time
from logging import getLogger
from time import time
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont
from pyrogram import enums, filters
from pyrogram.types import ChatMemberUpdated
import config
from VIPMUSIC import app
from VIPMUSIC.utils.database import get_assistant

# Define a dictionary to track the last message timestamp for each user
user_last_message_time = {}
user_command_count = {}
# Define the threshold for command spamming (e.g., 20 commands within 60 seconds)
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

# --------------------------------------------------------------------------------- #


LOGGER = getLogger(__name__)


class WelDatabase:
    def __init__(self):
        self.data = {}

    async def find_one(self, chat_id):
        return chat_id in self.data

    async def add_wlcm(self, chat_id):
        if chat_id not in self.data:
            self.data[chat_id] = {"state": "on"}  # Default state is "on"

    async def rm_wlcm(self, chat_id):
        if chat_id in self.data:
            del self.data[chat_id]


wlcm = WelDatabase()


class temp:
    ME = None
    CURRENT = 2
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None


@app.on_message(filters.command("welcome") & ~filters.private)
async def auto_state(_, message):
    user_id = message.from_user.id
    current_time = time()
    # Update the last message timestamp for the user
    last_message_time = user_last_message_time.get(user_id, 0)

    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        # If less than the spam window time has passed since the last message
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            # Block the user if they exceed the threshold
            hu = await message.reply_text(
                f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**"
            )
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        # If more than the spam window time has passed, reset the command count and update the message timestamp
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    usage = "**ᴜsᴀɢᴇ:**\n**⦿ /awelcome [on|off]**"
    if len(message.command) == 1:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    if user.status in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ):
        A = await wlcm.find_one(chat_id)
        state = message.text.split(None, 1)[1].strip().lower()
        if state == "off":
            if A:
                await message.reply_text(
                    "**ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ !**"
                )
            else:
                await wlcm.add_wlcm(chat_id)
                await message.reply_text(
                    f"**ᴅɪsᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ** {message.chat.title} ʙʏ ᴀssɪsᴛᴀɴᴛ"
                )
        elif state == "on":
            if not A:
                await message.reply_text("**ᴇɴᴀʙʟᴇᴅ ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ.**")
            else:
                await wlcm.rm_wlcm(chat_id)
                await message.reply_text(
                    f"**ᴇɴᴀʙʟᴇᴅ ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ ** {message.chat.title}"
                )
        else:
            await message.reply_text(usage)
    else:
        await message.reply(
            "**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ!**"
        )

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
from pyrogram import filters
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

# Other necessary imports...

def circle(pfp, size=(80, 80), brightness_factor=10):
    pfp = pfp.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    pfp = ImageEnhance.Brightness(pfp).enhance(brightness_factor)
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.Resampling.LANCZOS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp
"""
def welcomepic(user_id, chat_name, user_photo, chat_photo):
    background = Image.open("assets/wel2.png")
    user_img = Image.open(user_photo).convert("RGBA")
    chat_img = Image.open(chat_photo).convert("RGBA")
    
    user_img_circle = circle(user_img, size=(200, 200), brightness_factor=1.2)
    chat_img_circle = circle(chat_img, size=(200, 200), brightness_factor=1.2)
    
    background.paste(chat_img_circle, (280, 260), chat_img_circle)
    background.paste(user_img_circle, (827, 260), user_img_circle)
    
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("assets/font.ttf", size=45)
   
    draw.text((350, 100), f"WELCOME IN NEW GROUP", fill="red", font=font)
    draw.text((350, 200), f"Chat: {chat_name}", fill="black", font=font)
    draw.text((420, 570), f"Id:: {user_id}", fill="blue", font=font)
    
    background.save(f"downloads/welcome#{user_id}.png")
    return f"downloads/welcome#{user_id}.png"
"""

from PIL import Image, ImageDraw, ImageFont

def circle(image, size, brightness_factor=1.0):
    # Resize and apply a circular mask to the image
    image = image.resize(size, Image.ANTIALIAS)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    image.putalpha(mask)
    
    # Brightness enhancement (optional)
    image = ImageEnhance.Brightness(image).enhance(brightness_factor)
    return image

def welcomepic(user_id, chat_name, user_photo, chat_photo):
    background = Image.open("assets/wel2.png")
    user_img = Image.open(user_photo).convert("RGBA")
    chat_img = Image.open(chat_photo).convert("RGBA")
    
    # Circle cropping with size 200x200 for both images
    user_img_circle = circle(user_img, size=(200, 200), brightness_factor=1.2)
    chat_img_circle = circle(chat_img, size=(200, 200), brightness_factor=1.2)
    
    # Paste chat image into the left circle at the correct position
    background.paste(chat_img_circle, (100, 130), chat_img_circle)  # Adjusted position
    
    # Paste user image into the right circle at the correct position
    background.paste(user_img_circle, (850, 130), user_img_circle)  # Adjusted position
    
    # Draw text for chat_name and user_id
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("assets/font.ttf", size=45)
    
    # Big rectangle: Center the chat_name and use a stylish color (gradient or vibrant color)
    chat_name_position = (background.width // 2 - draw.textsize(chat_name, font=font)[0] // 2, 400)
    draw.text(chat_name_position, f"Chat: {chat_name}", fill="#FF69B4", font=font)  # Using a vibrant color (Hot Pink)
    
    # Small rectangle: Center the user_id and use a stylish color
    user_id_text = f"Id: {user_id}"
    user_id_position = (background.width // 2 - draw.textsize(user_id_text, font=font)[0] // 2, 570)
    draw.text(user_id_position, user_id_text, fill="#4682B4", font=font)  # Steel Blue color for stylish look
    
    
    background.save(f"downloads/welcome#{user_id}.png")
    return f"downloads/welcome#{user_id}.png"

# Example call



@app.on_chat_member_updated(filters.group, group=-4)
async def greet_new_members(_, member: ChatMemberUpdated):
    try:
        chat_id = member.chat.id
        chat = await app.get_chat(chat_id)
        
        # Prioritize the member's username first, then chat's username, then chat title
        user = member.new_chat_member.user
        user_id = user.id
        user_mention = user.mention
        
        # First priority: member's username
        if user.username:
            chat_name = f"@{user.username}"
        # Second priority: group's username
        elif chat.username:
            chat_name = f"@{chat.username}"
        # Final fallback: chat title
        else:
            chat_name = chat.title
        
        if member.new_chat_member and not member.old_chat_member:
            try:
                pic = await app.download_media(
                    user.photo.big_file_id, file_name=f"pp{user.id}.png"
                )
            except AttributeError:
                pic = "VIPMUSIC/assets/upic.png"
            
            # Get chat profile photo
            try:
                chat_pic = await app.download_media(
                    member.chat.photo.big_file_id, file_name=f"chatpp{chat_id}.png"
                )
            except AttributeError:
                chat_pic = "VIPMUSIC/assets/upic.png"
            
            welcomeimg = welcomepic(user_id, chat_name, pic, chat_pic)
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(f"✪ ᴛᴀᴘ ᴛᴏ ᴄʟᴏsᴇ ✪", url=f"https://t.me/ok_win_predictions")]]
            )

            if (temp.MELCOW).get(f"welcome-{member.chat.id}") is not None:
                try:
                    await temp.MELCOW[f"welcome-{member.chat.id}"].delete()
                except Exception as e:
                    LOGGER.error(e)
            
            welcome_text = (
                f"**๏ ʜᴇʟʟᴏ ☺️** {user_mention}\n\n"
                f"**๏ ᴡᴇʟᴄᴏᴍᴇ ɪɴ 🥀** {chat_name}\n\n"
                f"**๏ ʜᴀᴠᴇ ᴀ ɴɪᴄᴇ ᴅᴀʏ ✨** @{user.username if user.username else ''}"
            )
            await app.send_photo(chat_id, photo=welcomeimg, caption=welcome_text, reply_markup=reply_markup)

    except Exception as e:
        LOGGER.exception(f"Error in greeting new members: {e}")
        return

__MODULE__ = "Wᴇᴄᴏᴍᴇ"
__HELP__ = """
## Aᴜᴛᴏ-Wᴇᴄᴏᴍᴇ Mᴏᴅᴜᴇ Cᴏᴍᴍᴀɴᴅs

### Cᴏᴍᴍᴀɴᴅ: /ᴀᴡᴇᴄᴏᴍᴇ
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
Eɴᴀʙᴇs ᴏʀ ᴅɪsᴀʙᴇs ᴛʜᴇ ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ ғᴇᴀᴛᴜʀᴇ ɪɴ ᴀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ.

**Usᴀɢᴇ:**
/awelcome [ᴏɴ|ᴏғғ]

**Dᴇᴛᴀɪs:**
- ᴏɴ: Eɴᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴs.
- ᴏғғ: Dɪsᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴs.

**Nᴏᴛᴇs:**
- Oɴʏ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs ᴀɴᴅ ᴛʜᴇ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.

### Sᴘᴀᴍ Pʀᴏᴛᴇᴄᴛɪᴏɴ
Pʀᴇᴠᴇɴᴛs ᴄᴏᴍᴍᴀɴᴅ sᴘᴀᴍᴍɪɴɢ. Iғ ᴀ ᴜsᴇʀ sᴇɴᴅs ᴍᴏʀᴇ ᴛʜᴀɴ 2 ᴄᴏᴍᴍᴀɴᴅs ᴡɪᴛʜɪɴ 5 sᴇᴄᴏɴᴅs, ᴛʜᴇʏ ᴡɪ ʙᴇ ᴡᴀʀɴᴇᴅ ᴀɴᴅ ᴛᴇᴍᴘᴏʀᴀʀɪʏ ʙᴏᴄᴋᴇᴅ.

### Wᴇᴄᴏᴍᴇ Nᴇᴡ Mᴇᴍʙᴇʀs
Aᴜᴛᴏᴍᴀᴛɪᴄᴀʏ sᴇɴᴅs ᴀ ᴡᴇᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ɴᴇᴡ ᴍᴇᴍʙᴇʀs ᴡʜᴏ ᴊᴏɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ.

**Bᴇʜᴀᴠɪᴏʀ:**
- Sᴇɴᴅs ᴀ ᴡᴇᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴍᴇɴᴛɪᴏɴɪɴɢ ᴛʜᴇ ɴᴇᴡ ᴜsᴇʀ.
- Tʜᴇ ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴀғᴛᴇʀ ᴀ 3-sᴇᴄᴏɴᴅ ᴅᴇᴀʏ.

### Exᴀᴍᴘᴇs
- /awelcome on: Eɴᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ.
- /awelcome off: Dɪsᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ.

Iғ ᴀ ᴜsᴇʀ sᴇɴᴅs ᴍᴜᴛɪᴘᴇ ᴄᴏᴍᴍᴀɴᴅs ǫᴜɪᴄᴋʏ:
Tʜᴇʏ ᴡɪ ʀᴇᴄᴇɪᴠᴇ ᴀ sᴘᴀᴍ ᴡᴀʀɴɪɴɢ.
"""
