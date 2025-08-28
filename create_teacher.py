from django.contrib.auth import get_user_model
from accounts.models import TeacherProfile

User = get_user_model()
admin = User.objects.get(id=1)  # Get the admin user
if not hasattr(admin, 'teacher_profile'):
    TeacherProfile.objects.create(user=admin)
print("Teacher profile created successfully")
