from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'courses'

router = DefaultRouter()
router.register(r"categories", views.CourseCategoryViewSet, basename="category")
router.register(r"courses", views.CourseViewSet, basename="course")
router.register(r"videos", views.VideoViewSet, basename="video")

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
]
