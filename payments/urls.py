from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import webhooks

app_name = 'payments'

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Webhook URL
    path('webhook/', webhooks.stripe_webhook, name='stripe-webhook'),
]
