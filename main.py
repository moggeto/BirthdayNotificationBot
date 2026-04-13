import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot import bot, dp
from config import NOTIFICATION_CHECK_HOUR, NOTIFICATION_CHECK_MINUTE
from app.database.session import get_session
from app.database.models import User
from app.handlers import register_handlers
from app.services.sent_notifications import was_sent, mark_as_sent
from app.services.reminders import (
    get_upcoming_birthdays_for_user,
    build_notification_message,
)


logging.basicConfig(level=logging.INFO)

TZ = ZoneInfo("Asia/Jerusalem")


async def send_scheduled_notifications():
    today = datetime.now(TZ).date()
    logging.info("Проверка уведомлений. today=%s", today)

    with get_session() as session:
        users = session.query(User).all()
        logging.info("Найдено пользователей: %s", len(users))

        for user in users:
            birthdays_by_days = get_upcoming_birthdays_for_user(session, user, today=today)

            total_found = sum(len(items) for items in birthdays_by_days.values())
            logging.info(
                "Пользователь %s (%s), найдено подходящих ДР: %s",
                user.id,
                user.telegram_id,
                total_found,
            )

            for days_before, birthdays in birthdays_by_days.items():
                if not birthdays:
                    continue

                for birthday in birthdays:
                    if was_sent(session, user.id, birthday.id, today, days_before):
                        logging.info(
                            "Уведомление уже отправлялось сегодня. user_id=%s birthday_id=%s days_before=%s",
                            user.id,
                            birthday.id,
                            days_before,
                        )
                        continue

                    message_text = build_notification_message([birthday], days_before)

                    if not message_text:
                        continue

                    try:
                        await bot.send_message(chat_id=user.telegram_id, text=message_text)
                        mark_as_sent(session, user.id, birthday.id, today, days_before)
                        logging.info(
                            "Уведомление отправлено пользователю %s для birthday_id=%s days_before=%s",
                            user.telegram_id,
                            birthday.id,
                            days_before,
                        )
                    except Exception as e:
                        logging.exception(
                            "Не удалось отправить уведомление пользователю %s: %s",
                            user.telegram_id,
                            e,
                        )


def setup_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=TZ)
    scheduler.add_job(
        send_scheduled_notifications,
        trigger="cron",
        hour=NOTIFICATION_CHECK_HOUR,
        minute=NOTIFICATION_CHECK_MINUTE,
        timezone=TZ,
        id="birthday_notifications",
        replace_existing=True,
    )
    scheduler.start()

    logging.info(
        "Планировщик уведомлений запущен. Проверка каждый день в %02d:%02d (%s)",
        NOTIFICATION_CHECK_HOUR,
        NOTIFICATION_CHECK_MINUTE,
        TZ,
    )

    for job in scheduler.get_jobs():
        logging.info("Job %s, next run: %s", job.id, job.next_run_time)

    return scheduler


async def main():
    register_handlers(dp)
    scheduler = setup_scheduler()

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())