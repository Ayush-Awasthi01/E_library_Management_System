# dao/user_dao.py
import mysql.connector
from config import DB_CONFIG
import hashlib

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class UserDAO:
    def add_user(self, username, password, user_type='Student', email=None):
        conn = get_connection()
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute("INSERT INTO users (username, password, user_type, email) VALUES (%s,%s,%s,%s)",
                       (username, hashed, user_type, email))
        conn.commit()
        cursor.close()
        conn.close()

    def authenticate(self, username, password):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        hashed = hash_password(password)
        cursor.execute("SELECT username, user_type, email FROM users WHERE username=%s AND password=%s",
                       (username, hashed))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user

    def get_all_students(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username, email, created_at FROM users WHERE user_type='Student'")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def delete_user(self, username):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username=%s", (username,))
        conn.commit()
        cursor.close()
        conn.close()
