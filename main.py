from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import logging
from handlers import user, admin
from models.database import init_db

TOKEN = "8075810325:AAFBRhW3wNIZEHWDoBcGHmocjQV6_dgxxRo"  # Замените на ваш реальный токен
ADMIN_IDS = [473088323]   # Укажите ID администратора (продавца)

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    await init_db()

    user.register(dp)
    admin.register(dp, ADMIN_IDS)

    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
