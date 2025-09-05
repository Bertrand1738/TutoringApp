"""
Fix user passwords to match what we've been using in our tests
"""
import os
import django
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

User = get_user_model()

def set_passwords():
    """Set passwords for all users"""
    print("Setting passwords for all users...")
    
    # Define default passwords for different user types
    default_passwords = {
        'admin': 'admin123',
        'teacher': 'teacherpass',
        'student': 'studentpass',
        'teacher2': 'teacherpass',
        'student1': 'studentpass',
        'Salah': 'admin123',
        'Bertrand': 'admin123',
        'john': 'studentpass'
    }
    
    # Get all users
    all_users = User.objects.all()
    print(f"Found {all_users.count()} users")
    
    # Reset each user's password
    for user in all_users:
        # Get the default password or use username as password if not in defaults
        password = default_passwords.get(user.username, user.username)
        user.set_password(password)
        user.save()
        print(f"✅ Reset password for {user.username}")
    
    print("\nAll passwords have been reset!")
    
    print("\nVerifying passwords...")
    
    # Verify passwords
    from django.contrib.auth import authenticate
    
    users = [
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'teacher', 'password': 'teacherpass'},
        {'username': 'student', 'password': 'studentpass'},
    ]
    
    for user_data in users:
        user = authenticate(username=user_data['username'], password=user_data['password'])
        if user:
            print(f"✅ Authentication SUCCESS for {user_data['username']}")
        else:
            print(f"❌ Authentication FAILED for {user_data['username']}")

if __name__ == "__main__":
    set_passwords()
