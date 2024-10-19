from VIPMUSIC import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from VIPMUSIC.misc import SUDOERS
from pyrogram.errors import UserNotParticipant

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

async def delete_messages_range(client, message, chat_id, repliedmsg_id, purge_to):
    try:
        message_ids = []
        deleted_count = 0

        # Iterate over the range from replied message to purge_to message
        for message_id in range(repliedmsg_id, purge_to):
            message_ids.append(message_id)

            # Max message deletion limit is 100
            if len(message_ids) == 100:
                await client.delete_messages(
                    chat_id=chat_id,
                    message_ids=message_ids,
                    revoke=True  # Deletes for both sides
                )
                deleted_count += len(message_ids)

                # Clear the list and continue to delete the next batch
                message_ids = []

        # Delete any remaining messages that are less than 100
        if message_ids:
            await client.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=True
            )
            deleted_count += len(message_ids)

        await message.edit(f"๏ ᴅᴇʟᴇᴛᴇᴅ {deleted_count} ᴍᴇssᴀɢᴇs.")
    except Exception as e:
        await message.edit(f"๏ ᴇʀʀᴏʀ: {str(e)}")


# Command handler to trigger the delete action
@app.on_message(filters.command(["deleteallmsg", "delallmsg", "deleteallmessage", "delallmessage"]) & filters.group)
async def delete_all_messages(client, message):
    try:
        # Check if user is admin or sudo
        if not await is_admin_or_sudo(client, message.chat.id, message.from_user.id):
            await message.reply_text("๏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
            return

        # Ensure the command is used as a reply to a message to start from
        if not message.reply_to_message:
            await message.reply_text("๏ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs ғʀᴏᴍ.")
            return

        # Check if a range is provided in the command
        if len(message.command) < 2:
            await message.reply_text("๏ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ ᴇɴᴅ ᴍᴇssᴀɢᴇ ɪᴅ.")
            return

        purge_to = int(message.command[1])
        repliedmsg_id = message.reply_to_message.id
        chat_id = message.chat.id

        # Delete messages in the given range
        await delete_messages_range(client, message, chat_id, repliedmsg_id, purge_to)

    except Exception as e:
        await message.reply_text(f"๏ ᴇʀʀᴏʀ: {str(e)}")


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

