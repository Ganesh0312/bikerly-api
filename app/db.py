from motor.motor_asyncio import AsyncIOMotorClient
from beanie  import init_beanie
from app.services.config import MONGO_URL, MONGO_DB_NAME
from app.models.user import  User

client = None
async def init_db():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB_NAME]
    await init_beanie(database = db, document_models = [User])

async def close_db():
    if client:
        client.close()
        logger.info("❌ MongoDB connection closed")
    