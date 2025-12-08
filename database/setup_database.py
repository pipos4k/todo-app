import sqlite3, os

DB_PATH = "/data/todo.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    db_connection = sqlite3.connect(DB_PATH)
    cursor = db_connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            timestamp TEXT
        )
    ''')
    db_connection.commit()
    db_connection.close()

def get_db_connection():
    db_connection = sqlite3.connect(DB_PATH)
    db_connection.row_factory = sqlite3.Row
    return db_connection