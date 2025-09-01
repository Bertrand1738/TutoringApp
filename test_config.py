from django.core.cache import cache
from django.conf import settings
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_configuration():
    print("Testing Redis connection...")
    try:
        cache.set('test_key', 'Redis is working!')
        result = cache.get('test_key')
        print(f'Redis test result: {result}')
    except Exception as e:
        print(f'Redis error: {str(e)}')

    print("\nTesting Zoom settings...")
    try:
        print(f'ZOOM_ACCOUNT_ID: {bool(settings.ZOOM_ACCOUNT_ID)}')
        print(f'ZOOM_CLIENT_ID: {bool(settings.ZOOM_CLIENT_ID)}')
        print(f'ZOOM_CLIENT_SECRET: {bool(settings.ZOOM_CLIENT_SECRET)}')
    except Exception as e:
        print(f'Zoom settings error: {str(e)}')

if __name__ == '__main__':
    test_configuration()
