from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views
from . import content_views

app_name = 'courses'

# Main router
router = DefaultRouter()
router.register(r'categories', views.CourseCategoryViewSet, basename='category')
router.register(r'courses', views.CourseViewSet, basename='course')

# Nested routers for course content
courses_router = NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'videos', content_views.VideoViewSet, basename='course-video')
courses_router.register(r'pdfs', content_views.PDFViewSet, basename='course-pdf')
# Commented out due to missing models
# courses_router.register(r'assignments', content_views.AssignmentViewSet, basename='course-assignment')
# courses_router.register(r'quizzes', content_views.QuizViewSet, basename='course-quiz')

# Standalone content endpoints (for direct access with content ID)
router.register(r'videos', content_views.VideoViewSet, basename='video')
router.register(r'pdfs', content_views.PDFViewSet, basename='pdf')
# Commented out due to missing models
# router.register(r'assignments', content_views.AssignmentViewSet, basename='assignment')
# router.register(r'quizzes', content_views.QuizViewSet, basename='quiz')

urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
]
