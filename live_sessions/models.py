"""
Models for managing live tutoring sessions.
Handles teacher availability and session scheduling.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

class TimeSlot(models.Model):
    """Teacher availability slots"""
    teacher = models.ForeignKey(
        "accounts.TeacherProfile",
        on_delete=models.CASCADE,
        related_name="availability_slots"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)
    recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly')
        ],
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=['start_time', 'is_available']),
            models.Index(fields=['teacher', 'is_available'])
        ]

    def __str__(self):
        return f"{self.teacher.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")
        if self.start_time < timezone.now():
            raise ValidationError("Cannot create slots in the past")
        if self.recurring and not self.recurrence_pattern:
            raise ValidationError("Recurring slots must have a recurrence pattern")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class LiveSession(models.Model):
    """Live tutoring sessions"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('missed', 'Missed')
    ]

    from core.services.zoom import ZoomMeetingService
    from core.services.notifications import NotificationService

    course = models.ForeignKey(
        'courses.Course', 
        on_delete=models.CASCADE,
        related_name="live_sessions"
    )
    time_slot = models.OneToOneField(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name="session"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="booked_sessions"
    )
    meeting_platform = models.CharField(
        max_length=20,
        choices=[
            ('zoom', 'Zoom'),
            ('meet', 'Google Meet')
        ],
        default='zoom'
    )
    meeting_url = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=20, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    student_notes = models.TextField(
        blank=True,
        help_text="Notes from student about what they want to cover"
    )
    teacher_notes = models.TextField(
        blank=True,
        help_text="Teacher's notes about the session"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status'])
        ]

    def __str__(self):
        return f"{self.course.title} - {self.time_slot.start_time.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        if not self.time_slot.is_available:
            raise ValidationError("This time slot is not available")
        if self.time_slot.teacher != self.course.teacher:
            raise ValidationError("Time slot teacher must match course teacher")

    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = not self.pk
        
        if is_new:
            # Create Zoom meeting
            zoom_service = ZoomMeetingService()
            duration = int((self.time_slot.end_time - self.time_slot.start_time).total_seconds() / 60)
            meeting_info = zoom_service.create_meeting(
                topic=f"{self.course.title} - Session with {self.student.get_full_name()}",
                start_time=self.time_slot.start_time,
                duration_minutes=duration,
                teacher_email=self.course.teacher.user.email
            )
            
            # Save meeting details
            self.meeting_url = meeting_info['join_url']
            self.meeting_id = meeting_info['id']
            self.meeting_password = meeting_info['password']
            self.meeting_start_url = meeting_info['start_url']
            
            # Mark the time slot as unavailable
            self.time_slot.is_available = False
            self.time_slot.save()
        
        super().save(*args, **kwargs)

        if is_new:
            # Send notifications
            NotificationService.send_session_scheduled_notification(self)
