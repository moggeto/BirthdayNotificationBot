
import asyncio
from app.bot import bot, dp
from app.handlers import register_handlers
from app.database.session import init_db

async def main():
    # Инициализация базы данных
    init_db()

    # Регистрация всех обработчиков
    register_handlers(dp)

    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())