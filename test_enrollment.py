import requests
import json

def test_enrollment_api():
    # Base URL
    base_url = 'http://127.0.0.1:8000/api'
    
    # First, get a token through login
    print("\n1. Logging in...")
    login_data = {
        'username': 'student1',  # Make sure this student user exists
        'password': 'student123'
    }
    response = requests.post(f'{base_url}/auth/login/', json=login_data)
    print(f"Login Status Code: {response.status_code}")
    print(f"Login Response: {response.text}")
    
    if response.status_code != 200:
        print("Login failed!")
        return
        
    token = response.json()['access']
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # 2. List available courses (to get a course ID)
    print("\n2. Getting available courses...")
    response = requests.get(f'{base_url}/courses/', headers=headers)
    print(f"GET Courses Status Code: {response.status_code}")
    courses = response.json()
    if not courses:
        print("No courses available!")
        return
    
    course_id = courses[0]['id']  # Get the first course ID
    print(f"Selected course ID: {course_id}")

    # 3. Try to enroll in the course
    print("\n3. Attempting to enroll in the course...")
    enroll_data = {
        'course': course_id
    }
    response = requests.post(
        f'{base_url}/enrollments/enroll/',
        headers=headers,
        json=enroll_data
    )
    print(f"Enrollment Status Code: {response.status_code}")
    print(f"Enrollment Response: {response.text}")

    # 4. List my enrollments
    print("\n4. Getting my enrollments...")
    response = requests.get(f'{base_url}/enrollments/my-enrollments/', headers=headers)
    print(f"My Enrollments Status Code: {response.status_code}")
    print(f"My Enrollments Response: {response.text}")

    # 5. Try to access a video from the enrolled course
    print("\n5. Attempting to access course videos...")
    response = requests.get(f'{base_url}/courses/{course_id}/videos/', headers=headers)
    print(f"Video Access Status Code: {response.status_code}")
    print(f"Video Access Response: {response.text}")

if __name__ == '__main__':
    test_enrollment_api()
