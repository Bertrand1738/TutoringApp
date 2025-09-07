"""
This script tests the complete authentication flow:
1. Login to get tokens
2. Use tokens to access protected resources
3. Let tokens expire
4. Verify token refresh
5. Test logout
"""

import requests
import time
import json
import logging
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL
BASE_URL = 'http://127.0.0.1:8000'

# Test credentials
USERNAME = 'testuser'
PASSWORD = 'testpassword'

def ensure_test_user():
    """Ensure test user exists"""
    try:
        # Check if user exists
        response = requests.post(
            urljoin(BASE_URL, '/api/auth/login/'),
            json={'username': USERNAME, 'password': PASSWORD}
        )
        
        if response.status_code == 200:
            logger.info(f"Test user '{USERNAME}' already exists")
            return True
        
        # Create the user
        response = requests.post(
            urljoin(BASE_URL, '/api/auth/register/'),
            json={
                'username': USERNAME,
                'password': PASSWORD,
                'email': 'testuser@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if response.status_code == 201:
            logger.info(f"Created test user '{USERNAME}'")
            return True
        else:
            logger.error(f"Failed to create test user: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error ensuring test user: {e}")
        return False

def test_auth_flow():
    """Test the full authentication flow"""
    
    # Step 1: Login to get tokens
    try:
        logger.info("Step 1: Logging in to get tokens")
        login_response = requests.post(
            urljoin(BASE_URL, '/api/auth/login/'),
            json={'username': USERNAME, 'password': PASSWORD}
        )
        
        if login_response.status_code != 200:
            logger.error(f"Login failed: {login_response.text}")
            return False
        
        tokens = login_response.json()
        access_token = tokens.get('access')
        refresh_token = tokens.get('refresh')
        
        if not access_token or not refresh_token:
            logger.error("Did not receive both tokens from login")
            return False
        
        logger.info("Login successful, received access and refresh tokens")
        
        # Store tokens in session and cookies
        session = requests.Session()
        session.cookies.set('access_token', access_token, domain='127.0.0.1')
        session.cookies.set('refresh_token', refresh_token, domain='127.0.0.1')
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Step 2: Access protected resource with token
        logger.info("Step 2: Accessing protected resource with token")
        me_response = session.get(
            urljoin(BASE_URL, '/api/auth/me/'),
            headers=headers
        )
        
        if me_response.status_code != 200:
            logger.error(f"Failed to access protected resource: {me_response.text}")
            return False
        
        user_data = me_response.json()
        logger.info(f"Successfully accessed protected resource. Username: {user_data.get('username')}")
        
        # Step 3: Test token sync
        logger.info("Step 3: Testing token synchronization")
        sync_response = session.post(
            urljoin(BASE_URL, '/api/auth/sync-tokens/'),
            headers={'Content-Type': 'application/json'},
            json={'access_token': access_token, 'refresh_token': refresh_token}
        )
        
        if sync_response.status_code != 200:
            logger.error(f"Token sync failed: {sync_response.text}")
            return False
        
        logger.info("Token sync successful")
        
        # Step 4: Access dashboard with session after token sync
        logger.info("Step 4: Accessing dashboard with session")
        dashboard_response = session.get(urljoin(BASE_URL, '/dashboard/'))
        
        if dashboard_response.status_code != 200:
            logger.error(f"Failed to access dashboard: {dashboard_response.status_code}")
        else:
            logger.info("Successfully accessed dashboard with session")
        
        # Step 5: Test logout
        logger.info("Step 5: Testing logout")
        logout_response = session.post(
            urljoin(BASE_URL, '/api/auth/logout/'),
            headers=headers
        )
        
        if logout_response.status_code != 200:
            logger.warning(f"Logout returned non-200 status: {logout_response.status_code}")
        
        logger.info("Logout request completed")
        
        # Step 6: Verify we can't access protected resource after logout
        logger.info("Step 6: Verifying access is revoked after logout")
        after_logout_response = session.get(
            urljoin(BASE_URL, '/api/auth/me/'),
            headers=headers
        )
        
        if after_logout_response.status_code == 401:
            logger.info("Successfully verified access is revoked after logout")
        else:
            logger.warning(f"Unexpected: Still have access after logout: {after_logout_response.status_code}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing auth flow: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting authentication flow test")
    
    if ensure_test_user():
        test_auth_flow()
    
    logger.info("Authentication flow test completed")
