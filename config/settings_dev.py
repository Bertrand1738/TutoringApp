from .settings import *

# Override settings for development
DEBUG = True
SECRET_KEY = 'django-insecure-dev-key-for-testing'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Mock Stripe settings for development
STRIPE_PUBLISHABLE_KEY = 'dummy'
STRIPE_SECRET_KEY = 'dummy'
STRIPE_WEBHOOK_SECRET = 'dummy'

# Disable SSL/HTTPS requirements in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
