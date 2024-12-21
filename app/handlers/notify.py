
from aiogram import types, Dispatcher
from aiogram.filters import Command
from app.database.session import Session
from app.database.models import NotificationSetting


async def set_notification_time(message: types.Message):
    """
    Устанавливает количество дней до уведомления для пользователя.
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Используй формат: /set_notify <Дней до уведомления>\nПример: /set_notify 3")
        return

    notify_before = args[1]
    session = Session()

    try:
        notify_before = int(notify_before)
        if notify_before <= 0:
            raise ValueError("Количество дней должно быть больше 0.")

        # Проверяем, есть ли настройка для пользователя
        setting = session.query(NotificationSetting).filter_by(user_id=message.from_user.id).first()
        if setting:
            setting.notify_before = notify_before
        else:
            setting = NotificationSetting(user_id=message.from_user.id, notify_before=notify_before)
            session.add(setting)
        session.commit()

        await message.reply(f"Настройка уведомлений обновлена: за {notify_before} дней до дня рождения.")
    except Exception as e:
        await message.reply("Ошибка при обновлении настройки: " + str(e))
    finally:
        session.close()


def register_notify_handlers(dp: Dispatcher):
    """
    Регистрирует хендлеры для управления уведомлениями.
    """
    dp.message.register(set_notification_time, Command("set_notify"))
