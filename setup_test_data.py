import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from courses.models import CourseCategory, Course
from accounts.models import TeacherProfile

User = get_user_model()

def setup_test_data():
    # Create a student user if it doesn't exist
    student, created = User.objects.get_or_create(
        username='student1',
        email='student1@example.com',
        defaults={
            'is_active': True
        }
    )
    if created:
        student.set_password('student123')
        student.save()
        print("Created student user: student1")
    
    # Create a test category if none exists
    category, created = CourseCategory.objects.get_or_create(
        name='French Basics',
        defaults={
            'description': 'Basic French language courses'
        }
    )
    if created:
        print("Created course category: French Basics")
    
    # Get the first teacher profile
    teacher = TeacherProfile.objects.first()
    if not teacher:
        print("No teacher found! Please run setup_teacher.py first")
        return
    
    # Create a test course if none exists
    course, created = Course.objects.get_or_create(
        title='French for Beginners',
        defaults={
            'description': 'Learn basic French conversation skills',
            'price': 49.99,
            'published': True,
            'teacher': teacher,
            'category': category
        }
    )
    if created:
        print("Created test course: French for Beginners")

if __name__ == '__main__':
    setup_test_data()
    print("Test data setup completed!")
