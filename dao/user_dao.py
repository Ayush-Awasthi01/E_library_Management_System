# dao/book_dao.py
import psycopg
from psycopg.rows import dict_row
from config import DB_CONFIG

# ----- Helper -----
def get_connection():
    return psycopg.connect(DB_CONFIG["url"], row_factory=dict_row)

# ----- DAO Class -----
class BookDAO:

    def add_book(self, title, author, category, isbn=None, description=None, cover_image=None, pdf_file=None):
        """Add a new book to the database."""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO books (title, author, category, isbn, description, cover_image, pdf_file)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (title, author, category, isbn, description, cover_image, pdf_file)
                )
                conn.commit()

    def get_all_books(self):
        """Return a list of all books."""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM books ORDER BY id")
                return cursor.fetchall()

    def get_book(self, book_id):
        """Return a single book by ID."""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM books WHERE id=%s", (book_id,))
                return cursor.fetchone()

    def update_book(self, book_id, title, author, category, isbn=None, description=None, cover_image=None, pdf_file=None):
        """Update a book's information."""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE books
                    SET title=%s, author=%s, category=%s, isbn=%s, description=%s, cover_image=%s, pdf_file=%s
                    WHERE id=%s
                    """,
                    (title, author, category, isbn, description, cover_image, pdf_file, book_id)
                )
                conn.commit()

    def delete_book(self, book_id):
        """Delete a book by ID."""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
                conn.commit()

    def search_books(self, keyword=None, category=None, only_available=False):
        """Search books with optional keyword, category, and availability filter."""
        query = "SELECT * FROM books"
        conditions = []
        params = []

        if keyword:
            conditions.append("(title ILIKE %s OR author ILIKE %s OR description ILIKE %s)")
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])

        if category:
            conditions.append("category=%s")
            params.append(category)

        if only_available:
            conditions.append("available_copies>0")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY id"

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
