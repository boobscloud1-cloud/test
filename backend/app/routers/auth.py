from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app import database, crud, schemas
from app.security import verify_telegram_init_data, TelegramInitDataError
from typing import Optional

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

async def get_current_user(
    x_telegram_id: Optional[str] = Header(None, alias="X-Telegram-ID"),
    db: AsyncSession = Depends(database.get_db)
):
    """
    Dependency to get the current user. 
    In PROD, this should verify initData or a session token.
    For DEV/Phase 1, we accept a raw Telegram ID in the header.
    """
    if not x_telegram_id:
        raise HTTPException(status_code=401, detail="Missing X-Telegram-ID header")
    
    try:
        telegram_id = int(x_telegram_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Telegram-ID format")

    user = await crud.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.post("/verify", response_model=schemas.AuthVerifyResponse)
async def verify(init: schemas.AuthVerifyRequest, db: AsyncSession = Depends(database.get_db)):
    """
    Verify Telegram WebApp initData and upsert the user.
    This endpoint enables secure authentication using Telegram-signed data.
    It is backward-compatible with the existing app (no frontend change required to keep current flow).
    """
    try:
        payload = verify_telegram_init_data(init.init_data)
    except TelegramInitDataError as e:
        raise HTTPException(status_code=401, detail=str(e))

    user_payload = payload.get("user")
    if not isinstance(user_payload, dict):
        raise HTTPException(status_code=400, detail="Missing or invalid user payload")

    telegram_id = user_payload.get("id")
    username = user_payload.get("username")

    if not isinstance(telegram_id, int) or telegram_id < 1:
        raise HTTPException(status_code=400, detail="Invalid user id in init_data")

    # Upsert user
    db_user = await crud.get_user_by_telegram_id(db, telegram_id=telegram_id)
    if not db_user:
        # Register minimal fields; no referrer linkage here
        db_user = await crud.create_user(db, schemas.UserCreate(telegram_id=telegram_id, username=username))

    return schemas.AuthVerifyResponse(user=db_user)
