import asyncio
import logging
from aiogram import Bot
from datetime import datetime, timedelta, time

from commands.report import report_payments

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_good_morning(bot: Bot, chat_id: str):
    while True:
        now = datetime.now()

        target_time = time(18, 40)
        if now.time() > target_time:
            next_day = now.date() + timedelta(days=1)
            next_time = datetime.combine(next_day, target_time)
        else:
            next_time = datetime.combine(now.date(), target_time)

        wait_seconds = (next_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        try:
            overdue, actual, today = report_payments()
            if overdue:
                await bot.send_message(chat_id, overdue)
            if actual:
                await bot.send_message(chat_id, actual)
            if today:
                await bot.send_message(chat_id, actual)
            logger.info("Отправлено утреннее сообщение")
        except Exception as e:
            logger.error(f"Ошибка отправки утреннего сообщения: {e}")


async def send_hourly_message(bot: Bot, chat_id: str):
    """Отправляет сообщение каждый час в HH:00"""
    while True:
        now = datetime.now()
        next_hour = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        wait_seconds = (next_hour - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        current_time = datetime.now().strftime("%H:%M")
        try:
            # Используем переданный экземпляр bot
            await bot.send_message(chat_id, f"Сейчас {current_time} ⏰")
            logger.info(f"Отправлено часовое сообщение: {current_time}")
        except Exception as e:
            logger.error(f"Ошибка отправки часового сообщения: {e}")
