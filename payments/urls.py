from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import webhooks

app_name = 'payments'

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Checkout endpoints
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('confirm-payment/<int:payment_id>/', 
         views.PaymentConfirmView.as_view(), name='confirm-payment'),
    
    # Webhook URL
    path('webhook/', webhooks.stripe_webhook, name='stripe-webhook'),
]
