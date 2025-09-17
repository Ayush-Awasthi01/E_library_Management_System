# dao/user_dao.py
import psycopg
from psycopg.rows import dict_row
from config import DB_CONFIG
import bcrypt # Using bcrypt for secure password hashing

# ----- Helper functions -----
def get_connection():
    """Returns a new connection to the database with dict-like row access."""
    return psycopg.connect(DB_CONFIG["url"], row_factory=dict_row)

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    # bcrypt automatically handles salting and is designed to be slow
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Checks a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ----- DAO Class -----
class UserDAO:
    def add_user(self, username: str, password: str, user_type: str = 'Student', email: str = None) -> bool:
        """Adds a new user. Returns True if successful."""
        conn = None
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
        except psycopg.IntegrityError as e:
            # Handle unique constraint violation (e.g., username or email already exists)
            print(f"Error adding user: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def authenticate(self, username: str, password: str) -> dict | None:
        """Authenticates a user. Returns user dict if valid, else None."""
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT username, user_type, email, password FROM users WHERE username=%s",
                    (username,)
                )
                user = cursor.fetchone()
                if user and check_password(password, user['password']):
                    # Remove the password hash before returning the user dict
                    del user['password']
                    return user
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_all_students(self) -> list:
        """Returns a list of all student users."""
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT username, email FROM users WHERE user_type='Student'")
                return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving students: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def delete_user(self, username: str) -> bool:
        """Deletes a user by username. Returns True if successful."""
        conn = None
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
            if conn:
                conn.close()