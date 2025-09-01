from rest_framework import serializers
from .models import CourseCategory
from .course_serializers import CourseListSerializer
from .content_serializers import VideoSerializer, PDFSerializer, AssignmentSerializer, QuizSerializer, ContentProgressSerializer
from payments.models import Order


class OrderSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "course", "amount", "status", "created_at"]
