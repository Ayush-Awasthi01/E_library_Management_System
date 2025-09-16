# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from config import SECRET_KEY, DB_CONFIG, EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT

from dao.user_dao import UserDAO, hash_password, get_connection as user_get_connection
from dao.book_dao import BookDAO
from dao.transaction_dao import TransactionDAO
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_PERMANENT'] = False

# DAOs
user_dao = UserDAO()
book_dao = BookDAO()
tx_dao = TransactionDAO()

# Upload folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "pdfs")
COVER_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "covers")
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(COVER_FOLDER, exist_ok=True)

ALLOWED_PDF = {'pdf'}
ALLOWED_IMAGE = {'png','jpg','jpeg','gif'}

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in allowed_set

# ----- Helpers -----
def send_overdue_email(to_email, subject, body):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Email credentials not configured; skipping sending")
        return
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print("Failed to send email:", e)

# ----- Routes -----
@app.route('/')
def index():
    if session.get('username'):
        return redirect(url_for('catalog'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        user = user_dao.authenticate(username, password)
        if user:
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            session.permanent = False
            flash("Logged in successfully", "success")
            return redirect(url_for('catalog'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        username = request.form['username']
        email = request.form.get('email')
        password = request.form['password']
        if not username or not password:
            flash("Username and password are required", "danger")
            return redirect(url_for('register'))
        try:
            user_dao.add_user(username, password, 'Student', email)
            flash("Registration successful — please login", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash("Registration error: " + str(e), "danger")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for('login'))

# ------- Catalog/Search/Filter -------
BOOK_CATEGORIES = [
    "Science Fiction", "Romantic", "Mystery", "Biography", "History", "Fantasy", "Self-Help", "Technology"
]

@app.route('/catalog', methods=['GET','POST'])
def catalog():
    keyword = request.args.get('keyword') or request.form.get('keyword')
    category = request.args.get('category') or request.form.get('category')
    only_available = request.args.get('only_available')=='1' or (request.form.get('only_available')=='on')
    books = book_dao.search_books(keyword=keyword, category=category, only_available=only_available)
    return render_template('view_books.html', books=books, categories=BOOK_CATEGORIES,
                           keyword=keyword, category=category, only_available=only_available)

# ------- Admin routes -------
@app.route('/admin')
def admin_dashboard():
    if session.get('user_type')!='Admin':
        return redirect(url_for('login'))
    books = book_dao.get_all_books()
    students = user_dao.get_all_students()
    transactions = tx_dao.get_all_transactions()
    return render_template('dashboard_admin.html', books=books, students=students, transactions=transactions)

@app.route('/admin/add', methods=['GET','POST'])
def admin_add_book():
    if session.get('user_type')!='Admin':
        return redirect(url_for('login'))
    if request.method=='POST':
        title = request.form['title']; author = request.form['author']; category = request.form.get('category')
        isbn = request.form.get('isbn'); description = request.form.get('description')
        cover = request.files.get('cover_image'); pdf = request.files.get('pdf_file')
        cover_filename = secure_filename(cover.filename) if cover and allowed_file(cover.filename, ALLOWED_IMAGE) else None
        pdf_filename = secure_filename(pdf.filename) if pdf and allowed_file(pdf.filename, ALLOWED_PDF) else None
        if cover_filename: cover.save(os.path.join(COVER_FOLDER, cover_filename))
        if pdf_filename: pdf.save(os.path.join(PDF_FOLDER, pdf_filename))
        book_dao.add_book(title, author, category, isbn, description, cover_filename, pdf_filename)
        flash("Book added", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('add_book.html')

@app.route('/admin/edit/<int:book_id>', methods=['GET','POST'])
def admin_edit_book(book_id):
    if session.get('user_type')!='Admin':
        return redirect(url_for('login'))
    book = book_dao.get_book(book_id)
    if request.method=='POST':
        title = request.form['title']; author = request.form['author']; category = request.form.get('category')
        isbn = request.form.get('isbn'); description = request.form.get('description')
        cover = request.files.get('cover_image'); pdf = request.files.get('pdf_file')
        cover_filename = secure_filename(cover.filename) if cover and allowed_file(cover.filename, ALLOWED_IMAGE) else book.get('cover_image')
        pdf_filename = secure_filename(pdf.filename) if pdf and allowed_file(pdf.filename, ALLOWED_PDF) else book.get('pdf_file')
        if cover and cover_filename: cover.save(os.path.join(COVER_FOLDER, cover_filename))
        if pdf and pdf_filename: pdf.save(os.path.join(PDF_FOLDER, pdf_filename))
        book_dao.update_book(book_id, title, author, category, isbn, description, cover_filename, pdf_filename)
        flash("Book updated", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_book.html', book=book)

@app.route('/admin/delete/<int:book_id>', methods=['POST'])
def admin_delete_book(book_id):
    if session.get('user_type')!='Admin':
        return redirect(url_for('login'))
    book_dao.delete_book(book_id)
    flash("Book deleted", "info")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users', methods=['GET','POST'])
def admin_manage_users():
    if session.get('user_type')!='Admin':
        return redirect(url_for('login'))
    students = user_dao.get_all_students()
    return render_template('manage_users.html', students=students)

@app.route('/admin/delete_user/<username>', methods=['POST'])
def admin_delete_user(username):
    if session.get('user_type')!='Admin':
        return redirect(url_for('login'))
    user_dao.delete_user(username)
    flash("User deleted", "info")
    return redirect(url_for('admin_manage_users'))

@app.route('/admin/transactions')
def admin_transactions():
    if session.get('user_type')!='Admin':
        return redirect(url_for('login'))
    transactions = tx_dao.get_all_transactions()
    return render_template('transactions.html', transactions=transactions)

@app.route('/admin/send_overdue')
def admin_send_overdue():
    if session.get('user_type')!='Admin':
        return redirect(url_for('login'))
    overdue = tx_dao.get_overdue_transactions()
    for t in overdue:
        if t.get('email'):
            subject = f"Overdue notice for '{t['title']}'"
            body = f"Dear {t['student_username']},\nYour borrowed book '{t['title']}' was due on {t['return_date']}. Please return it as soon as possible."
            send_overdue_email(t['email'], subject, body)
    flash(f"Overdue emails processed ({len(overdue)}).", "info")
    return redirect(url_for('admin_dashboard'))

# ------- Student actions -------
@app.route('/borrow/<int:book_id>')
def borrow(book_id):
    if not session.get('username') or session.get('user_type')!='Student':
        return redirect(url_for('login'))
    ok = tx_dao.borrow_book(book_id, session['username'])
    flash("Borrowed — check My Books", "success" if ok else "Cannot borrow (not available)", "success" if ok else "danger")
    return redirect(url_for('catalog'))

@app.route('/mybooks')
def mybooks():
    if not session.get('username') or session.get('user_type')!='Student':
        return redirect(url_for('login'))
    books = tx_dao.get_student_transactions(session['username'])
    return render_template('my_books.html', books=books)

@app.route('/return/<int:book_id>')
def return_book(book_id):
    if not session.get('username') or session.get('user_type')!='Student':
        return redirect(url_for('login'))
    tx_dao.return_book(book_id, session['username'])
    flash("Returned. Thank you!", "success")
    return redirect(url_for('mybooks'))

@app.route('/download/pdf/<filename>')
def download_pdf(filename):
    if session.get('user_type')=='Admin':
        return send_from_directory(PDF_FOLDER, filename, as_attachment=True)
    conn = user_get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.* FROM transactions t
        JOIN books b ON t.book_id=b.id
        WHERE b.pdf_file=%s AND t.student_username=%s AND t.is_returned=FALSE
    """, (filename, session.get('username')))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return send_from_directory(PDF_FOLDER, filename, as_attachment=True)
    flash("You must borrow this book to download/read its PDF.", "danger")
    return redirect(url_for('mybooks'))

if __name__=='__main__':
    app.run(debug=True)
