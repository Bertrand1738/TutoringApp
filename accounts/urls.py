from django.urls import path
from .views import RegisterView, MeView, sync_tokens, logout_view
from .views_dashboard import my_enrollments, my_orders
from .debug_views import debug_registration
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", logout_view, name="logout"),
    path("sync-tokens/", sync_tokens, name="sync_tokens"),
    path("me/", MeView.as_view(), name="me"),
    path("me/enrollments/", my_enrollments, name="my_enrollments"),
    path("me/orders/", my_orders, name="my_orders"),
    # Debug endpoints
    path("debug-register/", debug_registration, name="debug_register"),
]
