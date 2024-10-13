

# Haber komutunu tanımlayın
import random
import asyncio
import json
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from VIPMUSIC import app
from pyrogram.types import ChatMemberUpdated
import requests
from datetime import datetime, timedelta

api_key = "04c79b64b4c24a7c99dea83fcbfc3b1c"  # Haber API anahtarınız

def get_news_update():
    url = f"http://newsapi.org/v2/top-headlines?country=tr&apiKey={api_key}"
    response = requests.get(url)
    article = response.json()['articles'][0]  # İlk haber başlığı ve içeriği
    news = f"{article['title']}\n\n{article['description']}"
    return news

# Otomatik haber güncellemesi gönderme
async def send_news_updates():
    news_update = get_news_update()
    updates = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nGünlük Haber Başlığı:\n{news_update}"
    
    # Botun bulunduğu tüm gruplara gönder
    async for dialog in app.iter_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            await app.send_message(dialog.chat.id, updates)
    
    while True:
        news_update = get_news_update()
        updates = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n**HABER📰 SAATİ⏰:\n{news_update}"
        
        # Botun bulunduğu tüm gruplara gönder
        async for dialog in app.iter_dialogs():
            if dialog.chat.type in ["group", "supergroup"]:
                await app.send_message(dialog.chat.id, updates)
        
        await asyncio.sleep(3600)  # 1 saat bekle

# Botu başlat ve güncellemeleri otomatik başlat


@app.on_message(filters.command('haber', prefixes='/'))
async def get_news(client, message: Message):
    try:
        news_api_url = 'https://newsapi.org/v2/top-headlines'
        api_key = '04c79b64b4c24a7c99dea83fcbfc3b1c'
        params = {
            'apiKey': api_key,
            'country': 'TR',  # Haberlerin alınacağı ülkeyi belirtin
        }
        response = requests.get(news_api_url, params=params)
        
        if response.status_code != 200:
            await client.send_message(chat_id=message.chat.id, text=f"API hatası: {response.status_code}")
            return
        
        data = response.json()
        
        if not data.get('articles'):
            await client.send_message(chat_id=message.chat.id, text="Haber bulunamadı.")
            return

        news_text = ""
        for i, article in enumerate(data['articles'], start=1):
            title = article.get('title', 'Başlık bulunamadı')
            description = article.get('description', 'Açıklama mevcut değil')
            url = article.get('url', '#')
            news_text += f"{i}. {title}\n\n{description}\nDetay için tıklayın\n\n"

        # Telegram mesaj uzunluğu sınırını kontrol et ve böl
        max_message_length = 4096
        while len(news_text) > max_message_length:
            part = news_text[:max_message_length]
            news_text = news_text[max_message_length:]
            await client.send_message(chat_id=message.chat.id, text=part)
        
        # Kalan metni gönder
        if news_text:
            await client.send_message(chat_id=message.chat.id, text=news_text)

    except Exception as e:
        await client.send_message(chat_id=message.chat.id, text=f"Haberleri alırken bir hata oluştu: {str(e)}")

