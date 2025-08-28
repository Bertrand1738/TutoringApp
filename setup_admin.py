import os
import django
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    from accounts.models import TeacherProfile
    from django.utils import timezone

    User = get_user_model()

    # Create superuser if it doesn't exist
    try:
        admin_user = User.objects.get(username='admin')
        print("Admin user already exists")
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("Created admin superuser")

    # Create teacher group
    teacher_group, created = Group.objects.get_or_create(name='teacher')
    if created:
        print("Created teacher group")

    # Add admin to teacher group
    if not admin_user.groups.filter(name='teacher').exists():
        admin_user.groups.add(teacher_group)
        print(f"Added {admin_user.username} to teacher group")

    # Create teacher profile
    teacher_profile, created = TeacherProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'bio': 'Experienced French teacher',
            'verification_status': 'verified'
        }
    )

    if created:
        print(f"Created teacher profile for {admin_user.username}")
    else:
        print(f"Teacher profile already exists for {admin_user.username}")

if __name__ == "__main__":
    main()
