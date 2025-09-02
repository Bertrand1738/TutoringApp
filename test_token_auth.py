"""
Test API authentication using Token authentication rather than SimpleJWT
"""
import requests
import json

def test_token_auth():
    # Base URL
    base_url = 'http://127.0.0.1:8000/api'
    
    # Try multiple users
    users = [
        {'email': 'admin@example.com', 'password': 'admin123'},  # Admin user
        {'email': 'teacher@example.com', 'password': 'teacherpass'},  # Teacher user
        {'email': 'student@example.com', 'password': 'studentpass'}  # Student user
    ]
    
    # Try different token endpoints
    token_endpoints = [
        f'{base_url}/auth/token/login/',
        f'{base_url}/auth/token/',
        f'{base_url}/v1/auth/token/login/',
        f'{base_url}/v1/auth/token/',
    ]
    
    for user in users:
        print(f"\nTrying to log in with user: {user['email']}")
        
        for endpoint in token_endpoints:
            print(f"\nTesting endpoint: {endpoint}")
            
            # Try with form data
            response = requests.post(endpoint, data=user)
            print(f"Form data - Status Code: {response.status_code}")
            if response.status_code == 200:
                token_data = response.json()
                print(f"SUCCESS! Authentication succeeded.")
                print(f"Token data: {token_data}")
                
                # Try making a request to courses endpoint using the token
                if 'auth_token' in token_data:
                    token = token_data['auth_token']
                    headers = {'Authorization': f'Token {token}'}
                    courses_url = f"{base_url}/courses/"
                    
                    print("\nTesting access to courses endpoint with token...")
                    courses_response = requests.get(courses_url, headers=headers)
                    print(f"Status Code: {courses_response.status_code}")
                    if courses_response.status_code == 200:
                        print("Successfully accessed courses endpoint!")
                        courses = courses_response.json()
                        print(f"Found {len(courses)} courses")
                    else:
                        print(f"Failed to access courses: {courses_response.text}")
            else:
                print(f"Response: {response.text}")
            
            # Try with JSON
            response = requests.post(endpoint, json=user)
            print(f"JSON - Status Code: {response.status_code}")
            if response.status_code == 200:
                token_data = response.json()
                print(f"SUCCESS! Authentication succeeded.")
                print(f"Token data: {token_data}")
                
                # Try making a request to courses endpoint using the token
                if 'auth_token' in token_data:
                    token = token_data['auth_token']
                    headers = {'Authorization': f'Token {token}'}
                    courses_url = f"{base_url}/courses/"
                    
                    print("\nTesting access to courses endpoint with token...")
                    courses_response = requests.get(courses_url, headers=headers)
                    print(f"Status Code: {courses_response.status_code}")
                    if courses_response.status_code == 200:
                        print("Successfully accessed courses endpoint!")
                        courses = courses_response.json()
                        print(f"Found {len(courses)} courses")
                    else:
                        print(f"Failed to access courses: {courses_response.text}")
            else:
                print(f"Response: {response.text}")

if __name__ == '__main__':
    test_token_auth()
