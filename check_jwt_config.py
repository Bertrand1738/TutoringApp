import os
import sys
import django
from django.contrib.auth import get_user_model
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now we can import from Django apps
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate

User = get_user_model()

def check_jwt_config():
    print("Checking JWT Configuration...")
    print(f"Django version: {django.get_version()}")
    
    try:
        from rest_framework_simplejwt.settings import api_settings
        print("\nJWT Settings:")
        print(f"  AUTH_HEADER_TYPES: {api_settings.AUTH_HEADER_TYPES}")
        print(f"  AUTH_HEADER_NAME: {api_settings.AUTH_HEADER_NAME}")
        print(f"  USER_ID_FIELD: {api_settings.USER_ID_FIELD}")
        print(f"  USER_ID_CLAIM: {api_settings.USER_ID_CLAIM}")
    except Exception as e:
        print(f"Error checking JWT settings: {e}")
    
    print("\nChecking authentication directly...")
    try:
        # Try direct authentication
        username = 'admin'
        password = 'admin123'
        user = authenticate(username=username, password=password)
        if user:
            print(f"✅ Authentication successful for {username}")
            print(f"  User ID: {user.id}")
            print(f"  Is active: {user.is_active}")
            print(f"  Is staff: {user.is_staff}")
            print(f"  Is superuser: {user.is_superuser}")
            
            # Try creating tokens manually
            try:
                refresh = RefreshToken.for_user(user)
                print("\nManual Token Creation:")
                print(f"  Refresh token: {str(refresh)[:20]}...")
                print(f"  Access token: {str(refresh.access_token)[:20]}...")
            except Exception as e:
                print(f"Error creating tokens: {e}")
                
        else:
            print(f"❌ Authentication failed for {username}")
            
            # Check if user exists
            try:
                user = User.objects.get(username=username)
                print(f"User {username} exists in the database but authentication failed")
                print(f"  Is active: {user.is_active}")
                print(f"  Last login: {user.last_login}")
                print(f"  Password: {user.password[:15]}...")
            except User.DoesNotExist:
                print(f"User {username} does not exist in database")
    except Exception as e:
        print(f"Error during authentication check: {e}")

    print("\nAttempting to manually create a token with TokenObtainPairSerializer...")
    try:
        serializer = TokenObtainPairSerializer(data={
            'username': 'admin',
            'password': 'admin123'
        })
        if serializer.is_valid():
            print("✅ TokenObtainPairSerializer accepted the credentials")
            print(f"  Token data: {serializer.validated_data}")
        else:
            print("❌ TokenObtainPairSerializer rejected the credentials")
            print(f"  Errors: {serializer.errors}")
    except Exception as e:
        print(f"Error with TokenObtainPairSerializer: {e}")

    # Try a different user - teacher
    print("\nTrying with 'teacher' user...")
    try:
        username = 'teacher'
        password = 'teacherpass'
        user = authenticate(username=username, password=password)
        if user:
            print(f"✅ Authentication successful for {username}")
            
            # Try creating tokens manually
            try:
                refresh = RefreshToken.for_user(user)
                print(f"  Refresh token: {str(refresh)[:20]}...")
                print(f"  Access token: {str(refresh.access_token)[:20]}...")
            except Exception as e:
                print(f"Error creating tokens: {e}")
                
        else:
            print(f"❌ Authentication failed for {username}")
    except Exception as e:
        print(f"Error during teacher authentication check: {e}")

if __name__ == "__main__":
    check_jwt_config()
