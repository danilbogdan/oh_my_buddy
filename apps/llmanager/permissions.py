from rest_framework import permissions
from django.core.cache import cache


class IsAuthenticatedWithTrial(permissions.BasePermission):
    RATE_LIMIT = 10
    RATE_LIMIT_KEY_PREFIX = "rate_limit_"
    
    def has_permission(self, request, view):
        ip_address = self.get_client_ip(request)
        request.ip_address = ip_address
        if request.method in permissions.SAFE_METHODS:
            return True
        view_name = view.__class__.__name__
        cache_key = f"{self.RATE_LIMIT_KEY_PREFIX}{view_name}_{ip_address}"
        request_count = cache.get(cache_key, 0)
        if not request.user.is_authenticated and request_count >= self.RATE_LIMIT:
            return False

        if not request.user.is_authenticated:
            cache.set(cache_key, request_count + 1, timeout=24 * 3600)  # Reset count every hour
        return True

    def has_object_permission(self, request, view, obj):
        request.ip_address = self.get_client_ip(request)
        return True

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
