import os
from dotenv import load_dotenv
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from filters.chat_types import ChatTypeFilter
from commands.login import create_employee, exit_employee
import markups as nav
from utils.keyboard import show_channel

# Роутер для приватных каналов
private_channel_router = Router()
private_channel_router.message.filter(ChatTypeFilter(['private']))

load_dotenv()
CHANNEL_ID = os.getenv('CHANNEL_ID')

async def check_sub_channels(user_id, bot):
    chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    if chat_member.status == 'left':
        return False
    return True

@private_channel_router.message(CommandStart())
async def send_welcome(message: types.Message):
    if await check_sub_channels(message.from_user.id, message.bot):
        await message.answer(f'Привет, {message.from_user.first_name}!')
    else:
        await message.bot.send_message(message.from_user.id,  'Для доступа, подпишитесь и дождитесь подтверждения',
                                       reply_markup=nav.show_channel())




@private_channel_router.message(Command('show_payment'))
@private_channel_router.message(F.text.lower().contains('оплат'))
async def show_payment(message: types.Message):
    await message.answer('1')
    await message.answer('2')


# Обработчики для новых участников и вышедших участников
@private_channel_router.chat_member()
async def handle_chat_member_update(update: types.ChatMemberUpdated):
    # Обработка нового участника
    if update.new_chat_member.status == 'member':
        create_employee(update.new_chat_member.user)
        await welcome_new_member(update)

    # Обработка вышедшего участника
    elif update.new_chat_member.status in ['left', 'kicked']:
        exit_employee(update.new_chat_member.user.id)
        await handle_user_removal(update.new_chat_member.user)


async def welcome_new_member(update: types.ChatMemberUpdated):
    new_member = update.new_chat_member.user
    # Отправляем приветственное сообщение
    await update.bot.send_message(
        chat_id=update.chat.id,
        text=f"Добро пожаловать в наш приватный канал, {new_member.first_name}!"
    )


async def handle_user_removal(user: types.User):
    # Логика, связанная с удалением пользователя
    print(f"Пользователь {user.id} ({user.username}) покинул приватный канал.")
