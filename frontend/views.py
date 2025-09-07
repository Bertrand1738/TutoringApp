from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Avg, Count, Q
from django.utils import timezone

from courses.models import Course, CourseCategory
from accounts.models import TeacherProfile, StudentProfile
from live_sessions.models import TimeSlot

# We'll create the Review model later
# from reviews.models import Review

import requests
import json

def home(request):
    """Home page view with featured courses and teachers"""
    featured_courses = Course.objects.filter(published=True).order_by('-created_at')[:6]
    categories = CourseCategory.objects.all()
    
    # Get featured teachers (high-rated and with courses)
    featured_teachers = TeacherProfile.objects.filter(
        verification_status=TeacherProfile.VerificationStatus.VERIFIED
    ).order_by('-avg_rating')[:4]
    
    # For each featured teacher, get their courses
    for teacher in featured_teachers:
        teacher.courses_count = Course.objects.filter(
            teacher=teacher, 
            published=True
        ).count()
        
        teacher.students_count = Course.objects.filter(
            teacher=teacher, 
            published=True, 
            enrolled_students__isnull=False
        ).aggregate(total=Count('enrolled_students', distinct=True))['total'] or 0
        
        # Get current availability
        teacher.available_slots = TimeSlot.objects.filter(
            teacher=teacher, 
            is_available=True,
            start_time__gte=timezone.now()
        ).count()
        
        # Ensure profile_picture exists
        if not hasattr(teacher.user, 'student_profile') or not teacher.user.student_profile:
            # Create student profile if it doesn't exist
            from accounts.models import StudentProfile
            student_profile, created = StudentProfile.objects.get_or_create(user=teacher.user)
    
    # Add a debug flag to check template issues
    debug_mode = request.GET.get('debug', 'false') == 'true'
    
    return render(request, 'frontend/home.html', {
        'featured_courses': featured_courses,
        'categories': categories,
        'featured_teachers': featured_teachers,
        'debug_mode': debug_mode
    })
    
def test_navbar(request):
    """Simple test view to check navbar rendering"""
    return render(request, 'test_navbar.html')

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
    
    # Pass next parameter to template if it exists
    next_url = request.GET.get('next', '/dashboard/')
    return render(request, 'frontend/login.html', {
        'next': next_url,
        'redirect_field_name': 'next'
    })

def register_view(request):
    """User registration view"""
    import logging
    import json
    import traceback
    
    logger = logging.getLogger(__name__)
    
    # Function to get client IP for logging
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    if request.method == 'POST':
        # Log the request information
        logger.info(f"Registration request received from IP: {get_client_ip(request)}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Method: {request.method}")
        
        # Check if request is JSON (from JS client) or form data
        content_type = request.content_type if hasattr(request, 'content_type') else request.META.get('CONTENT_TYPE', '')
        is_json_request = 'application/json' in content_type
        
        if is_json_request:
            # Parse JSON data
            try:
                body_unicode = request.body.decode('utf-8')
                body_data = json.loads(body_unicode)
                logger.info(f"JSON request data: {body_data.keys()}")
                
                username = body_data.get('username')
                email = body_data.get('email')
                password = body_data.get('password')
                first_name = body_data.get('first_name')
                last_name = body_data.get('last_name')
                role = body_data.get('role', 'student')
                password2 = password  # In JSON requests, we don't have a confirm password
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return JsonResponse({"error": "Invalid JSON"}, status=400)
        else:
            # Get form data
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            role = request.POST.get('user_type', 'student')
        
        # Log the collected data (except password)
        logger.info(f"Registration data - Username: {username}, Email: {email}, Role: {role}")
        
        # Validate form data
        if password != password2:
            logger.warning("Passwords do not match")
            if is_json_request:
                return JsonResponse({"error": "Passwords do not match"}, status=400)
            messages.error(request, 'Passwords do not match.')
            return render(request, 'frontend/register.html')
        
        # Create a payload for the API
        data = {
            'username': username,
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'role': role
        }
        
        try:
            # Make a request to the API
            logger.info(f"Making API request to register user: {username}")
            
            api_url = f'{request.build_absolute_uri("/").rstrip("/")}/api/auth/register/'
            logger.info(f"API URL: {api_url}")
            
            # Make the request with detailed logging
            try:
                response = requests.post(api_url, json=data)
                logger.info(f"API response status: {response.status_code}")
                logger.info(f"API response headers: {dict(response.headers)}")
                
                try:
                    response_data = response.json()
                    # Don't log any password data in response
                    if isinstance(response_data, dict) and 'password' in response_data:
                        response_data['password'] = '******'
                    logger.info(f"API response data: {response_data}")
                except Exception as e:
                    logger.warning(f"Could not parse JSON response: {e}")
                    logger.info(f"API response text: {response.text[:500]}...")  # Log first 500 chars only
                
            except requests.RequestException as e:
                logger.error(f"API request exception: {e}")
                raise
            
            if response.status_code == 201:  # Created
                logger.info(f"Registration successful for: {username}")
                
                # Log the user in
                user = authenticate(request, username=username, password=password)
                logger.info(f"Authentication result for {username}: {'Success' if user else 'Failed'}")
                
                if user is not None:
                    login(request, user)
                    logger.info(f"User {username} logged in via Django session")
                    
                    # Obtain token for API requests
                    try:
                        token_response = requests.post(
                            f'{request.build_absolute_uri("/").rstrip("/")}/api/auth/token/',
                            json={
                                'username': username,
                                'password': password
                            }
                        )
                        
                        if token_response.status_code == 200:
                            token_data = token_response.json()
                            # Store token in session
                            request.session['access_token'] = token_data.get('access')
                            logger.info(f"Token obtained for new user: {username}")
                            
                            # Also set the token as a cookie for JavaScript access
                            response = redirect('frontend:dashboard')
                            response.set_cookie(
                                'access_token',
                                token_data.get('access'),
                                max_age=60*60*24,  # 1 day
                                httponly=False,    # Allow JavaScript access
                                samesite='Lax'
                            )
                            
                            # Add success message
                            messages.success(request, 'Registration successful! Welcome to French Tutor Hub.')
                            
                            # Check if JSON request
                            if is_json_request:
                                return JsonResponse({
                                    'success': True,
                                    'message': 'Registration successful!',
                                    'redirect': reverse('frontend:dashboard'),
                                    'token': token_data
                                })
                                
                            return response
                        else:
                            logger.error(f"Token request failed: {token_response.status_code} - {token_response.text}")
                    except Exception as e:
                        logger.error(f"Error obtaining token after registration: {str(e)}")
                        logger.error(traceback.format_exc())
                    
                    # If we get here, we still logged the user in but couldn't get a token
                    # Redirect to dashboard anyway
                    messages.success(request, 'Registration successful! Welcome to French Tutor Hub.')
                    
                    if is_json_request:
                        return JsonResponse({
                            'success': True,
                            'message': 'Registration successful!',
                            'redirect': reverse('frontend:dashboard')
                        })
                        
                    return redirect('frontend:dashboard')
                else:
                    logger.warning(f"Failed to authenticate new user: {username} after registration")
                    messages.warning(request, 'Registration successful! Please log in with your new account.')
                    
                    if is_json_request:
                        return JsonResponse({
                            'success': True,
                            'message': 'Registration successful, but automatic login failed. Please log in.',
                            'redirect': reverse('frontend:login')
                        })
                        
                    return redirect('frontend:login')
            else:
                # Handle API errors
                logger.error(f"Registration API error for {username}: {response.status_code}")
                try:
                    error_data = response.json()
                    error_messages = []
                    
                    for field, errors in error_data.items():
                        if isinstance(errors, list):
                            for error in errors:
                                messages.error(request, f"{field}: {error}")
                                error_messages.append(f"{field}: {error}")
                        else:
                            messages.error(request, f"{field}: {errors}")
                            error_messages.append(f"{field}: {errors}")
                            
                    if is_json_request:
                        return JsonResponse({
                            'success': False,
                            'errors': error_data,
                            'message': 'Registration failed'
                        }, status=400)
                        
                except Exception as parse_error:
                    logger.error(f"Error parsing API response: {str(parse_error)}")
                    messages.error(request, f"Registration failed: {response.text}")
                    
                    if is_json_request:
                        return JsonResponse({
                            'success': False,
                            'message': f'Registration failed: {response.text}'
                        }, status=400)
        except Exception as e:
            logger.error(f"Registration exception for {username}: {str(e)}")
            logger.error(traceback.format_exc())  # Log the full traceback
            messages.error(request, f'Registration failed: {str(e)}')
            
            if is_json_request:
                return JsonResponse({
                    'success': False,
                    'message': f'Registration failed: {str(e)}'
                }, status=500)
    
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
        # Check enrollment status from the enrollments model
        from enrollments.models import Enrollment
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    
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
        from enrollments.models import Enrollment
        from live_sessions.models import LiveSession
        import datetime
        
        # Get active enrollments
        enrollments = Enrollment.objects.filter(student=user, status='active').select_related(
            'course', 'course__teacher', 'content_type'
        ).prefetch_related('video_details')
        
        # Calculate completed courses
        completed_courses = 0
        for enrollment in enrollments:
            if enrollment.course:
                progress = enrollment.course.calculate_student_progress_percentage(user)
                if progress >= 100:
                    completed_courses += 1
                
        # Get upcoming sessions
        now = datetime.datetime.now()
        upcoming_sessions = LiveSession.objects.filter(
            student=user,
            time_slot__start_time__gt=now,
            status__in=['scheduled', 'confirmed']
        ).select_related('course', 'time_slot').order_by('time_slot__start_time')[:5]
        
        # Add student-specific data to context
        context.update({
            'enrollments': enrollments,
            'completed_courses': completed_courses,
            'upcoming_sessions': upcoming_sessions,
            'now': datetime.datetime.now(),
        })
        
        return render(request, 'frontend/student_dashboard.html', context)

@login_required
def dashboard_enrollments(request):
    """View enrolled courses"""
    user = request.user
    
    # Get enrollments from the enrollment model
    from enrollments.models import Enrollment
    from django.utils import timezone
    
    # Get all enrollments for the user
    all_enrollments = Enrollment.objects.filter(student=user).select_related(
        'course', 'course__teacher', 'content_type'
    ).prefetch_related('video_details').order_by('-enrolled_at')
    
    # Process enrollments to include progress
    enrollments = []
    for enrollment in all_enrollments:
        enrollment_data = {
            'id': enrollment.id,
            'content_name': enrollment.get_content_name(),
            'content_type': enrollment.content_type.model if enrollment.content_type else 'course',
            'enrolled_at': enrollment.enrolled_at,
            'is_active': enrollment.is_active,
            'last_activity': enrollment.last_accessed or enrollment.enrolled_at,
            'progress': 0
        }
        
        # Add content-specific data
        if enrollment.course:
            enrollment_data['course'] = enrollment.course
            enrollment_data['progress'] = enrollment.course.calculate_student_progress_percentage(user)
        elif enrollment.content_type and enrollment.content_type.model == 'video':
            enrollment_data['video'] = enrollment.content_object
            enrollment_data['progress'] = 100 if hasattr(enrollment, 'video_details') and enrollment.video_details.views_count > 0 else 0
        elif enrollment.content_type and enrollment.content_type.model == 'livesession':
            enrollment_data['session'] = enrollment.content_object
            # Session progress is based on whether it's completed or not
            from django.utils import timezone
            enrollment_data['progress'] = 100 if enrollment.content_object.end_time < timezone.now() else 0
            
        enrollments.append(enrollment_data)
    
    return render(request, 'frontend/dashboard_enrollments.html', {
        'enrollments': enrollments,
        'now': timezone.now(),
        'standalone': True,  # Mark as standalone when accessed directly via URL
        'active_tab': 'courses'  # Set active tab for sidebar highlighting
    })

@login_required
def dashboard_messages(request):
    """View messages dashboard"""
    user = request.user
    
    # We'll inject the current user ID into the template context
    # The actual conversations will be loaded via AJAX/fetch
    
    return render(request, 'frontend/dashboard_messages.html', {
        'active_tab': 'messages',
        'current_user_id': user.id
    })

@login_required
def dashboard_schedule(request):
    """View and manage scheduled sessions"""
    user = request.user
    
    from live_sessions.models import LiveSession
    from django.utils import timezone
    
    # Get upcoming sessions
    now = timezone.now()
    upcoming_sessions = LiveSession.objects.filter(
        student=user,
        time_slot__start_time__gt=now,
        status__in=['scheduled', 'confirmed']
    ).select_related('course', 'time_slot', 'course__teacher').order_by('time_slot__start_time')
    
    # Check if user is a teacher
    is_teacher = hasattr(user, 'teacher_profile')
    
    return render(request, 'frontend/dashboard_schedule.html', {
        'upcoming_sessions': upcoming_sessions,
        'is_teacher': is_teacher
    })

@login_required
def book_session_view(request):
    """View available time slots and book a session"""
    user = request.user
    
    from enrollments.models import Enrollment
    from live_sessions.models import TimeSlot
    from django.utils import timezone
    
    # Get student's enrolled courses
    enrollments = Enrollment.objects.filter(
        student=user, 
        status='active'
    ).select_related('course', 'course__teacher')
    
    # Get available time slots for the next 30 days
    now = timezone.now()
    thirty_days_later = now + timezone.timedelta(days=30)
    
    # If a specific teacher is selected
    teacher_id = request.GET.get('teacher')
    available_slots = TimeSlot.objects.filter(
        is_available=True,
        start_time__gt=now,
        start_time__lt=thirty_days_later
    ).select_related('teacher', 'teacher__user').order_by('start_time')
    
    if teacher_id:
        available_slots = available_slots.filter(teacher_id=teacher_id)
    
    return render(request, 'frontend/book_session.html', {
        'enrollments': enrollments,
        'available_slots': available_slots,
    })

@login_required
def create_session(request):
    """Create a new session booking"""
    if request.method != 'POST':
        return redirect('frontend:teacher_list')
    
    course_id = request.POST.get('course_id')
    time_slot_id = request.POST.get('time_slot_id')
    teacher_id = request.POST.get('teacher_id')
    student_notes = request.POST.get('notes', '')
    
    if not course_id or not time_slot_id:
        messages.error(request, 'Please select both a course and a time slot.')
        if teacher_id:
            return redirect('frontend:teacher_detail', teacher_id=teacher_id)
        else:
            return redirect('frontend:teacher_list')
    
    try:
        # Make API request to create session
        response = requests.post(
            f'{request.build_absolute_uri("/").rstrip("/")}/api/live/sessions/',
            json={
                'course_id': int(course_id),
                'time_slot_id': int(time_slot_id),
                'student_notes': student_notes,
                'meeting_platform': 'zoom'  # Default to Zoom
            },
            headers={'Authorization': f'Bearer {request.session.get("access_token")}'}
        )
        
        if response.status_code == 201:
            session_data = response.json()
            messages.success(request, 'Session booked successfully!')
            return redirect('frontend:dashboard_schedule')
        else:
            error_data = response.json()
            messages.error(request, f'Booking failed: {error_data.get("detail", "Unknown error")}')
    except Exception as e:
        messages.error(request, f'Booking failed: {str(e)}')
    
def teacher_list(request):
    """View to display all teachers with filtering options"""
    teachers = TeacherProfile.objects.filter(verification_status=TeacherProfile.VerificationStatus.VERIFIED)
    
    # Get query parameters for filtering
    search_query = request.GET.get('q', '')
    language_level = request.GET.get('level', '')
    min_rating = request.GET.get('rating', '')
    subject = request.GET.get('subject', '')
    
    # Apply filters
    if search_query:
        teachers = teachers.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) |
            Q(bio__icontains=search_query)
        )
    
    # Get courses for each teacher
    for teacher in teachers:
        teacher.courses_count = Course.objects.filter(teacher=teacher, published=True).count()
        teacher.students_count = Course.objects.filter(
            teacher=teacher, 
            published=True, 
            enrolled_students__isnull=False
        ).aggregate(total=Count('enrolled_students', distinct=True))['total'] or 0
        
        # Get current availability
        from django.utils import timezone
        teacher.available_slots = TimeSlot.objects.filter(
            teacher=teacher, 
            is_available=True,
            start_time__gte=timezone.now()
        ).count()
        
        # Ensure student profile exists
        if not hasattr(teacher.user, 'student_profile') or not teacher.user.student_profile:
            from accounts.models import StudentProfile
            student_profile, created = StudentProfile.objects.get_or_create(user=teacher.user)
    
    # Get popular courses for sidebar
    popular_courses = Course.objects.filter(published=True).annotate(
        students_count=Count('enrolled_students')
    ).order_by('-students_count')[:5]
    
    # Get course categories for filtering sidebar
    categories = CourseCategory.objects.all()
    
    return render(request, 'frontend/teacher_list.html', {
        'teachers': teachers,
        'popular_courses': popular_courses,
        'categories': categories,
        'search_query': search_query,
        'language_level': language_level,
        'min_rating': min_rating,
        'subject': subject,
    })
    
def teacher_detail(request, teacher_id):
    """View for detailed teacher profile and booking options"""
    teacher = get_object_or_404(TeacherProfile, id=teacher_id, verification_status=TeacherProfile.VerificationStatus.VERIFIED)
    
    # Ensure student profile exists
    if not hasattr(teacher.user, 'student_profile') or not teacher.user.student_profile:
        from accounts.models import StudentProfile
        student_profile, created = StudentProfile.objects.get_or_create(user=teacher.user)
    
    # Get teacher's courses
    courses = Course.objects.filter(teacher=teacher, published=True)
    
    # Temporarily use dummy reviews until we create the Review model
    reviews = []
    review_stats = {
        'count': 0,
        'avg_rating': teacher.avg_rating or 0,
    }
    
    # Get teacher's available time slots
    from django.utils import timezone
    available_slots = TimeSlot.objects.filter(
        teacher=teacher, 
        is_available=True,
        start_time__gte=timezone.now()
    ).order_by('start_time')
    
    # Group slots by day for easier display
    from collections import defaultdict
    from datetime import datetime, timedelta
    
    # Get next 14 days
    today = timezone.now().date()
    days = [today + timedelta(days=i) for i in range(14)]
    
    # Initialize slots by day dictionary
    slots_by_day = defaultdict(list)
    
    # Group slots by day
    for slot in available_slots:
        slot_date = slot.start_time.date()
        if slot_date in days:
            slots_by_day[slot_date].append(slot)
    
    return render(request, 'frontend/teacher_detail.html', {
        'teacher': teacher,
        'courses': courses,
        'reviews': reviews,
        'review_stats': review_stats,
        'days': days,
        'slots_by_day': dict(slots_by_day),  # Convert defaultdict to regular dict for template
        'today': today,
    })
