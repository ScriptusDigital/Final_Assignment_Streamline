""" Rules for asset access and workflow decisions """

from __future__ import annotations
from assets.models import Asset
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from assets.models import Asset, AssetEvent


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

def _required_metadata(
      asset: Asset,         
)  -> list[str]:
    """ Returns a list of required metadata fields for the asset. """
    required = {
        "title": asset.title,
        "alt_text": asset.alt_text,
        "photographer_credit": (
            asset.photographer_credit
        ),
    }

    missing = [
       label.replace("_", " ")
       for label, value in required.items()
       if not str(value).strip()
    ]

    if (
        asset.rights_status
        == Asset.RightsStatus.UNKNOWN    
):
        missing.append("rights status")

    return missing  


def _assert_action (
        user,
        asset: Asset,
        action: str,
) -> None:
    """ Check role, ownership and current state. """

    role = user_role(user)
    owns_asset = asset.uploader_id == getattr(user, "pk", None)

    if action == "submit":
        if (
            role not in ("editor", "admin")
            or (
                role == "editor"
                and not owns_asset
            )
        ):
            raise PermissionDenied(
                "You cannot submit this asset."
            )

        if asset.status not in (
            Asset.Status.DRAFT,
            Asset.Status.CHANGES_REQUESTED,
        ):
            raise WorkflowError({
                "status": (
                    "Only drafts or revisions "
                    "can be submitted."
                ),
            })

        return

    raise WorkflowError({
        "action": "Unknown workflow action.", 
    })