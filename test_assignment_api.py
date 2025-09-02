"""
Test the assignment API endpoints
"""
import requests
import json
from pprint import pprint

# Base URL for our API
BASE_URL = "http://127.0.0.1:8000/api/"

def login(email, password):
    """Login and get auth token"""
    login_url = f"{BASE_URL}auth/token/login/"
    login_data = {
        'email': email,
        'password': password
    }
    
    response = requests.post(login_url, data=login_data)
    if response.status_code == 200:
        token = response.json().get('auth_token')
        return token
    else:
        print(f"Login failed: {response.text}")
        return None


def test_assignments_api():
    """Test the assignments API endpoints"""
    # Login as teacher
    teacher_token = login('teacher@example.com', 'teacherpass')
    if not teacher_token:
        print("Teacher login failed, aborting tests")
        return
    
    teacher_headers = {'Authorization': f'Token {teacher_token}'}
    
    # Step 1: List all courses to get a valid course ID
    courses_url = f"{BASE_URL}courses/"
    response = requests.get(courses_url, headers=teacher_headers)
    if response.status_code != 200:
        print(f"Failed to retrieve courses: {response.text}")
        return
    
    courses = response.json()
    if not courses:
        print("No courses found, please create a course first")
        return
    
    course_id = courses[0]['id']
    print(f"Using course: {courses[0]['title']} (ID: {course_id})")
    
    # Step 2: Create a new assignment
    assignment_url = f"{BASE_URL}assignments/"
    assignment_data = {
        'course': course_id,
        'title': 'French Grammar Exercise',
        'description': 'Practice your French grammar skills',
        'instructions': 'Complete the exercises in the attached worksheet.',
        'max_points': 100,
        'due_date': '2025-10-01T23:59:59Z',
        'is_preview': False
    }
    
    print("\nCreating a new assignment...")
    response = requests.post(assignment_url, json=assignment_data, headers=teacher_headers)
    if response.status_code != 201:
        print(f"Failed to create assignment: {response.text}")
        return
    
    assignment = response.json()
    assignment_id = assignment['id']
    print(f"Assignment created successfully: {assignment['title']} (ID: {assignment_id})")
    pprint(assignment)
    
    # Step 3: List all assignments
    print("\nListing all assignments...")
    response = requests.get(assignment_url, headers=teacher_headers)
    if response.status_code != 200:
        print(f"Failed to list assignments: {response.text}")
        return
    
    assignments = response.json()
    print(f"Found {len(assignments)} assignments")
    
    # Step 4: Login as student
    student_token = login('student@example.com', 'studentpass')
    if not student_token:
        print("Student login failed, aborting student tests")
        return
    
    student_headers = {'Authorization': f'Token {student_token}'}
    
    # Step 5: Student views assignments
    print("\nStudent viewing assignments...")
    response = requests.get(assignment_url, headers=student_headers)
    if response.status_code != 200:
        print(f"Student failed to list assignments: {response.text}")
        return
    
    assignments = response.json()
    print(f"Student sees {len(assignments)} assignments")
    
    # Step 6: Student submits an assignment
    submission_url = f"{BASE_URL}assignments/{assignment_id}/submissions/"
    submission_data = {
        'text_content': 'Here is my completed French grammar exercise.'
    }
    
    print("\nStudent submitting assignment...")
    response = requests.post(submission_url, json=submission_data, headers=student_headers)
    if response.status_code != 201:
        print(f"Failed to submit assignment: {response.text}")
        print(f"Response status code: {response.status_code}")
    else:
        submission = response.json()
        submission_id = submission['id']
        print(f"Submission created successfully (ID: {submission_id})")
        pprint(submission)
        
        # Step 7: Teacher grades the submission
        print("\nTeacher grading submission...")
        feedback_url = f"{BASE_URL}submissions/{submission_id}/feedback/"
        feedback_data = {
            'comment': 'Good work, but you need to review the past tense.',
            'points_earned': 85
        }
        
        response = requests.post(feedback_url, json=feedback_data, headers=teacher_headers)
        if response.status_code != 201:
            print(f"Failed to provide feedback: {response.text}")
            print(f"Response status code: {response.status_code}")
        else:
            feedback = response.json()
            print("Feedback provided successfully:")
            pprint(feedback)
            
            # Step 8: Student views feedback
            print("\nStudent viewing feedback...")
            response = requests.get(feedback_url, headers=student_headers)
            if response.status_code != 200:
                print(f"Student failed to view feedback: {response.text}")
            else:
                feedback = response.json()
                print("Student sees feedback:")
                pprint(feedback)


if __name__ == "__main__":
    test_assignments_api()
