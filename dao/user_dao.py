# dao/user_dao.py
import psycopg
from psycopg.rows import dict_row
from config import DB_CONFIG
import hashlib

# ----- Helper functions -----
def get_connection():
    # Returns a connection with dict-like row access
    return psycopg.connect(DB_CONFIG["url"], row_factory=dict_row)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ----- DAO Class -----
class UserDAO:
    def add_user(self, username, password, user_type='Student', email=None):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            hashed = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, user_type, email) VALUES (%s, %s, %s, %s)",
                (username, hashed, user_type, email)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def authenticate(self, username, password):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            hashed = hash_password(password)
            cursor.execute(
                "SELECT username, user_type, email FROM users WHERE username=%s AND password=%s",
                (username, hashed)
            )
            return cursor.fetchone()  # returns a dict thanks to row_factory=dict_row
        finally:
            cursor.close()
            conn.close()

    def get_all_students(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT username, email FROM users WHERE user_type='Student'")
            return cursor.fetchall()  # list of dicts
        finally:
            cursor.close()
            conn.close()

    def delete_user(self, username):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username=%s", (username,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
