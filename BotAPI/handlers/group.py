from aiogram import types, Router, F
from aiogram.enums import ChatType
from aiogram.filters import CommandStart, Command
from filters.chat_types import ChatTypeFilter
from commands.report import report_payments, report_delivery

from commands.login import create_employee, exit_employee
import os
from dotenv import load_dotenv

group_private_router = Router()
group_private_router.message.filter(ChatTypeFilter(['group']))

load_dotenv()

ALLOWED_UPDATES = ['message', 'edited_message']

token = os.getenv('BOT_TOKEN')

@group_private_router.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer(f'Привет, {message.from_user.first_name}!')

@group_private_router.message(Command('show_payment'))
@group_private_router.message(F.text.lower().contains('оплат'))
async def show_payment(message: types.Message):
    await message.answer('1')
    await message.answer('2')

@group_private_router.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    for new_member in message.new_chat_members:
        create_employee(new_member)


@group_private_router.message(lambda message: message.left_chat_member is not None)
async def farewell_member(message: types.Message):
    exit_employee(message.left_chat_member.id)
    left_member = message.left_chat_member
    await handle_user_removal(left_member)


async def handle_user_removal(user):
    # Логика, связанная с удалением пользователя
    print(f"Пользователь {user.id} ({user.username}) был удален из группы.")
