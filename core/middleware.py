import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class JWTAuthenticationMiddleware:
    """
    Custom middleware to handle JWT authentication alongside session authentication.
    
    This middleware checks for a JWT token in the Authorization header or in the session
    and authenticates the user if a valid token is found. It works in parallel with Django's
    session authentication.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is already authenticated via session
        if request.user.is_authenticated:
            # User is already authenticated via session, continue
            logger.debug(f"User {request.user.username} already authenticated via session")
            return self.get_response(request)
        
        # Check for JWT in Authorization header
        jwt_token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
            logger.debug("Found JWT token in Authorization header")
        
        # Check for JWT in session
        if not jwt_token:
            jwt_token = request.session.get('access_token')
            if jwt_token:
                logger.debug("Found JWT token in session")
        
        # Check for JWT in localStorage via cookies or query params (fallback)
        if not jwt_token:
            if 'access_token' in request.COOKIES:
                jwt_token = request.COOKIES.get('access_token')
                logger.debug("Found JWT token in cookies")
            elif request.GET.get('token'):
                jwt_token = request.GET.get('token')
                logger.debug("Found JWT token in query params")
            elif request.session.get('token'):
                jwt_token = request.session.get('token')
                logger.debug("Found JWT token in Django session")
        
        if jwt_token:
            try:
                # Decode the JWT token
                payload = jwt.decode(
                    jwt_token, 
                    settings.SECRET_KEY, 
                    algorithms=['HS256']
                )
                
                # Get user from the token payload
                user_id = payload.get('user_id')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        
                        # Set the user on the request
                        request.user = user
                        
                        # Create a Django session for this user (important for redirects)
                        if not hasattr(request, 'session'):
                            logger.warning("Request has no session attribute")
                        else:
                            # Store the token in the session
                            request.session['access_token'] = jwt_token
                            
                            # Create a proper Django session for this user
                            if not request.user.is_authenticated:
                                login(request, user)
                                logger.debug(f"Created Django session for user {user.username} from JWT")
                        
                    except User.DoesNotExist:
                        logger.warning(f"User with ID {user_id} from JWT not found in database")
                        request.user = AnonymousUser()
                else:
                    logger.warning("JWT token did not contain user_id")
            
            except jwt.ExpiredSignatureError:
                # Token has expired
                logger.warning("JWT token has expired")
                request.user = AnonymousUser()
            except jwt.InvalidTokenError as e:
                # Invalid token
                logger.warning(f"Invalid JWT token: {str(e)}")
                request.user = AnonymousUser()
        
        return self.get_response(request)
