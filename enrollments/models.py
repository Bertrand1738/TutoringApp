"""
Models for managing course enrollments.
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from courses.models import Course
from .content_models import ContentType as EnrollmentContentType, ContentBundle

class Enrollment(models.Model):
    """
    Represents a student's enrollment in a course, video, or other content.
    Created automatically after successful payment processing.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
    ]
    
    # Basic enrollment fields
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )
    # Legacy support for course enrollments
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrolled_students',
        null=True,
        blank=True
    )
    
    # Support for any content type
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='enrollments'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Content type reference (optional)
    enrollment_content = models.ForeignKey(
        EnrollmentContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollments'
    )
    
    # Bundle reference if this enrollment is part of a bundle
    bundle = models.ForeignKey(
        ContentBundle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollments'
    )
    
    # Enrollment status and timing
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='active'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Payment reference
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollments'
    )
    
    # Metadata
    is_trial = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-enrolled_at']
    
    def __str__(self):
        if self.course:
            return f"{self.student.username} enrolled in {self.course.title}"
        elif self.content_object:
            return f"{self.student.username} enrolled in {self.content_object}"
        else:
            return f"Enrollment {self.id} for {self.student.username}"
    
    def save(self, *args, **kwargs):
        """Ensure either course or content_object is set"""
        if not self.course and not (self.content_type and self.object_id):
            from django.core.exceptions import ValidationError
            raise ValidationError("Either course or content_object must be set")
        
        # If course is set but content_object is not, set content_object to the course
        if self.course and not (self.content_type and self.object_id):
            self.content_type = ContentType.objects.get_for_model(Course)
            self.object_id = self.course.id
            
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Check if enrollment is currently active"""
        return self.status == 'active' and not self.is_expired
    
    @property
    def is_expired(self):
        """Check if enrollment has expired (if applicable)"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
        
    def get_content_name(self):
        """Get a display name for the enrolled content"""
        if self.course:
            return self.course.title
        elif self.content_object:
            if hasattr(self.content_object, 'title'):
                return self.content_object.title
            return str(self.content_object)
        elif self.enrollment_content:
            return self.enrollment_content.name
        return f"Enrollment {self.id}"
        
    def mark_accessed(self):
        """Mark enrollment as being accessed now"""
        from django.utils import timezone
        self.last_accessed = timezone.now()
        self.save(update_fields=['last_accessed'])


class VideoEnrollment(models.Model):
    """
    Represents access to individual video content.
    """
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='video_details'
    )
    video = models.ForeignKey(
        'courses.Video',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    purchased_at = models.DateTimeField(auto_now_add=True)
    max_views = models.PositiveIntegerField(default=0)  # 0 means unlimited
    views_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.video.title}"
    
    @property
    def has_views_remaining(self):
        """Check if there are views remaining"""
        if self.max_views == 0:  # Unlimited views
            return True
        return self.views_count < self.max_views
        
    def increment_view_count(self):
        """Increment the view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
        
    def can_view(self):
        """Check if student can view this video"""
        return self.enrollment.is_active and self.has_views_remaining
