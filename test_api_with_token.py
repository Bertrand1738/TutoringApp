"""
Test API endpoints with both JWT and Token authentication
"""
import requests
import json

# Tokens for the teacher user from get_token.py
TEACHER_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODAxMzc5LCJpYXQiOjE3NTY3OTc3NzksImp0aSI6ImY2NWFjYjViMzM4NTRhY2JhODM3OWRlODYwZDRmZTM5IiwidXNlcl9pZCI6M30.IQUXttvyTqiuMpLk5flgvcyf1bIadp1atgrQVBmxIhQ"

# Tokens for the student user from get_token.py
STUDENT_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODAxMzc5LCJpYXQiOjE3NTY3OTc3NzksImp0aSI6Ijc4NTk3ZDIxMzQ3NzQ0MDVhZTNmM2ExNDgxMTE2ZGFhIiwidXNlcl9pZCI6NH0.UxNGg3b-XWS8Im2EfI8oOrusRqunwnOhJoivZesQQ48"

# Attempt to create DRF auth tokens for users first
def create_drf_tokens():
    """
    Try to create DRF auth tokens for users
    """
    base_url = "http://127.0.0.1:8000/api/"
    users = [
        {"username": "admin", "password": "admin123"},
        {"username": "teacher", "password": "teacherpass"},
        {"username": "student", "password": "studentpass"}
    ]
    
    tokens = {}
    
    # Try multiple token endpoints
    token_endpoints = [
        "auth/token/login/", 
        "auth/token/", 
        "v1/auth/token/login/", 
        "v1/auth/token/",
        "token/",
        "auth/token/obtain/"
    ]
    
    print("Attempting to obtain DRF tokens...")
    
    for user in users:
        print(f"\nTrying to get token for {user['username']}:")
        
        for endpoint in token_endpoints:
            url = f"{base_url}{endpoint}"
            
            # Try with username
            user_data = {"username": user["username"], "password": user["password"]}
            
            try:
                # Try JSON format
                response = requests.post(url, json=user_data)
                if response.status_code == 200:
                    tokens[user["username"]] = response.json()
                    print(f"Success with JSON at {url}: {json.dumps(tokens[user['username']])[:50]}...")
                    break
                    
                # Try form data
                response = requests.post(url, data=user_data)
                if response.status_code == 200:
                    tokens[user["username"]] = response.json()
                    print(f"Success with form data at {url}: {json.dumps(tokens[user['username']])[:50]}...")
                    break
            
                # Try with email
                user_data = {"email": f"{user['username']}@example.com", "password": user["password"]}
                
                # Try JSON format
                response = requests.post(url, json=user_data)
                if response.status_code == 200:
                    tokens[user["username"]] = response.json()
                    print(f"Success with JSON email at {url}: {json.dumps(tokens[user['username']])[:50]}...")
                    break
                    
                # Try form data
                response = requests.post(url, data=user_data)
                if response.status_code == 200:
                    tokens[user["username"]] = response.json()
                    print(f"Success with form data email at {url}: {json.dumps(tokens[user['username']])[:50]}...")
                    break
                
            except Exception as e:
                print(f"Error with {url}: {str(e)}")
        
        if user["username"] not in tokens:
            print(f"Failed to get token for {user['username']} from any endpoint")
    
    return tokens

# API base URL
BASE_URL = "http://127.0.0.1:8000/api/"

def test_api_with_token():
    """Test API endpoints using different authentication methods"""
    
    # Try to get DRF tokens first
    drf_tokens = create_drf_tokens()
    
    # Authentication header formats to try
    auth_headers = [
        # SimpleJWT format
        {"jwt_teacher": {"Authorization": f"Bearer {TEACHER_JWT_TOKEN}", "Content-Type": "application/json"}},
        {"jwt_student": {"Authorization": f"Bearer {STUDENT_JWT_TOKEN}", "Content-Type": "application/json"}},
        
        # DRF Token format 
        {"token_teacher": {"Authorization": f"Token {TEACHER_JWT_TOKEN}", "Content-Type": "application/json"}},
        {"token_student": {"Authorization": f"Token {STUDENT_JWT_TOKEN}", "Content-Type": "application/json"}},
    ]
    
    # Add any successful DRF tokens
    if "teacher" in drf_tokens and "auth_token" in drf_tokens["teacher"]:
        auth_headers.append({
            "drf_teacher": {"Authorization": f"Token {drf_tokens['teacher']['auth_token']}", "Content-Type": "application/json"}
        })
    
    if "student" in drf_tokens and "auth_token" in drf_tokens["student"]:
        auth_headers.append({
            "drf_student": {"Authorization": f"Token {drf_tokens['student']['auth_token']}", "Content-Type": "application/json"}
        })
    
    # List of endpoints to test
    endpoints = [
        # Basic endpoints
        "",
        "auth/me/",
        
        # Courses endpoints
        "courses/",
        "courses/1/",
        
        # Assignments endpoints (nested under courses)
        "courses/1/assignments/",
        "courses/1/assignments/1/",
        
        # Submissions endpoints (nested under assignments)
        "courses/1/assignments/1/submissions/",
        "courses/1/assignments/1/submissions/1/",
        
        # Feedback endpoints (nested under submissions)
        "courses/1/assignments/1/submissions/1/feedback/",
    ]
    
    # Test each authentication header format
    for header_dict in auth_headers:
        for auth_name, headers in header_dict.items():
            print(f"\n===== Testing API with {auth_name} authentication =====\n")
            
            for endpoint in endpoints:
                url = f"{BASE_URL}{endpoint}"
                print(f"Testing GET {url}")
                try:
                    response = requests.get(url, headers=headers)
                    print(f"Status Code: {response.status_code}")
                    
                    if response.status_code < 300:  # Success
                        try:
                            data = response.json()
                            if isinstance(data, list):
                                print(f"Response: List with {len(data)} items")
                                if len(data) > 0:
                                    print(f"First item: {json.dumps(data[0])[:100]}...")
                            elif isinstance(data, dict):
                                print(f"Response: Object with keys {list(data.keys())}")
                                print(f"Content: {json.dumps(data)[:100]}...")
                            else:
                                print(f"Response: {data}")
                        except Exception as e:
                            print(f"Response (non-JSON): {response.text[:100]}...")
                    else:
                        print(f"Response: {response.text[:100]}...")
                except requests.exceptions.RequestException as e:
                    print(f"Error: {e}")
                print()  # Line break after each endpoint test

if __name__ == "__main__":
    test_api_with_token()

if __name__ == "__main__":
    test_api_with_token()
