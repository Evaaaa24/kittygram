from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Полный доступ — только автору (created_by).
    Остальным — только чтение.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user
