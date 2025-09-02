"""
Test SimpleJWT authentication with the API
"""
import requests
import json

# Base URL for our API
BASE_URL = "http://127.0.0.1:8000/"

def test_auth():
    """Test SimpleJWT authentication endpoints"""
    # Try multiple potential URLs for SimpleJWT
    urls_to_try = [
        f"{BASE_URL}api/auth/login/",    # From accounts/urls.py - This is the correct one based on our URL config
        f"{BASE_URL}api/auth/token/",     # Common SimpleJWT URL
        f"{BASE_URL}api/token/"           # Default SimpleJWT URL
    ]
    
    print("Testing SimpleJWT authentication...")
    
    # First find the correct authentication URL
    login_url = None
    for url in urls_to_try:
        try:
            print(f"Trying endpoint: {url}")
            response = requests.post(url, json={"username": "test", "password": "test"})
            print(f"Status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            # Consider 400 (Bad Request) and 401 (Unauthorized) as valid endpoints
            # as they likely mean the endpoint exists but credentials are wrong
            if response.status_code in [200, 400, 401]:  
                login_url = url
                print(f"Found authentication endpoint: {login_url}")
                break
        except Exception as e:
            print(f"Error trying {url}: {str(e)}")
            continue
    
    if not login_url:
        print("Could not find a valid authentication endpoint.")
        return
    
    # Try teacher login
    print("Testing teacher login...")
    login_data = {
        'username': 'teacher',  # Username
        'password': 'teacherpass'
    }
    
    try:
        # Try JWT authentication with both JSON and form data
        # First try with JSON data
        response = requests.post(login_url, json=login_data)
        print(f"Status code (JSON): {response.status_code}")
        print(f"Response (JSON): {response.text}")
        
        # Then try with form data
        response_form = requests.post(login_url, data=login_data)
        print(f"Status code (form data): {response_form.status_code}")
        print(f"Response (form data): {response_form.text}")
        
        # Check if either request was successful
        if response.status_code == 200:
            token = response.json()
            print(f"Authentication successful with JSON! Access token: {token.get('access')[:20]}...")
            return token
        elif response_form.status_code == 200:
            token = response_form.json()
            print(f"Authentication successful with form data! Access token: {token.get('access')[:20]}...")
            return token
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Try student login
    # Try student login
    print("\nTesting student login...")
    login_data = {
        'username': 'student',  # Username
        'password': 'studentpass'
    }
    
    try:
        # Try both JSON and form data
        response = requests.post(login_url, json=login_data)
        print(f"Status code (JSON): {response.status_code}")
        print(f"Response (JSON): {response.text}")
        
        # Then try with form data
        response_form = requests.post(login_url, data=login_data)
        print(f"Status code (form data): {response_form.status_code}")
        print(f"Response (form data): {response_form.text}")
        
        if response.status_code == 200:
            token = response.json()
            print(f"Authentication successful with JSON! Access token: {token.get('access')[:20]}...")
        elif response_form.status_code == 200:
            token = response_form.json()
            print(f"Authentication successful with form data! Access token: {token.get('access')[:20]}...")
    except Exception as e:
        print(f"Error: {str(e)}")
        
    # Also try with a non-existent user to verify error handling
    print("\nTesting invalid login...")
    invalid_data = {
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }
    
    try:
        # Try both JSON and form data
        response = requests.post(login_url, json=invalid_data)
        print(f"Status code (JSON): {response.status_code}")
        print(f"Response (JSON): {response.text}")
        
        # Then try with form data
        response_form = requests.post(login_url, data=invalid_data)
        print(f"Status code (form data): {response_form.status_code}")
        print(f"Response (form data): {response_form.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_auth()
