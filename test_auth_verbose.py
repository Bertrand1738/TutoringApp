"""
Test authentication with verbose error reporting
"""
import requests
import json
import sys

def test_auth_verbose():
    # Base URL
    base_url = 'http://127.0.0.1:8000/api'
    
    # Try with the most likely endpoint and credential format
    auth_url = f'{base_url}/auth/login/'
    
    # Try multiple users with different credential formats
    test_cases = [
        {'username': 'admin', 'password': 'admin123'},
        {'email': 'admin@example.com', 'password': 'admin123'},
        {'username': 'teacher', 'password': 'teacherpass'},
        {'email': 'teacher@example.com', 'password': 'teacherpass'},
    ]
    
    # Add debug headers to get more information
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    for credentials in test_cases:
        print(f"\nTrying credentials: {credentials}")
        
        response = requests.post(auth_url, json=credentials, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        # Try to parse as JSON for better error reporting
        try:
            response_data = response.json()
            print(f"Response JSON: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response text: {response.text}")
        
        # Try with explicit DEBUG parameter to get more info
        params = {'debug': 'true'}
        response = requests.post(auth_url, json=credentials, headers=headers, params=params)
        print(f"\nWith debug parameter - Status code: {response.status_code}")
        try:
            response_data = response.json()
            print(f"Response JSON: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response text: {response.text}")

if __name__ == '__main__':
    test_auth_verbose()
