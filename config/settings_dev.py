from .settings import *

# Override settings for development
DEBUG = True
SECRET_KEY = 'django-insecure-dev-key-for-testing'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Authentication settings
LOGIN_URL = '/login/'  # Set login URL to our custom login page
LOGIN_REDIRECT_URL = '/dashboard/'  # Redirect to dashboard after login
LOGOUT_REDIRECT_URL = '/'  # Redirect to home page after logout

# Mock Stripe settings for development
STRIPE_PUBLISHABLE_KEY = 'dummy'
STRIPE_SECRET_KEY = 'dummy'
STRIPE_WEBHOOK_SECRET = 'dummy'

# Disable SSL/HTTPS requirements in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
