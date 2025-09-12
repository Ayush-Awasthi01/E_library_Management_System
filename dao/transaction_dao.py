# dao/transaction_dao.py
import mysql.connector
from config import DB_CONFIG
from datetime import date, timedelta

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

BORROW_DAYS = 14

class TransactionDAO:
    def borrow_book(self, book_id, username):
        conn = get_connection()
        cursor = conn.cursor()
        # check availability
        cursor.execute("SELECT is_available FROM books WHERE id=%s", (book_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            cursor.close(); conn.close(); return False
        borrow_date = date.today()
        return_date = borrow_date + timedelta(days=BORROW_DAYS)
        cursor.execute("INSERT INTO transactions (book_id, student_username, borrow_date, return_date, is_returned) VALUES (%s,%s,%s,%s, FALSE)",
                       (book_id, username, borrow_date, return_date))
        cursor.execute("UPDATE books SET is_available=FALSE WHERE id=%s", (book_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def return_book(self, book_id, username):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE transactions SET is_returned=TRUE, returned_at=NOW() WHERE book_id=%s AND student_username=%s AND is_returned=FALSE",
                       (book_id, username))
        cursor.execute("UPDATE books SET is_available=TRUE WHERE id=%s", (book_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def get_student_transactions(self, username):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.*, b.title, b.pdf_file
            FROM transactions t
            JOIN books b ON t.book_id=b.id
            WHERE t.student_username=%s
            ORDER BY t.borrow_date DESC
        """, (username,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def get_all_transactions(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.*, b.title, u.email
            FROM transactions t
            JOIN books b ON t.book_id=b.id
            JOIN users u ON t.student_username=u.username
            ORDER BY t.borrow_date DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def get_overdue_transactions(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, t.student_username, t.return_date, b.title, u.email
            FROM transactions t
            JOIN books b ON t.book_id=b.id
            JOIN users u ON t.student_username=u.username
            WHERE t.is_returned=FALSE AND t.return_date < CURDATE()
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
