import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Adjust path to include backend
import os
import sys
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(os.path.dirname(current_dir), 'backend')
env_path = os.path.join(backend_dir, '.env')

# Load .env explicitly before importing settings
load_dotenv(env_path)

# Add backend directory to path (for app imports)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Add project root directory to path (for bot imports if running from inside bot folder)
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Fix database path to be absolute to avoid relative path issues
# This ensures the bot connects to the correct backend/app.db regardless of CWD
db_path = os.path.join(backend_dir, 'app.db')
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"

# Handle import differences based on run location
try:
    from bot.handlers import router
except ImportError:
    # Fallback if running directly inside bot folder without package context
    from handlers import router

from app.config import settings

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # And the run events dispatching
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
