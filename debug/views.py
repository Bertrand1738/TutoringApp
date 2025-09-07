from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def debug_registration(request):
    """Debug endpoint to log registration request data"""
    try:
        # Log the raw request
        logger.info(f"Debug Registration - Method: {request.method}")
        logger.info(f"Debug Registration - Headers: {dict(request.headers)}")
        
        # Log the data received
        data = request.data.copy()
        if 'password' in data:
            data['password'] = '******'  # Don't log the actual password
        logger.info(f"Debug Registration - Data: {data}")
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message': 'Registration data received and logged',
            'data': data
        })
    except Exception as e:
        logger.error(f"Debug Registration - Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
