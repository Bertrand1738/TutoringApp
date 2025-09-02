"""
Serializers for progress tracking
"""
from rest_framework import serializers
from courses.progress_models import ContentProgress, CourseProgress
from courses.models import Course


class ContentProgressSerializer(serializers.ModelSerializer):
    """Serializer for content progress records"""
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)
    content_title = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentProgress
        fields = [
            'id', 'student', 'course', 'content_type', 'content_type_name', 
            'object_id', 'content_title', 'first_accessed', 'last_accessed',
            'is_completed', 'completed_at', 'progress_percent', 'total_time_spent'
        ]
        read_only_fields = ['first_accessed', 'student', 'course', 'content_type', 'object_id']
    
    def get_content_title(self, obj):
        """Get the title of the content object"""
        if obj.content_object and hasattr(obj.content_object, 'title'):
            return obj.content_object.title
        return "Unknown Content"


class CourseProgressSerializer(serializers.ModelSerializer):
    """Serializer for course progress records"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = CourseProgress
        fields = [
            'id', 'student', 'course', 'course_title', 'progress_percent',
            'last_activity', 'completed_items', 'total_items', 'total_time_spent'
        ]
        read_only_fields = ['student', 'course', 'last_activity']


class CourseProgressDetailSerializer(CourseProgressSerializer):
    """Extended course progress serializer with content details"""
    content_progress = serializers.SerializerMethodField()
    
    class Meta(CourseProgressSerializer.Meta):
        fields = CourseProgressSerializer.Meta.fields + ['content_progress']
    
    def get_content_progress(self, obj):
        """Get detailed progress for all content in the course"""
        content_progress = ContentProgress.objects.filter(
            student=obj.student,
            course=obj.course
        )
        return ContentProgressSerializer(content_progress, many=True).data
