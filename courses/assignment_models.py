"""
Models for course assignments.

This module provides models for:
1. Assignment - The assignment itself with instructions
2. Submission - Student submissions for assignments
3. AssignmentFeedback - Teacher feedback on submissions
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from courses.models import Course

class Assignment(models.Model):
    """
    Represents a course assignment that students need to complete.
    """
    # Basic information
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    instructions = models.TextField(
        help_text="Detailed instructions for completing the assignment"
    )
    
    # Metadata
    order_index = models.PositiveIntegerField(default=1)
    is_preview = models.BooleanField(
        default=False,
        help_text="If true, this assignment is visible to non-enrolled students"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Scheduling
    due_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Optional due date for the assignment"
    )
    available_from = models.DateTimeField(
        default=timezone.now,
        help_text="When this assignment becomes available to students"
    )
    
    # Grading
    max_points = models.PositiveIntegerField(
        default=100,
        help_text="Maximum points possible for this assignment"
    )
    
    # Attached files
    attachment = models.FileField(
        upload_to='assignment_files/',
        null=True,
        blank=True,
        help_text="Optional file attachment (worksheet, template, etc.)"
    )
    
    class Meta:
        ordering = ['course', 'order_index']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def is_available(self):
        """Check if the assignment is currently available to students."""
        now = timezone.now()
        return now >= self.available_from
    
    @property
    def is_past_due(self):
        """Check if the assignment is past its due date."""
        if not self.due_date:
            return False
        return timezone.now() > self.due_date


class Submission(models.Model):
    """
    Represents a student's submission for an assignment.
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('resubmitted', 'Resubmitted'),
        ('graded', 'Graded'),
        ('returned', 'Returned'),
    ]
    
    # Relations
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignment_submissions'
    )
    
    # Submission content
    text_content = models.TextField(
        blank=True,
        help_text="Written response for the assignment"
    )
    file = models.FileField(
        upload_to='assignment_submissions/',
        null=True,
        blank=True,
        help_text="File upload for the assignment"
    )
    
    # Submission metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )
    
    # Grading
    points_earned = models.PositiveIntegerField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.username}'s submission for {self.assignment.title}"
    
    @property
    def is_late(self):
        """Check if the submission was submitted after the due date."""
        if not self.assignment.due_date:
            return False
        return self.submitted_at > self.assignment.due_date
    
    @property
    def grade_percentage(self):
        """Calculate grade as a percentage."""
        if self.points_earned is None or self.assignment.max_points == 0:
            return None
        return (self.points_earned / self.assignment.max_points) * 100


class AssignmentFeedback(models.Model):
    """
    Feedback given on a student's assignment submission.
    """
    # Relations
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_feedback'
    )
    
    # Feedback content
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional attachment
    attachment = models.FileField(
        upload_to='feedback_attachments/',
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Feedback on {self.submission}"
