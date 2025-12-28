from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from filters.chat_types import ChatTypeFilter, IsGroupMember
from commands.report import report_payments, report_delivery, report_payments_user, report_delivery_user
from commands.login import start_employee

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']), IsGroupMember())

@user_private_router.message(CommandStart())
async def send_welcome(message: types.Message):
    login, password = start_employee(message.from_user)
    if login:
        await message.answer(f'Ваш логин: {login}\nВаш пароль: {password}')
    else: await message.answer("Простите, {}, но вы не работает в отделе снабжения".format(message.from_user.first_name))

@user_private_router.message(Command('show_payment'))
@user_private_router.message(F.text.lower().contains('оплат'))
async def show_payment(message: types.Message):
    overdue, actual, today = report_payments_user(message.from_user.id)
    print(overdue, actual, today)
    if overdue:
        await message.answer(overdue)
    if actual:
        await message.answer(actual)
    if today:
        await message.answer(today)
    if actual is None and overdue is None and today is None:
        await message.answer('Записи отсуствуют')

@user_private_router.message(Command('show_supplies'))
@user_private_router.message(F.text.lower().contains('постав'))
async def show_supplies(message: types.Message):
    overdue, actual = report_delivery_user(message.from_user.id)
    if overdue != '':
        await message.answer(overdue)
    if actual != '':
        await message.answer(actual)
    if actual=='' and overdue=='':
        await message.answer('Записи отсуствуют')



