from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Log incoming data (without password)
            data = request.data.copy()
            if 'password' in data:
                data['password'] = '******'
            logger.info(f"Registration request received: {data}")
            
            # Create the user with standard DRF logic
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            # Return the response
            logger.info(f"User created successfully: {user.username}")
            return Response(serializer.data, status=201, headers=headers)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            # Let DRF handle the exception with its standard error responses
            raise
    
    def perform_create(self, serializer):
        user = serializer.save()
        # Profile will be created automatically via signals
        return user


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
def logout_view(request):
    """
    Log out the user, clear the Django session, and blacklist the JWT token
    """
    import logging
    from rest_framework_simplejwt.tokens import RefreshToken
    logger = logging.getLogger(__name__)
    
    try:
        # Get token from authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            # Try to blacklist the token if it's a valid JWT
            try:
                # This would need token blacklisting to be enabled in settings
                refresh_token = request.session.get('refresh_token')
                if refresh_token:
                    RefreshToken(refresh_token).blacklist()
                    logger.info(f"Blacklisted refresh token for user {request.user.username}")
            except Exception as e:
                logger.warning(f"Could not blacklist token: {str(e)}")
        
        # Clear session data
        request.session.flush()
        
        # Django logout to clear the session completely
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            logger.info(f"Logged out user: {username}")
        
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({"detail": f"Error during logout: {str(e)}"}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated access for token sync
def sync_tokens(request):
    """
    Sync JWT tokens with the Django session.
    This ensures that both authentication mechanisms are in sync.
    """
    import logging
    import jwt
    from django.conf import settings
    logger = logging.getLogger(__name__)
    
    try:
        # Get tokens from request
        access_token = request.data.get('access_token')
        refresh_token = request.data.get('refresh_token')
        
        if not access_token:
            return Response({
                "detail": "Access token is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Store tokens in session
        request.session['access_token'] = access_token
        
        if refresh_token:
            request.session['refresh_token'] = refresh_token
            logger.debug("Stored refresh token in session")
        
        # Validate token and get user
        try:
            # Decode the JWT token
            payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Get user from token
            user_id = payload.get('user_id')
            if not user_id:
                return Response({
                    "detail": "Invalid token: no user_id in payload"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user from database
            user = User.objects.get(id=user_id)
            
            # Log in the user to create a session
            login(request, user)
            
            return Response({
                "detail": "Tokens synchronized successfully",
                "username": user.username,
                "user_id": user.id,
                "is_authenticated": True
            }, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError:
            return Response({
                "detail": "Expired token"
            }, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({
                "detail": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({
                "detail": f"User with ID {user_id} not found"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
    except Exception as e:
        logger.error(f"Token sync error: {str(e)}")
        return Response({
            "detail": f"Failed to sync tokens: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)



