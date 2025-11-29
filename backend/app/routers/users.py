from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas, database

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    db_user = await crud.get_user_by_telegram_id(db, telegram_id=user.telegram_id)
    if db_user:
        return db_user
    return await crud.create_user(db=db, user=user)

@router.get("/{telegram_id}", response_model=schemas.UserResponse)
async def read_user(telegram_id: int = Path(..., ge=1), db: AsyncSession = Depends(database.get_db)):
    db_user = await crud.get_user_by_telegram_id(db, telegram_id=telegram_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
