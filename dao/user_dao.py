# dao/user_dao.py
import psycopg
from psycopg.rows import dict_row
from config import DB_CONFIG
import hashlib

# ----- Helper functions -----
def get_connection():
    """
    Returns a new connection to the database with dict-like row access.
    """
    return psycopg.connect(DB_CONFIG["url"], row_factory=dict_row)

def hash_password(password: str) -> str:
    """
    Returns SHA-256 hash of the given password.
    """
    return hashlib.sha256(password.encode()).hexdigest()

# ----- DAO Class -----
class UserDAO:
    def add_user(self, username: str, password: str, user_type: str = 'Student', email: str = None) -> bool:
        """
        Adds a new user. Returns True if successful.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                hashed = hash_password(password)
                cursor.execute(
                    """
                    INSERT INTO users (username, password, user_type, email)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (username, hashed, user_type, email)
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            conn.close()

    def authenticate(self, username: str, password: str) -> dict | None:
        """
        Authenticates a user. Returns user dict if valid, else None.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                hashed = hash_password(password)
                cursor.execute(
                    "SELECT username, user_type, email FROM users WHERE username=%s AND password=%s",
                    (username, hashed)
                )
                return cursor.fetchone()
        finally:
            conn.close()

    def get_all_students(self) -> list:
        """
        Returns a list of all student users.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT username, email FROM users WHERE user_type='Student'")
                return cursor.fetchall()
        finally:
            conn.close()

    def delete_user(self, username: str) -> bool:
        """
        Deletes a user by username. Returns True if successful.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE username=%s", (username,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            conn.close()
