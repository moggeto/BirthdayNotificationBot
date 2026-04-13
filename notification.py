from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.session import Session
from app.database.models import NotificationSetting, Birthday
from bot import bot  # Импортируйте экземпляр вашего бота

async def send_birthday_notifications():
    """
    Проверяет дни рождения и отправляет уведомления пользователям.
    """
    session = Session()
    try:
        today = datetime.today()
        all_settings = session.query(NotificationSetting).all()

        for setting in all_settings:
            notify_date = today + timedelta(days=setting.notify_before)

            # Найти дни рождения для notify_date
            birthdays = session.query(Birthday).filter(
                Birthday.user_id == setting.user_id,
                Birthday.day == notify_date.day,
                Birthday.month == notify_date.month
            ).all()

            for birthday in birthdays:
                await bot.send_message(
                    chat_id=setting.user_id,
                    text=f"Напоминание: через {setting.notify_before} дней день рождения у {birthday.first_name} {birthday.last_name}!"
                )
    except Exception as e:
        print(f"Ошибка при отправке уведомлений: {e}")
    finally:
        session.close()


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_birthday_notifications, "cron", hour=1, minute=12)
    scheduler.start()
    print("Scheduler started. Current jobs:")
    for job in scheduler.get_jobs():
        print(job)
