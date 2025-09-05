from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import StudentProfile, TeacherProfile

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'profile')
        read_only_fields = ('id', 'role')

    def get_role(self, obj):
        if obj.groups.filter(name='teacher').exists():
            return 'teacher'
        return 'student'

    def get_profile(self, obj):
        if hasattr(obj, 'teacher_profile'):
            return TeacherProfileSerializer(obj.teacher_profile).data
        if hasattr(obj, 'student_profile'):
            return StudentProfileSerializer(obj.student_profile).data
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=['student', 'teacher'], default='student')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'role')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate_email(self, value):
        """Validate that the email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Validate that the username is unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Log the validated data (without password)
            safe_data = {k: '******' if k == 'password' else v for k, v in validated_data.items()}
            logger.info(f"Creating new user with data: {safe_data}")
            
            role = validated_data.pop('role')
            password = validated_data.pop('password')
            
            # Create the user
            user = User.objects.create_user(**validated_data)
            user.set_password(password)
            user.save()
            
            # Assign role group
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)
            
            logger.info(f"User created successfully: {user.username}, ID: {user.id}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ('profile_picture', 'government_id', 'subscription_type')


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ('government_id', 'bio', 'verification_status', 'avg_rating')
