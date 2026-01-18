import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Charger variables locales (.env) si présent
load_dotenv()

# 🔑 MongoDB Railway URL
MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise Exception("❌ MONGO_URL not found in environment variables")

# Connexion MongoDB
client = MongoClient(MONGO_URL)
db = client.get_default_database()

jobs_col = db["jobs"]
candidates_col = db["candidates"]

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def seed():
    jobs = load_json("data/jobs.json")
    candidates = load_json("data/candidates.json")

    jobs_col.delete_many({})
    candidates_col.delete_many({})

    jobs_col.insert_many(jobs)
    candidates_col.insert_many(candidates)

    print("✅ Database seeded successfully")
    print("📦 Jobs:", jobs_col.count_documents({}))
    print("👥 Candidates:", candidates_col.count_documents({}))

if __name__ == "__main__":
    seed()
