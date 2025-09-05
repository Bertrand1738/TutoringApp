"""
Direct password checking script to diagnose authentication issues
"""
import os
import django
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_test')
django.setup()

User = get_user_model()

def check_passwords():
    """Check passwords directly using Django's check_password function"""
    print("Direct Password Check:")
    print("=====================\n")
    
    # Define users to check
    users_to_check = [
        {"username": "admin", "password": "admin123"},
        {"username": "teacher", "password": "teacherpass"},
        {"username": "student", "password": "studentpass"},
    ]
    
    # First, try Django's authenticate method
    print("1. Django authenticate() method:")
    for user_data in users_to_check:
        user = authenticate(username=user_data['username'], password=user_data['password'])
        if user:
            print(f"✅ Authentication SUCCESS for {user_data['username']}")
        else:
            print(f"❌ Authentication FAILED for {user_data['username']}")
    
    # Now, check passwords directly
    print("\n2. Direct password check with check_password():")
    for user_data in users_to_check:
        try:
            user = User.objects.get(username=user_data['username'])
            password_valid = check_password(user_data['password'], user.password)
            
            print(f"User: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Is active: {user.is_active}")
            print(f"  Password hash: {user.password[:20]}...")
            print(f"  Password valid: {'✅ YES' if password_valid else '❌ NO'}")
            print(f"  Auth backends: {django.conf.settings.AUTHENTICATION_BACKENDS}")
            print()
        except User.DoesNotExist:
            print(f"User {user_data['username']} not found in database")
    
    # Test with email auth
    print("\n3. Testing with email authentication:")
    for user_data in users_to_check:
        try:
            user = User.objects.get(username=user_data['username'])
            auth_user = authenticate(username=user.email, password=user_data['password'])
            
            if auth_user:
                print(f"✅ Email authentication SUCCESS for {user.email}")
            else:
                print(f"❌ Email authentication FAILED for {user.email}")
                
            # Also test direct password check against email
            password_valid = check_password(user_data['password'], user.password)
            print(f"  Direct password check: {'✅ Valid' if password_valid else '❌ Invalid'}")
        except User.DoesNotExist:
            print(f"User {user_data['username']} not found")
    
    # Check authentication backends
    print("\n4. Authentication Backends:")
    for backend in django.conf.settings.AUTHENTICATION_BACKENDS:
        print(f"  - {backend}")

if __name__ == "__main__":
    check_passwords()
