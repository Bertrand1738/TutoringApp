from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
from core.throttling import LiveSessionThrottle
from .models import TimeSlot, LiveSession
from .serializers import TimeSlotSerializer, LiveSessionSerializer
import requests
from datetime import timedelta
import json

class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to create/edit time slots
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(request.user, 'teacher_profile')

class TimeSlotViewSet(viewsets.ModelViewSet):
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    def get_queryset(self):
        queryset = TimeSlot.objects.all()
        
        if hasattr(self.request.user, 'teacher_profile'):
            # Teachers see their own slots
            return queryset.filter(teacher=self.request.user.teacher_profile)
        
        # Students see only available future slots
        now = timezone.now()
        return queryset.filter(
            is_available=True,
            start_time__gt=now
        )

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.teacher_profile)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get available time slots for a specific teacher
        """
        teacher_id = request.query_params.get('teacher', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        queryset = self.get_queryset()

        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_time__lte=end_date)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LiveSessionViewSet(viewsets.ModelViewSet):
    serializer_class = LiveSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [LiveSessionThrottle]

    def get_queryset(self):
        queryset = LiveSession.objects.select_related(
            'course', 'time_slot', 'student'
        )
        
        if hasattr(self.request.user, 'teacher_profile'):
            # Teachers see sessions where they teach
            return queryset.filter(
                course__teacher=self.request.user.teacher_profile
            )
        
        # Students see their booked sessions
        return queryset.filter(student=self.request.user)

    def perform_create(self, serializer):
        # Get the course and time slot from the request
        from courses.models import Course
        from .models import TimeSlot
        
        course_id = self.request.data.get('course_id')
        time_slot_id = self.request.data.get('time_slot_id')
        
        if not course_id or not time_slot_id:
            raise serializers.ValidationError({
                'detail': 'Course ID and Time Slot ID are required'
            })
            
        try:
            course = Course.objects.get(pk=course_id)
            time_slot = TimeSlot.objects.get(pk=time_slot_id)
        except (Course.DoesNotExist, TimeSlot.DoesNotExist):
            raise serializers.ValidationError({
                'detail': 'Invalid Course or Time Slot'
            })
            
        # Create Zoom/Meet meeting
        meeting_platform = self.request.data.get('meeting_platform', 'zoom')
        meeting_info = self.create_meeting({
            'course': course,
            'time_slot': time_slot,
            'meeting_platform': meeting_platform
        })
        
        # Save session with meeting details
        serializer.save(
            student=self.request.user,
            course=course,
            time_slot=time_slot,
            meeting_platform=meeting_platform,
            meeting_url=meeting_info.get('join_url', ''),
            meeting_id=meeting_info.get('id', ''),
            meeting_password=meeting_info.get('password', ''),
            student_notes=self.request.data.get('student_notes', '')
        )

    def create_meeting(self, data):
        """
        Create a Zoom/Meet meeting for the session
        """
        if data.get('meeting_platform') == 'zoom':
            return self.create_zoom_meeting(data)
        return self.create_meet_meeting(data)

    def create_zoom_meeting(self, data):
        """
        Create a Zoom meeting using our ZoomMeetingService
        """
        from core.services.zoom import ZoomMeetingService
        
        time_slot = data['time_slot']
        course = data['course']
        duration = int((time_slot.end_time - time_slot.start_time).total_seconds() / 60)
        
        zoom = ZoomMeetingService()
        return zoom.create_meeting(
            topic=f"{course.title} - Session with {self.request.user.get_full_name()}",
            start_time=time_slot.start_time,
            duration_minutes=duration,
            teacher_email=course.teacher.user.email
        )

    def create_meet_meeting(self, data):
        """
        Create a Google Meet meeting using Google Calendar API
        """
        # TODO: Implement actual Google Meet API integration
        # This is a placeholder implementation
        return {
            'id': 'abc-defg-hij',
            'join_url': f'https://meet.google.com/abc-defg-hij',
            'password': ''
        }

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a scheduled session and end associated Zoom meeting if it exists
        """
        session = self.get_object()
        
        if session.status not in ['scheduled', 'confirmed', 'ongoing']:
            return Response(
                {"detail": "Cannot cancel completed or already cancelled sessions"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # End Zoom meeting if it's ongoing
            if session.status == 'ongoing' and session.meeting_platform == 'zoom' and session.meeting_id:
                from core.services.zoom import ZoomMeetingService
                zoom = ZoomMeetingService()
                zoom.end_meeting(session.meeting_id)

            # Make the time slot available again
            session.time_slot.is_available = True
            session.time_slot.save()

            # Update session status
            session.status = 'cancelled'
            session.save()

            return Response({"status": "Session cancelled successfully"})
            
        except Exception as e:
            return Response(
                {"detail": f"Error cancelling session: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark a session as completed and end the Zoom meeting
        """
        session = self.get_object()
        
        if session.status != 'ongoing':
            return Response(
                {"detail": "Only ongoing sessions can be marked as completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # End Zoom meeting
            if session.meeting_platform == 'zoom' and session.meeting_id:
                from core.services.zoom import ZoomMeetingService
                zoom = ZoomMeetingService()
                zoom.end_meeting(session.meeting_id)

            # Update session status
            session.status = 'completed'
            session.save()

            return Response({"status": "Session marked as completed"})
            
        except Exception as e:
            return Response(
                {"detail": f"Error completing session: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
