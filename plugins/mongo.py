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


# Command handler for `/deletedb`
import re
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app
import os
from VIPMUSIC.misc import SUDOERS

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
@app.on_message(filters.command("deletedb") & SUDOERS)
async def delete_db_command(client, message: Message):
    try:
        mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        databases = mongo_client.list_database_names()
        
        # If the user provides a database or collection name
        if len(message.command) > 1:
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

# Command handler for `/checkdb`
from VIPMUSIC.utils.pastebin import VIPbin
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app
import os
from VIPMUSIC.misc import SUDOERS

# Environment variable for the MongoDB URL
MONGO_DB_URI = os.getenv("MONGO_DB_URI")

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
                    result += f"\n`{db_name}`:\n"
                    db = mongo_client[db_name]
                    for col_name in db.list_collection_names():
                        collection = db[col_name]
                        result += f"  `{col_name}` ({collection.count_documents({})} documents)\n"
            
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

__MODULE__ = "MongoDB Management"
__HELP__ = """
**MongoDB Management Commands:**

• `/deletedb [DatabaseName] [CollectionName]`:
   - Deletes a specific database or a specific collection in a database.
   - If no names are provided, it lists available databases and collections.

• `/checkdb`: Lists all databases and collections with the number of documents in the MongoDB.
"""

# Command handler for `/checkdb`
