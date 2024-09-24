import re
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app
import os

MONGO_DB_URI = os.getenv("MONGO_DB_URI")

mongo_url_pattern = re.compile(r"mongodb(?:\+srv)?:\/\/[^\s]+")

@app.on_message(filters.command("mongochk"))
async def mongo_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply(
            "ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴍᴏɴɢᴏᴅʙ ᴜʀʟ ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ  `/mongochk your_mongodb_url`"
        )
        return

    mongo_url = message.command[1]
    if re.match(mongo_url_pattern, mongo_url):
        try:
            # Use a different variable to avoid conflict with `client`
            mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            mongo_client.server_info()  # Will cause an exception if connection fails
            await message.reply("ᴍᴏɴɢᴏᴅʙ ᴜʀʟ ɪs ᴠᴀʟɪᴅ ᴀɴᴅ ᴄᴏɴɴᴇᴄᴛɪᴏɴ sᴜᴄᴄᴇssғᴜʟ ✅")
        except Exception as e:
            await message.reply(f"ғᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴍᴏɴɢᴏᴅʙ: {e}")
        finally:
            # Ensure the connection is closed after checking
            mongo_client.close()
    else:
        await message.reply("ᴜᴘs! ʏᴏᴜʀ ᴍᴏɴɢᴏᴅʙ ғᴏʀᴍᴀᴛ ɪs ɪɴᴠᴀʟɪᴅ")

__MODULE__ = "Mᴏɴɢᴏᴅʙ"
__HELP__ = """
**ᴍᴏɴɢᴏᴅʙ ᴄʜᴇᴄᴋᴇʀ:**

• `/mongochk [mongo_url]`: Cʜᴇᴄᴋs ᴛʜᴇ ᴠᴀʟɪᴅɪᴛʏ ᴏғ ᴀ ᴍᴏɴɢᴏᴅʙ URL ᴀɴᴅ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛᴏ ᴛʜᴇ ᴍᴏɴɢᴏᴅʙ ɪɴsᴛᴀɴᴄᴇ.
"""




import re
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app

mongo_url_pattern = re.compile(r"mongodb(?:\+srv)?:\/\/[^\s]+")
temp_storage = {}  # Dictionary to temporarily store data before migration


def backup_old_mongo_data(old_client):
    """
    Function to backup all data from the old MongoDB instance.
    It will fetch all the databases, collections, and documents from the old MongoDB instance.
    """
    backup_data = {}
    for db_name in old_client.list_database_names():
        db = old_client[db_name]
        backup_data[db_name] = {}
        for col_name in db.list_collection_names():
            collection = db[col_name]
            backup_data[db_name][col_name] = list(collection.find())  # Store all documents in the collection
    return backup_data


def restore_data_to_new_mongo(new_client, backup_data):
    """
    Function to restore the backed-up data into the new MongoDB instance.
    It will recreate databases, collections, and insert documents.
    """
    for db_name, collections in backup_data.items():
        db = new_client[db_name]
        for col_name, documents in collections.items():
            collection = db[col_name]
            if documents:
                collection.insert_many(documents)  # Insert all documents into the new collection


@app.on_message(filters.command("mongochange"))
async def mongo_change_command(client, message: Message):
    global temp_storage
    
    if len(message.command) < 2:
        # Step 1: No MongoDB URL provided, ask for a new MongoDB URL
        await message.reply("Please provide your new MongoDB URL with the command: `/mongochange your_new_mongodb_url`")
        return
    
    new_mongo_url = message.command[1]
    if re.match(mongo_url_pattern, new_mongo_url):
        try:
            # Step 2: Verify the new MongoDB URL connection
            new_mongo_client = MongoClient(new_mongo_url, serverSelectionTimeoutMS=5000)
            new_mongo_client.server_info()  # Test connection to the new MongoDB

            # Step 3: Notify the user that the new MongoDB is valid
            await message.reply("New MongoDB URL is valid and connected successfully. ✅")

            # Step 4: Backup data from the old MongoDB instance
            old_mongo_url = MONGO_DB_URI  # Replace with your old MongoDB URL
            old_mongo_client = MongoClient(old_mongo_url, serverSelectionTimeoutMS=5000)
            temp_storage = backup_old_mongo_data(old_mongo_client)
            old_mongo_client.close()

            # Step 5: Restore the backed-up data into the new MongoDB instance
            restore_data_to_new_mongo(new_mongo_client, temp_storage)
            new_mongo_client.close()

            await message.reply("Data migration to the new MongoDB was successful! 🎉")
        except Exception as e:
            await message.reply(f"Failed to connect to the new MongoDB: {e}")
    else:
        await message.reply("The provided MongoDB URL format is invalid! ❌")


__MODULE__ = "MongoDB Change"
__HELP__ = """
**MongoDB Changer:**

• `/mongochange [new_mongo_url]`: 
   1. Verifies the new MongoDB URL.
   2. Temporarily stores all data from the old MongoDB.
   3. Migrates the data to the new MongoDB.
"""
