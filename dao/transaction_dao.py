# dao/transaction_dao.py
import psycopg2
from psycopg2.extras import DictCursor
from config import DB_CONFIG
from datetime import datetime

# ----- Helper -----
def get_connection():
    return psycopg2.connect(DB_CONFIG["url"], cursor_factory=DictCursor)

# ----- DAO Class -----
class TransactionDAO:
    def borrow_book(self, book_id, student_username):
        conn = get_connection()
        cur = conn.cursor()
        # Check availability
        cur.execute("SELECT available FROM books WHERE id=%s", (book_id,))
        book = cur.fetchone()
        if not book or not book['available']:
            cur.close()
            conn.close()
            return False
        # Insert transaction
        cur.execute(
            "INSERT INTO transactions (book_id, student_username) VALUES (%s,%s)",
            (book_id, student_username)
        )
        # Mark book as unavailable
        cur.execute("UPDATE books SET available=TRUE WHERE id=%s", (book_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True

    def return_book(self, book_id, student_username):
        conn = get_connection()
        cur = conn.cursor()
        # Update transaction
        cur.execute(
            """UPDATE transactions 
               SET return_date=%s, is_returned=TRUE 
               WHERE book_id=%s AND student_username=%s AND is_returned=FALSE""",
            (datetime.now(), book_id, student_username)
        )
        # Mark book as available
        cur.execute("UPDATE books SET available=TRUE WHERE id=%s", (book_id,))
        conn.commit()
        cur.close()
        conn.close()

    def get_all_transactions(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions ORDER BY borrow_date DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def get_student_transactions(self, student_username):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT t.*, b.title, b.pdf_file 
               FROM transactions t 
               JOIN books b ON t.book_id=b.id 
               WHERE t.student_username=%s 
               ORDER BY t.borrow_date DESC""",
            (student_username,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def get_overdue_transactions(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT t.*, u.email, u.username AS student_username, b.title
               FROM transactions t
               JOIN users u ON t.student_username=u.username
               JOIN books b ON t.book_id=b.id
               WHERE t.is_returned=FALSE AND t.borrow_date < NOW() - INTERVAL '14 days'"""
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
