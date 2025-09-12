import mysql.connector
from config import DB_CONFIG

def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS library_management")
    cursor.execute("USE library_management")

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(50) PRIMARY KEY,
        password VARCHAR(255) NOT NULL,
        user_type ENUM('Admin','Student') NOT NULL,
        email VARCHAR(100)
    )
    """)

    # Create books table with created_at column
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        author VARCHAR(255) NOT NULL,
        isbn VARCHAR(50) NOT NULL UNIQUE,
        is_available BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        book_id INT NOT NULL,
        student_username VARCHAR(50) NOT NULL,
        borrow_date DATE NOT NULL,
        return_date DATE NOT NULL,
        is_returned BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (student_username) REFERENCES users(username) ON DELETE CASCADE
    )
    """)

    # Insert default admin if not exists
    cursor.execute("""
    INSERT IGNORE INTO users (username, password, user_type, email)
    VALUES ('admin', SHA2('admin123',256), 'Admin', 'admin@example.com')
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database initialized successfully with created_at column!")

if __name__ == "__main__":
    init_db()
