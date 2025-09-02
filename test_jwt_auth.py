"""
Test Simple JWT authentication with the API
"""
import requests
import json

# Base URL for our API
BASE_URL = "http://127.0.0.1:8000/"

def test_auth():
    """Test authentication endpoints"""
    # Try multiple potential URLs for SimpleJWT
    urls_to_try = [
        f"{BASE_URL}api/auth/login/",     # From accounts/urls.py
        f"{BASE_URL}api/auth/token/",     # Common SimpleJWT URL
        f"{BASE_URL}api/token/",          # Default SimpleJWT URL
        f"{BASE_URL}api/v1/auth/token/"   # Another common pattern
    ]
    
    # Try all URLs
    for url in urls_to_try:
        print(f"\nTrying URL: {url}")
        
        # Try both JSON and form data formats
        data_formats = [
            {"method": "json", "data": {"username": "teacher", "password": "teacherpass"}},
            {"method": "form", "data": {"username": "teacher", "password": "teacherpass"}},
            # JWT sometimes uses email as the username field
            {"method": "json", "data": {"email": "teacher@example.com", "password": "teacherpass"}}
        ]
        
        for format_data in data_formats:
            method = format_data["method"]
            data = format_data["data"]
            
            print(f"  Testing with {method} format: {data}")
            
            if method == "json":
                response = requests.post(url, json=data)
            else:
                response = requests.post(url, data=data)
                
            print(f"  Status code: {response.status_code}")
            print(f"  Response: {response.text[:200]}")  # Show only the first part if it's long
            
            if response.status_code == 200:
                print("  SUCCESS! Found working authentication endpoint.")
                login_url = url
                login_method = method
                login_data = data
                break
        
        if response.status_code == 200:
            break
    
    # Continue with the successful URL if found, otherwise use the first one
    if response.status_code != 200:
        print("\nNo successful authentication endpoint found. Using the first URL for the rest of the tests.")
        login_url = urls_to_try[0]
        login_method = "json"
        login_data = {"username": "teacher", "password": "teacherpass"}
    
    # Teacher login using the found working method
    print("\nTesting teacher login with discovered method...")
    
    if login_method == "json":
        response = requests.post(login_url, json=login_data)
    else:
        response = requests.post(login_url, data=login_data)
        
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text[:200]}")  # Show only the first part if it's long
    
    if response.status_code == 200:
        token = response.json()
        print(f"Authentication successful!")
        if 'access' in token:
            print(f"Access token: {token['access'][:20]}...")
        if 'refresh' in token:
            print(f"Refresh token: {token['refresh'][:20]}...")
        if 'auth_token' in token:
            print(f"Auth token: {token['auth_token'][:20]}...")
        
        # Test accessing a protected endpoint
        me_url = f"{BASE_URL}api/auth/me/"
        headers = {'Authorization': f"Bearer {token.get('access')}"}
        
        me_response = requests.get(me_url, headers=headers)
        print(f"\nAccessing protected endpoint:")
        print(f"Status code: {me_response.status_code}")
        print(f"Response: {me_response.text[:200]}")
    
    # Student login using the same method that worked for teacher
    print("\nTesting student login...")
    # Create student data based on the successful login format
    student_data = dict(login_data)  # Copy the format
    if 'username' in student_data:
        student_data['username'] = 'student'
    if 'email' in student_data:
        student_data['email'] = 'student@example.com'
    student_data['password'] = 'studentpass'
    
    if login_method == "json":
        response = requests.post(login_url, json=student_data)
    else:
        response = requests.post(login_url, data=student_data)
        
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        token = response.json()
        print(f"Authentication successful!")
        
        # Check for different token formats
        auth_header = None
        if 'access' in token:
            print(f"Access token: {token['access'][:20]}...")
            auth_header = {'Authorization': f"Bearer {token['access']}"}
        if 'refresh' in token:
            print(f"Refresh token: {token['refresh'][:20]}...")
        if 'auth_token' in token:
            print(f"Auth token: {token['auth_token'][:20]}...")
            auth_header = {'Authorization': f"Token {token['auth_token']}"}
        
        # Try both JWT and Token auth formats for the /me/ endpoint
        if auth_header:
            # Test accessing protected endpoints
            me_urls = [
                f"{BASE_URL}api/auth/me/",  # Common pattern
                f"{BASE_URL}api/v1/auth/me/",  # Version pattern
                f"{BASE_URL}api/users/me/",  # Another common pattern
            ]
            
            for me_url in me_urls:
                print(f"\nAccessing protected endpoint: {me_url}")
                me_response = requests.get(me_url, headers=auth_header)
                print(f"Status code: {me_response.status_code}")
                print(f"Response: {me_response.text[:200] if me_response.text else 'Empty response'}")
    
    # Invalid login
    print("\nTesting invalid login...")
    invalid_data = dict(login_data)  # Copy the format
    if 'username' in invalid_data:
        invalid_data['username'] = 'nonexistent'
    if 'email' in invalid_data:
        invalid_data['email'] = 'fake@example.com'
    invalid_data['password'] = 'wrongpassword'
    
    if login_method == "json":
        response = requests.post(login_url, json=invalid_data)
    else:
        response = requests.post(login_url, data=invalid_data)
        
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_auth()
