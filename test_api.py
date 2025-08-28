import requests
import json

def test_api():
    # Base URL
    base_url = 'http://127.0.0.1:8000/api'
    
    # First, get a token through login
    print("\nLogging in...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = requests.post(f'{base_url}/auth/login/', json=login_data)
    print(f"Login Status Code: {response.status_code}")
    print(f"Login Response: {response.text}")
    
    if response.status_code != 200:
        print("Login failed!")
        return
        
    token = response.json()['access']
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Test GET /courses/
    print("\nTesting GET /courses/")
    response = requests.get(f'{base_url}/courses/')
    print(f"GET Status Code: {response.status_code}")
    print(f"GET Response: {response.text}")
    
    # Test POST /courses/
    course_data = {
        'title': 'French for Beginners',
        'description': 'Learn basic French conversation skills',
        'price': '49.99',
        'published': True,
        'category': 1  # Make sure this category ID exists
    }
    
    print("\nTesting POST /courses/")
    response = requests.post(
        f'{base_url}/courses/',
        headers=headers,
        json=course_data
    )
    print(f"POST Status Code: {response.status_code}")
    print(f"POST Response: {response.text}")

if __name__ == '__main__':
    test_api()
