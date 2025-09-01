"""
Custom throttling classes for API rate limiting
"""
from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache

class UserBasedThrottle(SimpleRateThrottle):
    """
    Throttle class that rates limits based on user ID
    Authenticated users get higher rate limits
    """
    scope = 'user'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return f"throttle_{self.scope}_{ident}"

    def get_rate(self):
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name='teacher').exists():
                return '1000/hour'  # Teachers get higher limit
            return '100/hour'  # Regular authenticated users
        return '20/hour'  # Unauthenticated users

class LiveSessionThrottle(UserBasedThrottle):
    """
    Specific throttle for live session related endpoints
    More restrictive to prevent abuse
    """
    scope = 'live_session'

    def get_rate(self):
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name='teacher').exists():
                return '50/hour'  # Teachers
            return '20/hour'  # Students
        return '5/hour'  # Unauthenticated
