from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('enroll/', views.EnrollCourseView.as_view(), name='enroll-course'),
    path('my-enrollments/', views.MyEnrollmentsView.as_view(), name='my-enrollments'),
]
