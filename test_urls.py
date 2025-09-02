"""
Test to show available URLs in the Django application
"""
import requests
import sys

def test_urls():
    base_url = 'http://127.0.0.1:8000'

    # Common API endpoints to test
    endpoints = [
        '',                    # Root
        '/admin/',             # Admin
        '/api/',               # API root
        '/api/auth/',          # Auth root
        '/api/auth/login/',    # Login
        '/api/auth/token/',    # Token
        '/api/auth/me/',       # Me
        '/api/auth/register/', # Register
    ]

    print("Testing common endpoints to verify the server is running and URL configuration:")
    print("=" * 80)

    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"Checking URL: {url}")
            response = requests.get(url)
            print(f"  Status Code: {response.status_code}")
            print(f"  Content Type: {response.headers.get('Content-Type', 'Not specified')}")
            
            # For HTML responses, show only a brief snippet
            if 'text/html' in response.headers.get('Content-Type', ''):
                content_preview = response.text[:100].replace('\n', ' ').strip()
                print(f"  Content Preview: {content_preview}...")
            # For JSON responses, show the structure
            elif 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"  JSON Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"  JSON Array Length: {len(data)}")
                    else:
                        print(f"  JSON Data: {data}")
                except Exception as e:
                    print(f"  Error parsing JSON: {e}")
            else:
                content_preview = response.text[:100].replace('\n', ' ').strip()
                print(f"  Content Preview: {content_preview}...")
                
        except requests.exceptions.RequestException as e:
            print(f"  Error accessing URL: {e}")
        print()

    print("\nChecking for user setup endpoints:")
    print("=" * 80)
    setup_endpoints = [
        '/api/auth/users/',
        '/api/users/',
        '/api/v1/auth/users/',
        '/api/v1/users/',
    ]
    
    for endpoint in setup_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"Checking URL: {url}")
            response = requests.get(url)
            print(f"  Status Code: {response.status_code}")
            print(f"  Content Type: {response.headers.get('Content-Type', 'Not specified')}")
        except requests.exceptions.RequestException as e:
            print(f"  Error accessing URL: {e}")
        print()

    print("\nChecking API version structure:")
    print("=" * 80)
    version_endpoints = [
        '/api/v1/',
        '/api/v1/auth/',
        '/api/v1/auth/login/',
        '/api/v1/auth/token/',
    ]
    
    for endpoint in version_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"Checking URL: {url}")
            response = requests.get(url)
            print(f"  Status Code: {response.status_code}")
            print(f"  Content Type: {response.headers.get('Content-Type', 'Not specified')}")
        except requests.exceptions.RequestException as e:
            print(f"  Error accessing URL: {e}")
        print()

if __name__ == '__main__':
    test_urls()
