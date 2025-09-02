"""
Test settings for running tests
"""
import os
from .settings import *

# Use the same database as the main settings
# This way we have access to all our existing users and data
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use a constant secret key for tests
SECRET_KEY = 'test-secret-key-for-testing-only'

# Enable debugging for detailed error messages
DEBUG = True

# Add 127.0.0.1 to ALLOWED_HOSTS for local testing
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Use fast password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use simple file storage for tests
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# Disable logging during tests
LOGGING = {}

# Disable all security features that might cause issues
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = None
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = None

# Disable session and CSRF security
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_HTTPONLY = False

# Allow all CORS origins
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
