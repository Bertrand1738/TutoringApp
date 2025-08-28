from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from accounts.models import TeacherProfile
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a teacher profile for the admin user'

    def handle(self, *args, **options):
        # Get or create teacher group
        teacher_group, created = Group.objects.get_or_create(name='teacher')
        if created:
            self.stdout.write(self.style.SUCCESS('Created teacher group'))

        # Get admin user
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user not found. Please create one first.'))
            return

        # Add user to teacher group
        if not admin_user.groups.filter(name='teacher').exists():
            admin_user.groups.add(teacher_group)
            self.stdout.write(self.style.SUCCESS(f'Added {admin_user.username} to teacher group'))

        # Create teacher profile
        teacher_profile, created = TeacherProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'bio': 'Experienced French teacher',
                'teaching_since': timezone.now().date()
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created teacher profile for {admin_user.username}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Teacher profile already exists for {admin_user.username}')
            )
