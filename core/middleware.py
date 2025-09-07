import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import AnonymousUser
import logging
from django.http import HttpResponseRedirect
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError

logger = logging.getLogger(__name__)
User = get_user_model()

class JWTAuthenticationMiddleware:
    """
    Custom middleware to handle JWT authentication alongside session authentication.
    
    This middleware checks for a JWT token in the Authorization header, session, cookies, or URL
    and authenticates the user if a valid token is found.
    
    It also handles token refresh when the access token has expired.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is already authenticated via session
        if request.user.is_authenticated:
            # User is already authenticated via session
            return self.get_response(request)
        
        # Get tokens from various sources
        access_token = self._get_token_from_request(request)
        refresh_token = self._get_refresh_token_from_request(request)
        
        if access_token:
            # Check if token is valid
            user = self._authenticate_with_token(request, access_token, refresh_token)
            
            if user:
                # Set user and create session
                request.user = user
                login(request, user)
                
                # Store tokens in session for later use
                request.session['access_token'] = access_token
                if refresh_token:
                    request.session['refresh_token'] = refresh_token
            
            # If we're trying to access a protected page with a token in URL, 
            # redirect to clean up the URL
            if request.GET.get('token') and 'next' not in request.GET and not request.path.startswith('/api/'):
                return HttpResponseRedirect(request.path)
        
        return self.get_response(request)
    
    def _get_token_from_request(self, request):
        """Extract access token from request"""
        token = None
        
        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Check session
        if not token and 'access_token' in request.session:
            token = request.session.get('access_token')
        
        # Check cookies
        if not token and 'access_token' in request.COOKIES:
            token = request.COOKIES.get('access_token')
        
        # Check URL parameter (common in redirects)
        if not token and request.GET.get('token'):
            token = request.GET.get('token')
        
        return token
    
    def _get_refresh_token_from_request(self, request):
        """Extract refresh token from request"""
        token = None
        
        # Check session
        if 'refresh_token' in request.session:
            token = request.session.get('refresh_token')
        
        # Check cookies
        if not token and 'refresh_token' in request.COOKIES:
            token = request.COOKIES.get('refresh_token')
        
        # Check POST data (from login form)
        if not token and request.method == 'POST':
            token = request.POST.get('refresh_token')
        
        return token
    
    def _authenticate_with_token(self, request, access_token, refresh_token=None):
        """
        Authenticate user with JWT token
        
        Returns:
            User object if successful, None otherwise
        """
        try:
            # First check if token has been blacklisted
            try:
                # This is a simple check to see if the token is in the blacklist
                # We decode without verification to get the jti
                unverified_payload = jwt.decode(
                    access_token,
                    options={"verify_signature": False}
                )
                token_jti = unverified_payload.get('jti')
                
                if token_jti:
                    # Check if token is blacklisted
                    if OutstandingToken.objects.filter(jti=token_jti).exists():
                        if BlacklistedToken.objects.filter(token__jti=token_jti).exists():
                            logger.warning("Token has been blacklisted")
                            return None
            except Exception as e:
                logger.warning(f"Error checking blacklisted token: {e}")
            
            # First check if token has expired
            unverified_payload = jwt.decode(
                access_token,
                options={"verify_signature": False}
            )
            
            # Check expiration without verifying signature
            exp_timestamp = unverified_payload.get('exp')
            if exp_timestamp:
                current_timestamp = datetime.timestamp(datetime.now())
                if current_timestamp > exp_timestamp:
                    # Token has expired, try to refresh
                    if refresh_token:
                        logger.info("Access token expired, trying to refresh")
                        try:
                            # Use Django REST framework SimpleJWT
                            refresh = RefreshToken(refresh_token)
                            new_access_token = str(refresh.access_token)
                            
                            # Store the new token in session
                            request.session['access_token'] = new_access_token
                            
                            # Use the new token
                            access_token = new_access_token
                            logger.info("Successfully refreshed access token")
                        except TokenError as e:
                            logger.error(f"Token refresh error: {e}")
                            return None
                        except Exception as e:
                            logger.error(f"Failed to refresh token: {e}")
                            return None
                    else:
                        logger.warning("Access token expired and no refresh token available")
                        return None
            
            # Now verify the token properly
            payload = jwt.decode(
                access_token, 
                settings.SECRET_KEY, 
                algorithms=['HS256']
            )
            
            # Get user from token
            user_id = payload.get('user_id')
            if user_id:
                try:
                    return User.objects.get(id=user_id)
                except User.DoesNotExist:
                    logger.warning(f"User with ID {user_id} not found")
            else:
                logger.warning("Token payload does not contain user_id")
        
        except jwt.ExpiredSignatureError:
            logger.warning("JWT has expired during verification")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during JWT authentication: {e}")
        
        return None
