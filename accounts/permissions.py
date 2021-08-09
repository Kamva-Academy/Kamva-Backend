from rest_framework import permissions


class IsHimself(permissions.BasePermission):
    """
    Permission for updating user profile / account / user data
    """

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id and request.user.is_authenticated


class IsInstituteOwner(permissions.BasePermission):
    """
    Permission for updating or deleting or adding admin to institutes
    """
    message = 'You are not this institute\'s owner'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class IsInstituteAdmin(permissions.BasePermission):
    """
    Permission for institute's admin to update institute
    """
    message = 'You are not this institute\'s admin'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.admins.all()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user
