from django.urls import path
from . import views

urlpatterns = [
    path('debug-register/', views.debug_registration, name='debug_registration'),
]
