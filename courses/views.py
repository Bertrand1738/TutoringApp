from rest_framework import viewsets, permissions
from .models import CourseCategory, Course, Video
from .serializers import CourseCategorySerializer, CourseSerializer, VideoSerializer

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and 
            request.user.groups.filter(name='teacher').exists()
        )

class CourseCategoryViewSet(viewsets.ModelViewSet):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    permission_classes = [permissions.AllowAny]  # open to read, tighten later


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("teacher__user", "category").all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [IsTeacher()]

    def perform_create(self, serializer):
        teacher_profile = getattr(self.request.user, "teacher_profile", None)
        serializer.save(teacher=teacher_profile)


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.select_related("course").all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [IsTeacher()]



