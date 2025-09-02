"""
Models for tracking student progress through course content.

This module provides models for:
1. ContentProgress - Tracks individual content item completion
2. CourseProgress - Tracks overall course completion and statistics
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from courses.models import Course

class ContentProgress(models.Model):
    """
    Tracks a student's progress on a specific content item (video, PDF, etc.)
    using Django's ContentType framework for generic relations.
    """
    # The user who viewed/completed this content
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='content_progress'
    )
    
    # Generic relation to content (Video, PDF, Assignment, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # The course this content belongs to (for easier querying)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='content_progress_records'
    )
    
    # Progress information
    first_accessed = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # For videos, PDFs, etc.
    progress_percent = models.PositiveSmallIntegerField(default=0)  # 0-100
    
    # Time tracking
    total_time_spent = models.DurationField(default=timezone.timedelta)
    
    class Meta:
        unique_together = ['student', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['student', 'course', 'is_completed']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name_plural = 'Content progress records'
    
    def __str__(self):
        return f"{self.student.username}'s progress on {self.content_object}"
    
    def mark_complete(self):
        """Mark this content as completed."""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.progress_percent = 100
            self.save()


class CourseProgress(models.Model):
    """
    Tracks a student's overall progress in a course.
    Aggregates data from ContentProgress.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_progress'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='student_progress'
    )
    
    # Overall progress
    progress_percent = models.PositiveSmallIntegerField(default=0)  # 0-100
    last_activity = models.DateTimeField(auto_now=True)
    
    # Counts
    completed_items = models.PositiveIntegerField(default=0)
    total_items = models.PositiveIntegerField(default=0)
    
    # Time tracking
    total_time_spent = models.DurationField(default=timezone.timedelta)
    
    class Meta:
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student', 'last_activity']),
            models.Index(fields=['course', 'progress_percent']),
        ]
    
    def __str__(self):
        return f"{self.student.username}'s progress in {self.course.title}"
    
    def update_progress(self):
        """
        Calculate and update progress based on completed content items.
        """
        # Get all content items for this course
        from courses.models import Video, PDF
        
        content_types = {
            'videos': Video.objects.filter(course=self.course).count(),
            'pdfs': PDF.objects.filter(course=self.course).count(),
            # Add other content types as they're added to the system
        }
        
        # Get completed items
        completed_count = ContentProgress.objects.filter(
            student=self.student,
            course=self.course,
            is_completed=True
        ).count()
        
        # Calculate totals
        total_items = sum(content_types.values())
        self.completed_items = completed_count
        self.total_items = total_items
        
        # Calculate percentage
        if total_items > 0:
            self.progress_percent = int((completed_count / total_items) * 100)
        else:
            self.progress_percent = 0
            
        self.save()
        
        return self.progress_percent
