from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup

import config
from VIPMUSIC import app as nexichat
from pymongo import MongoClient
VIPdb = MongoClient(config.MONGO_DB_URI)
VIP = VIPdb["VIPDb"]["VIP"]


@nexichat.on_callback_query()
async def cb_handler(_, query: CallbackQuery):
    if query.data == "HELPSS":
        await query.message.edit_text("help")
            
    elif query.data == "addchat":
        user_id = query.from_user.id
        user_status = (await query.message.chat.get_member(user_id)).status
        if user_status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            return await query.answer(
                "ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴇᴠᴇɴ ᴀɴ ᴀᴅᴍɪɴ, ᴅᴏɴ'ᴛ ᴛʀʏ ᴛʜɪs ᴇxᴘʟᴏsɪᴠᴇ sʜɪᴛ!",
                show_alert=True,
            )
        else:
            is_VIP = VIP.find_one({"chat_id": query.message.chat.id})
            if not is_VIP:
                await query.edit_message_text(f"**ᴄʜᴀᴛ-ʙᴏᴛ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ.**")
            if is_VIP:
                VIP.delete_one({"chat_id": query.message.chat.id})
                await query.edit_message_text(
                    f"**ᴄʜᴀᴛ-ʙᴏᴛ ᴇɴᴀʙʟᴇᴅ ʙʏ** {query.from_user.mention}."
                )
    elif query.data == "rmchat":
        user_id = query.from_user.id
        user_status = (await query.message.chat.get_member(user_id)).status
        if user_status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            await query.answer(
                "ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴇᴠᴇɴ ᴀɴ ᴀᴅᴍɪɴ, ᴅᴏɴ'ᴛ ᴛʀʏ ᴛʜɪs ᴇxᴘʟᴏsɪᴠᴇ sʜɪᴛ!",
                show_alert=True,
            )
            return
        else:
            is_VIP = VIP.find_one({"chat_id": query.message.chat.id})
            if not is_VIP:
                VIP.insert_one({"chat_id": query.message.chat.id})
                await query.edit_message_text(
                    f"**ᴄʜᴀᴛ-ʙᴏᴛ ᴅɪsᴀʙʟᴇᴅ ʙʏ** {query.from_user.mention}."
                )
            if is_VIP:
                await query.edit_message_text("**ᴄʜᴀᴛ-ʙᴏᴛ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ.**")



import random
from Abg.chat_status import adminsOnly
from VIPMUSIC.utils.database import add_served_chat as add_served_chats
from VIPMUSIC.utils.database import add_served_user as add_served_users
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message
from config import OWNER_ID as OWNER
from config import MONGO_DB_URI as MONGO_URL

def is_admins(func: Callable) -> Callable:
    async def non_admin(c: nexichat, m: Message):
        if m.from_user.id == OWNER:
            return await func(c, m)

        admin = await c.get_chat_member(m.chat.id, m.from_user.id)
        if admin.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await func(c, m)

    return non_admin


CHATBOT_ON = [
    [
        InlineKeyboardButton(text="ᴇɴᴀʙʟᴇ", callback_data=f"addchat"),
        InlineKeyboardButton(text="ᴅɪsᴀʙʟᴇ", callback_data=f"rmchat"),
    ],
]


@nexichat.on_cmd("chatbot", group_only=True)
@adminsOnly("can_delete_messages")
async def chaton_(_, m: Message):
    await m.reply_text(
        f"ᴄʜᴀᴛ: {m.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )
    return


@nexichat.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_text(client: Client, message: Message):
    try:
        if (
            message.text.startswith("!")
            or message.text.startswith("/")
            or message.text.startswith("?")
            or message.text.startswith("@")
            or message.text.startswith("#")
        ):
            return
    except Exception:
        pass

    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]

    # Only trigger bot reply if bot's message is being replied to or its username is mentioned
    if not message.reply_to_message and client.username.lower() not in message.text.lower():
        return

    if not message.reply_to_message:
        VIPdb = MongoClient(MONGO_URL)
        VIP = VIPdb["VIPDb"]["VIP"]
        is_VIP = VIP.find_one({"chat_id": message.chat.id})
        if not is_VIP:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            K = []
            is_chat = chatai.find({"word": message.text})
            k = chatai.find_one({"word": message.text})

            # Modification: If no saved reply is found, send a random reply
            if not k:
                # Fetch all random replies if no exact match is found
                is_chat = chatai.find()
            for x in is_chat:
                K.append(x["text"])

            hey = random.choice(K)
            is_text = chatai.find_one({"text": hey})
            Yo = is_text["check"]
            if Yo == "sticker":
                await message.reply_sticker(f"{hey}")
            if not Yo == "sticker":
                await message.reply_text(f"{hey}")

    if message.reply_to_message:
        VIPdb = MongoClient(MONGO_URL)
        VIP = VIPdb["VIPDb"]["VIP"]
        is_VIP = VIP.find_one({"chat_id": message.chat.id})
        if message.reply_to_message.from_user.id == client.id:
            if not is_VIP:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                K = []
                is_chat = chatai.find({"word": message.text})
                k = chatai.find_one({"word": message.text})

                # Modification: If no saved reply is found, send a random reply
                if not k:
                    # Fetch all random replies if no exact match is found
                    is_chat = chatai.find()
                for x in is_chat:
                    K.append(x["text"])

                hey = random.choice(K)
                is_text = chatai.find_one({"text": hey})
                Yo = is_text["check"]
                if Yo == "sticker":
                    await message.reply_sticker(f"{hey}")
                if not Yo == "sticker":
                    await message.reply_text(f"{hey}")
        if not message.reply_to_message.from_user.id == client.id:
            # Save replies between users
            if message.sticker:
                is_chat = chatai.find_one(
                    {
                        "word": message.reply_to_message.text,
                        "id": message.sticker.file_unique_id,
                    }
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": message.reply_to_message.text,
                            "text": message.sticker.file_id,
                            "check": "sticker",
                            "id": message.sticker.file_unique_id,
                        }
                    )
            if message.text:
                is_chat = chatai.find_one(
                    {"word": message.reply_to_message.text, "text": message.text}
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": message.reply_to_message.text,
                            "text": message.text,
                            "check": "none",
                        }
                    )


@nexichat.on_message(
    (filters.sticker | filters.group | filters.text) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_sticker(client: Client, message: Message):
    await add_served_chats(message.chat.id)
    try:
        if (
            message.text.startswith("!")
            or message.text.startswith("/")
            or message.text.startswith("?")
            or message.text.startswith("@")
            or message.text.startswith("#")
        ):
            return
    except Exception:
        pass

    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]

    # Only trigger bot reply if bot's message is being replied to or its username is mentioned
    if not message.reply_to_message and client.username.lower() not in message.text.lower():
        return

    if not message.reply_to_message:
        VIPdb = MongoClient(MONGO_URL)
        VIP = VIPdb["VIPDb"]["VIP"]
        is_VIP = VIP.find_one({"chat_id": message.chat.id})
        if not is_VIP:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            K = []
            is_chat = chatai.find({"word": message.text})
            k = chatai.find_one({"word": message.text})

            # Modification: If no saved reply is found, send a random reply
            if not k:
                # Fetch all random replies if no exact match is found
                is_chat = chatai.find()
            for x in is_chat:
                K.append(x["text"])

            hey = random.choice(K)
            is_text = chatai.find_one({"text": hey})
            Yo = is_text["check"]
            if Yo == "sticker":
                await message.reply_sticker(f"{hey}")
            if not Yo == "sticker":
                await message.reply_text(f"{hey}")

    if message.reply_to_message:
        VIPdb = MongoClient(MONGO_URL)
        VIP = VIPdb["VIPDb"]["VIP"]
        is_VIP = VIP.find_one({"chat_id": message.chat.id})
        if message.reply_to_message.from_user.id == client.id:
            if not is_VIP:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                K = []
                is_chat = chatai.find({"word": message.text})
                k = chatai.find_one({"word": message.text})

                # Modification: If no saved reply is found, send a random reply
                if not k:
                    # Fetch all random replies if no exact match is found
                    is_chat = chatai.find()
                for x in is_chat:
                    K.append(x["text"])

                hey = random.choice(K)
                is_text = chatai.find_one({"text": hey})
                Yo = is_text["check"]
                if Yo == "sticker":
                    await message.reply_sticker(f"{hey}")
                if not Yo == "sticker":
                    await message.reply_text(f"{hey}")
        if not message.reply_to_message.from_user.id == client.id:
            # Save replies between users
            if message.sticker:
                is_chat = chatai.find_one(
                    {
                        "word": message.reply_to_message.text,
                        "id": message.sticker.file_unique_id,
                    }
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": message.reply_to_message.text,
                            "text": message.sticker.file_id,
                            "check": "sticker",
                            "id": message.sticker.file_unique_id,
                        }
                    )
            if message.text:
                is_chat = chatai.find_one(
                    {"word": message.reply_to_message.text, "text": message.text}
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": message.reply_to_message.text,
                            "text": message.text,
                            "check": "none",
                        }
                    )
