from rest_framework.permissions import BasePermission

class IsStaffUser(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        else:
            return False