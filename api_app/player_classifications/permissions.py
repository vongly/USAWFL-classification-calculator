from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsStaffUser(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        else:
            return False

class CreateOnlyAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return False
