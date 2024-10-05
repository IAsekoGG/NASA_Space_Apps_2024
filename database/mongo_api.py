from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()


def get_database(db_name):
    mongo_user = os.getenv("MONGO_USER")
    mongo_password = os.getenv("MONGO_PASSWORD")
    mongo_cluster = os.getenv("MONGO_CLUSTER")
    mongo_options = os.getenv("MONGO_OPTIONS", "")
    
    if not all([mongo_user, mongo_password, mongo_cluster]):
        raise ValueError("Missing environment variables for MongoDB connection.")
    
    mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_cluster}/?{mongo_options}"
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    return db

db = get_database("data")


def insert_data(collection_name, data):
    if collection_name not in db.list_collection_names():
        print(f"Collection '{collection_name}' does not exist. Creating collection...")
    collection = db[collection_name]
    collection.insert_one(data)


def insert_many_data(collection_name, data_list):
    if collection_name not in db.list_collection_names():
        print(f"Collection '{collection_name}' does not exist. Creating collection...")
    collection = db[collection_name]
    collection.insert_many(data_list)


def get_data(collection_name, query: dict):
    collection = db[collection_name]
    data = collection.find(query, {"_id": 0})
    return list(data)

print(get_data("telegram", {}))
