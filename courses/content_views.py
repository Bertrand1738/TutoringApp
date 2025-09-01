"""
Views for managing course content (Videos, PDFs, with other types to be added later)
"""
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Course, Video, PDF
from .content_serializers import VideoSerializer, PDFSerializer
from core.permissions import (
    CanManageCourseContent, IsEnrolledOrPreview
)

class BaseContentViewSet(viewsets.ModelViewSet):
    """Base viewset for all content types"""
    permission_classes = [CanManageCourseContent]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter by course if course_pk is provided
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            queryset = queryset.filter(course_id=course_pk)

        # For non-authenticated users, only show previews of published courses
        if not self.request.user.is_authenticated:
            return queryset.filter(is_preview=True, course__published=True)

        if hasattr(self.request.user, 'teacher_profile'):
            # Teachers can see all content in their courses
            return queryset.filter(course__teacher=self.request.user.teacher_profile)
        else:
            # Students can see previews and content of enrolled courses
            return queryset.filter(
                Q(is_preview=True, course__published=True) |
                Q(course__enrollments__student=self.request.user.student_profile,
                  course__enrollments__active=True)
            ).distinct()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsEnrolledOrPreview()]
        return [CanManageCourseContent()]

    def perform_create(self, serializer):
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            course = get_object_or_404(Course, pk=course_pk)
            serializer.save(course=course)
        else:
            serializer.save()


class VideoViewSet(BaseContentViewSet):
    """Viewset for managing video content"""
    queryset = Video.objects.select_related('course', 'course__teacher').all()
    serializer_class = VideoSerializer


class PDFViewSet(BaseContentViewSet):
    """Viewset for managing PDF content"""
    queryset = PDF.objects.select_related('course', 'course__teacher').all()
    serializer_class = PDFSerializer


# Commented out due to missing models
# class AssignmentViewSet(BaseContentViewSet):
#     """Viewset for managing assignments"""
#     queryset = Assignment.objects.select_related('course', 'course__teacher').all()
#     serializer_class = AssignmentSerializer


# class QuizViewSet(BaseContentViewSet):
#     """Viewset for managing quizzes"""
#     queryset = Quiz.objects.select_related('course', 'course__teacher').all()
#     serializer_class = QuizSerializer
