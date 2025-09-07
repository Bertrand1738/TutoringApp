from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from courses.models import Course
from payments.models import Order, Payment
from enrollments.models import Enrollment
import requests
import json

@login_required
def store_view(request):
    """
    Display the content store with all purchasable content types
    """
    from courses.models import Course, Video
    from live_sessions.models import LiveSession
    
    # Get all published courses
    courses = Course.objects.filter(published=True, is_purchasable=True)
    
    # Get all individual videos available for purchase
    videos = Video.objects.filter(published=True, is_purchasable=True)
    
    # Get upcoming live sessions that can be booked
    live_sessions = LiveSession.objects.filter(is_public=True, is_available=True)
    
    # Combine all content into a single list for the template
    contents = []
    
    # Add courses
    for course in courses:
        contents.append({
            'id': course.id,
            'type': 'course',
            'title': course.title,
            'description': course.description,
            'price': course.price,
            'image_url': course.image.url if course.image else None,
            'instructor_name': course.teacher.user.get_full_name() if course.teacher else 'Unknown',
            'instructor_image': course.teacher.profile_picture.url if course.teacher and course.teacher.profile_picture else None,
            'rating': 4,  # Placeholder, would come from reviews
            'reviews_count': 10,  # Placeholder
            'level': course.level if hasattr(course, 'level') else 'beginner'
        })
    
    # Add videos
    for video in videos:
        contents.append({
            'id': video.id,
            'type': 'video',
            'title': video.title,
            'description': video.description,
            'price': video.price,
            'image_url': video.thumbnail.url if hasattr(video, 'thumbnail') and video.thumbnail else None,
            'instructor_name': video.teacher.user.get_full_name() if hasattr(video, 'teacher') and video.teacher else 'Unknown',
            'instructor_image': video.teacher.profile_picture.url if hasattr(video, 'teacher') and video.teacher and video.teacher.profile_picture else None,
            'rating': 4,  # Placeholder
            'reviews_count': 5,  # Placeholder
            'level': video.level if hasattr(video, 'level') else 'beginner',
            'duration': video.duration if hasattr(video, 'duration') else 30  # Duration in minutes
        })
    
    # Add live sessions
    for session in live_sessions:
        contents.append({
            'id': session.id,
            'type': 'live',
            'title': f"Live Session: {session.title or 'Untitled'}",
            'description': session.description or "One-on-one live session with a tutor",
            'price': session.price,
            'image_url': None,
            'instructor_name': session.teacher.user.get_full_name() if session.teacher else 'Unknown',
            'instructor_image': session.teacher.profile_picture.url if session.teacher and session.teacher.profile_picture else None,
            'rating': 5,  # Placeholder
            'reviews_count': 3,  # Placeholder
            'level': 'any',
            'date': session.start_time if hasattr(session, 'start_time') else None
        })
    
    return render(request, 'frontend/store.html', {
        'contents': contents
    })

@login_required
def checkout_view(request, order_id):
    """
    Display checkout page for a specific order
    """
    # Get the order
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Make sure order is in draft status
    if order.status != 'draft':
        messages.warning(request, 'This order is already in progress or completed.')
        return redirect('frontend:dashboard')
    
    # Context data for the template
    context = {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY
    }
    
    return render(request, 'frontend/checkout.html', context)

@login_required
def payment_success_view(request, order_id):
    """
    Display payment success page
    """
    # Get the order with its related items and payment
    order = get_object_or_404(
        Order.objects.select_related('payment').prefetch_related('items__content_type'),
        id=order_id, 
        user=request.user,
        status='completed'  # Only show if payment was completed
    )
    
    return render(request, 'frontend/payment_success.html', {
        'order': order,
        'user': request.user
    })

@login_required
def bank_transfer_view(request, order_id):
    """
    Display bank transfer instructions
    """
    # Get the order
    order = get_object_or_404(
        Order.objects.select_related('payment').prefetch_related('items'),
        id=order_id, 
        user=request.user
    )
    
    # Make sure payment method is bank_transfer
    if not order.payment or order.payment.payment_method != 'bank_transfer':
        messages.warning(request, 'This order is not configured for bank transfer.')
        return redirect('frontend:checkout', order_id=order_id)
    
    return render(request, 'frontend/bank_transfer.html', {
        'order': order
    })

@login_required
def video_detail_view(request, video_id):
    """
    Display video details and purchase options
    """
    from courses.models import Video
    
    # Get the video
    video = get_object_or_404(Video, id=video_id, published=True)
    
    # Check if user has access
    has_access = False
    
    if request.user.is_authenticated:
        # Check if user has purchased this video
        # This uses the new content-type based enrollment model
        video_content_type = ContentType.objects.get_for_model(Video)
        has_access = Enrollment.objects.filter(
            student=request.user,
            content_type=video_content_type,
            object_id=video.id,
            status='active'
        ).exists()
    
    return render(request, 'frontend/video_detail.html', {
        'video': video,
        'has_access': has_access
    })

@login_required
def session_detail_view(request, session_id):
    """
    Display live session details and booking options
    """
    from live_sessions.models import LiveSession
    
    # Get the session
    session = get_object_or_404(LiveSession, id=session_id, is_public=True)
    
    # Check if user has already booked this session
    is_booked = False
    if request.user.is_authenticated:
        is_booked = session.student_id == request.user.id
    
    return render(request, 'frontend/session_detail.html', {
        'session': session,
        'is_booked': is_booked
    })

@login_required
def add_to_cart_api(request):
    """
    API endpoint to add item to cart
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        
        if not content_type or not object_id:
            return JsonResponse({'error': 'Missing content_type or object_id'}, status=400)
        
        # Create a draft order with one item
        response = requests.post(
            f'{request.build_absolute_uri("/").rstrip("/")}/api/payments/orders/',
            json={
                'items': [{
                    'content_type': content_type,
                    'object_id': int(object_id),
                    'quantity': 1
                }]
            },
            headers={'Authorization': f'Bearer {request.session.get("access_token")}'}
        )
        
        if response.status_code == 201:
            order_data = response.json()
            return JsonResponse({
                'success': True,
                'order_id': order_data['id'],
                'message': 'Item added to cart successfully!'
            })
        else:
            error_data = response.json()
            return JsonResponse({
                'success': False,
                'error': error_data.get('detail', 'Failed to add item to cart')
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
