from pymongo import MongoClient

# 1. Connect to MongoDB
# Replace with your MongoDB URI if needed
client = MongoClient("mongodb://localhost:27017/")

# 2. Select database
db = client["checkpointing_db"]  # change to your DB name

print(f"Connected to database: {db.name}")

# 3. List collections
collections = db.list_collection_names()

if not collections:
    print("No collections found.")
else:
    print("\nCollections:")
    for coll_name in collections:
        print(f"- {coll_name}")

    # 4. Show data in each collection
    for coll_name in collections:
        print(f"\nData in collection '{coll_name}':")
        collection = db[coll_name]

        documents = collection.find()

        found = False
        for doc in documents:
            print(doc)
            found = True

        if not found:
            print("  (No documents found)")