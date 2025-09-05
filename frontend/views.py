from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings

from courses.models import Course, CourseCategory
from accounts.models import TeacherProfile

import requests
import json

def home(request):
    """Home page view with featured courses"""
    featured_courses = Course.objects.filter(published=True).order_by('-created_at')[:6]
    categories = CourseCategory.objects.all()
    
    return render(request, 'frontend/home.html', {
        'featured_courses': featured_courses,
        'categories': categories
    })

def login_view(request):
    """Login view - handles both regular form submission and API requests"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Check if token is provided in POST data or Authorization header
    token = request.POST.get('token') or request.GET.get('token')
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    
    # If token exists, store it in session
    if token:
        logger.debug(f"Login view received token")
        request.session['access_token'] = token
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if this is coming from the API (JSON content type)
        content_type = request.META.get('CONTENT_TYPE', '')
        if 'application/json' in content_type:
            import json
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            except json.JSONDecodeError:
                return JsonResponse({'detail': 'Invalid JSON'}, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in using Django's session framework
            login(request, user)
            logger.debug(f"User {username} authenticated successfully")
            
            # If this is an API request, return JWT token
            if 'application/json' in content_type:
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                # Store token in session for future use
                request.session['access_token'] = access_token
                logger.debug(f"Stored access token in session for user {username}")
                
                return JsonResponse({
                    'access': access_token,
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                })
            
            # For regular form submission, redirect to dashboard
            messages.success(request, f'Welcome back, {user.username}!')
            next_page = request.GET.get('next', reverse('frontend:dashboard'))
            return redirect(next_page)
        else:
            if 'application/json' in content_type:
                logger.warning(f"Failed login attempt for username: {username}")
                return JsonResponse({'detail': 'Invalid username or password'}, status=401)
            
            logger.warning(f"Failed form login attempt for username: {username}")
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'frontend/login.html')

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Validate form data
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'frontend/register.html')
        
        # Create a payload for the API
        data = {
            'username': username,
            'email': email,
            'password': password
        }
        
        try:
            # Make a request to the API
            response = requests.post(
                f'{request.build_absolute_uri("/").rstrip("/")}/api/auth/register/',
                json=data
            )
            
            if response.status_code == 201:  # Created
                # Log the user in
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Registration successful! Welcome to French Tutor Hub.')
                    return redirect('frontend:dashboard')
            else:
                # Handle API errors
                error_data = response.json()
                for field, errors in error_data.items():
                    if isinstance(errors, list):
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                    else:
                        messages.error(request, f"{field}: {errors}")
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'frontend/register.html')

def logout_view(request):
    """Log out the user"""
    # Clear any token from session
    if 'access_token' in request.session:
        del request.session['access_token']
    
    # Clear any token from cookies
    response = redirect('frontend:login')
    if 'access_token' in request.COOKIES:
        response.delete_cookie('access_token')
    
    # Log the user out
    logout(request)
    
    # Add a message
    messages.info(request, 'You have been logged out successfully.')
    
    # Redirect to login page
    return response

@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    
    # Check if user is a teacher
    is_teacher = hasattr(user, 'teacher_profile')
    
    if request.method == 'POST':
        # Update profile logic here
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('frontend:profile')
    
    return render(request, 'frontend/profile.html', {
        'user': user,
        'is_teacher': is_teacher
    })

def course_list(request):
    """List all courses with filtering options"""
    courses = Course.objects.filter(published=True)
    categories = CourseCategory.objects.all()
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        courses = courses.filter(category_id=category_id)
    
    # Filter by search query
    search_query = request.GET.get('q')
    if search_query:
        courses = courses.filter(title__icontains=search_query)
    
    return render(request, 'frontend/course_list.html', {
        'courses': courses,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query
    })

def course_detail(request, course_id):
    """Course detail view"""
    course = get_object_or_404(Course, id=course_id, published=True)
    
    # Check if user is enrolled
    is_enrolled = False
    if request.user.is_authenticated:
        # This would need to be updated based on your enrollment model
        # is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        pass
    
    return render(request, 'frontend/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled
    })

@login_required
def enroll_course(request, course_id):
    """Enroll in a course"""
    course = get_object_or_404(Course, id=course_id, published=True)
    
    if request.method == 'POST':
        try:
            # Make API request to create enrollment
            response = requests.post(
                f'{request.build_absolute_uri("/").rstrip("/")}/api/enrollments/enroll/',
                json={'course_id': course_id},
                headers={'Authorization': f'Bearer {request.session.get("access_token")}'}
            )
            
            if response.status_code == 201:
                messages.success(request, f'Successfully enrolled in {course.title}')
                return redirect('frontend:dashboard_enrollments')
            else:
                error_data = response.json()
                messages.error(request, f'Enrollment failed: {error_data.get("detail", "Unknown error")}')
        except Exception as e:
            messages.error(request, f'Enrollment failed: {str(e)}')
    
    return redirect('frontend:course_detail', course_id=course_id)

@login_required
def dashboard(request):
    """User dashboard view"""
    import logging
    import jwt
    from django.conf import settings
    from django.contrib.auth import get_user_model
    
    logger = logging.getLogger(__name__)
    User = get_user_model()
    
    # Check for token in various places and use it to identify user
    token = None
    
    # First, check for token in query parameters (from redirect)
    if 'token' in request.GET:
        token = request.GET.get('token')
        logger.debug("Found token in query parameters")
        # Store in session for future requests
        request.session['access_token'] = token
    
    # Then check Authorization header
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            logger.debug("Found token in Authorization header")
            request.session['access_token'] = token
    
    # Check in session
    if not token and 'access_token' in request.session:
        token = request.session['access_token']
        logger.debug("Found token in session")
    
    # Check cookies
    if not token and 'access_token' in request.COOKIES:
        token = request.COOKIES['access_token']
        logger.debug("Found token in cookies")
        request.session['access_token'] = token
    
    # If we have a token but user is not authenticated via session yet
    if token and not request.user.is_authenticated:
        try:
            # Decode token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if user_id:
                # Get user from database
                try:
                    user = User.objects.get(id=user_id)
                    # Login user to create session
                    login(request, user)
                    logger.debug(f"Authenticated user {user.username} from token")
                except User.DoesNotExist:
                    logger.warning(f"User ID {user_id} from token not found")
        except Exception as e:
            logger.error(f"Error authenticating with token: {str(e)}")
    
    # Proceed with dashboard view logic
    user = request.user
    
    # Get the active tab from query parameter
    active_tab = request.GET.get('tab', 'dashboard')
    
    # Check if user is a teacher
    is_teacher = hasattr(user, 'teacher_profile') or user.groups.filter(name='teacher').exists()
    
    # Common context data
    context = {
        'active_tab': active_tab,
    }
    
    if is_teacher:
        # Teacher dashboard
        # We're using a simple query to retrieve courses
        # In a real app, you might want to use a more complex model relationship
        courses = Course.objects.filter(published=True)
        if hasattr(user, 'teacher_profile'):
            courses = courses.filter(teacher=user.teacher_profile)
        
        # Add teacher-specific data to context
        context.update({
            'courses': courses,
            'total_students': 0,  # This would come from your enrollment model
            'upcoming_sessions': 0,  # This would come from your sessions model
            'total_earnings': 0,  # This would come from your payments model
        })
        
        return render(request, 'frontend/teacher_dashboard.html', context)
    else:
        # Student dashboard
        # You would need to adjust this based on your enrollment model
        # enrollments = Enrollment.objects.filter(student=user)
        enrollments = []
        
        # Add student-specific data to context
        context.update({
            'enrollments': enrollments,
            'completed_courses': 0,  # This would be calculated from your enrollment model
            'upcoming_sessions': 0,  # This would come from your sessions model
        })
        
        return render(request, 'frontend/student_dashboard.html', context)

@login_required
def dashboard_enrollments(request):
    """View enrolled courses"""
    user = request.user
    
    # You would need to adjust this based on your enrollment model
    # enrollments = Enrollment.objects.filter(student=user)
    enrollments = []
    
    return render(request, 'frontend/dashboard_enrollments.html', {
        'enrollments': enrollments
    })
