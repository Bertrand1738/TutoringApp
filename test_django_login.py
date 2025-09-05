import os
import json
import django
from django.test import Client

# Let's try with the test settings first, then with regular settings if that doesn't work
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_test')

# We need to modify settings to allow 'testserver' before calling django.setup()
from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver']

django.setup()

def test_login():
    client = Client()
    
    print("Testing login with Django test client...")

    # Try with different possible credential field names
    users = [
        # Standard username/password (what we've been using)
        {"username": "admin", "password": "admin123"},
        # Common variations for email-based auth
        {"email": "admin@example.com", "password": "admin123"},
        # SimpleJWT sometimes expects these specific field names
        {"user": "admin", "password": "admin123"},
        # Try exact format from TokenObtainPairSerializer
        {"username": "teacher", "password": "teacherpass"},
    ]
    
    for user in users:
        print(f"\nTrying login for: {user['username']}")
        
        # First attempt: JSON content type with JSON-encoded data
        print("\nAttempt 1: JSON content type with JSON-encoded data")
        response = client.post(
            "/api/auth/login/", 
            data=json.dumps(user),
            content_type="application/json"
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.content[:300]}")
        
        # Second attempt: Form data
        print("\nAttempt 2: Form data")
        response = client.post("/api/auth/login/", user)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.content[:300]}")
        
        # Third attempt: Using URL-encoded content type
        print("\nAttempt 3: URL-encoded content type")
        response = client.post(
            "/api/auth/login/", 
            user,
            content_type="application/x-www-form-urlencoded"
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.content[:300]}")
        
        # If any attempt succeeds, try using the token
        if response.status_code == 200:
            print("SUCCESS! Token received.")
            try:
                data = response.json()
                if 'access' in data:
                    # Test accessing protected endpoint
                    token = data['access']
                    print(f"Access token: {token[:20]}...")
                    
                    # Try the me/ endpoint
                    # In Django test client, HTTP_ is automatically added to header names
                    headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
                    me_response = client.get("/api/auth/me/", **headers)
                    print(f"\nMe endpoint - Status code: {me_response.status_code}")
                    print(f"Me response: {me_response.content[:300]}")
                    
                    # Try alternative header format just in case
                    auth_headers = {"Authorization": f"Bearer {token}"}
                    me_response_alt = client.get("/api/auth/me/", **auth_headers)
                    print(f"\nMe endpoint (alt header) - Status code: {me_response_alt.status_code}")
                    print(f"Me response (alt): {me_response_alt.content[:300]}")
            except Exception as e:
                print(f"Error parsing response: {e}")
        else:
            print("FAILED. Check credentials and endpoint.")

if __name__ == "__main__":
    test_login()
