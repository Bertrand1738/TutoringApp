from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Enrollment
from .serializers import EnrollmentSerializer
from courses.models import Course

class EnrollCourseView(generics.CreateAPIView):
    """
    View for enrolling in a course.
    POST /api/enrollments/enroll/
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=request.data.get('course'))
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Handle payment processing here
        # For now, we'll create the enrollment directly
        enrollment = Enrollment.objects.create(
            student=request.user,
            course=course,
            is_active=True
        )
        
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MyEnrollmentsView(generics.ListAPIView):
    """
    View for listing user's enrollments
    GET /api/enrollments/my-enrollments/
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__teacher')  # Optimize queries
