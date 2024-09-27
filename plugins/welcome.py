import asyncio
import re
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
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
from pyrogram import filters
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from pytz import timezone
from datetime import datetime

user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

# --------------------------------------------------------------------------------- #


LOGGER = getLogger(__name__)

def convert_to_small_caps(text):
    # Mapping for regular letters to small caps
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘϙʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘϙʀꜱᴛᴜᴠᴡxʏᴢ",
    )
    return text.translate(mapping)


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
    
    
    border_size_violet = 1 
    border_size_blue = 4    
    outline = Image.new("RGBA", (pfp.size[0] + 2 * border_size_violet, pfp.size[1] + 2 * border_size_violet), (0, 0, 0, 0))
    outline_draw = ImageDraw.Draw(outline)
    
    violet = (148, 0, 211, 255)  
    blue = (0, 0, 255, 255)      
    green = (19, 136, 8, 255)    
    
    outline_draw.ellipse((0, 0, outline.size[0], outline.size[1]), outline=violet, width=border_size_violet)
    outline_draw.ellipse((border_size_violet - border_size_blue, border_size_violet - border_size_blue,
                          outline.size[0] - (border_size_violet - border_size_blue),
                          outline.size[1] - (border_size_violet - border_size_blue)), 
                          outline=blue, width=border_size_blue)

    
    outline_draw.ellipse((border_size_violet, border_size_violet,
                          outline.size[0] - border_size_violet,
                          outline.size[1] - border_size_violet), 
                          outline=green, width=border_size_violet)

    outline.paste(pfp, (border_size_violet, border_size_violet), pfp)
    
    return outline

def welcomepic(user_id, user_username, user_names, chat_name, user_photo, chat_photo):
    background = Image.open("assets/wel2.png")
    user_img = Image.open(user_photo).convert("RGBA")
    chat_img = Image.open(chat_photo).convert("RGBA")
    
    chat_img_circle = circle(chat_img, size=(240, 240), brightness_factor=1.2)
    user_img_circle = circle(user_img, size=(232, 232), brightness_factor=1.2)
    
    background.paste(chat_img_circle, (270, 260), chat_img_circle)
    background.paste(user_img_circle, (827, 260), user_img_circle)
    
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("assets/font.ttf", size=32)

  
    saffron = (255, 153, 51)  
    white = (255, 255, 255)   
    green = (19, 136, 8)

    draw.text((510, 517), f"Name:  {user_names}", fill=saffron, font=font)
    draw.text((510, 547), f"User Id:  {user_id}", fill=white, font=font)
    draw.text((510, 580), f"Username:  {user_username}", fill=green, font=font)
    
    background.save(f"downloads/welcome#{user_id}.png")
    return f"downloads/welcome#{user_id}.png"

@app.on_chat_member_updated(filters.group, group=-4)
async def greet_new_members(_, member: ChatMemberUpdated):
    try:
        chat_id = member.chat.id
        chat = await app.get_chat(chat_id)
        user = member.new_chat_member.user
        user_id = user.id
        user_mention = user.mention
        
        if chat.title:
            chat_name = chat.title
        else:
            chat_name = "Anjan Group"
        
        if user.username:
            user_username = f"@{user.username}"
        else:
            user_username = "No Username"

        if user.first_name:
            user_name = user.first_name
        else:
            user_name = "No Name"

        if user.first_name and re.match("^[A-Za-z0-9 ]+$", user.first_name):
            user_names = user.first_name
        else:
            user_names = "New Member"
        # Convert current UTC time to IST (Indian Standard Time)
        ist = timezone('Asia/Kolkata')
        joined_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

        if member.new_chat_member and not member.old_chat_member:
            try:
                users_photo = await app.download_media(
                    user.photo.big_file_id, file_name=f"pp{user.id}.png"
                )
                if users_photo:
                    user_photo = users_photo
                else:
                    user_photo = "assets/nodp.png"
            except AttributeError:
                user_photo = "assets/nodp.png"
                
            try:
                groups_photo = await app.download_media(
                    member.chat.photo.big_file_id, file_name=f"chatpp{chat_id}.png"
                )
                if groups_photo:
                    chat_photo = groups_photo
                else:
                    chat_photo = "assets/nodp.png"
            except AttributeError:
                chat_photo = "assets/nodp.png"
            
            welcomeimg = welcomepic(user_id, user_username, user_names, chat_name, user_photo, chat_photo)
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(f"{convert_to_small_caps('๏ add me in new group ๏')}", url=f"https://t.me/{app.username}?startgroup=true")]]
            )

            if (temp.MELCOW).get(f"welcome-{member.chat.id}") is not None:
                try:
                    await temp.MELCOW[f"welcome-{member.chat.id}"].delete()
                except Exception as e:
                    LOGGER.error(e)
            
            # Modified welcome text
            welcome_text = (
                f"**{convert_to_small_caps('ᴡᴇʟᴄᴍ ᴛᴏ')}** {convert_to_small_caps(chat_name)}\n\n"
                f"**{convert_to_small_caps('ɴᴀᴍᴇ')} :** {convert_to_small_caps(user.first_name)}\n"
                f"**{convert_to_small_caps('ᴜꜱᴇʀ ɪᴅ')} :** `{user_id}`\n"
                f"**{convert_to_small_caps('ᴜꜱᴇʀɴᴀᴍᴇ')} :** [{convert_to_small_caps(user_username)}](tg://openmessage?user_id={user_id})\n"
                f"**{convert_to_small_caps('ᴍᴇɴᴛɪᴏɴ')} :** [ᴏᴘᴇɴ ᴘʀᴏғɪʟᴇ](tg://openmessage?user_id={user_id})\n"
                f"**{convert_to_small_caps('ᴊᴏɪɴᴇᴅ ᴀᴛ')} :** {convert_to_small_caps(joined_time)}"
            )
            await app.send_photo(chat_id, photo=welcomeimg, caption=welcome_text, reply_markup=reply_markup)

    except Exception as e:
        
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
