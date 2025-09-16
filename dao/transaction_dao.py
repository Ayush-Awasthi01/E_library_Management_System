# dao/transaction_dao.py
import psycopg
from psycopg.rows import dict_row
from config import DB_CONFIG

# ----- Helper function -----
def get_connection():
    """
    Returns a new connection to the database with dict-like row access.
    """
    return psycopg.connect(DB_CONFIG["url"], row_factory=dict_row)

# ----- DAO Class -----
class TransactionDAO:
    def borrow_book(self, book_id: int, student_username: str) -> bool:
        """
        Borrows a book if available. Returns True if successful.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                # Check availability
                cursor.execute("SELECT is_available FROM books WHERE id=%s", (book_id,))
                book = cursor.fetchone()
                if not book or not book["is_available"]:
                    return False

                # Insert transaction
                cursor.execute(
                    "INSERT INTO transactions (book_id, student_username) VALUES (%s, %s)",
                    (book_id, student_username)
                )

                # Update book availability
                cursor.execute("UPDATE books SET is_available=FALSE WHERE id=%s", (book_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error borrowing book: {e}")
            return False
        finally:
            conn.close()

    def return_book(self, book_id: int, student_username: str) -> bool:
        """
        Returns a borrowed book. Returns True if successful.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE transactions SET is_returned=TRUE
                    WHERE book_id=%s AND student_username=%s AND is_returned=FALSE
                """, (book_id, student_username))
                cursor.execute("UPDATE books SET is_available=TRUE WHERE id=%s", (book_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error returning book: {e}")
            return False
        finally:
            conn.close()

    def get_all_transactions(self) -> list:
        """
        Returns all transactions, newest first.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM transactions ORDER BY borrow_date DESC")
                return cursor.fetchall()
        finally:
            conn.close()

    def get_student_transactions(self, student_username: str) -> list:
        """
        Returns all transactions for a given student.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT t.*, b.title, b.pdf_file
                    FROM transactions t
                    JOIN books b ON t.book_id=b.id
                    WHERE t.student_username=%s
                    ORDER BY t.borrow_date DESC
                """, (student_username,))
                return cursor.fetchall()
        finally:
            conn.close()

    def get_overdue_transactions(self) -> list:
        """
        Returns all overdue transactions with student emails for notifications.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT t.*, b.title, u.email, t.student_username
                    FROM transactions t
                    JOIN books b ON t.book_id=b.id
                    JOIN users u ON t.student_username=u.username
                    WHERE t.is_returned=FALSE AND t.return_date < CURRENT_DATE
                    ORDER BY t.return_date ASC
                """)
                return cursor.fetchall()
        finally:
            conn.close()
