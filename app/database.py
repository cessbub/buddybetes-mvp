import sqlite3
import os

def create_connection():
    """Create a database connection to the SQLite database."""
    db_path = os.path.join(os.getcwd(), 'buddybetes.db')
    conn = sqlite3.connect(db_path)
    return conn

def create_tables():
    """Create tables in the SQLite database."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            glucose_level REAL NOT NULL,
            bp_systolic INTEGER NOT NULL,
            bp_diastolic INTEGER NOT NULL,
            food_intake TEXT,
            mood TEXT,
            symptoms TEXT,
            meal_context TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Tables created successfully.")

def create_user_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            email_reminder TEXT DEFAULT 'Daily',
            reminder_time TEXT DEFAULT '07:58'
        )
    ''')
    conn.commit()
    conn.close()