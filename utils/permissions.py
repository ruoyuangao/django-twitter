from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    Permission is used to check whether obj.user == request.user
    - if action has detail=False, we only check has_permission
    - if action has detail=True, we check has_permission and has_object_permission
    the default error message will show content in IsObjectOwner.message
    """
    message = "You do not have permission to access this object"

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
