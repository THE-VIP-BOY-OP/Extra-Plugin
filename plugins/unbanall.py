from pyrogram import enums, filters
from VIPMUSIC import app

BOT_ID = app.id

@app.on_message(filters.command("unbanall"))
async def unban_all(_, msg):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    x = 0

    bot = await app.get_chat_member(chat_id, BOT_ID)
    bot_permission = bot.privileges.can_restrict_members == True

    user = await app.get_chat_member(chat_id, user_id)
    user_permission = user.privileges and user.privileges.can_restrict_members

    if bot_permission and user_permission:
        banned_users = []
        async for m in app.get_chat_members(
            chat_id, filter=enums.ChatMembersFilter.BANNED
        ):
            banned_users.append(m.user.id)

        ok = await app.send_message(
            chat_id,
            f"Total **{len(banned_users)}** users found to unban.\n**Started unbanning..**",
        )

        for user_id in banned_users:
            try:
                await app.unban_chat_member(chat_id, user_id)
                x += 1

                if x % 5 == 0:
                    await ok.edit_text(
                        f"Unbanned {x} out of {len(banned_users)} users."
                    )

            except Exception:
                pass

        await ok.edit_text(f"Unbanned all {len(banned_users)} users.")

    else:
        await msg.reply_text(
            "ᴇɪᴛʜᴇʀ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ʀɪɢʜᴛ ᴛᴏ ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs ᴏʀ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ sᴜᴅᴏ ᴜsᴇʀs ᴏʀ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ɴᴇᴄᴇssᴀʀʏ ᴀᴅᴍɪɴ"
        )

__MODULE__ = "Uɴʙᴀɴᴀʟʟ"
__HELP__ = """
**Uɴʙᴀɴ A**

Tʜɪs ᴍᴏᴅᴜʟᴇ ᴀʟʟᴏᴡs ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs ᴡɪᴛʜ ʀᴇsᴛʀɪᴄᴛɪᴏɴ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴜɴʙᴀɴ ᴜsᴇʀs ɪɴ ᴀ ɢʀᴏᴜᴘ ᴀᴛ ᴏɴᴄᴇ.

Cᴏᴍᴍᴀɴᴅs:
- /ᴜɴʙᴀɴᴀʟʟ: Sᴛᴀʀᴛ ᴜɴʙᴀɴɴɪɴɢ ᴀʟʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀs ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ.

Nᴏᴛᴇ:
- Oɴʟʏ ᴀᴅᴍɪɴs ᴡɪᴛʜ ʀᴇsᴛʀɪᴄᴛɪᴏɴ ᴘᴇʀᴍɪssɪᴏɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.
- Tʜᴇ ʙᴏᴛ ᴍᴜsᴛ ʜᴀᴠᴇ ᴛʜᴇ ɴᴇᴄᴇssᴀʀʏ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴜɴʙᴀɴ ᴜsᴇʀs.
"""
