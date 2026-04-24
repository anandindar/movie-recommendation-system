try:
    from auth import init_db
    init_db()
    print("MongoDB connection Success")
except Exception as e:
    print(f"MongoDB connection Failed: {e}")
