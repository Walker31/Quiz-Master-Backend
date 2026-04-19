from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperAdmin(BasePermission):
    """Allow access only to users with role='SUPERADMIN'."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'SUPERADMIN'
        )


class IsAdmin(BasePermission):
    """Allow access to ADMIN or SUPERADMIN users."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) in ('ADMIN', 'SUPERADMIN')
        )


class IsStudent(BasePermission):
    """Allow access only to users with role='STUDENT'."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'STUDENT'
        )


class IsAdminOrReadOnly(BasePermission):
    """Read access for all authenticated users; write access for ADMIN/SUPERADMIN."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(request.user, 'role', None) in ('ADMIN', 'SUPERADMIN')


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner can access their own object; admins can access any."""
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'role', None) in ('ADMIN', 'SUPERADMIN'):
            return True
        return getattr(obj, 'student', None) == request.user or \
               getattr(obj, 'user', None) == request.user
