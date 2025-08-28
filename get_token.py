from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()
refresh = RefreshToken.for_user(user)

print("Access token:")
print(str(refresh.access_token))
print("\nRefresh token:")
print(str(refresh))
