from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # Import select
from typing import Optional
from app import crud, schemas, database, models, config
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.get("/", response_model=list[schemas.TaskResponse])
async def read_tasks(db: AsyncSession = Depends(database.get_db)):
    # Fetch active tasks
    result = await db.execute(select(models.Task).where(models.Task.is_active == True))
    tasks = result.scalars().all()

    # Deduplicate by (name, cpa_network_id) to avoid showing duplicate task entries
    seen = set()
    unique_tasks: list[models.Task] = []
    for t in tasks:
        key = (t.name, t.cpa_network_id)
        if key not in seen:
            seen.add(key)
            unique_tasks.append(t)

    return unique_tasks

# Server-to-Server Postback endpoint (Legacy GET support)
@router.get("/postback")
async def cpa_postback_get(
    click_id: str = Query(..., min_length=1, max_length=128), 
    sub_id: int = Query(..., ge=1), 
    payout: float = Query(..., ge=0, le=100000), 
    token: str = Query(..., min_length=8, max_length=128), 
    db: AsyncSession = Depends(database.get_db)
):
    # Legacy logic for original setup or networks that use GET
    if token != config.settings.CPA_SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Token")
    
    user = await crud.get_user_by_telegram_id(db, sub_id)
    if not user:
        return {"status": "error", "message": "User not found"}
    
    task_id = 1
    reward_spins = 3
    
    completion = await crud.complete_task(db, user.id, task_id, click_id, reward_spins)
    
    if completion:
        return {"status": "ok", "new_spins": user.spins}
    else:
        return {"status": "duplicate"}

# CPAGrip Postback Schema
class CPAGripPayload(BaseModel):
    password: str = Field(..., description="Security token")
    payout: float = Field(..., description="Payout amount")
    offer_id: str = Field(..., description="Offer ID")
    tracking_id: str = Field(..., description="User ID (subid)")
    # Optional fields CPAGrip might send
    ip: Optional[str] = None

# CPAGrip POST Endpoint (Form Data or JSON? Docs say [POST] variables usually Form Data)
from fastapi import Form

@router.post("/cpagrip_postback")
async def cpagrip_postback(
    password: str = Form(...),
    payout: float = Form(...),
    offer_id: str = Form(...),
    tracking_id: str = Form(...),
    db: AsyncSession = Depends(database.get_db)
):
    """
    Dedicated endpoint for CPAGrip Global Postback
    """
    # Security Check
    if password != config.settings.CPA_SECRET_TOKEN:
        # Do not leak secrets in logs
        raise HTTPException(status_code=403, detail="Access Denied")  # Matches PHP example "Access Denied"

    try:
        telegram_id = int(tracking_id)
    except ValueError:
        return {"status": "error", "message": "Invalid Tracking ID"}

    user = await crud.get_user_by_telegram_id(db, telegram_id)
    if not user:
        return {"status": "error", "message": "User not found"}

    # Validate payout and compute reward spins safely
    if payout < 0:
        return {"status": "error", "message": "Invalid payout"}
    # 1 Spin per $0.50 payout (min 1, max 100)
    reward_spins = max(1, min(100, int(payout * 2))) 
    
    # Unique Transaction ID: CPAGrip doesn't send unique Trans ID in basic postback, only offer_id.
    # To allow multiple completions of DIFFERENT offers, we use offer_id.
    # To allow re-completion of same offer? Maybe limit unique(user_id, offer_id).
    # We use f"cpagrip_{offer_id}_{telegram_id}" as our internal transaction key.
    # Basic validation on offer_id length
    if len(offer_id) > 128:
        return {"status": "error", "message": "Invalid offer ID"}
    transaction_key = f"cpagrip_{offer_id}_{telegram_id}"
    
    # Use a generic "CPAGrip Task" ID from DB or just 0
    task_id = 999 

    completion = await crud.complete_task(db, user.id, task_id, transaction_key, reward_spins)
    
    if completion:
        return {"status": "ok", "message": "Postback processed"}
    else:
        # Already completed this offer
        return {"status": "duplicate", "message": "Offer already processed"}
