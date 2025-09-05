from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
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



