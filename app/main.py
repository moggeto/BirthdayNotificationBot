# import asyncio
# from aiogram import Dispatcher
# from app.bot import dp
# from app.database.session import init_db
# # from app.jobs.scheduler import start_scheduler
#
#
#
# async def main():
#     init_db()
#
#     # Регистрация хендлеров
#     register_handlers(dp)
#
#     # Запуск polling
#     await dp.start_polling(bot)
#
# if __name__ == "__main__":
#     asyncio.run(main())
#
# # if __name__ == "__main__":
# #     init_db()
# #     # start_scheduler()
# #     Dispatcher.start_polling(dp, skip_updates=True)
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