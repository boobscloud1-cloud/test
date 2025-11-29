from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app import crud, schemas, database, models
import secrets

router = APIRouter(
    prefix="/game",
    tags=["game"]
)

# Prize Config (Should be in DB or Config for production)
# Format: (Type, Value, Probability, Angle)
PRIZES = [
    ("spins", "1", 0.3, 0),
    ("points", "100", 0.3, 45),
    ("points", "500", 0.2, 90),
    ("spins", "5", 0.1, 135),
    ("item", "iphone", 0.001, 180), # Jackpot
    ("points", "50", 0.099, 225),
    ("spins", "2", 0.0, 270), # Placeholder
    ("points", "1000", 0.0, 315) # Placeholder
]

COST_PER_SPIN = 1000

@router.post("/spin", response_model=schemas.SpinResult)
async def spin_wheel(telegram_id: int = Query(..., ge=1), db: AsyncSession = Depends(database.get_db)):
    # Atomic decrement of spins (prevents race conditions)
    result = await db.execute(
        update(models.User)
        .where(models.User.telegram_id == telegram_id, models.User.spins > 0)
        .values(spins=models.User.spins - 1)
    )
    if result.rowcount == 0:
        # Determine if no user or no spins to provide accurate error
        user_check = await crud.get_user_by_telegram_id(db, telegram_id)
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=400, detail="No spins available")

    # Secure RNG-based prize selection with integer weights to avoid float drift
    PROB_SCALE = 1_000_000
    weights = [int(p[2] * PROB_SCALE) for p in PRIZES]
    total = sum(weights)
    if total <= 0:
        selected_index = len(PRIZES) - 1
    else:
        r = secrets.randbelow(total)
        cum = 0
        selected_index = len(PRIZES) - 1
        for i, w in enumerate(weights):
            cum += w
            if r < cum:
                selected_index = i
                break

    prize_type, prize_value, _, base_angle = PRIZES[selected_index]
    # 5..40 degrees offset to avoid wedge separators
    random_offset = 5 + secrets.randbelow(36)
    final_angle = (base_angle + random_offset) % 360

    # Fetch user (post-decrement) and log reward
    user = await crud.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reward = models.Reward(user_id=user.id, prize_type=prize_type, prize_value=prize_value)
    db.add(reward)

    # Apply prize atomically
    if prize_type == "spins":
        add_amount = int(prize_value)
        await db.execute(
            update(models.User)
            .where(models.User.id == user.id)
            .values(spins=models.User.spins + add_amount)
        )
    elif prize_type == "points":
        add_points = float(prize_value)
        await db.execute(
            update(models.User)
            .where(models.User.id == user.id)
            .values(points=models.User.points + add_points)
        )

    await db.commit()
    await db.refresh(user)

    return schemas.SpinResult(
        prize_type=prize_type,
        prize_value=prize_value,
        remaining_spins=user.spins,
        angle=final_angle
    )

@router.post("/buy_spins", response_model=schemas.PurchaseResult)
async def buy_spins(
    telegram_id: int = Query(..., ge=1),
    amount: int = Query(1, ge=1, le=1000),
    db: AsyncSession = Depends(database.get_db)
):
    user = await crud.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total_cost = COST_PER_SPIN * amount

    # Atomic points deduction if sufficient
    result = await db.execute(
        update(models.User)
        .where(models.User.id == user.id, models.User.points >= total_cost)
        .values(points=models.User.points - total_cost)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=400, detail="Insufficient points")

    # Increment spins
    await db.execute(
        update(models.User)
        .where(models.User.id == user.id)
        .values(spins=models.User.spins + amount)
    )

    await db.commit()
    await db.refresh(user)

    return schemas.PurchaseResult(
        spins_purchased=amount,
        remaining_spins=user.spins,
        remaining_points=user.points
    )
