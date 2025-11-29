from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app import models, schemas

async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    result = await db.execute(select(models.User).where(models.User.telegram_id == telegram_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    # DEV MODE: Give 5 free spins to new users
    db_user = models.User(telegram_id=user.telegram_id, username=user.username, spins=5)
    db.add(db_user)
    
    if user.referrer_id:
        # Check validity of referrer
        result = await db.execute(select(models.User).where(models.User.id == user.referrer_id))
        referrer = result.scalars().first()
        if referrer:
            db_referral = models.Referral(referrer_id=referrer.id, referred_id=db_user.id) # Note: ID not generated yet, might need flush
            # Referral logic usually needs user ID, so we commit first or flush
            await db.flush() 
            # Re-bind if needed, but usually handled by ORM if relationships set correctly
            # Here we need explicit ID for db_referral
            db_referral = models.Referral(referrer_id=referrer.id, referred_id=db_user.id)
            db.add(db_referral)

    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()

async def add_spins(db: AsyncSession, user_id: int, amount: int):
    """
    Atomic spin increment without committing; caller manages the transaction.
    """
    await db.execute(
        update(models.User)
        .where(models.User.id == user_id)
        .values(spins=models.User.spins + amount)
    )
    # Do not commit here; maintain atomicity at the caller level
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()

async def complete_task(db: AsyncSession, user_id: int, task_id: int, transaction_id: str, reward_amount: int):
    # Check duplicate
    result = await db.execute(select(models.TaskCompletion).where(models.TaskCompletion.transaction_id == transaction_id))
    if result.scalars().first():
        return None # Already processed

    # Record completion
    completion = models.TaskCompletion(user_id=user_id, task_id=task_id, transaction_id=transaction_id)
    db.add(completion)

    # Award spins
    await add_spins(db, user_id, reward_amount)
    
    # Check referral qualification
    # Find if this user was referred
    result = await db.execute(select(models.Referral).where(models.Referral.referred_id == user_id))
    referral = result.scalars().first()
    if referral and not referral.is_qualified:
        referral.is_qualified = True
        # Award referrer
        await add_spins(db, referral.referrer_id, 3) # Example: 3 spins for qualified referral
    
    await db.commit()
    return completion
