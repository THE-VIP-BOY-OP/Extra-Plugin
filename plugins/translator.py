from VIPMUSIC import app
from pyrogram import filters
from deep_translator import GoogleTranslator

@app.on_message(filters.command("tr"))
async def translate(client, message):
    if message.reply_to_message:
        text_to_translate = message.reply_to_message.text
        target_language = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else 'en'
    else:
        if len(message.text.split()) < 3:
            await message.reply_text("Kripya kisi sandesh ka jawab dein ya /tr ke baad bhasha code like ( hi for hindi , en for english ) aur anuvad karne ke liye text dein.")
            return
        target_language = message.text.split(None, 2)[1]
        text_to_translate = message.text.split(None, 2)[2]

    try:
        translated = GoogleTranslator(source='auto', target=target_language).translate(text_to_translate)
        await message.reply_text(f"Anuvad: {translated}\nBhasha: {target_language}")
    except Exception as e:
        await message.reply_text(f"Anuvad karne mein samasya hui: {str(e)}")
