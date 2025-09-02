"""
Test all possible authentication methods to identify the correct one
"""
import requests
import json

def test_auth_all_methods():
    # Base URL
    base_url = 'http://127.0.0.1:8000/api'
    
    # Try multiple users with both username and email
    users_to_try = [
        # Admin user
        {'username': 'admin', 'password': 'admin123'},
        {'email': 'admin@example.com', 'password': 'admin123'},
        # Teacher user
        {'username': 'teacher', 'password': 'teacherpass'},
        {'email': 'teacher@example.com', 'password': 'teacherpass'},
        # Student user
        {'username': 'student', 'password': 'studentpass'},
        {'email': 'student@example.com', 'password': 'studentpass'},
    ]
    
    # Try all possible endpoints
    endpoints = [
        f'{base_url}/auth/login/',
        f'{base_url}/auth/token/',
        f'{base_url}/auth/token/login/',
        f'{base_url}/token/',
        f'{base_url}/v1/auth/token/',
        f'{base_url}/auth/token/obtain/',
    ]
    
    # Try all methods (JSON and form data)
    for endpoint in endpoints:
        print(f"\n\n========== Testing endpoint: {endpoint} ==========")
        for user in users_to_try:
            print(f"\nTrying user: {user}")
            
            # Try with JSON
            try:
                response = requests.post(endpoint, json=user, timeout=5)
                print(f"JSON - Status Code: {response.status_code}")
                print(f"JSON - Response: {response.text[:200]}")
                
                if response.status_code == 200:
                    print("SUCCESS! Authentication worked with JSON.")
                    token_data = response.json()
                    print(f"Token data keys: {list(token_data.keys())}")
                    
                    # If we have a token, try to use it
                    if 'access' in token_data:
                        headers = {"Authorization": f"Bearer {token_data['access']}"}
                        me_endpoint = f"{base_url}/auth/me/"
                        try:
                            me_response = requests.get(me_endpoint, headers=headers, timeout=5)
                            print(f"Me endpoint ({me_endpoint}) - Status: {me_response.status_code}")
                            if me_response.status_code == 200:
                                print(f"Me endpoint - Data: {me_response.json()}")
                            else:
                                print(f"Me endpoint - Response: {me_response.text[:200]}")
                        except Exception as e:
                            print(f"Error with me endpoint: {e}")
                    
                    if 'auth_token' in token_data:
                        headers = {"Authorization": f"Token {token_data['auth_token']}"}
                        me_endpoint = f"{base_url}/auth/me/"
                        try:
                            me_response = requests.get(me_endpoint, headers=headers, timeout=5)
                            print(f"Me endpoint ({me_endpoint}) - Status: {me_response.status_code}")
                            if me_response.status_code == 200:
                                print(f"Me endpoint - Data: {me_response.json()}")
                            else:
                                print(f"Me endpoint - Response: {me_response.text[:200]}")
                        except Exception as e:
                            print(f"Error with me endpoint: {e}")
            except Exception as e:
                print(f"Error with JSON request: {e}")
            
            # Try with form data
            try:
                response = requests.post(endpoint, data=user, timeout=5)
                print(f"Form data - Status Code: {response.status_code}")
                print(f"Form data - Response: {response.text[:200]}")
                
                if response.status_code == 200:
                    print("SUCCESS! Authentication worked with form data.")
                    token_data = response.json()
                    print(f"Token data keys: {list(token_data.keys())}")
                    
                    # If we have a token, try to use it
                    if 'access' in token_data:
                        headers = {"Authorization": f"Bearer {token_data['access']}"}
                        me_endpoint = f"{base_url}/auth/me/"
                        try:
                            me_response = requests.get(me_endpoint, headers=headers, timeout=5)
                            print(f"Me endpoint ({me_endpoint}) - Status: {me_response.status_code}")
                            if me_response.status_code == 200:
                                print(f"Me endpoint - Data: {me_response.json()}")
                            else:
                                print(f"Me endpoint - Response: {me_response.text[:200]}")
                        except Exception as e:
                            print(f"Error with me endpoint: {e}")
                    
                    if 'auth_token' in token_data:
                        headers = {"Authorization": f"Token {token_data['auth_token']}"}
                        me_endpoint = f"{base_url}/auth/me/"
                        try:
                            me_response = requests.get(me_endpoint, headers=headers, timeout=5)
                            print(f"Me endpoint ({me_endpoint}) - Status: {me_response.status_code}")
                            if me_response.status_code == 200:
                                print(f"Me endpoint - Data: {me_response.json()}")
                            else:
                                print(f"Me endpoint - Response: {me_response.text[:200]}")
                        except Exception as e:
                            print(f"Error with me endpoint: {e}")
            except Exception as e:
                print(f"Error with form data request: {e}")

if __name__ == '__main__':
    test_auth_all_methods()
