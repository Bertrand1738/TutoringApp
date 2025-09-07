from django.urls import path
from . import views
from . import views_store

app_name = 'frontend'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Test route for navbar debugging
    path('test-navbar/', views.test_navbar, name='test_navbar'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    
    # Teachers
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/enrollments/', views.dashboard_enrollments, name='dashboard_enrollments'),
    path('dashboard/schedule/', views.dashboard_schedule, name='dashboard_schedule'),
    path('dashboard/messages/', views.dashboard_messages, name='dashboard_messages'),
    
    # Session booking
    path('book-session/', views.book_session_view, name='book_session'),
    path('create-session/', views.create_session, name='create_session'),
    
    # Store and checkout
    path('store/', views_store.store_view, name='store'),
    path('checkout/<int:order_id>/', views_store.checkout_view, name='checkout'),
    path('checkout/success/<int:order_id>/', views_store.payment_success_view, name='payment_success'),
    path('checkout/bank-transfer/<int:order_id>/', views_store.bank_transfer_view, name='bank_transfer'),
    
    # Individual content
    path('video/<int:video_id>/', views_store.video_detail_view, name='video_detail'),
    path('live-session/<int:session_id>/', views_store.session_detail_view, name='session_detail'),
    
    # Cart API
    path('api/add-to-cart/', views_store.add_to_cart_api, name='add_to_cart_api'),
]
