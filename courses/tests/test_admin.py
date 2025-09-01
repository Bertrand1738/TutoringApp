"""
Tests for admin actions and form validation.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from courses.models import PDF, Assignment, Quiz, ContentProgress
from .conftest import (
    create_test_user, create_test_course,
    create_test_pdf, create_test_quiz_data, future_date
)

User = get_user_model()

class AdminActionsTest(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client = Client()
        self.client.login(username='admin', password='adminpass')

        # Create test data
        self.teacher = create_test_user(is_teacher=True)
        self.course = create_test_course(self.teacher)
        
        # Create test content
        self.pdf = PDF.objects.create(
            course=self.course,
            title="Test PDF",
            file=create_test_pdf()
        )
        
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Test Assignment",
            instructions="Test instructions",
            due_date=future_date()
        )
        
        self.quiz = Quiz.objects.create(
            course=self.course,
            title="Test Quiz",
            questions=create_test_quiz_data()
        )

    def test_course_publish_action(self):
        url = reverse('admin:courses_course_changelist')
        data = {
            'action': 'publish_courses',
            '_selected_action': [self.course.id],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.course.refresh_from_db()
        self.assertTrue(self.course.published)

    def test_extend_assignment_deadline(self):
        original_due_date = self.assignment.due_date
        url = reverse('admin:courses_assignment_changelist')
        data = {
            'action': 'extend_deadline',
            '_selected_action': [self.assignment.id],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assignment.refresh_from_db()
        self.assertEqual(
            self.assignment.due_date,
            original_due_date + timezone.timedelta(days=7)
        )

    def test_reset_quiz_attempts(self):
        # Create some quiz attempts
        student = create_test_user(username='student')
        ContentProgress.objects.create(
            student=student.student_profile,
            content_type=ContentType.objects.get_for_model(Quiz),
            object_id=self.quiz.id,
            progress_data={'attempts': [{'score': 80}]}
        )

        url = reverse('admin:courses_quiz_changelist')
        data = {
            'action': 'reset_attempts',
            '_selected_action': [self.quiz.id],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verify attempts were reset
        self.assertEqual(
            ContentProgress.objects.filter(
                content_type=ContentType.objects.get_for_model(Quiz),
                object_id=self.quiz.id
            ).count(),
            0
        )

    def test_export_course_data(self):
        url = reverse('admin:courses_course_changelist')
        data = {
            'action': 'export_courses_data',
            '_selected_action': [self.course.id],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'text/csv'
        )
        self.assertIn(
            'attachment; filename="courses_export.csv"',
            response['Content-Disposition']
        )

    def test_export_quiz_results(self):
        # Create some quiz results
        student = create_test_user(username='student')
        ContentProgress.objects.create(
            student=student.student_profile,
            content_type=ContentType.objects.get_for_model(Quiz),
            object_id=self.quiz.id,
            progress_data={
                'attempts': [
                    {'score': 70, 'submitted_at': timezone.now().isoformat()}
                ]
            }
        )

        url = reverse('admin:courses_quiz_changelist')
        data = {
            'action': 'export_results',
            '_selected_action': [self.quiz.id],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'text/csv'
        )
        self.assertIn(
            'attachment; filename="quiz_results.csv"',
            response['Content-Disposition']
        )
