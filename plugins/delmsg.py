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

async def delete_messages(client, message, target=None, chat_id=None):
    try:
        deleted_count = 0
        if target:
            user_id = target.id
            last_message_id = 0  # To keep track of the last message fetched
            while True:
                message_ids = []
                async for msg in app.search_messages(chat_id, from_user=user_id, limit=150, offset_id=last_message_id):
                    message_ids.append(msg.message_id)
                    last_message_id = msg.message_id

                if not message_ids:
                    break  # If no more messages are found, break the loop

                # Now delete all the messages collected
                for msg_id in message_ids:
                    await client.delete_messages(chat_id, msg_id)
                    deleted_count += 1

            await message.edit(f"๏ ᴅᴇʟᴇᴛᴇᴅ {deleted_count} ᴍᴇssᴀɢᴇs ғʀᴏᴍ {target.mention}")
        else:
            await message.edit("๏ ᴇʀʀᴏʀ: No target user provided.")
    except Exception as e:
        await message.edit(f"๏ ᴇʀʀᴏʀ: {str(e)}")


@app.on_message(filters.command(["deleteallmsg", "delallmsg", "deleteallmessage", "delallmessage"]) & filters.group)
async def delete_all_messages(client, message):
    try:
        if not await is_admin_or_sudo(client, message.chat.id, message.from_user.id):
            await message.reply_text("๏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
            return

        if not message.reply_to_message and len(message.command) == 1:
            await message.reply_text("๏ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ ID/ᴜsᴇʀɴᴀᴍᴇ.")
            return

        target = message.reply_to_message.from_user if message.reply_to_message else None
        if not target and len(message.command) > 1:
            user_input = message.command[1]
            try:
                if user_input.isdigit():
                    target = await app.get_users(int(user_input))
                else:
                    target = await app.get_users(user_input)
            except Exception as e:
                await message.reply_text(f"๏ ᴇʀʀᴏʀ: {str(e)}")
                return

        if not target:
            await message.reply_text("๏ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")
            return

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


@app.on_callback_query(filters.regex(r"confirm_delete_user:(.+):(.+)"))
async def confirm_delete_user_callback(client, callback_query):
    try:
        chat_id, user_id = map(int, callback_query.data.split(":")[1:])
        target = await client.get_users(user_id)
        await delete_messages(client, callback_query.message, target=target, chat_id=chat_id)
    except Exception as e:
        await callback_query.message.edit(f"๏ ᴇʀʀᴏʀ: {str(e)}")



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

