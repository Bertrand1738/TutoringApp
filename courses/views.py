from rest_framework import viewsets, permissions, filters
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CourseCategory, Course, Video
from .course_serializers import CourseCategorySerializer, CourseSerializer
from .content_serializers import VideoSerializer
from core.permissions import IsTeacher

class CourseCategoryViewSet(viewsets.ModelViewSet):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can modify categories

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'category__name']
    permission_classes = [permissions.AllowAny]  # Default to AllowAny for list and retrieve actions

    def get_queryset(self):
        queryset = Course.objects.select_related("teacher__user", "category").all()
        
        # Filter by featured parameter if present
        featured = self.request.query_params.get('featured', None)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(published=True)
            # Get the limit parameter, default to 3
            limit = self.request.query_params.get('limit', 3)
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                limit = 3
            # Return limited number of courses
            return queryset[:limit]  # Return top N as featured
        
        # For non-authenticated users or students, only show published courses
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(published=True)
        
        # For teachers, show only their courses
        elif hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=self.request.user.teacher_profile)
        
        return queryset

    def get_permissions(self):
        # Always allow list and retrieve actions
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
            
        # Teacher permissions for create, update, delete
        return [IsTeacher()]

    def perform_create(self, serializer):
        teacher_profile = getattr(self.request.user, "teacher_profile", None)
        serializer.save(teacher=teacher_profile)

    @action(detail=True, methods=['get'])
    def enrolled_students(self, request, pk=None):
        """Return list of enrolled students for a course"""
        course = self.get_object()
        if request.user.teacher_profile != course.teacher:
            return Response({"detail": "Not authorized"}, status=403)
        
        enrollments = course.enrolled_students.select_related('student').all()
        return Response({
            'count': enrollments.count(),
            'students': [
                {
                    'id': enrollment.student.id,
                    'username': enrollment.student.username,
                    'email': enrollment.student.email,
                    'enrolled_at': enrollment.enrolled_at
                }
                for enrollment in enrollments
            ]
        })


class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = VideoSerializer

    def get_queryset(self):
        queryset = Video.objects.select_related("course").all()

        # For non-authenticated users, only show preview videos of published courses
        if not self.request.user.is_authenticated:
            return queryset.filter(is_preview=True, course__published=True)

        if hasattr(self.request.user, 'teacher_profile'):
            # Teachers can see all videos in their courses
            return queryset.filter(course__teacher=self.request.user.teacher_profile)
        else:
            # Students can see preview videos and videos of courses they're enrolled in
            return queryset.filter(
                Q(is_preview=True, course__published=True) |
                Q(course__enrolled_students__student=self.request.user, 
                  course__enrolled_students__is_active=True)
            ).distinct()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [IsTeacher()]

    def retrieve(self, request, *args, **kwargs):
        video = self.get_object()
        
        # Check if user has access to this video
        if not video.is_preview:
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required"}, status=401)
            
            # Check if user is enrolled in the course
            if not hasattr(request.user, 'teacher_profile'):
                enrollment = video.course.enrolled_students.filter(
                    student=request.user,
                    is_active=True
                ).first()
                
                if not enrollment:
                    return Response(
                        {"detail": "You must be enrolled in this course to access this video"},
                        status=403
                    )
        
        serializer = self.get_serializer(video)
        return Response(serializer.data)
