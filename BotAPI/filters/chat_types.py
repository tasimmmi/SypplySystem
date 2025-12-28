from aiogram import types, Bot
from aiogram.types import ChatMemberMember
from aiogram.filters import Filter
from dotenv import load_dotenv

import os

load_dotenv()


GROUP_ID = os.getenv('GROUP_ID')

class ChatTypeFilter(Filter):
    def __init__(self, chat_type: list[str]) -> None:
        self.chat_type = chat_type
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_type

class IsGroupMember(Filter):
    def __init__(self):
        self.group_id = GROUP_ID

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        try:
            # Получаем информацию о членстве пользователя в группе
            chat_member = await bot.get_chat_member(
                chat_id=self.group_id,
                user_id=message.from_user.id
            )
            # Проверяем, что пользователь является участником (не left/kicked)
            return isinstance(chat_member, ChatMemberMember) or chat_member.status in ['member', 'administrator', 'creator']
        except Exception:
            # Если произошла ошибка (например, пользователь не найден в группе)
            return False
