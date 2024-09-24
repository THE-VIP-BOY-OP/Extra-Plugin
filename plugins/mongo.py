import re
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app
import os
from VIPMUSIC.misc import SUDOERS

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
import os

# Environment variable for the old MongoDB URL
MONGO_DB_URI = os.getenv("MONGO_DB_URI")

# MongoDB URL regex pattern
mongo_url_pattern = re.compile(r"mongodb(?:\+srv)?:\/\/[^\s]+")
temp_storage = {}  # Dictionary to temporarily store data before migration

# Function to backup old MongoDB data
def backup_old_mongo_data(old_client):
    backup_data = {}
    for db_name in old_client.list_database_names():
        db = old_client[db_name]
        backup_data[db_name] = {}
        for col_name in db.list_collection_names():
            collection = db[col_name]
            backup_data[db_name][col_name] = list(collection.find())  # Store all documents
    return backup_data

# Function to restore data to new MongoDB instance
def restore_data_to_new_mongo(new_client, backup_data):
    for db_name, collections in backup_data.items():
        db = new_client[db_name]
        for col_name, documents in collections.items():
            collection = db[col_name]
            if documents:
                collection.insert_many(documents)  # Insert all documents into the new collection

# Function to delete all databases in the new MongoDB
def clean_new_mongo(new_client):
    for db_name in new_client.list_database_names():
        if db_name not in ["admin", "local"]:  # Exclude system databases
            new_client.drop_database(db_name)

# Command handler for `/mongochange`
@app.on_message(filters.command("mongochange") & SUDOERS)
async def mongo_change_command(client, message: Message):
    global temp_storage

    if len(message.command) < 2:
        await message.reply("Please provide your new MongoDB URL with the command: `/mongochange your_new_mongodb_url`")
        return

    new_mongo_url = message.command[1]
    
    if re.match(mongo_url_pattern, new_mongo_url):
        try:
            # Step 1: Verify the new MongoDB URL connection
            new_mongo_client = MongoClient(new_mongo_url, serverSelectionTimeoutMS=5000)
            new_mongo_client.server_info()  # Test connection to the new MongoDB
            await message.reply("New MongoDB URL is valid and connected successfully. ✅")

            # Step 2: Clean new MongoDB (delete all databases)
            clean_new_mongo(new_mongo_client)
            await message.reply("All databases in the new MongoDB have been deleted. 🧹")

            # Step 3: Backup data from the old MongoDB instance
            old_mongo_url = MONGO_DB_URI  # Using the old MongoDB URL from environment
            old_mongo_client = MongoClient(old_mongo_url, serverSelectionTimeoutMS=5000)
            temp_storage = backup_old_mongo_data(old_mongo_client)
            old_mongo_client.close()
            await message.reply("Data backup from old MongoDB is complete. 📦")

            # Step 4: Restore the backed-up data into the new MongoDB instance
            restore_data_to_new_mongo(new_mongo_client, temp_storage)
            new_mongo_client.close()
            await message.reply("Data migration to the new MongoDB is successful! 🎉")
            
        except Exception as e:
            await message.reply(f"Failed to connect to the new MongoDB: {e}")
    else:
        await message.reply("The provided MongoDB URL format is invalid! ❌")


__MODULE__ = "MongoDB Change"
__HELP__ = """
**MongoDB Changer:**

• `/mongochange [new_mongo_url]`: 
   1. Verifies the new MongoDB URL.
   2. Deletes all existing databases in the new MongoDB.
   3. Temporarily stores all data from the old MongoDB.
   4. Migrates the data to the new MongoDB.
   5. Sends confirmation messages at each step.
"""
