import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate(username, password):
    conn = sqlite3.connect('buddybetes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    if user and pwd_context.verify(password, user[3]):
        return user[2], True, username  # Return name, authentication status, and username
    return None, False, None

def get_user_info(username):
    conn = sqlite3.connect('buddybetes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_info(username, new_username, email, name):
    conn = sqlite3.connect('buddybetes.db')
    c = conn.cursor()
    c.execute('''
        UPDATE users
        SET username = ?, email = ?, name = ?
        WHERE username = ?
    ''', (new_username, email, name, username))
    conn.commit()
    conn.close()
