"""
Tests for course models validation.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from courses.models import PDF, Assignment, Quiz
from .conftest import (
    create_test_user, create_test_course,
    create_test_pdf, create_test_quiz_data, future_date
)

class PDFModelTests(TestCase):
    def setUp(self):
        self.teacher = create_test_user(is_teacher=True)
        self.course = create_test_course(self.teacher)
        self.pdf_file = create_test_pdf()

    def test_pdf_file_size_validation(self):
        # Create a file larger than 20MB
        large_file = SimpleUploadedFile(
            "large.pdf",
            b"x" * (20 * 1024 * 1024 + 1),
            content_type="application/pdf"
        )

        pdf = PDF(
            course=self.course,
            title="Test PDF",
            file=large_file
        )

        with self.assertRaises(ValidationError):
            pdf.full_clean()

    def test_pdf_file_type_validation(self):
        wrong_file = SimpleUploadedFile(
            "test.txt",
            b"Not a PDF",
            content_type="text/plain"
        )

        pdf = PDF(
            course=self.course,
            title="Test PDF",
            file=wrong_file
        )

        with self.assertRaises(ValidationError):
            pdf.full_clean()

    def test_valid_pdf(self):
        pdf = PDF(
            course=self.course,
            title="Test PDF",
            file=self.pdf_file
        )
        try:
            pdf.full_clean()
        except ValidationError:
            self.fail("PDF validation raised ValidationError unexpectedly")


class AssignmentModelTests(TestCase):
    def setUp(self):
        self.teacher = create_test_user(is_teacher=True)
        self.course = create_test_course(self.teacher)

    def test_past_due_date_validation(self):
        past_date = timezone.now() - timezone.timedelta(days=1)
        assignment = Assignment(
            course=self.course,
            title="Test Assignment",
            instructions="Test instructions",
            due_date=past_date
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_negative_points_validation(self):
        assignment = Assignment(
            course=self.course,
            title="Test Assignment",
            instructions="Test instructions",
            max_points=-10
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_valid_assignment(self):
        assignment = Assignment(
            course=self.course,
            title="Test Assignment",
            instructions="Test instructions",
            due_date=future_date(),
            max_points=100
        )
        try:
            assignment.full_clean()
        except ValidationError:
            self.fail("Assignment validation raised ValidationError unexpectedly")


class QuizModelTests(TestCase):
    def setUp(self):
        self.teacher = create_test_user(is_teacher=True)
        self.course = create_test_course(self.teacher)
        self.quiz_data = create_test_quiz_data()

    def test_time_limit_validation(self):
        quiz = Quiz(
            course=self.course,
            title="Test Quiz",
            time_limit_minutes=0
        )

        with self.assertRaises(ValidationError):
            quiz.full_clean()

    def test_passing_score_validation(self):
        # Test score < 0
        quiz = Quiz(
            course=self.course,
            title="Test Quiz",
            passing_score=-1
        )
        with self.assertRaises(ValidationError):
            quiz.full_clean()

        # Test score > 100
        quiz.passing_score = 101
        with self.assertRaises(ValidationError):
            quiz.full_clean()

    def test_max_attempts_validation(self):
        quiz = Quiz(
            course=self.course,
            title="Test Quiz",
            max_attempts=0
        )

        with self.assertRaises(ValidationError):
            quiz.full_clean()

    def test_questions_validation(self):
        # Test invalid questions format
        quiz = Quiz(
            course=self.course,
            title="Test Quiz",
            questions="not a list"
        )
        with self.assertRaises(ValidationError):
            quiz.full_clean()

        # Test missing required fields
        quiz.questions = [{"text": "Just a question"}]
        with self.assertRaises(ValidationError):
            quiz.full_clean()

        # Test invalid correct_answer
        quiz.questions = [{
            "text": "Test question?",
            "options": ["A", "B"],
            "correct_answer": 2  # Index out of range
        }]
        with self.assertRaises(ValidationError):
            quiz.full_clean()

    def test_valid_quiz(self):
        quiz = Quiz(
            course=self.course,
            title="Test Quiz",
            time_limit_minutes=30,
            passing_score=70,
            max_attempts=3,
            questions=self.quiz_data
        )
        try:
            quiz.full_clean()
        except ValidationError:
            self.fail("Quiz validation raised ValidationError unexpectedly")
