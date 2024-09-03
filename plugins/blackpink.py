from pyrogram import filters
from TheApi import api

from VIPMUSIC import app
from config import BANNED_USERS


@app.on_message(filters.command(["blackpink"]) & ~BANNED_USERS)
async def chatgpt_chat(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "/blackpink Radhe Radhe "
        )
    a = await message.reply_text("Creating BlackPink for You.....")

    args = " ".join(message.command[1:])

    results = api.blackpink(args)
    await message.reply_photo(results)
    try:
        await a.delete()
    except:
        pass

from pyrogram import Client, filters
import requests

# The bot token and API key should be securely handled (store them in environment variables or a config file)
API_URL = "https://api.openai.com/v1/images/generations"  # Replace with the correct endpoint
API_KEY = "your_openai_api_key"  # Replace with your actual API key

@app.on_message(filters.command(["bp", "redblue"]) & ~filters.user(BANNED_USERS))
async def generate_image(client, message):
    command = message.command[0].replace("/", "")
    args = " ".join(message.command[1:])
    
    if not args:
        await message.reply_text(f"Please provide a name for the /{command} command, e.g., '/{command} piyush'.")
        return
    
    status_msg = await message.reply_text(f"Creating {command.capitalize()} themed image for '{args}'...")

    # Construct the prompt based on the command
    prompt = ""
    if command == "blackpink":
        prompt = f"Create an artistic representation of the name '{args}' blended with the theme of the K-pop group BlackPink. The image should feature a stylish, modern design with pink and black color tones, incorporating elements like music notes, a microphone, and a neon sign that reads '{args}' in a bold, trendy font."
    elif command == "redblue":
        prompt = f"Design an artistic representation of the name '{args}' with a theme focused on red and blue colors. The image should incorporate bold, vibrant tones with elements like abstract shapes, dynamic lines, and a sleek font that spells out '{args}'."

    # Prepare the API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "size": "1024x1024",
        "n": 1
    }

    # Make the request to the API
    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        image_url = response.json()['data'][0]['url']
        await message.reply_photo(image_url)
    else:
        await message.reply_text("Failed to generate the image. Please try again later.")
    
    # Delete the status message
    await status_msg.delete()

