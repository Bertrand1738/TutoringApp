"""
Admin configuration for the messaging app.
"""
from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'started_at', 'updated_at')
    list_filter = ('started_at', 'updated_at')
    search_fields = ('participants__username', 'participants__email')
    date_hierarchy = 'started_at'
    
    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'conversation', 'get_truncated_content', 'sent_at', 'read_at')
    list_filter = ('sent_at', 'read_at')
    search_fields = ('content', 'sender__username', 'sender__email')
    date_hierarchy = 'sent_at'
    
    def get_truncated_content(self, obj):
        if len(obj.content) > 50:
            return f"{obj.content[:47]}..."
        return obj.content
    get_truncated_content.short_description = 'Content'
