"""
Script to completely reset migrations
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def reset_migrations():
    """Reset all migrations"""
    print("Resetting all migrations...")
    
    try:
        with connection.cursor() as cursor:
            # Delete all migration records
            cursor.execute("DELETE FROM django_migrations")
            print("✅ Migration records deleted from database")
    except Exception as e:
        print(f"❌ Error clearing migration records: {e}")
        return False
    
    print("\nNext steps:")
    print("1. Delete all migration files except __init__.py")
    print("2. Run 'python manage.py makemigrations'")
    print("3. Run 'python manage.py migrate --fake-initial'")
    
    return True

if __name__ == "__main__":
    reset_migrations()
