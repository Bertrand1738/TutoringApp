"""
Set up test users for authentication testing
"""
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User, Group

def setup_test_users():
    """Create test users and groups if they don't exist"""
    # Create groups
    student_group, _ = Group.objects.get_or_create(name='student')
    teacher_group, _ = Group.objects.get_or_create(name='teacher')
    
    # Create a test teacher
    if not User.objects.filter(username='teacher').exists():
        teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='teacherpass',
            first_name='Test',
            last_name='Teacher'
        )
        teacher.groups.add(teacher_group)
        print(f"Created teacher user: {teacher.username}")
    else:
        print("Teacher user already exists")
    
    # Create a test student
    if not User.objects.filter(username='student').exists():
        student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass',
            first_name='Test',
            last_name='Student'
        )
        student.groups.add(student_group)
        print(f"Created student user: {student.username}")
    else:
        print("Student user already exists")

if __name__ == "__main__":
    setup_test_users()
