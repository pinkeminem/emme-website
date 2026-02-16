import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', os.urandom(32).hex())
    DB_PATH = os.path.join(os.path.dirname(__file__), 'emme.db')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 150 * 1024 * 1024  # 150MB
    MAX_CONTENT_LENGTH = 150 * 1024 * 1024  # Flask rejects larger requests
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov'}

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # SMTP settings for contact form
    SMTP_HOST = os.getenv('SMTP_HOST', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASS = os.getenv('SMTP_PASS', '')
    SMTP_FROM = os.getenv('SMTP_FROM', '')
    CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'booking@emme-em.me')

    # Admin credentials (set in .env)
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'emme')

    # Drive / file manager — local folder mirrored to admin
    DRIVE_FOLDER = os.getenv('DRIVE_FOLDER',
                             os.path.join(os.path.dirname(__file__), 'drive'))
