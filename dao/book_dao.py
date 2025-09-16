# dao/book_dao.py
import psycopg2
from psycopg2.extras import DictCursor
from config import DB_CONFIG

def get_connection():
    return psycopg2.connect(DB_CONFIG["url"], cursor_factory=DictCursor)

class BookDAO:
    def add_book(self, title, author, category, isbn, description, cover_image, pdf_file):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO books (title, author, category, isbn, description, cover_image, pdf_file)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (title, author, category, isbn, description, cover_image, pdf_file))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def update_book(self, book_id, title, author, category, isbn, description, cover_image, pdf_file):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE books SET title=%s, author=%s, category=%s, isbn=%s, description=%s,
                cover_image=%s, pdf_file=%s WHERE id=%s
            """, (title, author, category, isbn, description, cover_image, pdf_file, book_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def delete_book(self, book_id):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def get_all_books(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
            books = cursor.fetchall()
            for book in books:
                if not book["description"]:
                    book["description"] = "No description available"
            return books
        finally:
            cursor.close()
            conn.close()

    def get_book(self, book_id):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE id=%s", (book_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def search_books(self, keyword=None, category=None, only_available=False):
        conn = get_connection()
        try:
            cursor = conn.cursor()
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
            cursor.close()
            conn.close()

    def set_availability(self, book_id, is_available: bool):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE books SET is_available=%s WHERE id=%s", (is_available, book_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
