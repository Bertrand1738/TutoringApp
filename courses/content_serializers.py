from rest_framework import serializers
from .models import Video, PDF

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'course', 'title', 'description', 'video_url',
                 'order_index', 'is_preview', 'created_at']
        read_only_fields = ['created_at']


class PDFSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PDF
        fields = ['id', 'course', 'title', 'description', 'file', 'file_url',
                 'order_index', 'is_preview', 'created_at']
        read_only_fields = ['created_at', 'file_url']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


# Uncomment when models are ready to be used
# from .models import Assignment, Quiz

# Uncomment when models are ready to be used
# class AssignmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Assignment
#         fields = ['id', 'course', 'title', 'description', 'instructions',
#                  'due_date', 'max_points', 'order_index', 'is_preview', 'created_at']
#         read_only_fields = ['created_at']


# class QuizSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Quiz
#         fields = ['id', 'course', 'title', 'description', 'time_limit_minutes',
#                  'passing_score', 'max_attempts', 'questions', 'order_index',
#                  'is_preview', 'created_at']
#         read_only_fields = ['created_at']
