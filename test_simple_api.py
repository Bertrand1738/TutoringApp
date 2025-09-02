"""
Simple test to check API access without authentication
"""
import requests

def test_simple_api():
    print("Testing API access without authentication...")
    
    endpoints = [
        "http://127.0.0.1:8000/",
        "http://127.0.0.1:8000/admin/",
        "http://127.0.0.1:8000/api/",
        "http://127.0.0.1:8000/api/courses/"
    ]
    
    for url in endpoints:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            if 'json' in response.headers.get('Content-Type', ''):
                print(f"JSON Response: {response.json()}")
            else:
                print(f"Text Response: {response.text[:100]}...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_api()
