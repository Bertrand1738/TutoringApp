"""
Views for the messaging app.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Max, OuterRef, Subquery
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, 
    MessageSerializer, 
    ConversationCreateSerializer
)


class IsParticipantPermission(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view and modify it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()


class ConversationViewSet(viewsets.ModelViewSet):
    """API endpoint for conversations"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantPermission]
    
    def get_queryset(self):
        user = self.request.user
        return (Conversation.objects
                .filter(participants=user)
                .prefetch_related('participants')
                .annotate(last_message_time=Max('messages__sent_at'))
                .order_by('-last_message_time'))
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark all messages in a conversation as read"""
        conversation = self.get_object()
        conversation.mark_all_as_read(request.user)
        return Response({'status': 'messages marked as read'})
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in a conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all()
        
        # Mark messages as read when viewed
        messages.filter(
            read_at__isnull=True
        ).exclude(sender=request.user).update(read_at=timezone.now())
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get total count of unread messages across all conversations"""
        user = request.user
        count = Message.objects.filter(
            conversation__participants=user,
            read_at__isnull=True
        ).exclude(sender=user).count()
        
        return Response({'unread_count': count})


class MessageViewSet(viewsets.ModelViewSet):
    """API endpoint for messages"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantPermission]
    
    def get_queryset(self):
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
    
    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']
        if self.request.user not in conversation.participants.all():
            self.permission_denied(
                self.request, 
                message="You are not a participant in this conversation."
            )
        serializer.save(sender=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a specific message as read"""
        message = self.get_object()
        if message.sender != request.user and not message.read_at:
            message.mark_as_read()
        serializer = self.get_serializer(message)
        return Response(serializer.data)
