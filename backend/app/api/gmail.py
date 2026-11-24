"""Gmail sync and connection status API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.oauth import generate_oauth_state, get_authorization_url, revoke_token
from app.core.security import decrypt_token, get_current_user
from app.database.connection import get_db
from app.models.oauth_credential import OAuthCredential
from app.models.user import User
from app.models.email import Email
from app.models.sync_history import SyncHistory
from app.services.gmail_service import GmailAuthError, GmailService

router = APIRouter()


class SyncOptions(BaseModel):
    max_emails: Optional[int] = None
    history_days: Optional[int] = None


@router.get("/connect")
async def connect_gmail():
    """Start Google OAuth so the user can connect Gmail."""
    state = generate_oauth_state()
    url = get_authorization_url(state)
    return {"auth_url": url, "authorization_url": url, "state": state}


@router.post("/sync")
async def sync_gmail(
    options: Optional[SyncOptions] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Synchronize the signed-in user's Gmail inbox into MailMind."""
    service = GmailService(db, user)
    opts = options or SyncOptions()
    try:
        return await service.sync_emails(opts.max_emails, opts.history_days)
    except GmailAuthError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach Gmail right now. Please try again in a moment.",
        )


@router.get("/sync/status")
async def sync_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve sync status and connection state."""
    last = (
        await db.execute(
            select(SyncHistory.completed_at)
            .where(SyncHistory.user_id == user.id, SyncHistory.status.in_(["success", "partial"]))
            .order_by(SyncHistory.completed_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    total = (
        await db.execute(select(func.count()).select_from(Email).where(Email.user_id == user.id))
    ).scalar_one()
    return {
        "is_syncing": False,
        "last_synced_at": last.isoformat() if last else None,
        "gmail_connected": user.gmail_connected,
        "total_synced": total,
    }


@router.post("/disconnect")
async def disconnect_gmail(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke Google tokens and mark Gmail as disconnected."""
    stmt = select(OAuthCredential).where(
        OAuthCredential.user_id == user.id, OAuthCredential.provider == "google"
    )
    cred = (await db.execute(stmt)).scalar_one_or_none()
    if cred:
        refresh = decrypt_token(cred.refresh_token or "")
        access = decrypt_token(cred.access_token or "")
        await revoke_token(refresh or access)
        await db.delete(cred)
    user.gmail_connected = False
    await db.commit()
    return {"status": "success", "message": "Gmail disconnected."}
