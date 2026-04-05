from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# List all databases
dbs = client.list_database_names()

if not dbs:
    print("No databases found.")
else:
    print("Databases in MongoDB instance:")
    for db in dbs:
        print(f"- {db}")