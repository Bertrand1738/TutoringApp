# French Tutor Hub

A comprehensive platform for learning French with professional tutors. This project combines a Django backend with a RESTful API and a modern frontend with full API integration.

## Features

- User authentication with JWT
- Role-based access (Students and Teachers)
- Course management and discovery
- Video lessons and learning materials
- Student enrollments and progress tracking
- Teacher profiles and dashboards
- Reviews and rating system
- Live session scheduling
- Payment integration (planned)

## Tech Stack

### Backend
- Python 3.13
- Django 4.2
- Django REST Framework
- PostgreSQL (production) / SQLite (development)
- JWT Authentication

### Frontend
- HTML5 + CSS3 + JavaScript
- Bootstrap 5 
- API Integration with Fetch API
- Bootstrap Icons
- Responsive Design

## API Integration

The frontend integrates with the backend API through several JavaScript modules:

### API Service (`/static/js/api.js`)

Core service for making API requests with proper authentication and error handling:

- Manages JWT token storage and retrieval
- Handles authentication headers
- Provides common API endpoints as methods
- Offers error handling utilities

### Authentication (`/static/js/main.js`)
- Login/logout functionality
- Registration
- Token management
- Form submission handling

### Course Management (`/static/js/courses.js`)
- Course listing and filtering
- Course detail view
- Enrollment functionality
- Progress tracking

## API Endpoints

### Authentication
- POST `/api/token/` - Obtain JWT token
- POST `/api/token/refresh/` - Refresh JWT token
- POST `/api/accounts/register/` - Register new user

### Users
- GET `/api/accounts/profile/` - Get current user profile
- PATCH `/api/accounts/profile/` - Update user profile
- GET `/api/accounts/me/` - Get current user details

### Courses
- GET `/api/courses/` - List all courses
- GET `/api/courses/{id}/` - Get course details
- POST `/api/courses/` - Create new course (teachers only)
- PUT `/api/courses/{id}/` - Update course (teachers only)
- DELETE `/api/courses/{id}/` - Delete course (teachers only)

### Categories
- GET `/api/categories/` - List categories
- POST `/api/categories/` - Create category (admin)

### Enrollments
- GET `/api/enrollments/user/` - List user enrollments
- POST `/api/enrollments/` - Enroll in a course
- PATCH `/api/enrollments/{id}/` - Update enrollment progress
- DELETE `/api/enrollments/{id}/` - Unenroll from a course

### Videos
- GET `/api/videos/` - List videos
- POST `/api/videos/` - Add video (teachers)
- GET `/api/videos/{id}/` - Get video details

## Frontend Templates

- `base.html` - Base template with navigation and layout
- `login.html` - User login form with API integration
- `register.html` - User registration form
- `course_list.html` - Course listing with filters and search
- `course_detail.html` - Course details and enrollment
- `student_dashboard.html` - Student dashboard showing enrollments and progress
- `teacher_dashboard.html` - Teacher dashboard for course management

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Run development server:
   ```bash
   python manage.py runserver
   ```

## Environment Variables

You can customize the application by setting these environment variables:

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `DATABASE_URL` - Database connection string (for production)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

## Testing

Run tests with:
```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
