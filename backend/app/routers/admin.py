from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List

from app import schemas, models, crud
from app.database import get_db
from app.config import settings

# For auth
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

async def get_current_admin(user: models.User = Depends(get_current_user)):
    admin_ids = [int(id_str.strip()) for id_str in settings.ADMIN_IDS.split(",") if id_str.strip()]
    print(f"DEBUG: Checking Admin. UserID={user.telegram_id}, Allowed={admin_ids}, Settings={settings.ADMIN_IDS}")
    if user.telegram_id not in admin_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin panel"
        )
    return user

@router.get("/stats", response_model=schemas.AdminStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    # Total Users
    result_users = await db.execute(select(func.count(models.User.id)))
    total_users = result_users.scalar()

    # Total Tasks Completed
    result_tasks = await db.execute(select(func.count(models.TaskCompletion.id)))
    total_tasks = result_tasks.scalar()
    
    # Estimate Revenue (Naive: count completions * task payout)
    # This requires joining TaskCompletion and Task
    revenue_query = select(func.sum(models.Task.cpa_payout)).join(models.TaskCompletion, models.Task.id == models.TaskCompletion.task_id)
    result_revenue = await db.execute(revenue_query)
    estimated_revenue = result_revenue.scalar() or 0.0

    # Total Spins Consumed (Needs a field or transaction log, currently we track current spins. 
    # Can approximation or adding a 'spins_used' field. For now, let's use a placeholder or derived if we had logs)
    # Since we don't have spin logs, we'll return 0 or implement logs later.
    # For now, let's just return 0.
    total_spins_consumed = 0 

    return schemas.AdminStats(
        total_users=total_users,
        total_tasks_completed=total_tasks,
        total_spins_consumed=total_spins_consumed,
        estimated_revenue=estimated_revenue
    )

@router.post("/tasks", response_model=schemas.TaskResponse)
async def create_task(
    task: schemas.TaskBase,
    db: AsyncSession = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    db_task = models.Task(**task.dict())
    # Note: cpa_payout isn't in TaskBase yet, so it will be default 0.0 unless we update Schema or pass it
    # We should update TaskBase to include cpa_payout if we want admin to set it.
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.post("/users/{user_id}/spins", response_model=schemas.UserResponse)
async def add_spins(
    user_id: int,
    payload: schemas.AdminAddSpins,
    db: AsyncSession = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.spins += payload.amount
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/broadcast")
async def broadcast_message(
    payload: schemas.AdminBroadcast,
    db: AsyncSession = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    # This would require integrating with the Bot to send messages.
    # We can either use the bot instance here or push to a queue.
    # For simplicity, we'll just log it or IMPLEMENT simple iteration if loop isn't blocked.
    
    # Ideally, we should import the bot instance, but `bot/main.py` is the entry point. 
    # We should create a shared `bot_instance.py` or similar.
    
    # For now, just a stub
    return {"status": "Broadcast initiated (stub)"}
