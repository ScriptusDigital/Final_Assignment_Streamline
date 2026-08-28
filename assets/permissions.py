""" Roles and permissions for the assets app. """
from rest_framework import request
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

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return workflow_service.can_view(request.user, obj)
        return workflow_service.can_edit_metadata(request.user, obj)

        if view.action in ("update", "partial_update"):
            return workflow_service.can_edit_metadata(request.user, obj)    

        return True

class TaxonomyPermission(BasePermission):
    """ Custom permission class for Tag and Collection models. """
   
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True

        return workflow_service.user_role(request.user
        ) in ("editor", "admin")

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        role = workflow_service.user_role(request.user)
        if role == "admin":
            return True

        creator_id = getattr(obj, "created_by_id", None)

        return(creator_id is not None and creator_id == request.user.pk)
