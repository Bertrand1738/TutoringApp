from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

class Command(BaseCommand):
    help = 'Test API endpoints internally without HTTP'

    def handle(self, *args, **options):
        User = get_user_model()
        
        self.stdout.write(self.style.SUCCESS('Testing API endpoints internally...'))
        
        # Get a user for authentication
        admin = User.objects.filter(is_superuser=True).first()
        teacher = User.objects.filter(username='teacher').first()
        student = User.objects.filter(username='student').first()
        
        if not admin and not teacher and not student:
            self.stdout.write(self.style.ERROR('No users found for testing!'))
            return
        
        user = admin or teacher or student
        self.stdout.write(f'Using user: {user.username} (ID: {user.id})')
        
        # Create API client
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Test endpoints
        endpoints = [
            '/',
            '/api/',
            '/api/courses/',
            '/api/auth/me/',
        ]
        
        for endpoint in endpoints:
            self.stdout.write(f'\nTesting endpoint: {endpoint}')
            response = client.get(endpoint)
            self.stdout.write(f'Status code: {response.status_code}')
            
            if response.status_code < 300:
                try:
                    data = response.json()
                    self.stdout.write(f'Response data: {data}')
                except:
                    self.stdout.write(f'Response content: {response.content[:100]}')
            else:
                self.stdout.write(self.style.ERROR(f'Error: {response.content[:100]}'))
