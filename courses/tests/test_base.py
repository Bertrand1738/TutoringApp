from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import TeacherProfile, StudentProfile
from ..models import CourseCategory, Course

User = get_user_model()

class CourseContentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create users
        cls.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        cls.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='teacher123'
        )
        
        cls.student_user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='student123'
        )
        
        # Create profiles
        cls.teacher = TeacherProfile.objects.create(user=cls.teacher_user)
        cls.student = StudentProfile.objects.create(user=cls.student_user)
        
        # Create category
        cls.category = CourseCategory.objects.create(
            name='Test Category',
            description='Test Category Description'
        )
        
        # Create course
        cls.course = Course.objects.create(
            teacher=cls.teacher,
            category=cls.category,
            title='Test Course',
            description='Test Course Description',
            price=99.99,
            published=True
        )

    def setUp(self):
        """Set up data for each test method"""
        # Nothing needed here yet, but good to have for future use
        pass
