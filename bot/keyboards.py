from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.config import settings

def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎰 Play Now",
                web_app=WebAppInfo(url=settings.WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(text="📢 Join Community", url="https://t.me/your_community_channel")
        ]
    ])
    return keyboard
