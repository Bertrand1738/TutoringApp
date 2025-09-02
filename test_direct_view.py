"""
This script is a direct interface to Django's request processing,
bypassing HTTP entirely to help diagnose issues.
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")
django.setup()

from django.http import HttpRequest
from django.urls import resolve, Resolver404
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory

User = get_user_model()

def test_url_resolution():
    """Test if URLs can be resolved correctly"""
    print("Testing URL resolution...")
    
    # URLs to test
    urls_to_test = [
        '/admin/',
        '/api/',
        '/api/courses/',
        '/api/auth/login/',
        '/api/auth/me/',
    ]
    
    for url in urls_to_test:
        print(f"\nTrying to resolve URL: {url}")
        try:
            match = resolve(url)
            print(f"  Resolved to: {match.func.__name__} in {match.func.__module__}")
            print(f"  View name: {match.view_name}")
            print(f"  URL name: {match.url_name}")
            print(f"  App name: {match.app_name}")
            print(f"  Namespace: {match.namespace}")
        except Resolver404:
            print(f"  ERROR: URL could not be resolved")
        except Exception as e:
            print(f"  ERROR: {str(e)}")

def test_direct_request_processing():
    """Test processing requests directly without HTTP"""
    print("\nTesting direct request processing...")
    
    # Get a user for authentication
    user = User.objects.filter(username='admin').first()
    if not user:
        user = User.objects.first()
        
    if user:
        print(f"Using user: {user.username} (ID: {user.id})")
    else:
        print("Warning: No user found for authentication")
    
    # Create a request factory (bypasses middleware)
    factory = RequestFactory()
    
    # URLs to test
    urls_to_test = [
        '/api/auth/login/',
        '/api/courses/',
    ]
    
    for url in urls_to_test:
        print(f"\nCreating direct request to: {url}")
        try:
            # First try to resolve the URL to get the view function
            match = resolve(url)
            view_func = match.func
            
            # Create a GET request
            get_request = factory.get(url)
            if user:
                get_request.user = user
            
            # Call the view function directly
            print("  Calling view function directly...")
            try:
                get_response = view_func(get_request, *match.args, **match.kwargs)
                print(f"  GET Response status: {get_response.status_code}")
                print(f"  GET Response content: {get_response.content[:100]}")
            except Exception as e:
                print(f"  Error calling view with GET: {str(e)}")
            
            # Create a POST request (for login endpoint)
            if 'login' in url:
                print("\n  Testing POST to login endpoint...")
                post_data = {
                    'username': 'admin',
                    'password': 'admin123'
                }
                post_request = factory.post(url, data=post_data, content_type='application/json')
                if user:
                    post_request.user = user
                
                try:
                    post_response = view_func(post_request, *match.args, **match.kwargs)
                    print(f"  POST Response status: {post_response.status_code}")
                    print(f"  POST Response content: {post_response.content[:100]}")
                except Exception as e:
                    print(f"  Error calling view with POST: {str(e)}")
        except Resolver404:
            print(f"  ERROR: URL could not be resolved")
        except Exception as e:
            print(f"  ERROR: {str(e)}")

if __name__ == "__main__":
    test_url_resolution()
    test_direct_request_processing()
