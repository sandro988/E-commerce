from rest_framework.permissions import BasePermission

class IsNotAuthenticated(BasePermission):
    """
    Custom permission to only allow unauthenticated users.
    """

    def has_permission(self, request, view):
        # Allow access only if the user is not authenticated
        return not request.user.is_authenticated