""" Rules for asset access and workflow decisions """

from __future__ import annotations
from assets.models import Asset
from django.core.exceptions import ValidationError

class WorkflowError(ValidationError):
    """The requested workflow transition is invalid."""

def user_role(user) -> str:
    """ Returns the role of the user as a string. """
    if not getattr(user, "is_authenticated", False):
        return "anonymous"

    if getattr(user, 'is_superuser', False):
        return "admin"

    return getattr(user, 'role', 'viewer') 

def is_admin(user) -> bool:
    return user_role(user) == "admin"


def is_editor(user) -> bool:
    return user_role(user) == "editor"

def can_edit_metadata(user, asset: Asset) -> bool:
    return is_admin(user) or (
        is_editor(user)
        and asset.uploader_id == user.pk
        and asset.status in (
            Asset.Status.DRAFT,
            Asset.Status.CHANGES_REQUESTED,
        )
    )
def can_view(user, asset: Asset) -> bool:
  if is_admin(user):
    return True

  if is_editor(user) and asset.uploader_id == user.pk:
    return True

  return asset.is_viewer_accessible