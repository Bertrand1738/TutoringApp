"""
Custom permissions for role-based access control.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'studentprofile')

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'teacher_profile') or request.user.groups.filter(name='teacher').exists()

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        owner = getattr(obj, "user", None)
        if not owner:
            owner = getattr(obj, "teacher", None)
        return owner == request.user
