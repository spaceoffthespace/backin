from rest_framework import permissions

class IsHousekeepingOrHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role in ['housekeeping', 'hr']

class IsHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'hr'
    
class IsOwnerOfNotification(permissions.BasePermission):
   
    def has_object_permission(self, request, view, obj):
        # Check if the user associated with the notification is the same as the authenticated user.
        return obj.user == request.user