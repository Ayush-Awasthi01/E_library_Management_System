import os

# Secret Key
SECRET_KEY = os.getenv("SECRET_KEY")

# Render PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

DB_CONFIG = {
    "url": DATABASE_URL
}

# File uploads
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif"}

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT", 587) # A non-sensitive fallback can be used here
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Add a check to ensure critical variables are set for production
if not all([SECRET_KEY, DATABASE_URL, EMAIL_ADDRESS, EMAIL_PASSWORD]):
    raise ValueError("One or more critical environment variables are not set. Please configure them before running the application.")