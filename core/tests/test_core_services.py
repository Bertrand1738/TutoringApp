"""
Tests for core services including notifications and rate limiting
"""
import unittest
from unittest.mock import patch, Mock, call
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime

from core.services.notifications import NotificationService
from core.services.zoom import ZoomMeetingService, ZoomAPIError, ZoomAuthenticationError
from core.throttling import UserBasedThrottle, LiveSessionThrottle
from live_sessions.models import LiveSession, TimeSlot

User = get_user_model()

class NotificationServiceTests(TestCase):
    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        settings.ADMINS = [('Admin', 'admin@example.com')]

    def test_system_error_notification(self):
        """Test system error notifications are sent correctly"""
        error_type = "test_error"
        details = "Test error details"
        context = {"key": "value"}

        # Send notification
        NotificationService.send_system_error_notification(error_type, details, context)

        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        # Verify email content
        self.assertEqual(email.subject, f"System Error Alert: {error_type}")
        self.assertIn(details, email.body)
        self.assertIn("key: value", email.body)
        self.assertEqual(email.to, ['admin@example.com'])

    @patch('core.services.notifications.logger')
    def test_notification_failure_logging(self, mock_logger):
        """Test that notification failures are logged"""
        with patch('django.core.mail.send_mail', side_effect=Exception('Test error')):
            NotificationService.send_system_error_notification('test', 'details')
            
        mock_logger.error.assert_called_with('Failed to send system error notification: Test error')

class ZoomServiceNotificationTests(TestCase):
    def setUp(self):
        self.zoom_service = ZoomMeetingService()
        settings.ADMINS = [('Admin', 'admin@example.com')]

    @patch('core.services.zoom.requests.post')
    def test_authentication_error_notification(self, mock_post):
        """Test that Zoom authentication errors trigger notifications"""
        # Setup mock to raise an error
        mock_post.side_effect = Exception('Auth failed')

        # Attempt to get access token
        with self.assertRaises(ZoomAuthenticationError):
            self.zoom_service.get_access_token()

        # Verify notification was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'System Error Alert: zoom_authentication_failed')
        self.assertIn('Auth failed', email.body)

    @patch('core.services.zoom.ZoomMeetingService.get_access_token')
    @patch('core.services.zoom.requests.request')
    def test_meeting_creation_error_notification(self, mock_request, mock_get_token):
        """Test that meeting creation errors trigger notifications"""
        # Setup mocks
        mock_get_token.return_value = 'fake-token'
        mock_request.side_effect = Exception('API error')

        # Attempt to create meeting
        with self.assertRaises(ZoomAPIError):
            self.zoom_service.create_meeting(
                'Test Meeting',
                datetime.now(),
                30,
                'teacher@example.com'
            )

        # Verify notification was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'System Error Alert: zoom_meeting_creation_failed')
        self.assertIn('API error', email.body)

class RateLimitingTests(APITestCase):
    def setUp(self):
        # Create test users
        self.student = User.objects.create_user(
            username='student',
            password='student123'
        )
        self.teacher = User.objects.create_user(
            username='teacher',
            password='teacher123'
        )
        
        # Create and assign groups
        student_group = Group.objects.create(name='student')
        teacher_group = Group.objects.create(name='teacher')
        self.student.groups.add(student_group)
        self.teacher.groups.add(teacher_group)

        # Setup request factory
        self.factory = RequestFactory()

    def test_user_based_throttle_rates(self):
        """Test that different user types get different rate limits"""
        throttle = UserBasedThrottle()
        
        # Test unauthenticated
        request = self.factory.get('/')
        request.user = Mock(is_authenticated=False)
        throttle.request = request
        self.assertEqual(throttle.get_rate(), '20/hour')
        
        # Test student
        request.user = self.student
        throttle.request = request
        self.assertEqual(throttle.get_rate(), '100/hour')
        
        # Test teacher
        request.user = self.teacher
        throttle.request = request
        self.assertEqual(throttle.get_rate(), '1000/hour')

    def test_live_session_throttle_rates(self):
        """Test that live session endpoints have more restrictive limits"""
        throttle = LiveSessionThrottle()
        
        # Test unauthenticated
        request = self.factory.get('/')
        request.user = Mock(is_authenticated=False)
        throttle.request = request
        self.assertEqual(throttle.get_rate(), '5/hour')
        
        # Test student
        request.user = self.student
        throttle.request = request
        self.assertEqual(throttle.get_rate(), '20/hour')
        
        # Test teacher
        request.user = self.teacher
        throttle.request = request
        self.assertEqual(throttle.get_rate(), '50/hour')

    def test_rate_limit_enforcement(self):
        """Test that rate limits are actually enforced"""
        from live_sessions.views import LiveSessionViewSet
        from rest_framework.test import APIRequestFactory
        from rest_framework.viewsets import ModelViewSet
        
        factory = APIRequestFactory()
        
        class TestView(ModelViewSet):
            throttle_classes = [LiveSessionThrottle]
            
            def list(self, request):
                return Response({'status': 'ok'})
        
        view = TestView.as_view({'get': 'list'})
        
        # Test rate limiting for unauthenticated user
        for _ in range(6):  # Limit is 5/hour
            request = factory.get('/api/test/')
            request.user = Mock(is_authenticated=False)
            response = view(request)
            
            if _ < 5:
                self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
