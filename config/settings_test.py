"""
Test settings for running tests
"""
import os
from .settings import *

# Use a fast test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

# Use a constant secret key for tests
SECRET_KEY = 'test-secret-key-for-testing-only'

# Disable debugging
DEBUG = False

# Use fast password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use simple file storage for tests
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# Disable logging during tests
LOGGING = {}
