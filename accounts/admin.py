from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import StudentProfile, TeacherProfile

# Extend UserAdmin to include profile information
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    
    def get_role(self, obj):
        if hasattr(obj, 'teacher_profile'):
            return 'Teacher'
        if hasattr(obj, 'student_profile'):
            return 'Student'
        return 'No Role'
    get_role.short_description = 'Role'

# Register the custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
