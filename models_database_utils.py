import sqlite3

def initialize_database(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS migration_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            species TEXT NOT NULL,
            date DATE NOT NULL,
            location TEXT NOT NULL,
            longitude REAL NOT NULL,
            latitude REAL NOT NULL,
            temperature_c REAL,
            rainfall_mm REAL,
            humidity_percent REAL,
            wind_speed_m_s REAL,
            altitude_m INTEGER,
            notes TEXT,
            migration_likelihood INTEGER
        )
    """)
    conn.commit()

def query_migration_records(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM migration_data")
    return cursor.fetchall()