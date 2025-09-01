"""
Notification service for handling all system notifications
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_system_error_notification(error_type: str, details: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Send error notification to system administrators
        
        Args:
            error_type: Type of error (e.g., 'zoom_meeting_creation_failed')
            details: Error details
            context: Additional context about the error
        """
        try:
            subject = f"System Error Alert: {error_type}"
            
            # Prepare email context
            email_context = {
                'error_type': error_type,
                'error_details': details,
                **(context or {})
            }
            
            # Render email template
            html_message = render_to_string('notifications/system_error_alert.html', email_context)
            text_message = strip_tags(html_message)
            
            # Send email to admins
            send_mail(
                subject=subject,
                message=text_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin[1] for admin in settings.ADMINS],
                fail_silently=True
            )
            
            # Log the error
            logger.error(f"{error_type}: {details}", extra=context or {})
            
        except Exception as e:
            logger.error(f"Failed to send system error notification: {str(e)}")

    @staticmethod
    def send_session_scheduled_notification(session):
        """Send notifications when a session is scheduled"""
        try:
            # Email to student
            student_context = {
                'student_name': session.student.get_full_name(),
                'course_title': session.course.title,
                'teacher_name': session.course.teacher.user.get_full_name(),
                'start_time': session.time_slot.start_time,
                'meeting_url': session.meeting_url,
                'meeting_password': session.meeting_password
            }
            
            student_html = render_to_string(
                'notifications/session_scheduled_student.html',
                student_context
            )
            student_text = strip_tags(student_html)
            
            send_mail(
                subject=f'Session Scheduled: {session.course.title}',
                message=student_text,
                html_message=student_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[session.student.email],
                fail_silently=False
            )

            # Email to teacher
            teacher_context = {
                'teacher_name': session.course.teacher.user.get_full_name(),
                'student_name': session.student.get_full_name(),
                'course_title': session.course.title,
                'start_time': session.time_slot.start_time,
                'meeting_url': session.meeting_url,
                'start_url': session.meeting_start_url
            }
            
            teacher_html = render_to_string(
                'notifications/session_scheduled_teacher.html',
                teacher_context
            )
            teacher_text = strip_tags(teacher_html)
            
            send_mail(
                subject=f'New Session Scheduled: {session.course.title}',
                message=teacher_text,
                html_message=teacher_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[session.course.teacher.user.email],
                fail_silently=False
            )

            # Create in-app notifications
            from live_sessions.models import Notification
            
            # For student
            Notification.objects.create(
                user=session.student,
                type='session_scheduled',
                title=f'Session Scheduled: {session.course.title}',
                message=f'Your session for {session.course.title} has been scheduled for {session.time_slot.start_time}'
            )

            # For teacher
            Notification.objects.create(
                user=session.course.teacher.user,
                type='session_scheduled',
                title=f'New Session Scheduled: {session.course.title}',
                message=f'A new session for {session.course.title} has been scheduled with {session.student.get_full_name()}'
            )

        except Exception as e:
            logger.error(f"Failed to send session scheduled notification: {str(e)}")
            raise

    @staticmethod
    def send_session_reminder(session):
        """Send reminder notifications for upcoming sessions"""
        try:
            # Email to student
            student_context = {
                'student_name': session.student.get_full_name(),
                'course_title': session.course.title,
                'start_time': session.time_slot.start_time,
                'meeting_url': session.meeting_url,
                'meeting_password': session.meeting_password
            }
            
            student_html = render_to_string(
                'notifications/session_reminder_student.html',
                student_context
            )
            student_text = strip_tags(student_html)
            
            send_mail(
                subject=f'Reminder: Upcoming Session - {session.course.title}',
                message=student_text,
                html_message=student_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[session.student.email],
                fail_silently=False
            )

            # Email to teacher
            teacher_context = {
                'teacher_name': session.course.teacher.user.get_full_name(),
                'student_name': session.student.get_full_name(),
                'course_title': session.course.title,
                'start_time': session.time_slot.start_time,
                'start_url': session.meeting_start_url
            }
            
            teacher_html = render_to_string(
                'notifications/session_reminder_teacher.html',
                teacher_context
            )
            teacher_text = strip_tags(teacher_html)
            
            send_mail(
                subject=f'Reminder: Upcoming Session - {session.course.title}',
                message=teacher_text,
                html_message=teacher_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[session.course.teacher.user.email],
                fail_silently=False
            )

            # Create in-app notifications
            from live_sessions.models import Notification
            
            # For student
            Notification.objects.create(
                user=session.student,
                type='session_reminder',
                title=f'Upcoming Session: {session.course.title}',
                message=f'Reminder: Your session for {session.course.title} starts in 24 hours'
            )

            # For teacher
            Notification.objects.create(
                user=session.course.teacher.user,
                type='session_reminder',
                title=f'Upcoming Session: {session.course.title}',
                message=f'Reminder: Your session with {session.student.get_full_name()} starts in 24 hours'
            )

        except Exception as e:
            logger.error(f"Failed to send session reminder notification: {str(e)}")
            raise

    @staticmethod
    def send_session_cancelled_notification(session, cancelled_by):
        """Send notifications when a session is cancelled"""
        try:
            # Email to student
            student_context = {
                'student_name': session.student.get_full_name(),
                'course_title': session.course.title,
                'start_time': session.time_slot.start_time,
                'cancelled_by': 'you' if cancelled_by == session.student else 'the teacher'
            }
            
            student_html = render_to_string(
                'notifications/session_cancelled_student.html',
                student_context
            )
            student_text = strip_tags(student_html)
            
            send_mail(
                subject=f'Session Cancelled: {session.course.title}',
                message=student_text,
                html_message=student_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[session.student.email],
                fail_silently=False
            )

            # Email to teacher
            teacher_context = {
                'teacher_name': session.course.teacher.user.get_full_name(),
                'student_name': session.student.get_full_name(),
                'course_title': session.course.title,
                'start_time': session.time_slot.start_time,
                'cancelled_by': 'you' if cancelled_by == session.course.teacher.user else 'the student'
            }
            
            teacher_html = render_to_string(
                'notifications/session_cancelled_teacher.html',
                teacher_context
            )
            teacher_text = strip_tags(teacher_html)
            
            send_mail(
                subject=f'Session Cancelled: {session.course.title}',
                message=teacher_text,
                html_message=teacher_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[session.course.teacher.user.email],
                fail_silently=False
            )

            # Create in-app notifications
            from live_sessions.models import Notification
            
            # For student
            Notification.objects.create(
                user=session.student,
                type='session_cancelled',
                title=f'Session Cancelled: {session.course.title}',
                message=f'The session for {session.course.title} scheduled for {session.time_slot.start_time} has been cancelled'
            )

            # For teacher
            Notification.objects.create(
                user=session.course.teacher.user,
                type='session_cancelled',
                title=f'Session Cancelled: {session.course.title}',
                message=f'The session with {session.student.get_full_name()} scheduled for {session.time_slot.start_time} has been cancelled'
            )

        except Exception as e:
            logger.error(f"Failed to send session cancelled notification: {str(e)}")
            raise
