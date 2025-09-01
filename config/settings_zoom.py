# Zoom API Configuration
import os
from django.core.exceptions import ImproperlyConfigured
from config.settings import get_env_variable

# Zoom OAuth credentials with development defaults
ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID', 'dummy-account-id')
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID', 'dummy-client-id')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET', 'dummy-client-secret')

# Cache Configuration (using local memory cache for development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
