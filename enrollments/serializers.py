from rest_framework import serializers
from .models import Enrollment
from courses.course_serializers import CourseSerializer

class EnrollmentSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_details', 'enrolled_at', 'is_active', 'expires_at']
        read_only_fields = ['student', 'enrolled_at', 'is_active', 'expires_at']
