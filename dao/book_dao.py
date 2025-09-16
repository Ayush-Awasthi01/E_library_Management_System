# dao/book_dao.py
import psycopg2
from psycopg2.extras import DictCursor
from config import DB_CONFIG

# ----- Helper -----
def get_connection():
    return psycopg2.connect(DB_CONFIG["url"], cursor_factory=DictCursor)

# ----- DAO Class -----
class BookDAO:
    def add_book(self, title, author, category, isbn=None, description=None, cover_image=None, pdf_file=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO books (title, author, category, isbn, description, cover_image, pdf_file) 
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (title, author, category, isbn, description, cover_image, pdf_file)
        )
        conn.commit()
        cur.close()
        conn.close()

    def update_book(self, book_id, title, author, category, isbn=None, description=None, cover_image=None, pdf_file=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE books SET title=%s, author=%s, category=%s, isbn=%s, description=%s, 
               cover_image=%s, pdf_file=%s WHERE id=%s""",
            (title, author, category, isbn, description, cover_image, pdf_file, book_id)
        )
        conn.commit()
        cur.close()
        conn.close()

    def delete_book(self, book_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
        conn.commit()
        cur.close()
        conn.close()

    def get_all_books(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM books ORDER BY created_at DESC")
        books = cur.fetchall()
        cur.close()
        conn.close()
        # Fallback for missing description
        for book in books:
            if not book.get("description"):
                book["description"] = "No description available"
        return books

    def get_book(self, book_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM books WHERE id=%s", (book_id,))
        book = cur.fetchone()
        cur.close()
        conn.close()
        return book

    def search_books(self, keyword=None, category=None, only_available=False):
        conn = get_connection()
        cur = conn.cursor()
        query = "SELECT * FROM books WHERE 1=1"
        params = []
        if keyword:
            query += " AND (title ILIKE %s OR author ILIKE %s)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if category:
            query += " AND category=%s"
            params.append(category)
        if only_available:
            query += " AND available=TRUE"
        query += " ORDER BY created_at DESC"
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def set_availability(self, book_id, is_available: bool):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE books SET available=%s WHERE id=%s", (is_available, book_id))
        conn.commit()
        cur.close()
        conn.close()
