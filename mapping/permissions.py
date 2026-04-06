from rest_framework import permissions
from django.conf import settings

class DevModePermission(permissions.BasePermission):
    """
    Custom permission that allows access if DEV_MODE is True.
    Otherwise, it requires the user to be authenticated.
    """
    def has_permission(self, request, view):
        # Allow access if DEV_MODE is enabled in settings
        if getattr(settings, 'DEV_MODE', False):
            return True
            
        # Fallback to standard IsAuthenticated check
        return bool(request.user and request.user.is_authenticated)
