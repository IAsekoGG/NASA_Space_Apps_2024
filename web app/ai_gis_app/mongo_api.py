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

db = get_database("web_app_data_test")


def insert_data(collection_name, data):
    if collection_name not in db.list_collection_names():
        print(f"Collection '{collection_name}' does not exist. Creating collection...")
    collection = db[collection_name]
    collection.insert_one(data)


def upsert_many_data(collection_name, data_list):
    if collection_name not in db.list_collection_names():
        print(f"Collection '{collection_name}' does not exist. Creating collection...")
    
    collection = db[collection_name]
    
    for data in data_list:
        # Assuming each document has a unique _id field
        collection.update_one(
            {"_id": data["_id"]},  # Find document by _id
            {"$set": data},  # Set document data
            upsert=True  # Insert if it doesn't exist
        )


def get_data(collection_name, query: dict):
    collection = db[collection_name]
    data = collection.find(query)
    return list(data)

# print(get_data("telegram.Общежитие #19 КПИ_no_comments", {}))
