from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ChatPermissions, Message
from VIPMUSIC import app
from VIPMUSIC.misc import SUDOERS
import asyncio
from VIPMUSIC.misc import SUDOERS
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from VIPMUSIC.utils.database import get_assistant
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant, ChatAdminRequired
from pyrogram.types import Message, ChatPrivileges
import asyncio
from typing import Optional
from random import randint
from pyrogram.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat


def get_keyboard(command):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data=f"{command}_yes"),
         InlineKeyboardButton("No", callback_data=f"{command}_no")]
    ])


@app.on_message(filters.command("purgeall"))
async def banall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    assistant = await get_assistant(chat_id)
    ass = await assistant.get_me()
    assid = ass.id
    
    AMBOTOK = await message.reply_text(f"Hey {message.from_user.mention}, 'deleteall' checking...")
    await asyncio.sleep(2)
    bot = await app.get_chat_member(chat_id, app.me.id)
    if not (
        bot.privileges.can_delete_messages and 
        bot.privileges.can_promote_members and
        bot.privileges.can_invite_users
    ):
        await AMBOTOK.edit(
            f"I don't have enough permissions to Mass Action !?!\n"
            f"Mass Action requires the bot permissions to Run properly Mass Action.\n"
            f"1.) delete messages.\n"
            f"2.) promote members.\n"
            f"3.) invite users."
        )
        return
    await asyncio.sleep(5)
    await AMBOTOK.delete()
    confirm_msg = await message.reply(
        f"{message.from_user.mention}, are you sure you want to delete all group messages?",
        reply_markup=get_keyboard("deleteall")
    )


@app.on_callback_query(filters.regex(r"^deleteall_(yes|no)$"))
async def handle_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    assistant = await get_assistant(chat_id)
    ass = await assistant.get_me()
    assid = ass.id
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer("Only the group owner can confirm this action.", show_alert=True)
        return

    if callback_query.data == "deleteall_yes":
        await callback_query.answer("Delete all process started...", show_alert=True)
        await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
            can_manage_chat=False,
            can_delete_messages=True,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_promote_members=False,
        ))

        try:
            async for msg in assistant.get_chat_history(chat_id):
                try:
                    await assistant.delete_messages(chat_id, msg.id)
                except Exception as e:
                    print(f"Failed to delete message {msg.id}: {e}")
                    continue  
            await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_promote_members=False,
            ))
            await callback_query.answer("All messages deleted successfully.", show_alert=False)
        except Exception as e:
            await callback_query.answer(f"An error occurred: {str(e)}", show_alert=False)
    elif callback_query.data == "deleteall_no":
        await callback_query.message.edit("Delete all process canceled.")

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired

@app.on_message(filters.command("abanall") & SUDOERS)
async def ban_all(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    userbot = await get_assistant(message.chat.id)
    # Get group owner
    
    bot_member = await client.get_chat_member(chat_id, userbot.id)
    if not bot_member.privileges or not bot_member.privileges.can_restrict_members:
        try:
            await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=True,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_promote_members=True,
            ))
        except ChatAdminRequired:
            await message.reply("I need admin rights to ban members.")
            return

    # Ban all members
    banned_count = 0
    async for member in client.get_chat_members(chat_id):
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] or member.user.id in [userbot.id, user_id]:
            continue
        try:
            await userbot.ban_chat_member(chat_id, member.user.id)
            banned_count += 1
        except Exception as e:
            print(f"Failed to ban {member.user.id}: {e}")

    await message.reply(f"Banned {banned_count} members successfully.")

"""
@app.on_message(filters.command("unbanall"))
async def unbanall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await message.reply_text(f"Hey {message.from_user.mention}, 'unbanall' can only be executed by the group owner {owner_AMBOT}.")
        return
    confirm_msg = await message.reply(
        f"{message.from_user.mention}, are you sure you want to unban all group members?",
        reply_markup=get_keyboard("unbanall")
    )

@app.on_callback_query(filters.regex(r"^unbanall_(yes|no)$"))
async def handle_unbanall_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer("Only the group owner can confirm this action.", show_alert=True)
        return
    if callback_query.data == "unbanall_yes":
        await callback_query.message.edit("Unbanall process started...")
        bot = await app.get_chat_member(chat_id, app.me.id)
        banned_users = []
        unbanned = 0
        if not bot.privileges.can_restrict_members:
            await callback_query.message.edit("I don't have permission to unban members in this group.")
            return
        async for member in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.BANNED):
            banned_users.append(member.user.id)
            try:
                await app.unban_chat_member(chat_id, banned_users[-1])
                unbanned += 1
            except Exception as e:
                print(f"Failed to unban {member.user.id}: {e}")
        await callback_query.message.edit(f"Unbanned {unbanned} members successfully.")
    elif callback_query.data == "unbanall_no":
        await callback_query.message.edit("Unbanall process canceled.")

"""
@app.on_message(filters.command("unmuteall"))
async def unmuteall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await message.reply_text(f"Hey {message.from_user.mention}, 'unmuteall' can only be executed by the group owner {owner_AMBOT}.")
        return
    
    confirm_msg = await message.reply(
        f"{message.from_user.mention}, are you sure you want to unmute all group members?",
        reply_markup=get_keyboard("unmuteall")
    )

@app.on_callback_query(filters.regex(r"^unmuteall_(yes|no)$"))
async def handle_unmuteall_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer("Only the group owner can confirm this action.", show_alert=True)
        return
    if callback_query.data == "unmuteall_yes":
        await callback_query.message.edit("Unmuteall process started...")
        bot = await app.get_chat_member(chat_id, app.me.id)
        if not bot.privileges.can_restrict_members:
            await callback_query.message.edit("I don't have permission to restrict members in this group.")
            return
        unmuted = 0
        async for member in app.get_chat_members(chat_id):
            if member.status in ['administrator', 'creator']:
                continue 
            try:
                await app.restrict_chat_member(
                    chat_id, 
                    member.user.id, 
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=False,
                        can_send_polls=False,
                        can_send_other_messages=True, 
                        can_add_web_page_previews=True
                    )
                )
                unmuted += 1
            except Exception as e:
                print(f"Failed to unmute {member.user.id}: {e}")
        await callback_query.message.edit(f"Unmuted {unmuted} members successfully.")
    elif callback_query.data == "unmuteall_no":
        await callback_query.message.edit("Unmuteall process canceled.")



@app.on_message(filters.command("muteall"))
async def muteall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await message.reply_text(f"Hey {message.from_user.mention}, 'muteall' can only be executed by the group owner {owner_AMBOT}.")
        return
    confirm_msg = await message.reply(
        f"{message.from_user.mention}, are you sure you want to mute all group members?",
        reply_markup=get_keyboard("muteall")
    )
@app.on_callback_query(filters.regex(r"^muteall_(yes|no)$"))
async def handle_muteall_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer("Only the group owner can confirm this action.", show_alert=True)
        return
    if callback_query.data == "muteall_yes":
        await callback_query.message.edit("Muteall process started...")
        bot = await app.get_chat_member(chat_id, app.me.id)
        if not bot.privileges.can_restrict_members:
            await callback_query.message.edit("I don't have permission to restrict members in this group.")
            return
        muted = 0
        async for member in app.get_chat_members(chat_id):
            if member.status in ['administrator', 'creator']:
                continue 
            try:
                await app.restrict_chat_member(chat_id, member.user.id, ChatPermissions(can_send_messages=False))
                muted += 1
            except Exception as e:
                print(f"Failed to mute {member.user.id}: {e}")
        await callback_query.message.edit(f"Muted {muted} members successfully.")
    elif callback_query.data == "muteall_no":
        await callback_query.message.edit("Muteall process canceled.")

@app.on_message(filters.command("kickall"))
async def kickall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await message.reply_text(f"Hey {message.from_user.mention}, 'kickall' can only be executed by the group owner {owner_AMBOT}.")
        return
    confirm_msg = await message.reply(
        f"{message.from_user.mention}, are you sure you want to kick all group members?",
        reply_markup=get_keyboard("kickall")
    )

@app.on_callback_query(filters.regex(r"^kickall_(yes|no)$"))
async def handle_kickall_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer("Only the group owner can confirm this action.", show_alert=True)
        return
    if callback_query.data == "kickall_yes":
        await callback_query.message.edit("Kickall process started...")
        bot = await app.get_chat_member(chat_id, app.me.id)
        if not bot.privileges.can_restrict_members:
            await callback_query.message.edit("I don't have permission to kick members in this group.")
            return
        kicked = 0
        async for member in app.get_chat_members(chat_id):
            if member.status in ['administrator', 'creator'] or member.user.id == app.me.id:
                continue 
            try:
                await app.kick_chat_member(chat_id, member.user.id)
                kicked += 1
            except Exception as e:
                print(f"Failed to kick {member.user.id}: {e}")
        await callback_query.message.edit(f"Kicked {kicked} members successfully.")
    elif callback_query.data == "kickall_no":
        await callback_query.message.edit("Kickall process canceled.")


@app.on_message(filters.command("unpinall"))
async def unpinall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await message.reply_text(f"Hey {message.from_user.mention}, 'unpinall' can only be executed by the group owner {owner_AMBOT}.")
        return
    confirm_msg = await message.reply(
        f"{message.from_user.mention}, are you sure you want to unpin all messages?",
        reply_markup=get_keyboard("unpinall")
    )

@app.on_callback_query(filters.regex(r"^unpinall_(yes|no)$"))
async def handle_unpinall_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer("Only the group owner can confirm this action.", show_alert=True)
        return
    if callback_query.data == "unpinall_yes":
        await callback_query.message.edit("Unpinning process started...")
        bot = await app.get_chat_member(chat_id, app.me.id)
        if not bot.privileges.can_pin_messages:
            await callback_query.message.edit("I don't have permission to unpin messages in this group.")
            return
        try:
            chat = await app.get_chat(chat_id)
            pinned_message = chat.pinned_message
            unpinned = 0
            if pinned_message:
                await app.unpin_chat_message(chat_id, pinned_message.message_id)
                unpinned += 1
                await callback_query.message.edit(f"Unpinned {unpinned} message successfully.")
            else:
                await callback_query.message.edit("There are no messages to unpin.")
        except Exception as e:
            print(f"Failed to unpin message: {e}")
            await callback_query.message.edit("An error occurred while trying to unpin the message.")
    elif callback_query.data == "unpinall_no":
        await callback_query.message.edit("Unpinning process canceled.")
