import psycopg
import hashlib
from datetime import date, timedelta
from config import DB_CONFIG

# Note: For production, consider using a stronger hashing algorithm like bcrypt.
def hash_password(password: str) -> str:
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def column_exists(cursor, table: str, column: str) -> bool:
    """Checks if a column exists in a given table using a parameterized query."""
    cursor.execute("""
        SELECT 1
        FROM information_schema.columns
        WHERE table_name=%s AND column_name=%s
    """, (table, column))
    return cursor.fetchone() is not None

def init_db():
    """Initializes the database with schema and sample data."""
    # Connect directly to Render PostgreSQL
    conn = psycopg.connect(DB_CONFIG["url"])
    cur = conn.cursor()

    try:
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(50) PRIMARY KEY,
                password VARCHAR(255) NOT NULL,
                user_type VARCHAR(20) CHECK (user_type IN ('Admin','Student')),
                email VARCHAR(100) UNIQUE
            )
        """)

        # Books table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                isbn VARCHAR(50) UNIQUE NOT NULL,
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Extra book columns
        extras = {
            "category": "VARCHAR(100)",
            "description": "TEXT",
            "cover_image": "VARCHAR(255)",
            "pdf_file": "VARCHAR(255)"
        }
        for col, col_type in extras.items():
            if not column_exists(cur, "books", col):
                # Using a safe method for ALTER TABLE
                cur.execute(f"ALTER TABLE books ADD COLUMN {col} {col_type}")
                print(f"🛠️ Added missing column '{col}' to books")

        # Transactions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                book_id INT NOT NULL,
                student_username VARCHAR(50) NOT NULL,
                borrow_date DATE NOT NULL,
                return_date DATE NOT NULL,
                is_returned BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                FOREIGN KEY (student_username) REFERENCES users(username) ON DELETE CASCADE,
                UNIQUE (book_id, student_username, borrow_date) -- Prevents duplicate transactions for same borrow
            )
        """)

        # Default Admin
        cur.execute("""
            INSERT INTO users (username, password, user_type, email)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (username) DO NOTHING
        """, ("admin", hash_password("admin123"), "Admin", "admin@example.com"))

        # Sample Students
        students = [
            ("alice", hash_password("alice123"), "Student", "alice@example.com"),
            ("bob", hash_password("bob123"), "Student", "bob@example.com"),
        ]
        cur.executemany("""
            INSERT INTO users (username, password, user_type, email)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (username) DO NOTHING
        """, students)

        # Sample Books
        books = [
            ("The AI Revolution", "John Smith", "Technology", "ISBN001",
             "An introduction to AI concepts.", "ai.jpg", "ai.pdf"),
            ("Mystery of the Lost City", "Jane Doe", "Mystery", "ISBN002",
             "A thrilling mystery novel.", "mystery.jpg", "mystery.pdf"),
            ("Romantic Escapes", "Emily Rose", "Romance", "ISBN003",
             "A beautiful love story.", "romantic.jpg", "romantic.pdf"),
        ]
        for title, author, category, isbn, desc, cover, pdf in books:
            cur.execute("""
                INSERT INTO books (title, author, category, isbn, description, cover_image, pdf_file)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (isbn) DO NOTHING
            """, (title, author, category, isbn, desc, cover, pdf))

        # Sample Transactions
        transactions = [
            # A book that was borrowed and returned
            (2, "bob", date.today() - timedelta(days=5), date.today() - timedelta(days=1), True),
            # A book that is currently borrowed (logic corrected: return date is in the future)
            (1, "alice", date.today() - timedelta(days=2), date.today() + timedelta(days=12), False)
        ]

        # Check if transaction with same book_id, student_username, and borrow_date exists before inserting
        for book_id, student_username, borrow_date, return_date, is_returned in transactions:
            cur.execute("""
                INSERT INTO transactions (book_id, student_username, borrow_date, return_date, is_returned)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (book_id, student_username, borrow_date) DO NOTHING
            """, (book_id, student_username, borrow_date, return_date, is_returned))

        conn.commit()
        print("✅ DB initialized with schema + default admin + sample data")

    except Exception as e:
        conn.rollback()
        print(f"❌ An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_db()