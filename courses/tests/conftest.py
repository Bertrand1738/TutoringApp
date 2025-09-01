"""
Test configuration and fixtures for course tests.
"""
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import TeacherProfile, StudentProfile
from courses.models import CourseCategory, Course
from django.utils import timezone

User = get_user_model()

def create_test_user(username="testuser", password="testpass", is_teacher=False):
    """Create a test user and optionally a teacher profile"""
    user = User.objects.create_user(username=username, password=password)
    if is_teacher:
        TeacherProfile.objects.create(user=user)
    else:
        StudentProfile.objects.create(user=user)
    return user

def create_test_course(teacher, title="Test Course"):
    """Create a test course"""
    category = CourseCategory.objects.create(name="Test Category")
    return Course.objects.create(
        teacher=teacher.teacher_profile,
        category=category,
        title=title,
        description="Test description",
        price=99.99,
        published=True
    )

def create_test_pdf():
    """Create a test PDF file"""
    return SimpleUploadedFile(
        "test.pdf",
        b"Test PDF content",
        content_type="application/pdf"
    )

def create_test_quiz_data():
    """Create test quiz questions"""
    return [
        {
            "text": "Test question 1?",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answer": 0
        },
        {
            "text": "Test question 2?",
            "options": ["Option A", "Option B", "Option C"],
            "correct_answer": 1
        }
    ]

def future_date():
    """Get a future date for testing"""
    return timezone.now() + timezone.timedelta(days=7)
