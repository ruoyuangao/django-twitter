from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    This permission is used to check whether obj.user is reuqest.user
    This class is very general
    Permission will be run one by one
    - if detail=False, the action will only look up the has_permission
    - if detail=True, the action will look up has_permission and has_object_permission
    if there is any error, the default error message will display IsObjectOwner.message
    """
    message = "You do not have permission to access this object"

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user