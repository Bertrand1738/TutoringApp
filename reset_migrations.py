"""
Reset migrations and fix app registration issues.
"""
import os
import sys
import shutil
import glob

def reset_migrations():
    """
    Removes all migration files except __init__.py and
    deletes the database to start fresh.
    """
    # Delete SQLite database
    db_path = 'db.sqlite3'
    if os.path.exists(db_path):
        print(f"Removing database: {db_path}")
        os.remove(db_path)
    else:
        print(f"Database not found: {db_path}")
    
    # List of apps to clean migrations for
    apps = [
        'accounts',
        'courses', 
        'enrollments',
        'live_sessions',
        'payments',
        'reviews',
        'badges',
        'student_enrollments',
    ]
    
    for app in apps:
        migrations_dir = os.path.join(app, 'migrations')
        
        if not os.path.exists(migrations_dir):
            print(f"Migrations directory not found: {migrations_dir}")
            continue
            
        print(f"Cleaning migrations for: {app}")
        
        # Get all Python files except __init__.py
        migration_files = glob.glob(os.path.join(migrations_dir, '*.py'))
        for file_path in migration_files:
            if os.path.basename(file_path) != '__init__.py':
                print(f"  Removing: {file_path}")
                os.remove(file_path)
        
        # Delete __pycache__ directory if exists
        pycache_dir = os.path.join(migrations_dir, '__pycache__')
        if os.path.exists(pycache_dir):
            print(f"  Removing: {pycache_dir}")
            shutil.rmtree(pycache_dir)
    
    print("\nMigration files removed. Ready to run makemigrations and migrate.")

def fix_app_registration():
    """
    Update __init__.py files to ensure correct app registration.
    """
    apps_to_fix = [
        'courses',
        'enrollments',
        'live_sessions',
        'payments',
        'reviews',
        'badges',
    ]
    
    for app in apps_to_fix:
        init_file = os.path.join(app, '__init__.py')
        
        if not os.path.exists(init_file):
            print(f"Creating __init__.py for {app}")
            with open(init_file, 'w') as f:
                f.write(f"default_app_config = '{app}.apps.{app.title()}Config'\n")
        else:
            # Update existing file
            with open(init_file, 'r') as f:
                content = f.read()
                
            if 'default_app_config' not in content:
                print(f"Updating __init__.py for {app}")
                with open(init_file, 'w') as f:
                    f.write(f"default_app_config = '{app}.apps.{app.title()}Config'\n")
                    f.write(content)
            else:
                print(f"{app}/__init__.py already has app_config, skipping.")

if __name__ == "__main__":
    print("Django Migration Reset Tool")
    print("=" * 40)
    
    # Check if user is in correct directory
    if not os.path.exists('manage.py'):
        print("Error: manage.py not found. Please run this script from your Django project root.")
        sys.exit(1)
    
    choice = input("This will delete all migrations and the database. Are you sure? (y/n): ")
    if choice.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    # Fix app registration first
    fix_app_registration()
    
    # Then reset migrations
    reset_migrations()
    
    print("\nNext steps:")
    print("1. Run: python manage.py makemigrations")
    print("2. Run: python manage.py migrate")
