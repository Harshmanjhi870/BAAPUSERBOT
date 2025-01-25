from pyrogram import Client, filters
from pyrogram.types import Message
import logging
from pymongo import MongoClient


import asyncio
import base64
import requests

API_URL = "http://cheatbot.twc1.net/getName"
API_TOKEN = "TEST-API-TOKEN"  # Test token provided

# MongoDB setup
client = MongoClient('mongodb+srv://test12:test12@cluster0.z1pajuv.mongodb.net/?retryWrites=true&w=majority')
db = client['character_database']
characters_collection = db['characters1']
users_collection = db['autograb_users']
groups_collection = db['autograb_groups']

# Bot setup
SUDO = [7577185215, 7946511580]
BOT_IDS = [7392456702, 7829763759, 6734386717, 7107840748, 6816539294, 7653554157, 7287370269, 7091726086]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client

from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters


mongo_url = "mongodb+srv://harshmanjhi1801:webapp@cluster0.xxwc4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
ddw = AsyncIOMotorClient(mongo_url)
dbt = ddw['gaming_create']

destination_char = dbt['gaming_anime_characters']
collection = destination_char

shivuu = app

def is_autograb_enabled(user_id: int) -> bool:
    """Check if autograb is enabled for a user."""
    user = users_collection.find_one({"user_id": user_id})
    return bool(user and user.get("autograb"))


def is_group_enabled(chat_id: int) -> bool:
    """Check if a group is enabled for autograb."""
    group = groups_collection.find_one({"chat_id": chat_id})
    return bool(group)

@app.on_message(filters.command("autograb", prefixes=".") & filters.me)
async def toggle_autograb(client: Client, message: Message):
    """Enable or disable autograb for a fixed user ID (0000000)."""
    if len(message.command) < 2:
        await message.reply("Usage: `.autograb on` or `.autograb off`")
        return

    state = message.command[1].lower()
    fixed_user_id = client.me.id

    if state == "on":
        users_collection.update_one(
            {"user_id": fixed_user_id}, {"$set": {"autograb": True}}, upsert=True
        )
        logger.info(f"Autograb enabled for user {fixed_user_id}")
        await message.reply("Autograb enabled ✅")
    elif state == "off":
        users_collection.update_one(
            {"user_id": fixed_user_id}, {"$set": {"autograb": False}}, upsert=True
        )
        logger.info(f"Autograb disabled for user {fixed_user_id}")
        await message.reply("Autograb disabled ❌")
    else:
        await message.reply("Invalid option. Use `.autograb on` or `.autograb off`")


@app.on_message(filters.command("autongrab", prefixes=".") & filters.me)
async def toggle_autograb(client: Client, message: Message):
    """Enable or disable autograb for a fixed user ID (0000000)."""
    if len(message.command) < 2:
        await message.reply("Usage: `.autograb on` or `.autograb off`")
        return

    state = message.command[1].lower()
    fixed_user_id = client.me.id   # Fixed user ID

    if state == "on":
        users_collection.update_one(
            {"user_id": fixed_user_id}, {"$set": {"autograb": True}}, upsert=True
        )
        logger.info(f"Autograb enabled for user {fixed_user_id}")
        await message.reply("Autograb enabled ✅")
    elif state == "off":
        users_collection.update_one(
            {"user_id": fixed_user_id}, {"$set": {"autograb": False}}, upsert=True
        )
        logger.info(f"Autograb disabled for user {fixed_user_id}")
        await message.reply("Autograb disabled ❌")
    else:
        await message.reply("Invalid option. Use `.autograb on` or `.autograb off`")


@app.on_message(filters.command("addgrab", prefixes=".") & filters.me)
async def add_grab_group(client: Client, message: Message):
    """Enable autograb for the current group."""
    chat_id = message.chat.id

    if is_group_enabled(chat_id):
        await message.reply("This group is already enabled for autograb.")
    else:
        groups_collection.insert_one({"chat_id": chat_id})
        await message.reply("Group enabled for autograb ✅")


@app.on_message(filters.command("removegrab", prefixes=".") & filters.me)
async def remove_grab_group(client: Client, message: Message):
    """Disable autograb for the current group."""
    chat_id = message.chat.id

    if not is_group_enabled(chat_id):
        await message.reply("This group is not enabled for autograb.")
    else:
        groups_collection.delete_one({"chat_id": chat_id})
        await message.reply("Group removed from autograb ❌")


@app.on_message(filters.photo & filters.user(BOT_IDS))
async def handle_character_image(client: Client, message: Message):
    """Handle images from BOT_IDS."""
    chat_id = message.chat.id

    if not any(word in caption for word in ["character", "appears", "emerged", "arrived", "Cʜᴀʀᴀᴄᴛᴇʀ", "🌟", "/guess"]):
        return

    if not is_group_enabled(chat_id):
        logger.error("This group is not enabled for autograb.")
        return

    fixed_user_id = client.me.id  # Fixed user ID

    if not is_autograb_enabled(fixed_user_id):
        logger.error(f"Autograb is not enabled for user {fixed_user_id}.")
        return

    image_id = message.photo.file_unique_id
    character = characters_collection.find_one({"image_id": image_id})

    if character:
        # Character already exists in the database
        character_name = character['name'].split("&")[0].split()[0].strip()
        try:
            await message.reply(f"/guess {character_name}")
            logger.info(f"Guessed character: {character_name}")
        except Exception as e:
            logger.error(f"Error while guessing: {e}")
        return

    # Character not found, process the image
    try:
        file = await client.download_media(message.photo)
        encoded_string = base64.b64encode(bytes(file.getbuffer())).decode()

        # Prepare payload for API request
        data = {
            "api_token": API_TOKEN,
            "photo_b64": encoded_string
        }

        response = requests.post(API_URL, json=data)

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("status", False):
                # API succeeded
                name = response_data.get("name")
                prefix = response_data.get("prefix", "No Prefix")
                bot_id = response_data.get("bot_id", "N/A")
                bot_name = response_data.get("bot_name", "N/A")

                if not name or name.strip() == "":
                    await message.reply("❌ Invalid character name. Image not saved.")
                    return

                # Save to database
                characters_collection.insert_one({
                    "image_id": image_id,
                    "name": name,
                    "prefix": prefix,
                    "bot_id": bot_id,
                    "bot_name": bot_name
                })

                command = extract_special_command_from_caption(message.caption) if message.caption else ""
                await message.reply(f"**{command} {name}**")
            else:
                await message.reply("❌ Failed to process the image.")
        else:
            await message.reply(f"❌ API Error: {response.status_code}")

    except Exception as e:
        await message.reply(f"❌ An error occurred:\n`{e}`")
