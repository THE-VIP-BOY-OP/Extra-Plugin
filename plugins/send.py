from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError
from VIPMUSIC import app 
from VIPMUSIC.misc import SUDOERS
@app.on_message(filters.command("send") & SUDOERS)
async def send_message(client, message: Message):
    try:
        # Check if the message is a reply or contains text to send
        if not message.reply_to_message and len(message.command) < 3:
            return await message.reply_text("Please provide a Group/User ID or username and a message to send.")

        # Extract group_id/user_id and message to send
        target_id = message.text.split(maxsplit=2)[1]

        # Resolve group link, username, or user_id
        if target_id.startswith("https://t.me/"):
            target = await client.resolve_chat(target_id.split("/")[-1])
            target_id = target.id
        elif target_id.startswith("@"):
            target = await client.get_chat(target_id)
            target_id = target.id
        else:
            target_id = int(target_id)

        # Determine if the message is a reply
        if message.reply_to_message:
            # Send the replied message to the target group/user
            sent_message = await message.reply_to_message.forward(target_id)
        else:
            # Use the rest of the message as the text to send
            text_to_send = message.text.split(maxsplit=2)[2]
            sent_message = await client.send_message(target_id, text_to_send)

        await message.reply_text(f"Message sent successfully to <code>{target_id}</code>.")

    except (ValueError, IndexError):
        await message.reply_text("Please provide a valid Group/User ID, username, or link.")
    except RPCError as e:
        await message.reply_text(f"An error occurred: {str(e)}")
