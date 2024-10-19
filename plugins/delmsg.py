from VIPMUSIC import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, Callbackquery
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

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Function to delete messages
async def delete_messages(client, message, target=None, chat_id=None):
    try:
        deleted_count = 0
        if target:
            user_id = target.id
            last_message_id = 0  # Track the last message fetched
            
            while True:
                message_ids = []
                async for msg in client.search_messages(chat_id, from_user=user_id, limit=100, offset_id=last_message_id):
                    message_ids.append(msg.message_id)
                    last_message_id = msg.message_id

                if not message_ids:
                    break  # No more messages found

                # Now delete all the messages collected
                await client.delete_messages(chat_id, message_ids)
                deleted_count += len(message_ids)

            await message.edit(f"๏ ᴅᴇʟᴇᴛᴇᴅ {deleted_count} ᴍᴇssᴀɢᴇs ғʀᴏᴍ {target.mention}")
        else:
            await message.edit("๏ ᴇʀʀᴏʀ: No target user provided.")
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

        # Get target user from replied message or user ID
        target = message.reply_to_message.from_user if message.reply_to_message else None
        if not target and len(message.command) > 1:
            user_input = message.command[1]
            try:
                target = await client.get_users(int(user_input) if user_input.isdigit() else user_input)
            except Exception as e:
                await message.reply_text(f"๏ ᴇʀʀᴏʀ: {str(e)}")
                return

        if not target:
            await message.reply_text("๏ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")
            return

        # Confirm deletion with buttons
        chat_id = message.chat.id
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ᴄᴏɴғɪʀᴍ ᴅᴇʟᴇᴛɪᴏɴ", callback_data=f"confirm_delete_user:{chat_id}:{target.id}")],
                [InlineKeyboardButton("ᴄᴀɴᴄᴇʟ", callback_data="cancel_delete")]
            ]
        )
        await message.reply_text(f"๏ ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴍᴇssᴀɢᴇs ғʀᴏᴍ {target.mention}?", reply_markup=keyboard)

    except Exception as e:
        await message.reply_text(f"๏ ᴇʀʀᴏʀ: {str(e)}")

# Callback query handler to process button click
@app.on_callback_query(filters.regex(r"confirm_delete_user:(\d+):(\d+)"))
async def confirm_delete_user(client, callback_query):
    try:
        chat_id, user_id = map(int, callback_query.data.split(":")[1:])
        target = await client.get_users(user_id)

        # Notify that the process has started
        await callback_query.message.edit_text(f"๏ sᴛᴀʀᴛɪɴɢ ᴅᴇʟᴇᴛɪᴏɴ ᴏғ {target.mention}'s ᴍᴇssᴀɢᴇs...")

        # Call the function to delete messages
        await delete_messages(client, callback_query.message, target=target, chat_id=chat_id)

    except Exception as e:
        await callback_query.message.edit_text(f"๏ ᴇʀʀᴏʀ: {str(e)}")

# Callback query handler for cancel
@app.on_callback_query(filters.regex("cancel_delete"))
async def cancel_delete(client, callback_query):
    await callback_query.message.edit_text("๏ ᴅᴇʟᴇᴛɪᴏɴ ᴄᴀɴᴄᴇʟᴇᴅ.")

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

