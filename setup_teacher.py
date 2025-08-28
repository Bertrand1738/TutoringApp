from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from accounts.models import TeacherProfile
from django.utils import timezone

# Get user model
User = get_user_model()

def setup_teacher():
    # Get or create teacher group
    teacher_group, _ = Group.objects.get_or_create(name='teacher')
    
    # Get the first user (admin)
    user = User.objects.first()
    if not user:
        print("No users found!")
        return
    
    # Add user to teacher group
    if not user.groups.filter(name='teacher').exists():
        user.groups.add(teacher_group)
        print(f"Added {user.username} to teacher group")
    else:
        print(f"{user.username} is already in teacher group")
    
    # Create teacher profile if doesn't exist
    teacher_profile, created = TeacherProfile.objects.get_or_create(
        user=user,
        defaults={
            'bio': 'Experienced French teacher',
            'teaching_since': timezone.now().date()
        }
    )
    
    if created:
        print(f"Created teacher profile for {user.username}")
    else:
        print(f"Teacher profile already exists for {user.username}")

if __name__ == "__main__":
    setup_teacher()
