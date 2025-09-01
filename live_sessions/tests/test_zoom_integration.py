"""
Integration tests for live sessions with Zoom and notifications
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from core.services.zoom import ZoomMeetingService
from core.services.notifications import NotificationService
from live_sessions.models import LiveSession, TimeSlot
from courses.models import Course
from accounts.models import TeacherProfile

User = get_user_model()

class LiveSessionZoomIntegrationTests(TestCase):
    def setUp(self):
        # Create teacher user and profile
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='teacher123'
        )
        teacher_group = Group.objects.create(name='teacher')
        self.teacher.groups.add(teacher_group)
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher,
            bio='Test teacher'
        )

        # Create student user
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='student123'
        )

        # Create course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            teacher=self.teacher_profile,
            price=50.00
        )

        # Create time slot
        self.time_slot = TimeSlot.objects.create(
            teacher=self.teacher_profile,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            is_available=True
        )

    @patch('core.services.zoom.ZoomMeetingService.create_meeting')
    def test_zoom_meeting_failure_notification(self, mock_create_meeting):
        """Test that Zoom meeting creation failures trigger notifications"""
        # Setup mock to raise an error
        mock_create_meeting.side_effect = Exception('Failed to create Zoom meeting')

        # Create live session
        live_session = LiveSession.objects.create(
            course=self.course,
            student=self.student,
            time_slot=self.time_slot
        )

        # Attempt to schedule Zoom meeting
        zoom_service = ZoomMeetingService()
        with self.assertRaises(Exception):
            zoom_service.create_meeting(
                topic=f"Test Course - Session with Student",
                start_time=self.time_slot.start_time,
                duration_minutes=60,
                teacher_email=self.teacher.email
            )

        # Check if notification was sent
        self.assertTrue(
            any(
                'zoom_meeting_creation_failed' in email.subject
                for email in self.client.session['_messages']
            )
        )
