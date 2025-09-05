"""
Basic course serializers that don't depend on content types
"""
from rest_framework import serializers
from .models import Course, CourseCategory

class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'description']


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "price", "description", "created_at"]


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(read_only=True)
    teacher_name = serializers.SerializerMethodField()
    category = CourseCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseCategory.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    def get_teacher_name(self, obj):
        if obj.teacher and obj.teacher.user:
            if obj.teacher.user.get_full_name():
                return obj.teacher.user.get_full_name()
            return obj.teacher.user.username
        return ""

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'price', 'created_at', 'published',
            'teacher', 'teacher_name', 'category', 'category_id'
        ]
