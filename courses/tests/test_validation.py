from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import TeacherProfile
from ..models import Course, PDF, Assignment, Quiz, CourseCategory
from ..serializers import PDFSerializer, AssignmentSerializer, QuizSerializer

User = get_user_model()

class ContentTypeValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a teacher
        user = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123'
        )
        cls.teacher = TeacherProfile.objects.create(user=user)
        
        # Create a category
        cls.category = CourseCategory.objects.create(
            name='Test Category',
            description='Test Description'
        )
        
        # Create a course
        cls.course = Course.objects.create(
            teacher=cls.teacher,
            category=cls.category,
            title='Test Course',
            description='Test Description',
            price=99.99
        )

    def test_pdf_file_validation(self):
        # Test PDF file size validation
        large_file = SimpleUploadedFile(
            'test.pdf',
            b'x' * (20 * 1024 * 1024 + 1),  # 20MB + 1 byte
            content_type='application/pdf'
        )
        
        serializer = PDFSerializer(data={
            'title': 'Test PDF',
            'file': large_file,
            'course': self.course.id
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('file', serializer.errors)
        
        # Test invalid file type
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'Hello World',
            content_type='text/plain'
        )
        
        serializer = PDFSerializer(data={
            'title': 'Test PDF',
            'file': invalid_file,
            'course': self.course.id
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('file', serializer.errors)

    def test_assignment_validation(self):
        # Test past due date
        past_date = timezone.now() - timezone.timedelta(days=1)
        
        serializer = AssignmentSerializer(data={
            'title': 'Test Assignment',
            'instructions': 'Test Instructions',
            'due_date': past_date.isoformat(),
            'max_points': 100,
            'course': self.course.id
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('due_date', serializer.errors)
        
        # Test invalid max points
        serializer = AssignmentSerializer(data={
            'title': 'Test Assignment',
            'instructions': 'Test Instructions',
            'max_points': -1,
            'course': self.course.id
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('max_points', serializer.errors)

    def test_quiz_validation(self):
        # Test invalid time limit
        serializer = QuizSerializer(data={
            'title': 'Test Quiz',
            'time_limit_minutes': 0,
            'passing_score': 70,
            'max_attempts': 3,
            'course': self.course.id
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('time_limit_minutes', serializer.errors)
        
        # Test invalid passing score
        serializer = QuizSerializer(data={
            'title': 'Test Quiz',
            'time_limit_minutes': 30,
            'passing_score': 101,  # Should be 0-100
            'max_attempts': 3,
            'course': self.course.id
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('passing_score', serializer.errors)
        
        # Test invalid quiz questions structure
        invalid_questions = [
            {
                'text': 'Question 1',
                # Missing options and correct_answer
            }
        ]
        
        serializer = QuizSerializer(data={
            'title': 'Test Quiz',
            'time_limit_minutes': 30,
            'passing_score': 70,
            'max_attempts': 3,
            'questions': invalid_questions,
            'course': self.course.id
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('questions', serializer.errors)
