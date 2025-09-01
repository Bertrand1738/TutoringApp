"""
Tests for Zoom integration service
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, Mock
from core.services.zoom import ZoomMeetingService, ZoomAuthenticationError, ZoomAPIError

class TestZoomMeetingService(TestCase):
    def setUp(self):
        """Set up test environment"""
        self.zoom_service = ZoomMeetingService()
        self.test_email = "teacher@example.com"
        self.test_topic = "Test French Lesson"
        self.test_start_time = timezone.now() + timedelta(hours=1)
        self.test_duration = 60

    @patch('core.services.zoom.requests.post')
    def test_get_access_token(self, mock_post):
        """Test OAuth token acquisition"""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        # Get token
        token = self.zoom_service.get_access_token()

        # Verify token was retrieved
        self.assertEqual(token, 'test_token')
        mock_post.assert_called_once()

    @patch('core.services.zoom.requests.post')
    def test_create_meeting(self, mock_post):
        """Test meeting creation"""
        # Mock successful meeting creation
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': '123456789',
            'join_url': 'https://zoom.us/j/123456789',
            'password': 'password123',
            'start_url': 'https://zoom.us/s/123456789'
        }
        mock_post.return_value = mock_response

        # Create meeting
        meeting = self.zoom_service.create_meeting(
            topic=self.test_topic,
            start_time=self.test_start_time,
            duration_minutes=self.test_duration,
            teacher_email=self.test_email
        )

        # Verify meeting was created
        self.assertEqual(meeting['id'], '123456789')
        self.assertTrue('join_url' in meeting)
        self.assertTrue('password' in meeting)
        self.assertTrue('start_url' in meeting)

    @patch('core.services.zoom.requests.request')
    def test_rate_limiting(self, mock_request):
        """Test rate limiting handling"""
        # Mock rate limit response then success
        mock_rate_limit = Mock()
        mock_rate_limit.status_code = 429
        mock_rate_limit.headers = {'Retry-After': '1'}

        mock_success = Mock()
        mock_success.status_code = 200
        mock_success.json.return_value = {'id': '123456789'}

        mock_request.side_effect = [mock_rate_limit, mock_success]

        # Make request that hits rate limit
        result = self.zoom_service._make_request('GET', '/test')

        # Verify rate limit was handled
        self.assertEqual(result['id'], '123456789')
        self.assertEqual(mock_request.call_count, 2)

    @patch('core.services.zoom.requests.request')
    def test_error_handling(self, mock_request):
        """Test error handling"""
        # Mock error response
        mock_request.side_effect = Exception("API Error")

        # Verify error is raised
        with self.assertRaises(ZoomAPIError):
            self.zoom_service._make_request('GET', '/test')

    def test_invalid_credentials(self):
        """Test handling of invalid credentials"""
        service = ZoomMeetingService()
        
        # Try to create meeting without valid credentials
        with self.assertRaises(ZoomAuthenticationError):
            service.create_meeting(
                topic=self.test_topic,
                start_time=self.test_start_time,
                duration_minutes=self.test_duration,
                teacher_email=self.test_email
            )
