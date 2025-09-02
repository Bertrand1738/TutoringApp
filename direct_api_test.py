"""
Direct API testing without HTTP
"""
import os
import sys
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now import Django modules
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

def test_direct_api_access():
    """Test API access directly using APIClient without HTTP"""
    User = get_user_model()
    
    # Get a user
    user = User.objects.filter(username='admin').first()
    if not user:
        user = User.objects.first()
    
    if not user:
        print("No users found in the database!")
        return
    
    print(f"Testing API with user: {user.username} (ID: {user.id})")
    
    # Create API client
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Test various endpoints
    endpoints = [
        '/',
        '/admin/',
        '/api/',
        '/api/courses/',
        '/api/auth/me/',
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        try:
            response = client.get(endpoint)
            print(f"Status code: {response.status_code}")
            
            if response.status_code < 300:
                if hasattr(response, 'data'):
                    print(f"Data: {response.data}")
                else:
                    print(f"Content: {response.content[:100]}...")
            else:
                print(f"Error: {response.content[:100]}...")
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test_direct_api_access()
