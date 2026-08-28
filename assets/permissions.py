""" Roles and permissions for the assets app. """
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .services import workflow_service

class AssetPermission(BasePermission):
    """ Custom permission class for Asset model. """
    message = "You do not have access to this asset."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if view.action == "create":
            return workflow_service.user_role(
                request.user
            ) in ("editor", "admin")

        return True