"""
Tests for course serializers validation.
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError
from courses.serializers import PDFSerializer, AssignmentSerializer, QuizSerializer
from courses.models import PDF, Assignment, Quiz
from .conftest import (
    create_test_user, create_test_course,
    create_test_pdf, create_test_quiz_data, future_date
)

class PDFSerializerTests(TestCase):
    def setUp(self):
        self.teacher = create_test_user(is_teacher=True)
        self.course = create_test_course(self.teacher)
        self.pdf_file = create_test_pdf()

    def test_file_size_validation(self):
        large_file = SimpleUploadedFile(
            "large.pdf",
            b"x" * (20 * 1024 * 1024 + 1),
            content_type="application/pdf"
        )
        
        data = {
            'title': 'Test PDF',
            'course': self.course.id,
            'file': large_file
        }
        
        serializer = PDFSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('file', serializer.errors)

    def test_file_type_validation(self):
        wrong_file = SimpleUploadedFile(
            "test.txt",
            b"Not a PDF",
            content_type="text/plain"
        )
        
        data = {
            'title': 'Test PDF',
            'course': self.course.id,
            'file': wrong_file
        }
        
        serializer = PDFSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('file', serializer.errors)

    def test_valid_data(self):
        data = {
            'title': 'Test PDF',
            'course': self.course.id,
            'file': self.pdf_file
        }
        
        serializer = PDFSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class AssignmentSerializerTests(TestCase):
    def setUp(self):
        self.teacher = create_test_user(is_teacher=True)
        self.course = create_test_course(self.teacher)

    def test_due_date_validation(self):
        from django.utils import timezone
        past_date = timezone.now() - timezone.timedelta(days=1)
        
        data = {
            'title': 'Test Assignment',
            'course': self.course.id,
            'instructions': 'Test instructions',
            'due_date': past_date.isoformat(),
            'max_points': 100
        }
        
        serializer = AssignmentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('due_date', serializer.errors)

    def test_max_points_validation(self):
        data = {
            'title': 'Test Assignment',
            'course': self.course.id,
            'instructions': 'Test instructions',
            'max_points': 0
        }
        
        serializer = AssignmentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('max_points', serializer.errors)

    def test_valid_data(self):
        data = {
            'title': 'Test Assignment',
            'course': self.course.id,
            'instructions': 'Test instructions',
            'due_date': future_date().isoformat(),
            'max_points': 100
        }
        
        serializer = AssignmentSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class QuizSerializerTests(TestCase):
    def setUp(self):
        self.teacher = create_test_user(is_teacher=True)
        self.course = create_test_course(self.teacher)
        self.quiz_data = create_test_quiz_data()

    def test_time_limit_validation(self):
        data = {
            'title': 'Test Quiz',
            'course': self.course.id,
            'time_limit_minutes': 0,
            'passing_score': 70,
            'max_attempts': 3,
            'questions': self.quiz_data
        }
        
        serializer = QuizSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('time_limit_minutes', serializer.errors)

    def test_passing_score_validation(self):
        data = {
            'title': 'Test Quiz',
            'course': self.course.id,
            'time_limit_minutes': 30,
            'passing_score': 101,  # Invalid score
            'max_attempts': 3,
            'questions': self.quiz_data
        }
        
        serializer = QuizSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('passing_score', serializer.errors)

    def test_questions_validation(self):
        # Test invalid questions format
        data = {
            'title': 'Test Quiz',
            'course': self.course.id,
            'time_limit_minutes': 30,
            'passing_score': 70,
            'max_attempts': 3,
            'questions': 'not a list'
        }
        
        serializer = QuizSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        # Test missing required fields
        data['questions'] = [{'text': 'Just a question'}]
        serializer = QuizSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_valid_data(self):
        data = {
            'title': 'Test Quiz',
            'course': self.course.id,
            'time_limit_minutes': 30,
            'passing_score': 70,
            'max_attempts': 3,
            'questions': self.quiz_data
        }
        
        serializer = QuizSerializer(data=data)
        self.assertTrue(serializer.is_valid())
