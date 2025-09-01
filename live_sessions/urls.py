from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'live_sessions'

router = DefaultRouter()
router.register(r'slots', views.TimeSlotViewSet, basename='time-slot')
router.register(r'sessions', views.LiveSessionViewSet, basename='live-session')

urlpatterns = [
    path('', include(router.urls)),
]
