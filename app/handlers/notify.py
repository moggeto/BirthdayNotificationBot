from aiogram import types, Dispatcher
from aiogram.filters import Command

from app.database.session import get_session
from app.services.notifications import set_notification_days
from app.services.users import get_or_create_user


async def set_notification_time(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Используй формат: /set_notify <дней>\nПример: /set_notify 3")
        return

    try:
        notify_before = int(args[1])

        with get_session() as session:
            user = get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
            )
            set_notification_days(session, user, notify_before)

        await message.reply(
            f"Настройка уведомлений обновлена: за {notify_before} дней до дня рождения."
        )

    except ValueError as e:
        await message.reply(str(e))
    except Exception as e:
        await message.reply("Ошибка при обновлении настройки: " + str(e))


def register_notify_handlers(dp: Dispatcher):
    dp.message.register(set_notification_time, Command("set_notify"))