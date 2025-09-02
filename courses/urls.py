from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views
from . import content_views
from . import progress_views
from . import assignment_views

app_name = 'courses'

# Main router
router = DefaultRouter()
router.register(r'categories', views.CourseCategoryViewSet, basename='category')
router.register(r'courses', views.CourseViewSet, basename='course')

# Standalone content endpoints (for direct access with content ID)
router.register(r'videos', content_views.VideoViewSet, basename='video')
router.register(r'pdfs', content_views.PDFViewSet, basename='pdf')
router.register(r'assignments', assignment_views.AssignmentViewSet, basename='assignment')
# Commented out due to missing models
# router.register(r'quizzes', content_views.QuizViewSet, basename='quiz')

# Progress tracking
router.register(r'content-progress', progress_views.ContentProgressViewSet, basename='content-progress')
router.register(r'course-progress', progress_views.CourseProgressViewSet, basename='course-progress')

# Submissions and feedback
router.register(r'submissions', assignment_views.SubmissionViewSet, basename='submission')
router.register(r'feedback', assignment_views.FeedbackViewSet, basename='feedback')

# Nested routers for course content
courses_router = NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'videos', content_views.VideoViewSet, basename='course-video')
courses_router.register(r'pdfs', content_views.PDFViewSet, basename='course-pdf')
courses_router.register(r'assignments', assignment_views.AssignmentViewSet, basename='course-assignment')
# Commented out due to missing models
# courses_router.register(r'quizzes', content_views.QuizViewSet, basename='course-quiz')

# Nested router for assignments -> submissions
assignments_router = NestedDefaultRouter(router, r'assignments', lookup='assignment')
assignments_router.register(r'submissions', assignment_views.SubmissionViewSet, basename='assignment-submission')

# Nested router for submissions -> feedback
submissions_router = NestedDefaultRouter(router, r'submissions', lookup='submission')
submissions_router.register(r'feedback', assignment_views.FeedbackViewSet, basename='submission-feedback')

urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
    path('', include(assignments_router.urls)),
    path('', include(submissions_router.urls)),
]
