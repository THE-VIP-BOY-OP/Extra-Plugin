import re
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app
import os
from config import OWNER_ID
from VIPMUSIC.misc import SUDOERS
from VIPMUSIC.utils.pastebin import VIPbin

# Environment variable for the old MongoDB URL
MONGO_DB_URI = os.getenv("MONGO_DB_URI")

@app.on_message(filters.command("mongochk") & SUDOERS)
async def mongo_check_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please provide your MongoDB URL with the command: `/mongochk your_mongo_url`")
        return
    
    mongo_url = message.command[1]
    
    try:
        mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        databases = mongo_client.list_database_names()

        result = f"MongoDB URL `{mongo_url}` is valid.\n\nAvailable Databases:\n"
        for db_name in databases:
            if db_name not in ["admin", "local"]:
                result += f"\n`{db_name}`:\n"
                db = mongo_client[db_name]
                for col_name in db.list_collection_names():
                    result += f"  `{col_name}` ({db[col_name].count_documents({})} documents)\n"
        
        # Check if message exceeds Telegram's limit
        if len(result) > 4096:
            paste_url = await VIPbin(result)
            await message.reply(f"The database list is too long to send here. You can view it at: {paste_url}")
        else:
            await message.reply(result)

        mongo_client.close()

    except Exception as e:
        await message.reply(f"Failed to connect to MongoDB: {e}")

#==============================[⚠️ DELETE DATABASE ⚠️]=======================================#

# Function to delete a specific collection from a database


# Environment variable for the old MongoDB URL
MONGO_DB_URI = os.getenv("MONGO_DB_URI")

# Function to delete a specific collection from a database
def delete_collection(client, db_name, col_name):
    db = client[db_name]
    db.drop_collection(col_name)

# Function to delete a specific database
def delete_database(client, db_name):
    client.drop_database(db_name)

# Function to delete all user databases
def clean_mongo(client):
    for db_name in client.list_database_names():
        if db_name not in ["admin", "local"]:  # Exclude system databases
            client.drop_database(db_name)

# Command handler for `/deletedb`
@app.on_message(filters.command("deletedb") & filters.user(OWNER_ID))
async def delete_db_command(client, message: Message):
    try:
        mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        databases = mongo_client.list_database_names()

        # Check if user wants to delete all databases
        if len(message.command) > 1 and message.command[1].lower() == "all":
            clean_mongo(mongo_client)
            await message.reply("All user databases have been deleted successfully. 🧹")
        
        # If the user provides a database or collection name
        elif len(message.command) > 1:
            db_name = message.command[1]
            
            # If both database and collection names are provided
            if len(message.command) == 3:
                col_name = message.command[2]
                if db_name in databases:
                    delete_collection(mongo_client, db_name, col_name)
                    await message.reply(f"Collection `{col_name}` from database `{db_name}` has been deleted successfully. 🧹")
                else:
                    await message.reply(f"Database `{db_name}` does not exist. ❌")
            
            # If only the database name is provided
            else:
                if db_name in databases:
                    delete_database(mongo_client, db_name)
                    await message.reply(f"Database `{db_name}` has been deleted successfully. 🧹")
                else:
                    await message.reply(f"Database `{db_name}` does not exist. ❌")
        
        # If no database or collection name is provided
        else:
            if len(databases) > 2:
                result = "Please provide a database name or a collection name after the database name. Example:\n"
                result += "/deletedb `DatabaseName` `CollectionName`\n\nAvailable Databases:\n"
                for db_name in databases:
                    if db_name not in ["admin", "local"]:
                        result += f"\n`{db_name}`:\n"
                        db = mongo_client[db_name]
                        for col_name in db.list_collection_names():
                            result += f"  `{col_name}`\n"
                await message.reply(result)
            else:
                await message.reply("No user databases found. ❌")
        
        mongo_client.close()

    except Exception as e:
        await message.reply(f"Failed to delete databases or collections: {e}")


#==============================[⚠️ CHECK DATABASE ⚠️]=======================================#



# Environment variable for the MongoDB URL
MONGO_DB_URI = os.getenv("MONGO_DB_URI")

# Command handler for /checkdb
@app.on_message(filters.command("checkdb") & SUDOERS)
async def check_db_command(client, message: Message):
    try:
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
                await message.reply(f"The database list is too long to send here. You can view it at: {paste_url}")
            else:
                await message.reply(result)
        else:
            await message.reply("No user databases found. ❌")
        
        mongo_client.close()

    except Exception as e:
        await message.reply(f"Failed to check databases: {e}")

#============================================[ ⚠️ TRANSFER DATABASE ⚠️ ]===============================#

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
@app.on_message(filters.command("transferdb") & filters.user(OWNER_ID))
async def transfer_db_command(client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply("Please provide the new MongoDB URL with the command: `/transferdb your_new_mongodb_url`")
            return
        await message.reply_text("Ok wait transfer process going...")
        new_mongo_url = message.command[1]
        
        if not re.match(mongo_url_pattern, new_mongo_url):
            await message.reply("The provided MongoDB URL format is invalid! ❌")
            return
        
        # Step 1: Backup data from the old MongoDB instance
        old_mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        backup_data = backup_old_mongo_data(old_mongo_client)
        old_mongo_client.close()
        await message.reply("Data backup from old MongoDB is complete. 📦\n\nNow opening new MongoDB and putting.")
        
        # Step 2: Restore the backed-up data into the new MongoDB instance
        new_mongo_client = MongoClient(new_mongo_url, serverSelectionTimeoutMS=5000)
        restore_data_to_new_mongo(new_mongo_client, backup_data)
        new_mongo_client.close()
        
        await message.reply("Data transfer to the new MongoDB is successful! 🎉")
    
    except Exception as e:
        await message.reply(f"Failed to transfer data: {e}")


__MODULE__ = "MongoDB"
__HELP__ = """
**MongoDB Management Commands:**

• `/deletedb [database_name]`: Deletes the specified database.

• `/deletedb [database_name] [collection_name]`: Deletes the specified collection within the database.

• `/deletedb all`: Deletes all user databases.

• `/checkdb`: Lists all databases and collections with the number of documents in the MongoDB.

• **MongoDB Transfer Commands:**

• `/transferdb [new_mongo_url]`: 
   - Transfers all databases from the old MongoDB (from environment) to the new MongoDB URL.

• `/mongochk [MongoDB_URL]`: Verifies the given MongoDB URL and lists all databases and collections in it.
"""
