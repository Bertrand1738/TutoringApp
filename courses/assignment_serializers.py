"""
Serializers for assignment models
"""
from rest_framework import serializers
from courses.assignment_models import Assignment, Submission, AssignmentFeedback


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model"""
    attachment_url = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'course', 'course_title', 'title', 'description', 'instructions',
            'order_index', 'is_preview', 'created_at', 'due_date', 'available_from',
            'max_points', 'attachment', 'attachment_url'
        ]
        read_only_fields = ['created_at']
    
    def get_attachment_url(self, obj):
        """Get full URL for attachment if present"""
        if obj.attachment and obj.attachment.url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
        return None


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model"""
    file_url = serializers.SerializerMethodField()
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    is_late = serializers.BooleanField(read_only=True)
    grade_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title', 'student', 'student_name',
            'text_content', 'file', 'file_url', 'submitted_at', 'modified_at',
            'status', 'points_earned', 'is_late', 'grade_percentage'
        ]
        read_only_fields = ['submitted_at', 'modified_at', 'student', 'status', 
                           'points_earned', 'graded_by', 'graded_at']
    
    def get_file_url(self, obj):
        """Get full URL for file if present"""
        if obj.file and obj.file.url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def create(self, validated_data):
        """Set the student to the current user"""
        validated_data['student'] = self.context['request'].user
        
        # Check if this is a resubmission
        existing = Submission.objects.filter(
            student=validated_data['student'],
            assignment=validated_data['assignment']
        ).first()
        
        if existing:
            # Update the existing submission
            existing.text_content = validated_data.get('text_content', existing.text_content)
            if 'file' in validated_data:
                existing.file = validated_data['file']
            existing.status = 'resubmitted'
            existing.save()
            return existing
        
        return super().create(validated_data)


class AssignmentFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for AssignmentFeedback model"""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    attachment_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentFeedback
        fields = [
            'id', 'submission', 'teacher', 'teacher_name', 'comment',
            'created_at', 'attachment', 'attachment_url'
        ]
        read_only_fields = ['created_at', 'teacher']
    
    def get_attachment_url(self, obj):
        """Get full URL for attachment if present"""
        if obj.attachment and obj.attachment.url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
        return None
    
    def create(self, validated_data):
        """Set the teacher to the current user"""
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)
