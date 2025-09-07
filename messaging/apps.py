"""
App configuration for the messaging app.
"""
from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'
    verbose_name = 'Messaging'
    
    def ready(self):
        import messaging.signals  # noqa
