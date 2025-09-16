# dao/transaction_dao.py
import psycopg2
from psycopg2.extras import DictCursor
from config import DB_CONFIG

def get_connection():
    return psycopg2.connect(DB_CONFIG["url"], cursor_factory=DictCursor)

class TransactionDAO:
    def borrow_book(self, book_id, student_username):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # Check availability
            cursor.execute("SELECT is_available FROM books WHERE id=%s", (book_id,))
            book = cursor.fetchone()
            if not book or not book["is_available"]:
                return False
            # Borrow book
            cursor.execute("""
                INSERT INTO transactions (book_id, student_username)
                VALUES (%s,%s)
            """, (book_id, student_username))
            cursor.execute("UPDATE books SET is_available=FALSE WHERE id=%s", (book_id,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def return_book(self, book_id, student_username):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions SET is_returned=TRUE
                WHERE book_id=%s AND student_username=%s AND is_returned=FALSE
            """, (book_id, student_username))
            cursor.execute("UPDATE books SET is_available=TRUE WHERE id=%s", (book_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def get_all_transactions(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions ORDER BY borrow_date DESC")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_student_transactions(self, student_username):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, b.title, b.pdf_file FROM transactions t
                JOIN books b ON t.book_id=b.id
                WHERE t.student_username=%s
            """, (student_username,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_overdue_transactions(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, b.title, u.email as email, t.student_username
                FROM transactions t
                JOIN books b ON t.book_id=b.id
                JOIN users u ON t.student_username=u.username
                WHERE t.is_returned=FALSE AND t.return_date < CURRENT_DATE
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
