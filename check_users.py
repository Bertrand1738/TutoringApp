"""
Test to verify test users exist in the database and have the correct credentials
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now we can import Django models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

def test_users():
    """Check if test users exist in the database"""
    print("Checking for test users in the database:")
    print("=" * 80)
    
    # Print all users
    users = User.objects.all()
    print(f"Total users in database: {users.count()}")
    
    # List all users with their details
    for user in users:
        print(f"\nUser: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Is active: {user.is_active}")
        print(f"  Is staff: {user.is_staff}")
        print(f"  Is superuser: {user.is_superuser}")
        print(f"  Date joined: {user.date_joined}")
        print(f"  Groups: {', '.join([g.name for g in user.groups.all()])}")
        
        # Check if we can verify the password
        test_passwords = ['admin123', 'adminpass', 'teacherpass', 'studentpass', 'password123']
        for pwd in test_passwords:
            if user.check_password(pwd):
                print(f"  Password verified: '{pwd}'")
                break
        else:
            print("  No password matched from test list")
    
    # Print all groups
    groups = Group.objects.all()
    print("\nGroups in the database:")
    for group in groups:
        print(f"  {group.name} - Users: {group.user_set.count()}")

if __name__ == "__main__":
    test_users()
