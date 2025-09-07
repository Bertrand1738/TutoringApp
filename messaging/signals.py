"""
Signal handlers for the messaging app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from django.utils import timezone

@receiver(post_save, sender=Message)
def update_conversation_timestamp(sender, instance, created, **kwargs):
    """Update the conversation's updated_at field when a new message is sent"""
    if created:
        conversation = instance.conversation
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['updated_at'])
