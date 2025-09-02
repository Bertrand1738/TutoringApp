import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

# Generate tokens for multiple users
users = [
    {'username': 'admin', 'name': 'Admin User'},
    {'username': 'teacher', 'name': 'Teacher User'},
    {'username': 'student', 'name': 'Student User'}
]

for user_info in users:
    try:
        user = User.objects.get(username=user_info['username'])
        refresh = RefreshToken.for_user(user)
        
        print(f"\n======= Tokens for {user_info['name']} ({user.username}) =======")
        print("Access token:")
        print(str(refresh.access_token))
        print("\nRefresh token:")
        print(str(refresh))
        print("\nAuthorization header:")
        print(f"Bearer {str(refresh.access_token)}")
    except User.DoesNotExist:
        print(f"\n{user_info['username']} not found in the database.")
