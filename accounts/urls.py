from django.urls import path
from .views import RegisterView, MeView
from .views_dashboard import my_enrollments, my_orders
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("me/enrollments/", my_enrollments, name="my_enrollments"),
    path("me/orders/", my_orders, name="my_orders"),
]
