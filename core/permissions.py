"""
Custom permissions for role-based access control.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.shortcuts import get_object_or_404
from courses.models import Course

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


class CanManageCourseContent(BasePermission):
    """Permission to manage course content (add/edit/delete content)"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Staff can manage all content
        if request.user.is_staff:
            return True
            
        # Only teachers can manage content
        if not hasattr(request.user, 'teacher_profile'):
            return False
            
        # For content creation/modification, check if teacher owns the course
        course_id = view.kwargs.get('course_pk') or request.data.get('course')
        if not course_id:
            return False
            
        course = get_object_or_404(Course, pk=course_id)
        return course.teacher.user == request.user

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.course.teacher.user == request.user


class IsEnrolledOrPreview(BasePermission):
    """Permission to access course content (view/download)"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or obj.is_preview:
            return True
            
        # Teachers can access their own content
        if hasattr(request.user, 'teacher_profile'):
            return obj.course.teacher.user == request.user
            
        # Students need to be enrolled
        if hasattr(request.user, 'student_profile'):
            return obj.course.enrollments.filter(
                student=request.user.student_profile
            ).exists()
            
        return False


class CanAccessProgress(BasePermission):
    """Permission to access content progress"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
            
        # Teachers can view progress for their courses
        if hasattr(request.user, 'teacher_profile'):
            return obj.content_object.course.teacher.user == request.user
            
        # Students can only view their own progress
        return obj.student.user == request.user
