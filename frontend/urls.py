from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/enrollments/', views.dashboard_enrollments, name='dashboard_enrollments'),
]
