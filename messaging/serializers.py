"""
Serializers for the messaging app.
"""
from rest_framework import serializers
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class UserMessageSerializer(serializers.ModelSerializer):
    """Minimal user representation for messages"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for individual messages"""
    sender_details = UserMessageSerializer(source='sender', read_only=True)
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_details', 
            'content', 'sent_at', 'read_at', 'is_read',
            'attachment'
        ]
        read_only_fields = ['sent_at', 'read_at']
    
    def get_is_read(self, obj):
        return obj.read_at is not None


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversation threads"""
    participants_details = UserMessageSerializer(source='participants', many=True, read_only=True)
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participants_details', 'started_at', 
            'updated_at', 'last_message_preview', 'unread_count',
            'other_participant'
        ]
        read_only_fields = ['started_at', 'updated_at']
    
    def get_last_message_preview(self, obj):
        last_message = obj.last_message
        if last_message:
            # Return a truncated preview of the last message
            content = last_message.content
            if len(content) > 50:
                content = content[:47] + "..."
            return {
                'content': content,
                'sent_at': last_message.sent_at,
                'sender_id': last_message.sender_id
            }
        return None
    
    def get_unread_count(self, obj):
        user = self.context.get('request').user
        return obj.unread_count(user)
    
    def get_other_participant(self, obj):
        """Get the other participant in a conversation (assuming 2 participants)"""
        user = self.context.get('request').user
        other_user = obj.participants.exclude(id=user.id).first()
        if other_user:
            serializer = UserMessageSerializer(other_user)
            return serializer.data
        return None


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new conversations"""
    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=True
    )
    initial_message = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Conversation
        fields = ['participants', 'initial_message']
        
    def validate_participants(self, participants):
        """Validate participants - must include the current user and at least one other user"""
        request = self.context.get('request')
        if request and request.user not in participants:
            participants.append(request.user)
        
        # Check if we have at least 2 participants
        if len(participants) < 2:
            raise serializers.ValidationError(
                "A conversation must have at least 2 participants."
            )
        
        return participants
    
    def create(self, validated_data):
        initial_message = validated_data.pop('initial_message')
        participants = validated_data.pop('participants')
        request = self.context.get('request')
        sender = request.user
        
        # Create conversation
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.add(*participants)
        
        # Create initial message
        Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=initial_message
        )
        
        return conversation
