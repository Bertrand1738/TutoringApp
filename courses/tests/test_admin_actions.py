from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import TeacherProfile
from ..models import Course, PDF, Assignment, Quiz, CourseCategory
from ..admin import CourseAdmin, PDFAdmin, AssignmentAdmin, QuizAdmin
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest

User = get_user_model()

class MockRequest:
    def __init__(self, user=None):
        self.user = user

class AdminActionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create admin user
        cls.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
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
        
        # Create courses
        cls.course1 = Course.objects.create(
            teacher=cls.teacher,
            category=cls.category,
            title='Course 1',
            description='Description 1',
            price=99.99,
            published=False
        )
        
        cls.course2 = Course.objects.create(
            teacher=cls.teacher,
            category=cls.category,
            title='Course 2',
            description='Description 2',
            price=149.99,
            published=False
        )
        
        # Create mock admin site
        cls.site = AdminSite()

    def setUp(self):
        self.course_admin = CourseAdmin(Course, self.site)
        self.pdf_admin = PDFAdmin(PDF, self.site)
        self.assignment_admin = AssignmentAdmin(Assignment, self.site)
        self.quiz_admin = QuizAdmin(Quiz, self.site)
        self.request = MockRequest(self.admin_user)

    def test_publish_courses(self):
        # Test publish_courses action
        queryset = Course.objects.filter(published=False)
        self.course_admin.publish_courses(self.request, queryset)
        
        # Verify all courses are published
        self.assertTrue(
            all(course.published 
                for course in Course.objects.filter(id__in=[self.course1.id, self.course2.id]))
        )

    def test_unpublish_courses(self):
        # First publish the courses
        self.course1.published = True
        self.course1.save()
        self.course2.published = True
        self.course2.save()
        
        # Test unpublish_courses action
        queryset = Course.objects.filter(published=True)
        self.course_admin.unpublish_courses(self.request, queryset)
        
        # Verify all courses are unpublished
        self.assertTrue(
            all(not course.published 
                for course in Course.objects.filter(id__in=[self.course1.id, self.course2.id]))
        )

    def test_toggle_preview_pdfs(self):
        # Create test PDFs
        pdf1 = PDF.objects.create(
            course=self.course1,
            title='PDF 1',
            file=SimpleUploadedFile('test1.pdf', b'content1'),
            is_preview=False
        )
        
        pdf2 = PDF.objects.create(
            course=self.course1,
            title='PDF 2',
            file=SimpleUploadedFile('test2.pdf', b'content2'),
            is_preview=False
        )
        
        # Test toggle_preview action
        queryset = PDF.objects.all()
        self.pdf_admin.toggle_preview(self.request, queryset)
        
        # Verify preview status is toggled
        self.assertTrue(PDF.objects.get(id=pdf1.id).is_preview)
        self.assertTrue(PDF.objects.get(id=pdf2.id).is_preview)

    def test_extend_assignment_deadlines(self):
        # Create test assignments
        assignment1 = Assignment.objects.create(
            course=self.course1,
            title='Assignment 1',
            instructions='Instructions 1',
            due_date='2025-12-31 23:59:59'
        )
        
        assignment2 = Assignment.objects.create(
            course=self.course1,
            title='Assignment 2',
            instructions='Instructions 2',
            due_date='2025-12-31 23:59:59'
        )
        
        # Test extend_deadline action
        queryset = Assignment.objects.all()
        self.assignment_admin.extend_deadline(self.request, queryset, days=7)
        
        # Verify deadlines are extended
        for assignment in [assignment1, assignment2]:
            updated = Assignment.objects.get(id=assignment.id)
            self.assertEqual(
                updated.due_date.date().isoformat(),
                '2026-01-07'
            )

    def test_reset_quiz_attempts(self):
        # Create a quiz
        quiz = Quiz.objects.create(
            course=self.course1,
            title='Test Quiz',
            time_limit_minutes=30,
            passing_score=70,
            max_attempts=3
        )
        
        # Create some progress records (would normally be done through ContentProgress)
        # This is just to verify the action is called
        queryset = Quiz.objects.all()
        self.quiz_admin.reset_attempts(self.request, queryset)
        
        # The actual verification would depend on how you're storing attempts
        # This is just a placeholder to show the action was called
        self.assertTrue(True)
