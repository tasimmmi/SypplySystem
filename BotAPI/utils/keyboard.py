from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import os
from dotenv import load_dotenv

load_dotenv()
CHANNEL_ID = os.getenv('CHANNEL_ID')

def show_channel():
    keyboard = InlineKeyboardMarkup(row_width=1)

    for channel in CHANNEL_ID:
        btn = InlineKeyboardButton(text=channel[0], url=channel[2])
        keyboard.insert(btn)
