# dao/transaction_dao.py
import psycopg
from psycopg.rows import dict_row
from datetime import date, timedelta
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
                # Check availability in a single query
                cursor.execute("SELECT is_available FROM books WHERE id=%s", (book_id,))
                book = cursor.fetchone()
                
                # If book does not exist or is unavailable
                if not book or not book["is_available"]:
                    return False

                # Insert transaction with borrow and return date
                borrow_date = date.today()
                return_date = borrow_date + timedelta(weeks=2)  # 2 weeks borrow period
                
                cursor.execute(
                    """
                    INSERT INTO transactions (book_id, student_username, borrow_date, return_date)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (book_id, student_username, borrow_date, return_date)
                )

                # Update book availability to FALSE
                cursor.execute("UPDATE books SET is_available=FALSE WHERE id=%s", (book_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error borrowing book: {e}")
            return False
        finally:
            if conn:
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
                
                if cursor.rowcount == 0:
                    # No un-returned transaction found
                    print("No un-returned transaction found for this user/book.")
                    return False

                # Update book availability to TRUE
                cursor.execute("UPDATE books SET is_available=TRUE WHERE id=%s", (book_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error returning book: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_all_transactions(self) -> list:
        """
        Returns all transactions, with book title and student email.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT t.*, b.title, u.email
                    FROM transactions t
                    JOIN books b ON t.book_id = b.id
                    JOIN users u ON t.student_username = u.username
                    ORDER BY t.borrow_date DESC
                """)
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()

    def get_student_transactions(self, student_username: str) -> list:
        """
        Returns all transactions for a given student.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT t.*, b.title, b.pdf_file, b.cover_image
                    FROM transactions t
                    JOIN books b ON t.book_id=b.id
                    WHERE t.student_username=%s
                    ORDER BY t.borrow_date DESC
                """, (student_username,))
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()

    def get_overdue_transactions(self) -> list:
        """
        Returns all overdue transactions with student emails for notifications.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT t.*, b.title, u.email, u.username as student_username
                    FROM transactions t
                    JOIN books b ON t.book_id=b.id
                    JOIN users u ON t.student_username=u.username
                    WHERE t.is_returned=FALSE AND t.return_date < CURRENT_DATE
                    ORDER BY t.return_date ASC
                """)
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()

    def check_borrow_status(self, filename: str, student_username: str) -> bool:
        """
        Checks if a student has a valid, un-returned borrow transaction for a given PDF file.
        """
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 1
                    FROM transactions t
                    JOIN books b ON t.book_id=b.id
                    WHERE b.pdf_file=%s AND t.student_username=%s AND t.is_returned=FALSE
                """, (filename, student_username))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking borrow status: {e}")
            return False
        finally:
            if conn:
                conn.close()
