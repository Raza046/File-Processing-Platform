from rest_framework.permissions import BasePermission, DjangoObjectPermissions


class IsOwnerOfFilePermission(BasePermission):
    message = 'Details of File is not allowed.'
    # def has_permission(self, request, view):
    #     return True

    def has_object_permission(self, request, view, obj):

        # Allowing just the owner of the file to view the details.
        return obj.uploaded_by == request.user
