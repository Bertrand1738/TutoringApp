from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentProfile, TeacherProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
        
    # Get or create role groups
    student_group, _ = Group.objects.get_or_create(name='student')
    teacher_group, _ = Group.objects.get_or_create(name='teacher')

    # Check user's groups to determine role
    if instance.groups.filter(name='teacher').exists():
        TeacherProfile.objects.get_or_create(user=instance)
    else:
        # Default to student if no specific role
        StudentProfile.objects.get_or_create(user=instance)
        if not instance.groups.filter(name='student').exists():
            instance.groups.add(student_group)
