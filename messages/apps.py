"""
App configuration for the messaging app.
"""
from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messages'
    verbose_name = 'Messaging'
    
    def ready(self):
        import messages.signals  # noqa
