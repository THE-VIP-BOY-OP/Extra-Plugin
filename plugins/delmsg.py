from VIPMUSIC import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from VIPMUSIC.misc import SUDOERS
from pyrogram.errors import UserNotParticipant
from utils.permissions import adminsOnly, member_permissions
from config import BANNED_USERS

async def is_admin_or_sudo(client, chat_id, user_id):
    if user_id in SUDOERS:
        return True
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except UserNotParticipant:
        return False
    except Exception:
        return False

@app.on_message(filters.command("purgeuser") & ~filters.private)
@adminsOnly("can_delete_messages")
async def purge_user_func(_, message: Message):
    # Get the user from reply, mention, or username/ID
    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
    else:
        if len(message.command) < 2:
            return await message.reply_text("Please reply to a user or provide a username/user ID.")

        user_input = message.command[1]
        if user_input.isdigit():  # If input is a user ID
            user = int(user_input)
        else:  # Otherwise, treat as username
            try:
                user = (await app.get_users(user_input)).id
            except Exception as e:
                return await message.reply_text(f"Error: {str(e)}")
    
    # Get chat ID and collect message IDs for the specific user
    chat_id = message.chat.id
    message_ids = []
    
    async for msg in app.search_messages(chat_id, from_user=user):
        message_ids.append(msg.id)
        
        if len(message_ids) == 100:
            await app.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=True,
            )
            message_ids = []

    # Delete any remaining messages
    if len(message_ids) > 0:
        await app.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=True,
        )

    await message.reply_text(f"All messages from user {user} have been deleted.")
@app.on_message(filters.command(["deleteallgroup", "deleteallgroupmsg", "delallgroupmessage", "cleangroupmsg"]) & filters.group)
async def delete_all_group_messages(client, message):
    try:
        if not await is_admin_or_sudo(client, message.chat.id, message.from_user.id):
            await message.reply_text("๏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
            return

        if len(message.command) == 1:
            await message.reply_text("๏ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ɢʀᴏᴜᴘ ID ᴏʀ ᴜsᴇʀɴᴀᴍᴇ.")
            return

        group_input = message.command[1]
        try:
            if group_input.isdigit():
                chat_id = int(group_input)
            else:
                chat = await app.get_chat(group_input)
                chat_id = chat.id
        except Exception as e:
            await message.reply_text(f"๏ ᴇʀʀᴏʀ: {str(e)}")
            return

        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ᴄᴏɴғɪʀᴍ ᴅᴇʟᴇᴛɪᴏɴ", callback_data=f"confirm_delete_group:{chat_id}")],
                [InlineKeyboardButton("ᴄᴀɴᴄᴇʟ", callback_data="cancel_delete")]
            ]
        )
        await message.reply_text("๏ ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴍᴇssᴀɢᴇs ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ?", reply_markup=keyboard)

    except Exception as e:
        await message.reply_text(f"๏ ᴇʀʀᴏʀ: {str(e)}")


@app.on_callback_query(filters.regex(r"^confirm_delete_group:(\d+)"))
async def confirm_delete_group(client, callback_query):
    try:
        chat_id = int(callback_query.data.split(":")[1])
        if not await is_admin_or_sudo(client, chat_id, callback_query.from_user.id):
            await callback_query.answer("๏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴜᴛᴛᴏɴ.", show_alert=True)
            return
        await delete_messages(client, callback_query.message, chat_id=chat_id)
        await callback_query.answer("๏ ᴅᴇʟᴇᴛɪᴏɴ ᴄᴏɴғɪʀᴍᴇᴅ.", show_alert=True)
    except Exception as e:
        await callback_query.message.edit(f"๏ ᴇʀʀᴏʀ: {str(e)}")


@app.on_callback_query(filters.regex(r"cancel_delete"))
async def cancel_delete(client, callback_query):
    try:
        if not await is_admin_or_sudo(client, callback_query.message.chat.id, callback_query.from_user.id):
            await callback_query.answer("๏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴜᴛᴛᴏɴ.", show_alert=True)
            return
        await callback_query.message.edit("๏ ᴅᴇʟᴇᴛɪᴏɴ ᴄᴀɴᴄᴇʟᴇᴅ.")
        await callback_query.answer("๏ ᴄᴀɴᴄᴇʟʟᴇᴅ.", show_alert=True)
    except Exception as e:
        await callback_query.message.edit(f"๏ ᴇʀʀᴏʀ: {str(e)}")

