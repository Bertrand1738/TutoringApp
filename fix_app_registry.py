"""
Fix Django app registry issues.
"""
import os
import sys
import django
from django.conf import settings

def main():
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    # Import app config classes
    from courses.apps import CoursesConfig
    from enrollments.apps import EnrollmentsConfig
    from django.apps import apps
    
    # Print all registered apps
    print("Currently registered apps:")
    for app_config in apps.get_app_configs():
        print(f"- {app_config.name}")
    
    # Check if specific apps are registered
    app_names = [app_config.name for app_config in apps.get_app_configs()]
    print("\nChecking specific apps:")
    print(f"'courses' registered: {'courses' in app_names}")
    print(f"'enrollments' registered: {'enrollments' in app_names}")
    print(f"'course_enrollments' registered: {'course_enrollments' in app_names}")
    
    # Print the INSTALLED_APPS setting
    print("\nINSTALLED_APPS setting:")
    for app in settings.INSTALLED_APPS:
        print(f"- {app}")
    
    # Create a simple recommendation
    print("\nRecommendations:")
    print("1. Check that each app is correctly included in INSTALLED_APPS")
    print("2. Make sure there are no duplicate app names or conflicts")
    print("3. Verify that each app has a proper apps.py with AppConfig")
    print("4. Check __init__.py in each app has default_app_config if needed")
    
    # Provide specific fixes for common issues
    print("\nSpecific fixes to try:")
    print("1. In courses/__init__.py: default_app_config = 'courses.apps.CoursesConfig'")
    print("2. In settings.py: Replace 'courses' with 'courses.apps.CoursesConfig'")
    print("3. Check if course_enrollments and enrollments might be conflicting")
    
    # Provide a fixable command to run
    print("\nCommand to run for a fresh start (make backup first!):")
    print("rm db.sqlite3")
    print("find . -path '*/migrations/*.py' -not -name '__init__.py' -delete")
    print("find . -path '*/migrations/*.pyc' -delete")
    print("python manage.py makemigrations")
    print("python manage.py migrate")

if __name__ == "__main__":
    main()
