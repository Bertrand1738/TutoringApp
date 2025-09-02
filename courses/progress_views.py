"""
Views for progress tracking
"""
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils import timezone

from courses.progress_models import ContentProgress, CourseProgress
from courses.progress_serializers import (
    ContentProgressSerializer, 
    CourseProgressSerializer,
    CourseProgressDetailSerializer
)
from courses.models import Course, Video, PDF
from core.permissions import IsEnrolledOrTeacher


class ContentProgressViewSet(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """
    API endpoints for tracking progress on course content.
    
    retrieve:
        Get a specific progress record
        
    list:
        Get all progress records for the authenticated user
        
    update:
        Update a progress record (e.g., mark as complete)
        
    mark_complete:
        Mark a content item as completed
        
    track_progress:
        Update progress percentage for a content item
    """
    serializer_class = ContentProgressSerializer
    permission_classes = [permissions.IsAuthenticated, IsEnrolledOrTeacher]
    
    def get_queryset(self):
        """Filter progress records to those for the current user"""
        return ContentProgress.objects.filter(student=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Mark a content item as completed"""
        progress = self.get_object()
        progress.mark_complete()
        
        # Update the corresponding CourseProgress
        try:
            course_progress = CourseProgress.objects.get(
                student=request.user,
                course=progress.course
            )
            course_progress.update_progress()
        except CourseProgress.DoesNotExist:
            # Create course progress if it doesn't exist
            course_progress = CourseProgress.objects.create(
                student=request.user,
                course=progress.course
            )
            course_progress.update_progress()
        
        serializer = self.get_serializer(progress)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def track_progress(self, request, pk=None):
        """Update progress percentage for a content item"""
        progress = self.get_object()
        
        # Update progress percentage
        if 'progress_percent' in request.data:
            progress.progress_percent = min(100, max(0, int(request.data['progress_percent'])))
            
            # If progress is 100%, mark as completed
            if progress.progress_percent == 100:
                progress.is_completed = True
                progress.completed_at = timezone.now()
                
            progress.save()
        
        # Update time spent if provided
        if 'time_spent_seconds' in request.data:
            seconds = int(request.data['time_spent_seconds'])
            progress.total_time_spent += timezone.timedelta(seconds=seconds)
            progress.save()
        
        serializer = self.get_serializer(progress)
        return Response(serializer.data)


class CourseProgressViewSet(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    API endpoints for tracking overall course progress.
    
    retrieve:
        Get progress for a specific course
        
    list:
        Get progress for all courses
        
    refresh:
        Recalculate progress for a course
    """
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter course progress to those for the current user"""
        return CourseProgress.objects.filter(student=self.request.user)
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return CourseProgressDetailSerializer
        return CourseProgressSerializer
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Recalculate progress for a course"""
        course_progress = self.get_object()
        course_progress.update_progress()
        
        serializer = CourseProgressDetailSerializer(course_progress)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def track_content(self, request):
        """Track progress for a specific content item"""
        # Required parameters
        required_params = ['course_id', 'content_type', 'object_id']
        for param in required_params:
            if param not in request.data:
                return Response(
                    {'error': f'Missing required parameter: {param}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get course
        course_id = request.data['course_id']
        course = get_object_or_404(Course, id=course_id)
        
        # Check enrollment
        if not course.enrolled_students.filter(student=request.user).exists():
            return Response(
                {'error': 'You are not enrolled in this course'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get content type
        content_type_name = request.data['content_type'].lower()
        content_models = {
            'video': Video,
            'pdf': PDF,
            # Additional content types can be added here in the future
        }
        
        if content_type_name not in content_models:
            return Response(
                {'error': f'Invalid content type: {content_type_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content_model = content_models[content_type_name]
        content_type = ContentType.objects.get_for_model(content_model)
        object_id = request.data['object_id']
        
        # Verify content belongs to course
        content_exists = content_model.objects.filter(
            id=object_id,
            course=course
        ).exists()
        
        if not content_exists:
            return Response(
                {'error': 'Content not found in this course'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create progress record
        progress, created = ContentProgress.objects.get_or_create(
            student=request.user,
            content_type=content_type,
            object_id=object_id,
            course=course
        )
        
        # Update progress if provided
        if 'progress_percent' in request.data:
            progress.progress_percent = min(100, max(0, int(request.data['progress_percent'])))
            
            # If progress is 100%, mark as completed
            if progress.progress_percent == 100 and not progress.is_completed:
                progress.is_completed = True
                progress.completed_at = timezone.now()
            
            progress.save()
        
        # Update time spent if provided
        if 'time_spent_seconds' in request.data:
            seconds = int(request.data['time_spent_seconds'])
            progress.total_time_spent += timezone.timedelta(seconds=seconds)
            progress.save()
        
        # Get or create course progress
        course_progress, _ = CourseProgress.objects.get_or_create(
            student=request.user,
            course=course
        )
        
        # Update course progress
        course_progress.update_progress()
        
        serializer = ContentProgressSerializer(progress)
        return Response(serializer.data)
