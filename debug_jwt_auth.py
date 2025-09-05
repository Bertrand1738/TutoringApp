"""
Debug all SimpleJWT authentication components to find why the API endpoint isn't accepting credentials
"""
import os
import sys
import django
import json
from pprint import pprint

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_test')
django.setup()

# Import Django-related modules after setup
from django.contrib.auth import get_user_model, authenticate
from django.test import Client
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from django.urls import resolve, reverse
from django.conf import settings

User = get_user_model()

def debug_jwt_configuration():
    """Debug SimpleJWT configuration"""
    print("\n1. SimpleJWT Configuration:")
    print(f"   TOKEN_USER_CLASS: {api_settings.TOKEN_USER_CLASS}")
    print(f"   AUTH_HEADER_TYPES: {api_settings.AUTH_HEADER_TYPES}")
    print(f"   AUTH_HEADER_NAME: {api_settings.AUTH_HEADER_NAME}")
    print(f"   USER_ID_FIELD: {api_settings.USER_ID_FIELD}")
    print(f"   USER_ID_CLAIM: {api_settings.USER_ID_CLAIM}")

def debug_django_auth():
    """Debug Django authentication"""
    print("\n2. Testing Django Authentication:")
    
    users = [
        {"username": "admin", "password": "admin123"},
        {"username": "teacher", "password": "teacherpass"},
        {"username": "student", "password": "studentpass"},
    ]
    
    for user_data in users:
        print(f"\n   Authenticating {user_data['username']}...")
        user = authenticate(username=user_data['username'], password=user_data['password'])
        
        if user:
            print(f"   ✅ SUCCESS for {user_data['username']}")
            print(f"     - User ID: {user.id}")
            print(f"     - Is active: {user.is_active}")
        else:
            print(f"   ❌ FAILED for {user_data['username']}")
            
            # Check if user exists
            try:
                user = User.objects.get(username=user_data['username'])
                print(f"     - User exists with username '{user_data['username']}'")
                print(f"     - Is active: {user.is_active}")
                print(f"     - Password hash: {user.password[:20]}...")
            except User.DoesNotExist:
                print(f"     - No user with username '{user_data['username']}' found")

def debug_jwt_serializer():
    """Debug SimpleJWT TokenObtainPairSerializer"""
    print("\n3. Testing SimpleJWT TokenObtainPairSerializer:")
    
    users = [
        {"username": "admin", "password": "admin123"},
        {"username": "teacher", "password": "teacherpass"},
        {"username": "student", "password": "studentpass"},
    ]
    
    for user_data in users:
        print(f"\n   Testing with {user_data['username']}...")
        
        # Try serializer
        serializer = TokenObtainPairSerializer(data=user_data)
        if serializer.is_valid():
            print(f"   ✅ VALID for {user_data['username']}")
            print(f"     - Access token: {serializer.validated_data['access'][:20]}...")
            print(f"     - Refresh token: {serializer.validated_data['refresh'][:20]}...")
        else:
            print(f"   ❌ INVALID for {user_data['username']}")
            print(f"     - Errors: {serializer.errors}")

def debug_api_client():
    """Debug API client access to login endpoint"""
    print("\n4. Testing Django Test Client:")
    
    # Add 'testserver' to ALLOWED_HOSTS for Django test client
    settings.ALLOWED_HOSTS.append('testserver')
    
    client = Client()
    
    users = [
        {"username": "admin", "password": "admin123"},
        {"username": "teacher", "password": "teacherpass"},
        {"username": "student", "password": "studentpass"},
    ]
    
    # URL where TokenObtainPairView is registered
    url = "/api/auth/login/"
    
    for user_data in users:
        print(f"\n   Testing {user_data['username']} with JSON:")
        response = client.post(
            url,
            data=json.dumps(user_data),
            content_type="application/json"
        )
        print(f"     - Status code: {response.status_code}")
        print(f"     - Response: {response.content[:150].decode()}")
        
        print(f"\n   Testing {user_data['username']} with form data:")
        response = client.post(url, user_data)
        print(f"     - Status code: {response.status_code}")
        print(f"     - Response: {response.content[:150].decode()}")

def debug_url_resolution():
    """Debug URL resolution"""
    print("\n5. URL Resolution:")
    
    urls_to_check = [
        '/api/auth/login/',
        '/api/auth/token/',
        '/api/token/',
        '/api/auth/token/obtain/',
    ]
    
    for url in urls_to_check:
        print(f"\n   Resolving URL: {url}")
        try:
            resolver_match = resolve(url)
            print(f"     - View function: {resolver_match.func.__name__}")
            print(f"     - View class: {resolver_match.func.view_class.__name__ if hasattr(resolver_match.func, 'view_class') else 'None'}")
            print(f"     - URL name: {resolver_match.url_name}")
            print(f"     - App name: {resolver_match.app_name}")
            print(f"     - Namespace: {resolver_match.namespace}")
        except Exception as e:
            print(f"     - Error: {str(e)}")

def debug_user_model():
    """Debug User model"""
    print("\n6. User Model Configuration:")
    
    print(f"   User model: {User.__name__}")
    print(f"   USERNAME_FIELD: {User.USERNAME_FIELD}")
    print(f"   REQUIRED_FIELDS: {User.REQUIRED_FIELDS}")
    
    # List all users in the database
    print("\n   Users in database:")
    for user in User.objects.all():
        print(f"     - {user.username}: {user.email} (active: {user.is_active})")

def run_diagnostics():
    """Run all diagnostics"""
    print("Running SimpleJWT Authentication Diagnostics:")
    print("============================================")
    
    debug_jwt_configuration()
    debug_django_auth()
    debug_jwt_serializer()
    debug_api_client()
    debug_url_resolution()
    debug_user_model()
    
    print("\nDiagnostics complete.")

if __name__ == "__main__":
    run_diagnostics()
