from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()


def get_database(db_name):
    # Get the MongoDB URI from the environment variable
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("No MONGO_URI found in environment variables")

    # Create a connection to MongoDB using the URI
    client = MongoClient(mongo_uri)
    # Access the specified database
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
