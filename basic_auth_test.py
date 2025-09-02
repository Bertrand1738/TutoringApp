"""
Simple authentication test script using Django test client directly
"""
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User

def test_auth_directly():
    """Test authentication using Django's APIClient directly"""
    print("Testing authentication using Django APIClient...")
    
    # Create a test client
    client = APIClient()
    
    # Try to authenticate with the teacher user
    print("\nTesting teacher login...")
    teacher = User.objects.get(username='teacher')
    print(f"Found teacher: {teacher.username}, {teacher.email}")
    
    # Get token with teacher credentials
    response = client.post('/api/auth/login/', 
                          {'username': 'teacher', 'password': 'teacherpass'}, 
                          format='json')
    print(f"Status code: {response.status_code}")
    print(f"Response content: {response.content.decode()}")
    
    # Try with student user
    print("\nTesting student login...")
    student = User.objects.get(username='student')
    print(f"Found student: {student.username}, {student.email}")
    
    response = client.post('/api/auth/login/', 
                          {'username': 'student', 'password': 'studentpass'}, 
                          format='json')
    print(f"Status code: {response.status_code}")
    print(f"Response content: {response.content.decode()}")

if __name__ == "__main__":
    test_auth_directly()
