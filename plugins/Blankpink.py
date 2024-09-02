from pyrogram import Client, filters
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from VIPMUSIC import app


def generate_blackpink_logo(text):
    # Use PIL to create a simple BLACKPINK style logo
    image = Image.new("RGB", (500, 200), color=(255, 182, 193))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 50)
    text_width, text_height = draw.textsize(text, font=font)
    position = ((image.width - text_width) // 2, (image.height - text_height) // 2)
    draw.text(position, text, (0, 0, 0), font=font)
    return image

@app.on_message(filters.command("blackpink", prefixes="/"))
async def blackpink_logo(client, message):
    # Extract the text after the command
    text = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else "BLACKPINK"
    
    # Generate the logo
    logo = generate_blackpink_logo(text)
    
    # Save to BytesIO
    bio = BytesIO()
    bio.name = "blackpink_logo.png"
    logo.save(bio, "PNG")
    bio.seek(0)
    
    # Send the generated logo
    await message.reply_photo(photo=bio)

