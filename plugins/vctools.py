from pyrogram import *
from pyrogram import filters
from pyrogram.types import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from VIPMUSIC import app


# vc on
@app.on_message(filters.video_chat_started)
async def brah(_, msg):
    await msg.reply("**😍ᴠɪᴅᴇᴏ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ🥳**")


# vc off
@app.on_message(filters.video_chat_ended)
async def brah2(_, msg):
    await msg.reply("**😕ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ💔**")


# invite members on vc
@app.on_message(filters.video_chat_members_invited)
async def brah3(app: app, message: Message):
    text = f"➻ {message.from_user.mention}\n\n**๏ ɪɴᴠɪᴛɪɴɢ ɪɴ ᴠᴄ ᴛᴏ :**\n\n**➻ **"
    x = 0
    for user in message.video_chat_members_invited.users:
        try:
            text += f"[{user.first_name}](tg://user?id={user.id}) "
            x += 1
        except Exception:
            pass

    try:
        invite_link = await app.export_chat_invite_link(message.chat.id)
        add_link = f"https://t.me/{app.username}?startgroup=true"
        reply_text = f"{text} 🤭🤭"

        await message.reply(
            reply_text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text="๏ ᴊᴏɪɴ ᴠᴄ ๏", url=add_link)],
                ]
            ),
        )
    except Exception as e:
        print(f"Error: {e}")


####


@app.on_message(filters.command("math", prefixes="/"))
def calculate_math(client, message):
    expression = message.text.split("/math ", 1)[1]
    try:
        result = eval(expression)
        response = f"ᴛʜᴇ ʀᴇsᴜʟᴛ ɪs : {result}"
    except:
        response = "ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇssɪᴏɴ"
    message.reply(response)


@app.on_message(filters.command(["spg"], ["/", "!", "."]))
async def search(event):
    msg = await event.respond("Searching...")
    async with aiohttp.ClientSession() as session:
        start = 1
        async with session.get(
            f"https://content-customsearch.googleapis.com/customsearch/v1?cx=ec8db9e1f9e41e65e&q={event.text.split()[1]}&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM&start={start}",
            headers={"x-referer": "https://explorer.apis.google.com"},
        ) as r:
            response = await r.json()
            result = ""

            if not response.get("items"):
                return await msg.edit("No results found!")
            for item in response["items"]:
                title = item["title"]
                link = item["link"]
                if "/s" in item["link"]:
                    link = item["link"].replace("/s", "")
                elif re.search(r"\/\d", item["link"]):
                    link = re.sub(r"\/\d", "", item["link"])
                if "?" in link:
                    link = link.split("?")[0]
                if link in result:
                    # remove duplicates
                    continue
                result += f"{title}\n{link}\n\n"
            prev_and_next_btns = [
                Button.inline("▶️Next▶️", data=f"next {start+10} {event.text.split()[1]}")
            ]
            await msg.edit(result, link_preview=False, buttons=prev_and_next_btns)
            await session.close()


__MODULE__ = "Mᴀᴛʜ"
__HELP__ = """

## Mᴀᴛʜ Cᴏᴍᴍᴀɴᴅ Hᴇᴘ

### 1. /ᴍᴀᴛʜ [ᴇxᴘʀᴇssɪᴏɴ]
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
Cᴀᴄᴜᴀᴛᴇs ᴛʜᴇ ʀᴇsᴜᴛ ᴏғ ᴀ ᴍᴀᴛʜᴇᴍᴀᴛɪᴄᴀ ᴇxᴘʀᴇssɪᴏɴ.

**Usᴀɢᴇ:**
/ᴍᴀᴛʜ [ᴇxᴘʀᴇssɪᴏɴ]

**Dᴇᴛᴀɪs:**
- Sᴜᴘᴘᴏʀᴛs ʙᴀsɪᴄ ᴀʀɪᴛʜᴍᴇᴛɪᴄ ᴏᴘᴇʀᴀᴛɪᴏɴs: ᴀᴅᴅɪᴛɪᴏɴ (+), sᴜʙᴛʀᴀᴄᴛɪᴏɴ (-), ᴍᴜᴛɪᴘɪᴄᴀᴛɪᴏɴ (*), ᴀɴᴅ ᴅɪᴠɪsɪᴏɴ (/).
- Rᴇᴛᴜʀɴs ᴛʜᴇ ʀᴇsᴜᴛ ᴏғ ᴛʜᴇ ᴇxᴘʀᴇssɪᴏɴ.
- Dɪsᴘᴀʏs "Iɴᴠᴀɪᴅ ᴇxᴘʀᴇssɪᴏɴ" ɪғ ᴛʜᴇ ᴇxᴘʀᴇssɪᴏɴ ɪs ɴᴏᴛ ᴠᴀɪᴅ.

## Gᴏᴏɢᴇ Sᴇᴀʀᴄʜ Cᴏᴍᴍᴀɴᴅ Hᴇᴘ

### 1. /sᴘɢ [ǫᴜᴇʀʏ]
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
Sᴇᴀʀᴄʜᴇs Gᴏᴏɢᴇ ᴀɴᴅ ᴅɪsᴘᴀʏs sᴇᴀʀᴄʜ ʀᴇsᴜᴛs.

**Usᴀɢᴇ:**
/sᴘɢ [ǫᴜᴇʀʏ]

**Dᴇᴛᴀɪs:**
- Sᴇᴀʀᴄʜᴇs Gᴏᴏɢᴇ ғᴏʀ ᴛʜᴇ sᴘᴇᴄɪғɪᴇᴅ ǫᴜᴇʀʏ.
- Dɪsᴘᴀʏs sᴇᴀʀᴄʜ ʀᴇsᴜᴛs ᴡɪᴛʜ ᴛɪᴛᴇs ᴀɴᴅ ɪɴᴋs.
- Sᴜᴘᴘᴏʀᴛs ᴘᴀɢɪɴᴀᴛɪᴏɴ ᴡɪᴛʜ ɴᴇxᴛ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴠɪᴇᴡ ᴍᴏʀᴇ ʀᴇsᴜᴛs.
"""
