import re
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app
import os
from config import OWNER_ID
from VIPMUSIC.misc import SUDOERS
from VIPMUSIC.utils.pastebin import VIPbin


MONGO_DB_URI = os.getenv("MONGO_DB_URI")

@app.on_message(filters.command("mongochk"))
async def mongo_check_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please provide your MongoDB URL with the command: `/mongochk your_mongo_url`")
        return
    ok = await message.reply_text("**Please wait i am checking your mongo...**")
    mongo_url = message.command[1]
    
    try:
        mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        databases = mongo_client.list_database_names()

        result = f"**MongoDB URL** `{mongo_url}` **is valid**.\n\n**Available Databases:**\n"
        for db_name in databases:
            if db_name not in ["admin", "local"]:
                result += f"\n`{db_name}`:\n"
                db = mongo_client[db_name]
                for col_name in db.list_collection_names():
                    result += f"  `{col_name}` ({db[col_name].count_documents({})} documents)\n"
        
        
        if len(result) > 4096:
            paste_url = await VIPbin(result)
            await ok.delete()
            await message.reply(f"**The database list is too long to send here. You can view it at:** {paste_url}")
        else:
            await ok.delete()
            await message.reply(result)

        mongo_client.close()

    except Exception as e:
        await message.reply(f"**Failed to connect to MongoDB**\n\n**Your Mongodb is dead❌**\n\n**Error:-** `{e}`")

#==============================[⚠️ DELETE DATABASE ⚠️]=======================================


def delete_collection(client, db_name, col_name):
    db = client[db_name]
    db.drop_collection(col_name)


def delete_database(client, db_name):
    client.drop_database(db_name)


def list_databases_and_collections(client):
    numbered_list = []
    counter = 1
    for db_name in client.list_database_names():
        if db_name not in ["admin", "local"]:  
            numbered_list.append((counter, db_name, None))
            counter += 1
            db = client[db_name]
            for col_name in db.list_collection_names():
                numbered_list.append((counter, db_name, col_name))
                counter += 1
    return numbered_list


def delete_all_databases_and_collections(client):
    for db_name in client.list_database_names():
        if db_name not in ["admin", "local"]:
            db = client[db_name]
            for col_name in db.list_collection_names():
                db.drop_collection(col_name)
            client.drop_database(db_name)

@app.on_message(filters.command(["deletedb", "deletedatabase", "deldb", "deldatabase"]) & filters.user(OWNER_ID))
async def delete_db_command(client, message: Message):
    try:
        mongo_url = get_mongo_url(message)
        mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        databases_and_collections = list_databases_and_collections(mongo_client)

        if len(message.command) == 1:
            if len(databases_and_collections) > 0:
                result = "**MongoDB Databases and Collections:**\n\n"
                for num, db_name, col_name in databases_and_collections:
                    if col_name:
                        result += f"{num}.) `{col_name}`\n"
                    else:
                        result += f"\n{num}.) **{db_name}** (Database)\n"
                await message.reply(result)
            else:
                await message.reply("**No user databases found. ❌**")

        elif message.command[1].lower() == "all":
            delete_all_databases_and_collections(mongo_client)
            await message.reply("**All databases and collections have been deleted successfully. 🧹**")

        elif "," in message.command[1]:
            numbers = message.command[1].split(",")
            failed = []
            for num_str in numbers:
                num_str = num_str.strip()  
                if num_str.isdigit():
                    number = int(num_str)
                    if number > 0 and number <= len(databases_and_collections):
                        num, db_name, col_name = databases_and_collections[number - 1]
                        try:
                            if col_name:
                                delete_collection(mongo_client, db_name, col_name)
                            else:
                                delete_database(mongo_client, db_name)
                        except Exception:
                            failed.append(num_str)
                    else:
                        failed.append(num_str)
                else:
                    failed.append(num_str)
            if failed:
                await message.reply(f"Failed to delete: {', '.join(failed)} ❌")
            else:
                await message.reply("Selected databases/collections deleted successfully.")
        else:
            await message.reply("Invalid command format.")

        mongo_client.close()

    except Exception as e:
        await message.reply(f"**Failed to delete databases:** {e}")



#==============================[⚠️ CHECK DATABASE ⚠️]=======================================



# Environment variable for the MongoDB URL
MONGO_DB_URI = os.getenv("MONGO_DB_URI")

# Command handler for /checkdb
@app.on_message(filters.command(["checkdb", "checkdatabase"]) & SUDOERS)
async def check_db_command(client, message: Message):
    try:
        ok = await message.reply_text("**Please wait while checking your bot mongodb database...**")
        mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        databases = mongo_client.list_database_names()
        
        if len(databases) > 2:  # More than just admin and local
            result = "MongoDB Databases:\n"
            for db_name in databases:
                if db_name not in ["admin", "local"]:
                    result += f"\n{db_name}:\n"
                    db = mongo_client[db_name]
                    for col_name in db.list_collection_names():
                        collection = db[col_name]
                        result += f"  {col_name} ({collection.count_documents({})} documents)\n"
            
            # Check if message exceeds Telegram's limit
            if len(result) > 4096:  # Telegram's message length limit is 4096 characters
                paste_url = await VIPbin(result)
                await message.reply(f"**The database list is too long to send here. You can view it at:** {paste_url}")
                await ok.delete()
            else:
                await ok.delete()
                await message.reply(result)
        else:
            await ok.delete()
            await message.reply("**No user databases found. ❌**")
        
        mongo_client.close()

    except Exception as e:
        await ok.delete()
        await message.reply(f"**Failed to check databases:** {e}")

#============================================[ ⚠️ TRANSFER DATABASE ⚠️ ]===============================

mongo_url_pattern = re.compile(r"mongodb(?:\+srv)?:\/\/[^\s]+")

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

# Command handler for `/transferdb`
@app.on_message(filters.command(["transferdb", "copydb", "paste", "copydatabase", "transferdatabase"]) & filters.user(OWNER_ID))
async def transfer_db_command(client, message: Message):
    try:
        if len(message.command) == 2:
            main_mongo_url = MONGO_DB_URI
            target_mongo_url = message.command[1]
        elif len(message.command) == 3:
            main_mongo_url = message.command[1]
            target_mongo_url = message.command[2]
        else:
            await message.reply("Please provide one or two MongoDB URLs as required.")
            return

        if not re.match(mongo_url_pattern, target_mongo_url):
            await message.reply("**The target MongoDB URL format is invalid! ❌**")
            return

        # Backup data from the main MongoDB instance
        main_client = MongoClient(main_mongo_url, serverSelectionTimeoutMS=5000)
        backup_data = backup_old_mongo_data(main_client)
        main_client.close()

        # Restore to the target MongoDB instance
        target_client = MongoClient(target_mongo_url, serverSelectionTimeoutMS=5000)
        restore_data_to_new_mongo(target_client, backup_data)
        target_client.close()

        await message.reply("**Data transfer to the new MongoDB is successful! 🎉**")

    except Exception as e:
        await message.reply(f"**Data transfer failed:** {e}")
        
#================DOWNLOAD-DATA===================

import json
import io

@app.on_message(filters.command("downloaddata") & filters.user(OWNER_ID))
async def download_data_command(client, message: Message):
    try:
        mongo_url = get_mongo_url(message)
        mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)

        data = {}
        for db_name in mongo_client.list_database_names():
            if db_name not in ["admin", "local"]:
                data[db_name] = {}
                db = mongo_client[db_name]
                for col_name in db.list_collection_names():
                    data[db_name][col_name] = list(db[col_name].find())

        mongo_client.close()

        # Convert data to JSON and send as a file
        json_data = json.dumps(data, default=str, indent=2)
        file = io.BytesIO(json_data.encode('utf-8'))
        file.name = "mongo_data.json"
        await client.send_document(chat_id=message.chat.id, document=file)

    except Exception as e:
        await message.reply(f"**Failed to download data:** {e}")

__MODULE__ = "MongoDB"
__HELP__ = """
**MongoDB Management Commands:**

• /deletedb : You can delete by /deletedb 1,2,7,5.

• /deletedb [database_name] [collection_name]: Deletes the specified collection within the database.

• /deletedb all: Deletes all user databases.

• /checkdb: Lists all databases and collections with the number of documents in the MongoDB.

• **MongoDB Transfer Commands:**

• /transferdb [new_mongo_url]: - Transfers all databases from the old MongoDB (from environment) to the new MongoDB URL.

• /downloaddata - Download your all data from database in a document file.

• /mongochk [MongoDB_URL]: Verifies the given MongoDB URL and lists all databases and collections in it.
"""




