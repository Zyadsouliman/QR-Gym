from app.database import update_db

if __name__ == "__main__":
    print("Updating database schema...")
    update_db()
    print("Database schema updated successfully!") 