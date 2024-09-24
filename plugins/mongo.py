import re
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app
import os
from VIPMUSIC.misc import SUDOERS

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

# Function to delete all databases in the MongoDB instance
def clean_mongo(client):
    for db_name in client.list_database_names():
        if db_name not in ["admin", "local"]:  # Exclude system databases
            client.drop_database(db_name)

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
            clean_mongo(new_mongo_client)
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


# Command handler for `/deletedb`
@app.on_message(filters.command("deletedb") & SUDOERS)
async def delete_db_command(client, message: Message):
    try:
        mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        databases = mongo_client.list_database_names()
        if len(databases) > 2:  # Only system databases remain if 2 or less (admin, local)
            clean_mongo(mongo_client)
            await message.reply("All user databases have been deleted successfully. 🧹")
        else:
            await message.reply("No user databases found to delete. ❌")
        mongo_client.close()
    except Exception as e:
        await message.reply(f"Failed to delete databases: {e}")

# Command handler for `/checkdb`
@app.on_message(filters.command("checkdb") & SUDOERS)
async def check_db_command(client, message: Message):
    try:
        mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        databases = mongo_client.list_database_names()
        if len(databases) > 2:  # More than just admin and local
            result = "MongoDB Databases:\n"
            for db_name in databases:
                if db_name not in ["admin", "local"]:
                    result += f"\nDatabase: {db_name}\n"
                    db = mongo_client[db_name]
                    for col_name in db.list_collection_names():
                        collection = db[col_name]
                        result += f"  Collection: {col_name} ({collection.count_documents({})} documents)\n"
            await message.reply(result)
        else:
            await message.reply("No user databases found. ❌")
        mongo_client.close()
    except Exception as e:
        await message.reply(f"Failed to check databases: {e}")

__MODULE__ = "MongoDB Management"
__HELP__ = """
**MongoDB Management Commands:**

• `/mongochange [new_mongo_url]`: 
   - Verifies the new MongoDB URL.
   - Deletes all existing databases in the new MongoDB.
   - Migrates data from the old MongoDB to the new MongoDB.

• `/deletedb`: Deletes all non-system databases from the MongoDB.

• `/checkdb`: Lists all databases and collections with the number of documents in the MongoDB.
"""
