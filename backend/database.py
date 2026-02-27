import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ai_fashion")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
designs_col = db["designs"]
uploads_col = db["uploads"]
recommendations_col = db["recommendations"]
products_col = db["products"]
users_col = db["users"]
