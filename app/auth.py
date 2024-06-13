import sqlite3
from passlib.context import CryptContext
from database import create_connection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate(username, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    if user and pwd_context.verify(password, user[3]):  # Assuming password is the 4th column
        return True, user[2], user[0]  # Assuming name is the 3rd column, username is the 1st column
    return False, None, None

def get_user_info(username):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_info(old_username, new_username, email, name, email_reminder, reminder_time):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE users
        SET username = ?, email = ?, name = ?, email_reminder = ?, reminder_time = ?
        WHERE username = ?
    ''', (new_username, email, name, email_reminder, reminder_time, old_username))
    conn.commit()
    conn.close()
