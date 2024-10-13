import random
import asyncio
import os
import requests
import json
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from VIPMUSIC import app
from VIPMUSIC.utils.database import get_served_chats

AUTO_GCAST_NEWS = True
API_KEY = os.getenv("NEWS_API_KEY", "04c79b64b4c24a7c99dea83fcbfc3b1c")  # Use environment variable

def get_news_update():
    url = f"http://newsapi.org/v2/top-headlines?country=tr&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for failed responses
        articles = response.json().get('articles', [])
        
        if not articles:
            return "Haber bulunamadı."

        article = articles[0]  # First article
        news = f"{article.get('title', 'Başlık bulunamadı')}\n\n{article.get('description', 'Açıklama mevcut değil')}"
        return news
    except requests.RequestException as e:
        return f"Haber alınamadı: {e}"


@app.on_message(filters.command('haber', prefixes='/'))
async def get_news(client, message: Message):
    try:
        news_api_url = 'https://newsapi.org/v2/top-headlines'
        params = {
            'apiKey': API_KEY,
            'country': 'TR',
        }
        response = requests.get(news_api_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('articles'):
            await client.send_message(chat_id=message.chat.id, text="Haber bulunamadı.")
            return

        news_text = ""
        for i, article in enumerate(data['articles'], start=1):
            title = article.get('title', 'Başlık bulunamadı')
            description = article.get('description', 'Açıklama mevcut değil')
            news_text += f"{i}. {title}\n\n{description}\n\n"

        max_message_length = 4096
        while len(news_text) > max_message_length:
            part = news_text[:max_message_length]
            news_text = news_text[max_message_length:]
            await client.send_message(chat_id=message.chat.id, text=part)

        if news_text:
            await client.send_message(chat_id=message.chat.id, text=news_text)

    except Exception as e:
        await client.send_message(chat_id=message.chat.id, text=f"Haberleri alırken bir hata oluştu: {str(e)}")


async def send_message_to_chats(updates):
    try:
        chats = await get_served_chats()

        for chat_info in chats:
            chat_id = chat_info.get("chat_id")
            if isinstance(chat_id, int):
                try:
                    await app.send_message(chat_id, updates)
                    await asyncio.sleep(20)  # Delay between messages
                except Exception as e:
                    print(f"Error sending message to chat {chat_id}: {e}")
    except Exception as e:
        print(f"Error fetching chats: {e}")


async def gcast_news():
    while True:
        if AUTO_GCAST_NEWS:
            news_update = get_news_update()
            updates = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nGünlük Haber Başlığı:\n{news_update}"
            try:
                await send_message_to_chats(updates)
            except Exception as e:
                print(f"Error broadcasting news: {e}")
        
        await asyncio.sleep(100000)


# Start the continuous broadcast loop
if AUTO_GCAST_NEWS:
    asyncio.create_task(gcast_news())
