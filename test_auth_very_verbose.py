import os
import sys
import json
import requests
from urllib.parse import urljoin

def test_auth_verbose():
    """
    Test authentication with detailed information and proper JSON formatting
    """
    print("Testing authentication with verbose output...")
    
    # Base URL for API
    base_url = "http://127.0.0.1:8000"
    auth_url = urljoin(base_url, "/api/auth/login/")
    
    # Test credentials (username, email)
    credentials = [
        # Test with username field
        {
            "data": {"username": "admin", "password": "admin123"},
            "desc": "Admin with username field"
        },
        {
            "data": {"username": "teacher", "password": "teacherpass"},
            "desc": "Teacher with username field"
        },
        {
            "data": {"username": "student", "password": "studentpass"},
            "desc": "Student with username field"
        },
        
        # Test with email field
        {
            "data": {"email": "admin@example.com", "password": "admin123"},
            "desc": "Admin with email field"
        },
        {
            "data": {"email": "teacher@example.com", "password": "teacherpass"},
            "desc": "Teacher with email field"
        },
        {
            "data": {"email": "student@example.com", "password": "studentpass"},
            "desc": "Student with email field"
        },
        
        # Test with both username and email fields
        {
            "data": {"username": "admin", "email": "admin@example.com", "password": "admin123"},
            "desc": "Admin with both username and email fields"
        }
    ]
    
    # Headers to try
    headers_to_try = [
        {"Content-Type": "application/json"},
        {"Content-Type": "application/x-www-form-urlencoded"},
        {"Accept": "application/json", "Content-Type": "application/json"},
    ]
    
    # Try each credential set
    for cred in credentials:
        print(f"\n{'=' * 80}")
        print(f"TESTING: {cred['desc']}")
        print(f"{'=' * 80}")
        
        # First, try with JSON data
        print("\n[TEST] Sending as JSON data:")
        for headers in headers_to_try:
            try:
                print(f"\nUsing headers: {headers}")
                print(f"Request data: {json.dumps(cred['data'], indent=2)}")
                
                response = requests.post(
                    auth_url,
                    json=cred['data'],  # This will be serialized and sent with proper content-type
                    headers=headers,
                    timeout=5
                )
                
                print(f"Status code: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    print("SUCCESS! Authentication successful.")
                    
                    try:
                        response_data = response.json()
                        print(f"Response data: {json.dumps(response_data, indent=2)}")
                        
                        # If we got access token, try to use it
                        if 'access' in response_data:
                            token = response_data['access']
                            print("\nTesting access with token...")
                            
                            # Try different endpoints with the token
                            auth_endpoints = [
                                "/api/auth/me/",
                                "/api/courses/",
                                "/api/"
                            ]
                            
                            for endpoint in auth_endpoints:
                                try:
                                    auth_headers = {"Authorization": f"Bearer {token}"}
                                    auth_url = urljoin(base_url, endpoint)
                                    
                                    print(f"\nGET {auth_url}")
                                    print(f"Headers: {auth_headers}")
                                    
                                    auth_response = requests.get(
                                        auth_url,
                                        headers=auth_headers,
                                        timeout=5
                                    )
                                    
                                    print(f"Status code: {auth_response.status_code}")
                                    if auth_response.status_code == 200:
                                        try:
                                            auth_data = auth_response.json()
                                            print(f"Response: {json.dumps(auth_data, indent=2)[:200]}...")
                                        except:
                                            print(f"Response: {auth_response.text[:200]}...")
                                    else:
                                        print(f"Response: {auth_response.text[:200]}...")
                                        
                                except Exception as e:
                                    print(f"Error testing endpoint {endpoint}: {str(e)}")
                    except:
                        print(f"Response (non-JSON): {response.text}")
                else:
                    try:
                        error_data = response.json()
                        print(f"Error response: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"Error response (non-JSON): {response.text}")
                        
            except Exception as e:
                print(f"Exception: {str(e)}")
        
        # Then, try with form data
        print("\n[TEST] Sending as form data:")
        try:
            print(f"Request data: {cred['data']}")
            
            response = requests.post(
                auth_url,
                data=cred['data'],  # This will be sent as form data
                timeout=5
            )
            
            print(f"Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("SUCCESS! Authentication successful.")
                
                try:
                    response_data = response.json()
                    print(f"Response data: {json.dumps(response_data, indent=2)}")
                    
                    # If we got access token, try to use it
                    if 'access' in response_data:
                        token = response_data['access']
                        print("\nTesting access with token...")
                        
                        # Try different endpoints with the token
                        auth_endpoints = [
                            "/api/auth/me/",
                            "/api/courses/",
                            "/api/"
                        ]
                        
                        for endpoint in auth_endpoints:
                            try:
                                auth_headers = {"Authorization": f"Bearer {token}"}
                                auth_url = urljoin(base_url, endpoint)
                                
                                print(f"\nGET {auth_url}")
                                print(f"Headers: {auth_headers}")
                                
                                auth_response = requests.get(
                                    auth_url,
                                    headers=auth_headers,
                                    timeout=5
                                )
                                
                                print(f"Status code: {auth_response.status_code}")
                                if auth_response.status_code == 200:
                                    try:
                                        auth_data = auth_response.json()
                                        print(f"Response: {json.dumps(auth_data, indent=2)[:200]}...")
                                    except:
                                        print(f"Response: {auth_response.text[:200]}...")
                                else:
                                    print(f"Response: {auth_response.text[:200]}...")
                                    
                            except Exception as e:
                                print(f"Error testing endpoint {endpoint}: {str(e)}")
                except:
                    print(f"Response (non-JSON): {response.text}")
            else:
                try:
                    error_data = response.json()
                    print(f"Error response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error response (non-JSON): {response.text}")
                    
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test_auth_verbose()
