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


from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from VIPMUSIC import app
import os
from VIPMUSIC.misc import SUDOERS

# MongoDB URI from environment
MONGO_DB_URI = os.getenv("MONGO_DB_URI")

# Initialize MongoClient
mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)

# Function to clean all databases
def clean_mongo(client):
    for db_name in client.list_database_names():
        if db_name not in ["admin", "local"]:  # Exclude system databases
            client.drop_database(db_name)

# Command handler for `/deletedb`
@app.on_message(filters.command("deletedb") & SUDOERS)
async def delete_db_command(client, message: Message):
    # Show buttons for 'Delete All DB' and 'Delete Specific DB'
    keyboard = [
        [InlineKeyboardButton("Delete All DB", callback_data="delete_all_db")],
        [InlineKeyboardButton("Delete Specific DB", callback_data="delete_specific_db")]
    ]
    await message.reply("Select an option:", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback handler for deleting all databases
@app.on_callback_query(filters.regex("delete_all_db") & SUDOERS)
async def delete_all_db_callback(client, callback_query):
    try:
        clean_mongo(mongo_client)
        await callback_query.edit_message_text("All databases have been deleted successfully. 🧹")
    except Exception as e:
        await callback_query.edit_message_text(f"Failed to delete all databases: {e}")

# Callback handler for deleting a specific database
@app.on_callback_query(filters.regex("delete_specific_db") & SUDOERS)
async def delete_specific_db_callback(client, callback_query):
    # Get all non-system databases
    databases = [db for db in mongo_client.list_database_names() if db not in ["admin", "local"]]
    
    if not databases:
        await callback_query.edit_message_text("No user databases found. ❌")
        return

    # Show buttons for each database
    keyboard = [[InlineKeyboardButton(f"Database: {db}", callback_data=f"db_{db}")] for db in databases]
    keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_main")])
    
    await callback_query.edit_message_text("Select a database to delete its collections:", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback handler for selecting a database and showing its collections
@app.on_callback_query(filters.regex(r"db_(.+)") & SUDOERS)
async def db_select_callback(client, callback_query):
    db_name = callback_query.data.split("_")[1]
    db = mongo_client[db_name]
    
    collections = db.list_collection_names()
    if not collections:
        await callback_query.edit_message_text(f"No collections found in {db_name}. Deleting the database.")
        mongo_client.drop_database(db_name)
        await callback_query.edit_message_text(f"Database {db_name} has been deleted. 🧹")
        return

    # Show buttons for each collection in the selected database
    keyboard = [[InlineKeyboardButton(f"Collection: {col} ({db[col].count_documents({})} documents)", callback_data=f"col_{db_name}_{col}")]
                for col in collections]
    keyboard.append([InlineKeyboardButton("Back", callback_data="delete_specific_db")])

    await callback_query.edit_message_text(f"Collections in {db_name}:", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback handler for deleting a collection
@app.on_callback_query(filters.regex(r"col_(.+)") & SUDOERS)
async def collection_delete_callback(client, callback_query):
    _, db_name, col_name = callback_query.data.split("_")
    db = mongo_client[db_name]

    try:
        db.drop_collection(col_name)
        collections = db.list_collection_names()

        if not collections:
            # If no collections remain, delete the database
            mongo_client.drop_database(db_name)
            await callback_query.edit_message_text(f"Collection {col_name} and Database {db_name} have been deleted. 🧹")
        else:
            # Update the message to remove the deleted collection's button
            keyboard = [[InlineKeyboardButton(f"Collection: {col} ({db[col].count_documents({})} documents)", callback_data=f"col_{db_name}_{col}")]
                        for col in collections]
            keyboard.append([InlineKeyboardButton("Back", callback_data="delete_specific_db")])

            await callback_query.edit_message_text(f"Collections in {db_name}:", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await callback_query.edit_message_text(f"Failed to delete collection {col_name}: {e}")

# Callback handler for going back to the main menu
@app.on_callback_query(filters.regex("back_to_main") & SUDOERS)
async def back_to_main_callback(client, callback_query):
    # Show the main buttons again
    keyboard = [
        [InlineKeyboardButton("Delete All DB", callback_data="delete_all_db")],
        [InlineKeyboardButton("Delete Specific DB", callback_data="delete_specific_db")]
    ]
    await callback_query.edit_message_text("Select an option:", reply_markup=InlineKeyboardMarkup(keyboard))

__MODULE__ = "MongoDB Deletion"
__HELP__ = """
**MongoDB Deletion Commands:**

• `/deletedb`: Choose to delete all databases or delete specific ones.
    - "Delete All DB": Deletes all non-system databases.
    - "Delete Specific DB": Shows a list of databases. Choose one, then select collections to delete from the database.
"""


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
