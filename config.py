import os
import dotenv
from telethon import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient

dotenv.load_dotenv('.env')

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
db_url = os.environ.get('MONGO_DB_URL')
database_name = os.environ.get('DATABASE_NAME')
collection_name = os.environ.get('COLLECTION_NAME')

bot = TelegramClient(
        'bot', 
        api_id, 
        api_hash, 
    ).start(bot_token=bot_token)

client = AsyncIOMotorClient(db_url)