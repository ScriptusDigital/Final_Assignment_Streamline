""" Rules for asset access and workflow decisions """

from __future__ import annotations
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from assets.models import Asset, AssetEvent
from django.utils import timezone

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

    if action in (
            "approve", 
            "request_changes"
    ):
        if role != "admin":
            readable_action = action.replace(
                "_", 
                " "
                )

            raise PermissionDenied(
                    "Only an administrator can "
                    f"{readable_action} an asset."
            )

        if asset.status != Asset.Status.IN_REVIEW:
            raise WorkflowError({
                "status": (
                    "The asset must be in review."
                ),
            })
        return

    raise WorkflowError({
        "action": "Unknown workflow action.", 
    })

@transaction.atomic
def submit(
    asset: Asset,
    actor,  
)   -> Asset:
    """ Submit a completed asset for review. """

    _assert_action(actor, asset, "submit",)

    missing = _required_metadata(asset)
    if missing:
        raise WorkflowError({
            "metadata": (
                "Complete these fields before "
                f"submission: {', '.join(missing)}."
            ),
        })

    previous_status = asset.status
    asset.status = Asset.Status.IN_REVIEW
    asset.approved_at = None
    asset.approved_at = None

    asset.save(update_fields=(
        "status",
        "approver",
        "approved_at",
        "updated_at",
    ))

    AssetEvent.objects.create(
        asset=asset,
        actor=actor,
        action=AssetEvent.Action.SUBMITTED,
        from_status=previous_status,
        to_status=asset.status,
    )

@transaction.atomic
def approve(
    asset: Asset,
    actor,
) -> Asset:
        """Approve an asset currently under review."""

        _assert_action(
            actor,
            asset,
            "approve",
        )

        if asset.rights_status not in (
            Asset.RightsStatus.CLEARED,
            Asset.RightsStatus.RESTRICTED,
        ):
            raise WorkflowError({
                "rights_status": (
                    "Rights must be cleared or "
                    "restricted before approval."
                ),
            })

        if (
            asset.expiry_date
            and asset.expiry_date
            < timezone.localdate()
        ):
            raise WorkflowError({
                "expiry_date": (
                    "An asset with expired rights "
                    "cannot be approved."
                ),
            })

        if (
            asset.permitted_use
            == Asset.PermittedUse.INTERNAL
        ):
            raise WorkflowError({
                "permitted_use": (
                    "Choose an external permitted "
                    "use before approval."
                ),
            })

        previous_status = asset.status

        asset.status = Asset.Status.APPROVED
        asset.approver = actor
        asset.approved_at = timezone.now()

        asset.full_clean()

        asset.save(
            update_fields=(
                "status",
                "approver",
                "approved_at",
                "updated_at",
            )
        )

        AssetEvent.objects.create(
            asset=asset,
            actor=actor,
            action=AssetEvent.Action.APPROVED,
            from_status=previous_status,
            to_status=asset.status,
        )

        return asset

@transaction.atomic
def request_changes(
    asset: Asset,
    actor,
    reason: str,
) -> Asset:
    """Return an asset to its editor for revision."""

    _assert_action(
        actor,
        asset,
        "request_changes",
    )

    reason = (reason or "").strip()

    if not reason:
        raise WorkflowError({
            "reason": (
                "Explain why the asset needs changes."
            ),
        })

    previous_status = asset.status

    asset.status = (Asset.Status.CHANGES_REQUESTED
    )
    asset.approver = None
    asset.approved_at = None

    asset.save(update_fields=(
        "status",
        "approver",
        "approved_at",
        "updated_at",
    ))

    AssetEvent.objects.create(
        asset=asset,
        actor=actor,
        action=AssetEvent.Action.CHANGES_REQUESTED,
        from_status=previous_status,
        to_status=asset.status,
        message=reason,
    )

    return asset