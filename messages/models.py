"""
Models for handling direct messaging between students and tutors.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone

class Conversation(models.Model):
    """
    Represents a conversation thread between users.
    A conversation is a container for messages exchanged between two users.
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participants_names = ', '.join(
            [user.get_full_name() or user.username 
             for user in self.participants.all()]
        )
        return f"Conversation between {participants_names}"
    
    @property
    def last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.order_by('-sent_at').first()
    
    def unread_count(self, user):
        """Count unread messages for a specific user"""
        return self.messages.filter(
            read_at__isnull=True
        ).exclude(sender=user).count()
    
    def mark_all_as_read(self, user):
        """Mark all messages as read for a specific user"""
        now = timezone.now()
        self.messages.filter(
            read_at__isnull=True
        ).exclude(sender=user).update(read_at=now)


class Message(models.Model):
    """
    Represents a single message in a conversation.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Optional attachment
    attachment = models.FileField(
        upload_to='message_attachments/',
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['sent_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.sent_at}"
    
    def mark_as_read(self):
        """Mark this message as read"""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])
