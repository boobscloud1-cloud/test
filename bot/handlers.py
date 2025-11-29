import logging
from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import AsyncSessionLocal
from app import crud, schemas
from app.models import Referral
from bot.keyboards import get_main_menu_keyboard
from app.config import settings
from sqlalchemy import func
from app.models import User, TaskCompletion, Task

router = Router()

async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

def is_admin(telegram_id: int) -> bool:
    admin_ids = [int(id_str.strip()) for id_str in settings.ADMIN_IDS.split(",") if id_str.strip()]
    return telegram_id in admin_ids

@router.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject):
    """
    This handler receives messages with `/start` command
    """
    telegram_id = message.from_user.id
    username = message.from_user.username
    
    # Extract referral code if present (e.g., /start ref_123)
    args = command.args
    referrer_id = None
    
    if args and args.startswith("ref_"):
        try:
            referrer_id_str = args.replace("ref_", "")
            referrer_id = int(referrer_id_str)
        except ValueError:
            logging.warning(f"Invalid referral code: {args}")

    async with AsyncSessionLocal() as db:
        # Check if user exists
        user = await crud.get_user_by_telegram_id(db, telegram_id)
        
        if not user:
            # Create new user
            user_create = schemas.UserCreate(
                telegram_id=telegram_id,
                username=username
            )
            user = await crud.create_user(db, user_create)
            logging.info(f"New user created: {telegram_id}")
            
            # Handle Referral
            if referrer_id and referrer_id != user.id:
                # Check if referrer exists
                referrer = await crud.get_user(db, referrer_id)
                if referrer:
                    # Create Referral record
                    new_referral = Referral(
                        referrer_id=referrer.id,
                        referred_id=user.id,
                        is_qualified=False
                    )
                    db.add(new_referral)
                    await db.commit()
                    logging.info(f"Referral registered: {referrer_id} -> {user.id}")
    
    await message.answer(
        f"Hello, {message.from_user.full_name}! 👋\n\n"
        "Welcome to the Wheel of Fortune! 🎡\n"
        "Spin the wheel, complete tasks, and win amazing prizes!",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("stats"))
async def command_stats_handler(message: Message):
    if not is_admin(message.from_user.id):
        return # Ignore non-admins

    async with AsyncSessionLocal() as db:
        # Total Users
        result_users = await db.execute(func.count(User.id))
        total_users = result_users.scalar()
        
        await message.answer(f"📊 <b>Statistics</b>\n\nTotal Users: {total_users}")

@router.message(Command("broadcast"))
async def command_broadcast_handler(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return

    text = command.args
    if not text:
        await message.answer("Usage: /broadcast <message>")
        return

    # In a real app, queue this task or iterate carefully.
    # For now, simplistic iteration (beware of limits)
    async with AsyncSessionLocal() as db:
        # Get all users (LIMIT for safety in dev)
        # users_res = await db.execute(select(User.telegram_id).limit(100))
        # users = users_res.scalars().all()
        # count = 0
        # for uid in users:
        #     try:
        #         await message.bot.send_message(uid, text)
        #         count += 1
        #     except:
        #         pass
        pass
    
    await message.answer(f"📢 Broadcast initiated (stub).")
