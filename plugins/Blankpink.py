from pyrogram import Client, filters
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Initialize the Pyrogram Client
from VIPMUSIC import app

# Predefined color schemes
COLOR_SCHEMES = {
    "blackpink": {"background": (255, 182, 193), "text": (0, 0, 0)},  # Pink background, black text
    "redblack": {"background": (255, 0, 0), "text": (0, 0, 0)},       # Red background, black text
    "bluewhite": {"background": (0, 0, 255), "text": (255, 255, 255)},# Blue background, white text
    "greenyellow": {"background": (0, 255, 0), "text": (255, 255, 0)},# Green background, yellow text
    "purplewhite": {"background": (128, 0, 128), "text": (255, 255, 255)},# Purple background, white text
    "orangeblack": {"background": (255, 165, 0), "text": (0, 0, 0)},  # Orange background, black text
    "cyanblack": {"background": (0, 255, 255), "text": (0, 0, 0)},    # Cyan background, black text
    "yellowred": {"background": (255, 255, 0), "text": (255, 0, 0)},  # Yellow background, red text
    "pinkblue": {"background": (255, 105, 180), "text": (0, 0, 255)}, # Pink background, blue text
    "greyblack": {"background": (169, 169, 169), "text": (0, 0, 0)},  # Grey background, black text
}

# Function to generate the logo
def generate_logo(text, background_color, text_color):
    # Create a blank image with the specified background color
    image = Image.new("RGB", (500, 200), color=background_color)
    draw = ImageDraw.Draw(image)
    
    # Load a font
    font = ImageFont.truetype("arial.ttf", 50)  # Replace with the path to a suitable .ttf font file
    
    # Calculate text size and position it at the center
    text_width, text_height = draw.textsize(text, font=font)
    position = ((image.width - text_width) // 2, (image.height - text_height) // 2)
    
    # Draw the text onto the image
    draw.text(position, text, fill=text_color, font=font)
    
    return image

# Command handler for the logo generation
@app.on_message(filters.command("logo", prefixes="/"))
async def logo_command(client, message):
    try:
        # Extract the color scheme and text from the command
        command_parts = message.text.split(" ", 2)
        color_scheme_name = command_parts[1].lower() if len(command_parts) > 1 else "blackpink"
        text = command_parts[2] if len(command_parts) > 2 else "BLACKPINK"
        
        # Check if the specified color scheme exists
        if color_scheme_name not in COLOR_SCHEMES:
            await message.reply_text(f"Color scheme '{color_scheme_name}' not found! Please choose from: {', '.join(COLOR_SCHEMES.keys())}")
            return
        
        # Get the background and text colors from the scheme
        colors = COLOR_SCHEMES[color_scheme_name]
        background_color = colors["background"]
        text_color = colors["text"]
        
        # Generate the logo
        logo = generate_logo(text, background_color, text_color)
        
        # Save the logo to a BytesIO object
        bio = BytesIO()
        bio.name = f"{color_scheme_name}_logo.png"
        logo.save(bio, "PNG")
        bio.seek(0)
        
        # Send the generated logo as a photo
        await message.reply_photo(photo=bio)
        
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# Run the bot
