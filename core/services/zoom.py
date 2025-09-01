"""
Zoom API integration service using Server-to-Server OAuth
"""
import time
import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from .notifications import NotificationService

logger = logging.getLogger(__name__)

class ZoomAuthenticationError(Exception):
    """Raised when authentication with Zoom API fails"""
    pass

class ZoomAPIError(Exception):
    """Raised when Zoom API returns an error"""
    pass

class ZoomMeetingService:
    """Service for interacting with Zoom API using Server-to-Server OAuth"""
    
    def __init__(self):
        """Initialize the service with credentials from settings"""
        self.account_id = settings.ZOOM_ACCOUNT_ID
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.base_url = "https://api.zoom.us/v2"
        
    def get_access_token(self):
        """
        Get OAuth access token, using cache to prevent repeated requests
        Returns cached token if valid, otherwise requests new token
        """
        # Check cache first
        cache_key = 'zoom_access_token'
        token = cache.get(cache_key)
        
        if token:
            return token
            
        try:
            # Request new token
            auth_url = "https://zoom.us/oauth/token"
            response = requests.post(
                auth_url,
                auth=(self.client_id, self.client_secret),
                data={
                    'grant_type': 'account_credentials',
                    'account_id': self.account_id
                }
            )
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data['access_token']
            expires_in = token_data['expires_in']
            
            # Cache token for slightly less than its expiry time
            cache.set(
                cache_key,
                access_token,
                timeout=expires_in - 300  # 5 minutes less than expiry
            )
            
            return access_token
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get Zoom access token: {str(e)}"
            logger.error(error_msg)
            
            # Send error notification
            NotificationService.send_system_error_notification(
                'zoom_authentication_failed',
                error_msg,
                context={
                    'request_url': auth_url,
                    'status_code': getattr(e.response, 'status_code', None),
                    'response_text': getattr(e.response, 'text', None)
                }
            )
            
            raise ZoomAuthenticationError("Failed to authenticate with Zoom API") from e

    def _make_request(self, method, endpoint, data=None, params=None, retries=3):
        """
        Make an authenticated request to Zoom API with retries
        
        Args:
            method (str): HTTP method (GET, POST, PATCH, DELETE)
            endpoint (str): API endpoint (e.g., /users/{userId}/meetings)
            data (dict): Request body for POST/PATCH requests
            params (dict): Query parameters for GET requests
            retries (int): Number of retry attempts for failed requests
            
        Returns:
            dict: Response data from Zoom API
        """
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(retries):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    json=data,
                    params=params
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited by Zoom API, waiting {retry_after} seconds")
                    time.sleep(retry_after)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:  # Last attempt
                    error_msg = f"Failed to {method} {endpoint}: {str(e)}"
                    logger.error(error_msg)
                    
                    # Send error notification
                    NotificationService.send_system_error_notification(
                        'zoom_api_request_failed',
                        error_msg,
                        context={
                            'method': method,
                            'endpoint': endpoint,
                            'url': url,
                            'status_code': getattr(e.response, 'status_code', None),
                            'response_text': getattr(e.response, 'text', None)
                        }
                    )
                    
                    raise ZoomAPIError(f"Zoom API request failed: {str(e)}") from e
                time.sleep(2 ** attempt)  # Exponential backoff
        
    def create_meeting(self, topic, start_time, duration_minutes, teacher_email):
        """
        Create a Zoom meeting
        
        Args:
            topic (str): Meeting topic/title
            start_time (datetime): Meeting start time
            duration_minutes (int): Duration in minutes
            teacher_email (str): Host email address
            
        Returns:
            dict: Meeting details including join URL and password
        """
        try:
            data = {
                'topic': topic,
                'type': 2,  # Scheduled meeting
                'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'duration': duration_minutes,
                'timezone': 'UTC',
                'settings': {
                    'host_video': True,
                    'participant_video': True,
                    'join_before_host': False,
                    'mute_upon_entry': True,
                    'waiting_room': True,
                    'audio': 'both',
                    'auto_recording': 'none',
                    'alternative_hosts': '',  # Can be set if needed
                    'registrants_email_notification': True
                }
            }
            
            meeting_info = self._make_request(
                'POST',
                f'/users/{teacher_email}/meetings',
                data=data
            )
            
            return {
                'id': meeting_info['id'],
                'join_url': meeting_info['join_url'],
                'password': meeting_info.get('password', ''),
                'start_url': meeting_info['start_url']
            }
            
        except Exception as e:
            error_msg = f"Failed to create Zoom meeting: {str(e)}"
            logger.error(error_msg)
            
            # Send error notification
            NotificationService.send_system_error_notification(
                'zoom_meeting_creation_failed',
                error_msg,
                context={
                    'topic': topic,
                    'start_time': start_time.isoformat(),
                    'duration_minutes': duration_minutes,
                    'teacher_email': teacher_email
                }
            )
            
            raise ZoomAPIError("Failed to create Zoom meeting") from e

    def get_meeting(self, meeting_id):
        """
        Get meeting details by ID
        
        Args:
            meeting_id (str): The Zoom meeting ID
            
        Returns:
            dict: Meeting details from Zoom API
        """
        try:
            return self._make_request('GET', f'/meetings/{meeting_id}')
        except Exception as e:
            error_msg = f"Failed to get meeting {meeting_id}: {str(e)}"
            logger.error(error_msg)
            
            # Send error notification
            NotificationService.send_system_error_notification(
                'zoom_meeting_fetch_failed',
                error_msg,
                context={'meeting_id': meeting_id}
            )
            
            raise ZoomAPIError(f"Failed to get meeting details") from e

    def update_meeting(self, meeting_id, **kwargs):
        """
        Update an existing meeting's settings
        
        Args:
            meeting_id (str): The Zoom meeting ID
            **kwargs: Meeting settings to update
                     (topic, start_time, duration, etc.)
        """
        try:
            return self._make_request('PATCH', f'/meetings/{meeting_id}', data=kwargs)
        except Exception as e:
            error_msg = f"Failed to update meeting {meeting_id}: {str(e)}"
            logger.error(error_msg)
            
            # Send error notification
            NotificationService.send_system_error_notification(
                'zoom_meeting_update_failed',
                error_msg,
                context={
                    'meeting_id': meeting_id,
                    'update_params': kwargs
                }
            )
            
            raise ZoomAPIError(f"Failed to update meeting") from e

    def delete_meeting(self, meeting_id):
        """
        Delete/cancel a scheduled meeting
        
        Args:
            meeting_id (str): The Zoom meeting ID
            
        Returns:
            bool: True if successful
        """
        try:
            self._make_request('DELETE', f'/meetings/{meeting_id}')
            return True
        except Exception as e:
            error_msg = f"Failed to delete meeting {meeting_id}: {str(e)}"
            logger.error(error_msg)
            
            # Send error notification
            NotificationService.send_system_error_notification(
                'zoom_meeting_deletion_failed',
                error_msg,
                context={'meeting_id': meeting_id}
            )
            
            raise ZoomAPIError(f"Failed to delete meeting") from e
            
    def end_meeting(self, meeting_id):
        """
        End an ongoing meeting
        
        Args:
            meeting_id (str): The Zoom meeting ID
        """
        try:
            self._make_request('PUT', f'/meetings/{meeting_id}/status', data={
                'action': 'end'
            })
            return True
        except Exception as e:
            error_msg = f"Failed to end meeting {meeting_id}: {str(e)}"
            logger.error(error_msg)
            
            # Send error notification
            NotificationService.send_system_error_notification(
                'zoom_meeting_end_failed',
                error_msg,
                context={'meeting_id': meeting_id}
            )
            
            raise ZoomAPIError(f"Failed to end meeting") from e
