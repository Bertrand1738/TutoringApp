"""
Models for managing course enrollments.
"""
from django.db import models
from django.conf import settings
from courses.models import Course

class Enrollment(models.Model):
    """
    Represents a student's enrollment in a course.
    Created automatically after successful payment processing.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrolled_students'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'course']  # Prevent duplicate enrollments
        ordering = ['-enrolled_at']  # Most recent first
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"
    
    @property
    def is_expired(self):
        """Check if enrollment has expired (if applicable)"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
