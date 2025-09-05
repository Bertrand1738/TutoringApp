import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def debug_registration(request):
    """
    A debug endpoint to log registration requests and help diagnose issues.
    """
    try:
        # Parse the request body
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            body = {"error": "Could not parse JSON body"}
        
        # Log the request details
        logger.info(f"DEBUG REGISTRATION: Received registration request")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Mask the password for security
        safe_body = {k: '******' if k == 'password' else v for k, v in body.items()}
        logger.info(f"Body: {safe_body}")
        
        # Return details about the request
        return JsonResponse({
            "message": "Registration request received and logged",
            "received_data": safe_body,
            "content_type": request.content_type,
            "method": request.method,
            "headers": {key: request.headers[key] for key in request.headers if key.startswith('x-') or key in ['content-type', 'accept']}
        })
    except Exception as e:
        logger.error(f"Error in debug_registration: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
