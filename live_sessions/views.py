from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
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
        # Create Zoom/Meet meeting
        meeting_info = self.create_meeting(serializer.validated_data)
        
        # Save session with meeting details
        serializer.save(
            student=self.request.user,
            meeting_url=meeting_info.get('join_url', ''),
            meeting_id=meeting_info.get('id', ''),
            meeting_password=meeting_info.get('password', '')
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
        Create a Zoom meeting using Zoom API
        """
        # TODO: Implement actual Zoom API integration
        # This is a placeholder implementation
        return {
            'id': '123456789',
            'join_url': f'https://zoom.us/j/123456789',
            'password': 'password123'
        }

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
        Cancel a scheduled session
        """
        session = self.get_object()
        
        if session.status not in ['scheduled', 'confirmed']:
            return Response(
                {"detail": "Only scheduled or confirmed sessions can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Make the time slot available again
        session.time_slot.is_available = True
        session.time_slot.save()

        # Update session status
        session.status = 'cancelled'
        session.save()

        return Response({"status": "Session cancelled successfully"})
