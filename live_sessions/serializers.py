from rest_framework import serializers
from .models import TimeSlot, LiveSession
from courses.course_serializers import CourseSerializer
from accounts.serializers import UserSerializer

class TimeSlotSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)

    class Meta:
        model = TimeSlot
        fields = [
            'id', 'teacher', 'teacher_name', 'start_time', 'end_time',
            'is_available', 'recurring', 'recurrence_pattern'
        ]
        read_only_fields = ['is_available']

    def validate(self, data):
        """
        Check that start time is before end time and not in past
        """
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError(
                "End time must be after start time"
            )
        return data


class LiveSessionSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)
    student_details = UserSerializer(source='student', read_only=True)
    time_slot_details = TimeSlotSerializer(source='time_slot', read_only=True)

    class Meta:
        model = LiveSession
        fields = [
            'id', 'course', 'course_details', 'time_slot', 'time_slot_details',
            'student', 'student_details', 'meeting_platform', 'meeting_url',
            'meeting_id', 'meeting_password', 'status', 'student_notes',
            'teacher_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'meeting_url', 'meeting_id', 'meeting_password',
            'created_at', 'updated_at'
        ]

    def validate(self, data):
        """
        Check that the time slot is available and matches the course teacher
        """
        time_slot = data.get('time_slot')
        course = data.get('course')

        if not time_slot.is_available:
            raise serializers.ValidationError(
                "This time slot is not available"
            )

        if time_slot.teacher != course.teacher:
            raise serializers.ValidationError(
                "Time slot teacher must match course teacher"
            )

        return data
