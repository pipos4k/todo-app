import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = os.getenv('DATABASE_URL')

# DATABASE_URL=postgresql://user:pass@host:port/dbname
if not DATABASE_URL:
    raise ValueError("DATABASE_URL enviroment variable is not set!")

def init_db():
    try:     
        db_connection = psycopg2.connect(DATABASE_URL)
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
        cursor.close()
        db_connection.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization failed: {e}.")
        raise

def get_db_connection():
    db_connection = psycopg2.connect(DATABASE_URL)
    db_connection.cursor_factory = RealDictCursor
    return db_connection