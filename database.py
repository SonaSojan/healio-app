import sqlite3

def get_db_connection():
    conn = sqlite3.connect("healio.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            message TEXT,
            severity TEXT,
            reply TEXT
        )
    """)
    conn.commit()
    conn.close()
