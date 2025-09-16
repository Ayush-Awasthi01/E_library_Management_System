# dao/book_dao.py
import psycopg
from psycopg.rows import dict_row
from config import DB_CONFIG

# ----- Helper function -----
def get_connection():
    """Returns a new connection to the database with dict-like row access."""
    return psycopg.connect(DB_CONFIG["url"], row_factory=dict_row)

# ----- DAO Class -----
class BookDAO:
    def add_book(self, title, author, category, isbn, description, cover_image, pdf_file) -> bool:
        """Adds a new book to the database."""
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO books (title, author, category, isbn, description, cover_image, pdf_file, is_available)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                """, (title, author, category, isbn, description, cover_image, pdf_file))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error adding book: {e}")
            return False
        finally:
            conn.close()

    def update_book(self, book_id, title, author, category, isbn, description, cover_image, pdf_file) -> bool:
        """Updates an existing book."""
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE books
                    SET title=%s, author=%s, category=%s, isbn=%s, description=%s,
                        cover_image=%s, pdf_file=%s
                    WHERE id=%s
                """, (title, author, category, isbn, description, cover_image, pdf_file, book_id))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error updating book: {e}")
            return False
        finally:
            conn.close()

    def delete_book(self, book_id) -> bool:
        """Deletes a book from the database."""
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting book: {e}")
            return False
        finally:
            conn.close()

    def get_all_books(self) -> list:
        """Returns all books, newest first."""
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
                books = cursor.fetchall()
                for book in books:
                    if not book["description"]:
                        book["description"] = "No description available"
                return books
        finally:
            conn.close()

    def get_book(self, book_id):
        """Returns a single book by ID."""
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM books WHERE id=%s", (book_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    def search_books(self, keyword=None, category=None, only_available=False) -> list:
        """Search books by keyword, category, and availability."""
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                query = "SELECT * FROM books WHERE 1=1"
                params = []
                if keyword:
                    query += " AND (title ILIKE %s OR author ILIKE %s)"
                    params.extend([f"%{keyword}%", f"%{keyword}%"])
                if category:
                    query += " AND category=%s"
                    params.append(category)
                if only_available:
                    query += " AND is_available=TRUE"
                query += " ORDER BY created_at DESC"
                cursor.execute(query, tuple(params))
                return cursor.fetchall()
        finally:
            conn.close()

    def set_availability(self, book_id: int, is_available: bool) -> bool:
        """Updates the availability of a book."""
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("UPDATE books SET is_available=%s WHERE id=%s", (is_available, book_id))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error setting book availability: {e}")
            return False
        finally:
            conn.close()
