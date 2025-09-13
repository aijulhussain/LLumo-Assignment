import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "assessment_db")
COLLECTION_NAME = os.getenv("EMP_COLLECTION", "employees")

client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
employees_collection = db[COLLECTION_NAME]


async def ensure_indexes_and_schema():
    # Create unique index on employee_id
    await employees_collection.create_index([("employee_id", ASCENDING)], unique=True)

    # JSON Schema validator (optional, requires permissions)
    json_schema = {
        "bsonType": "object",
        "required": ["employee_id", "name", "department", "salary", "joining_date", "skills"],
        "properties": {
            "employee_id": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "department": {"bsonType": "string"},
            "salary": {"bsonType": ["int", "double", "long"]},
            "joining_date": {"bsonType": "date"},
            "skills": {"bsonType": "array", "items": {"bsonType": "string"}}
        }
    }

    existing = await db.list_collection_names()
    if COLLECTION_NAME not in existing:
        await db.create_collection(
            COLLECTION_NAME,
            validator={"$jsonSchema": json_schema},
            validationLevel="moderate"
        )
