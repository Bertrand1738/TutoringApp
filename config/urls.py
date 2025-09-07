"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API URLs
    path("api/auth/", include("accounts.urls", namespace="accounts")),
    path("api/", include(("courses.urls", "courses"), namespace="courses")),
    path("api/payments/", include("payments.urls", namespace="payments")),
    path("api/enrollments/", include("enrollments.urls", namespace="enrollments")),
    path("api/live/", include("live_sessions.urls", namespace="live_sessions")),
    path("api/messaging/", include("messaging.urls", namespace="messaging")),
    path("api/debug/", include("debug.urls")),
    # reviews, badges will be added next
    
    # Frontend URLs
    path('', include('frontend.urls', namespace='frontend')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
