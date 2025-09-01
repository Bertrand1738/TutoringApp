"""
Student enrollments proxy models and managers
"""
from django.db import models
from enrollments.models import Enrollment as BaseEnrollment

class StudentEnrollmentManager(models.Manager):
    """Custom manager for student-specific enrollment operations"""
    def get_queryset(self):
        return super().get_queryset().select_related('course', 'student')

class StudentEnrollment(BaseEnrollment):
    """
    Proxy model for student-specific enrollment operations
    """
    objects = StudentEnrollmentManager()

    class Meta:
        proxy = True
