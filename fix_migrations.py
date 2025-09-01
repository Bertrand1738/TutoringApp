"""
This script diagnoses and fixes migration issues in the Django project.
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
from django.conf import settings
from django.db.migrations.recorder import MigrationRecorder

def check_installed_apps():
    """Check if all apps are correctly installed."""
    print("Checking installed apps...")
    all_app_configs = apps.get_app_configs()
    app_names = [app.name for app in all_app_configs]
    
    print(f"Found {len(app_names)} installed apps:")
    for name in app_names:
        print(f"- {name}")
    
    # Check for specific apps we know should be installed
    critical_apps = ['courses', 'enrollments', 'live_sessions', 'payments']
    for app_name in critical_apps:
        if app_name in app_names:
            print(f"✅ {app_name} is correctly installed")
        else:
            print(f"❌ ERROR: {app_name} is NOT installed!")

def check_app_models():
    """Check if all critical models can be imported."""
    print("\nChecking critical models...")
    try:
        from courses.models import Course, PDF, Video
        print("✅ Course models (Course, PDF, Video) imported successfully")
    except ImportError as e:
        print(f"❌ ERROR importing Course models: {e}")
    
    try:
        from enrollments.models import Enrollment
        print("✅ Enrollment model imported successfully")
    except ImportError as e:
        print(f"❌ ERROR importing Enrollment model: {e}")
        
    try:
        from payments.models import Order
        print("✅ Order model imported successfully")
    except ImportError as e:
        print(f"❌ ERROR importing Order model: {e}")
        
    try:
        from live_sessions.models import LiveSession
        print("✅ LiveSession model imported successfully")
    except ImportError as e:
        print(f"❌ ERROR importing LiveSession model: {e}")

def check_migrations():
    """Check migration files for consistency."""
    print("\nChecking migration files...")
    
    # List of apps to check
    apps_to_check = ['courses', 'enrollments', 'payments', 'live_sessions']
    
    for app_name in apps_to_check:
        migrations_path = os.path.join(settings.BASE_DIR, app_name, 'migrations')
        if not os.path.exists(migrations_path):
            print(f"❌ No migrations directory found for {app_name}")
            continue
            
        migration_files = [f for f in os.listdir(migrations_path) 
                          if f.endswith('.py') and not f.startswith('__')]
        
        print(f"Found {len(migration_files)} migration files for {app_name}:")
        for migration_file in sorted(migration_files):
            print(f"  - {migration_file}")

def fix_initial_migrations():
    """Fix issues with initial migrations that might be causing problems."""
    print("\nFixing initial migrations...")
    
    # Check and possibly fix courses initial migration
    courses_initial = os.path.join(settings.BASE_DIR, 'courses', 'migrations', '0001_initial.py')
    if os.path.exists(courses_initial):
        print(f"Found courses initial migration at {courses_initial}")
        # Check if it's a placeholder migration that might be causing issues
        with open(courses_initial, 'r') as f:
            content = f.read()
        
        if "replaces" in content and "operations = []" in content:
            print("⚠️ This appears to be a placeholder migration that might cause issues")
            print("Recommendation: Create proper initial migration or remove placeholder")
    else:
        print("No courses initial migration found")

def suggest_fixes():
    """Provide suggestions to fix migration issues."""
    print("\nSuggested fixes for migration issues:")
    print("1. Make sure all apps are correctly listed in INSTALLED_APPS")
    print("2. Check for circular dependencies between app models")
    print("3. Fix any 'replaces' migrations that might be causing issues")
    print("4. For a fresh start, consider:")
    print("   a. Delete all migration files (except __init__.py)")
    print("   b. Delete db.sqlite3")
    print("   c. Run 'python manage.py makemigrations'")
    print("   d. Run 'python manage.py migrate'")
    print("\nSpecific to your error about 'courses' not being installed:")
    print("- Verify 'courses' app is correctly in INSTALLED_APPS with correct path")
    print("- Check courses/__init__.py includes default_app_config")
    print("- Check that courses/apps.py has a correctly defined CoursesConfig")
    
if __name__ == "__main__":
    print("Django Migration Diagnostic Tool")
    print("=" * 40)
    
    # Run all checks
    check_installed_apps()
    check_app_models()
    check_migrations()
    fix_initial_migrations()
    suggest_fixes()
    
    print("\nDiagnostic complete!")
