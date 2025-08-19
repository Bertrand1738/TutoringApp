# French Tutor Hub

A Django REST API for an online French tutoring platform.

## Features

- User authentication (JWT)
- Role-based access (Students and Teachers)
- Course management
- Video lessons
- Student enrollments
- Teacher profiles
- Reviews system
- Payment integration (planned)

## Tech Stack

- Python 3.13
- Django 4.2
- Django REST Framework
- PostgreSQL (planned)
- JWT Authentication

## API Endpoints

### Authentication
- POST `/api/auth/register/` - Register new user
- POST `/api/auth/login/` - Get JWT token
- POST `/api/auth/token/refresh/` - Refresh JWT token
- GET `/api/auth/me/` - Get current user

### Courses
- GET `/api/categories/` - List categories
- POST `/api/categories/` - Create category (admin)
- GET `/api/courses/` - List courses
- POST `/api/courses/` - Create course (teachers)
- GET `/api/videos/` - List videos
- POST `/api/videos/` - Add video (teachers)

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
5. Run development server:
   ```bash
   python manage.py runserver
   ```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
