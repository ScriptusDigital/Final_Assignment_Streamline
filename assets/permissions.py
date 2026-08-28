""" ROles and permissions for the assets app. """
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .services import workflow_service