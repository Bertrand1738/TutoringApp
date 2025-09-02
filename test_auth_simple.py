"""
Test API authentication using the same approach as test_api.py
"""
import requests
import json

def test_auth_simple():
    # Base URL
    base_url = 'http://127.0.0.1:8000/api'
    
    # Try multiple users
    users = [
        {'username': 'admin', 'password': 'admin123'},  # From original test_api.py
        {'username': 'teacher', 'password': 'teacherpass'},  # Our test teacher
        {'username': 'student', 'password': 'studentpass'}  # Our test student
    ]
    
    for user in users:
        print(f"\nTrying to log in with user: {user['username']}")
        login_data = user
        
        # Try all possible endpoints with JSON (SimpleJWT typically expects JSON)
        endpoints = [
            f'{base_url}/auth/login/',     # From accounts/urls.py
            f'{base_url}/token/',          # Alternative common pattern
            f'{base_url}/auth/token/',     # Another alternative
            f'{base_url}/auth/token/obtain/',  # Yet another common pattern
            f'{base_url}/v1/auth/token/',  # Version prefix pattern
        ]
        
        for endpoint in endpoints:
            print(f"\nTrying endpoint: {endpoint}")
            
            # Try with JSON data
            response = requests.post(endpoint, json=login_data)
            print(f"JSON - Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("SUCCESS with JSON! Authentication succeeded.")
                token_data = response.json()
                if 'access' in token_data:
                    print(f"Access token: {token_data['access'][:20]}...")
                    
                    # Try making a request to the protected endpoint
                    headers = {"Authorization": f"Bearer {token_data['access']}"}
                    me_response = requests.get(f"{base_url}/auth/me/", headers=headers)
                    print(f"Me endpoint - Status Code: {me_response.status_code}")
                    if me_response.status_code == 200:
                        print(f"Me endpoint - Data: {me_response.json()}")
                    else:
                        print(f"Me endpoint - Response: {me_response.text}")
                else:
                    print(f"Token response: {token_data}")
            else:
                print(f"JSON Response: {response.text[:200]}")
                
            # Try with form data
            response_form = requests.post(endpoint, data=login_data)
            print(f"Form data - Status Code: {response_form.status_code}")
            
            # Try with explicit content-type for application/x-www-form-urlencoded
            headers_form = {"Content-Type": "application/x-www-form-urlencoded"}
            response_form_explicit = requests.post(endpoint, data=login_data, headers=headers_form)
            print(f"Form data (explicit content-type) - Status Code: {response_form_explicit.status_code}")
            
            if response_form.status_code == 200 or response_form_explicit.status_code == 200:
                success_response = response_form if response_form.status_code == 200 else response_form_explicit
                print("SUCCESS with form data! Authentication succeeded.")
                token_data = success_response.json()
                if 'access' in token_data:
                    print(f"Access token: {token_data['access'][:20]}...")
                    
                    # Try making a request to the protected endpoint
                    headers = {"Authorization": f"Bearer {token_data['access']}"}
                    me_response = requests.get(f"{base_url}/auth/me/", headers=headers)
                    print(f"Me endpoint - Status Code: {me_response.status_code}")
                    if me_response.status_code == 200:
                        print(f"Me endpoint - Data: {me_response.json()}")
                    else:
                        print(f"Me endpoint - Response: {me_response.text}")
                else:
                    print(f"Token response: {token_data}")
            else:
                print(f"Form data Response: {response_form.text[:200]}")
                print(f"Form data (explicit) Response: {response_form_explicit.text[:200]}")

if __name__ == '__main__':
    test_auth_simple()
