import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from dotenv import load_dotenv

from create_bot import ADMIN_ID
from handlers.user_private import user_private_router
from handlers.group import group_private_router
from handlers.сhanel import private_channel_router
from commands.schedule import *
from utils.bot_cmds_list import PRIVATE

load_dotenv()

ALLOWED_UPDATES = ['message', 'edited_message']

token = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(bot=bot, storage=MemoryStorage())

# dp.include_router(private_channel_router)
dp.include_routers(user_private_router)
dp.include_router(group_private_router)



async def main():
    await bot.delete_webhook()
    await bot.set_my_commands(commands=PRIVATE, scope=types.BotCommandScopeAllPrivateChats())
    asyncio.create_task(send_good_morning(bot, GROUP_ID))
    asyncio.create_task(send_hourly_message(bot, GROUP_ID))
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


if __name__ == '__main__':
    asyncio.run(main())