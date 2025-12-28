import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = os.getenv('ADMIN_ID')
BOT_TOKEN = os.getenv("BOT_TOKEN")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
WEBHOOK_PATH = f'/{BOT_TOKEN}'
BASE_URL = os.getenv("BASE_URL")


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()