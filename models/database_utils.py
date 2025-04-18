import sqlite3
import os

def initialize_database():
    db_path = 'Quelea Birds database.db'
    
    # Check if database file exists
    if not os.path.exists(db_path):
        return "Error: Database file not found"
    
    # Test connection
    try:
        conn = sqlite3.connect(db_path)
        conn.close()
        return "Database connection successful"
    except Exception as e:
        return f"Database connection error: {e}"

def query_migration_records():
    conn = sqlite3.connect('Quelea Birds database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM migration_records")
    records = cursor.fetchall()
    conn.close()
    return records
