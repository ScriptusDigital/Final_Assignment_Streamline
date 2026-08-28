""" Rules for asset access and workflow decisions """

from __future__ import annotations
from assets.models import Asset

def user_role(user) -> str:
    """ Returns the role of the user as a string. """
    if not getattr(user, "is_authenticated", False):
        return "anonymous"

    if getattr(user, 'is_superuser', False):
        return "admin"

    return getattr(user, 'role', 'viewer')  # Default to 'viewer' if role is not set