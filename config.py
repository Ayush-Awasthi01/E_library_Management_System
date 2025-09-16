import os

# Secret Key
SECRET_KEY = "supersecretkey"

# Render PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL") or \
"postgresql://library_management_pdq4_user:xcFZrRwqm7oKqGweUQrR5QkQn2V691fI@dpg-d31vqi7fte5s7380gpo0-a.oregon-postgres.render.com/library_management_pdq4"

DB_CONFIG = {
    "url": DATABASE_URL
}

# File uploads
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif"}

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS") or "ayushawasthi765@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or "1223950Ayush@#"
