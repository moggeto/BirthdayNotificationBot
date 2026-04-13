from app.database.models import NotificationSetting, User


def get_notification_settings(session, user: User) -> list[NotificationSetting]:
    return (
        session.query(NotificationSetting)
        .filter_by(user_id=user.id)
        .order_by(NotificationSetting.days_before.desc())
        .all()
    )


def get_notification_days_list(session, user: User, default: list[int] | None = None) -> list[int]:
    settings = get_notification_settings(session, user)

    if settings:
        return [setting.days_before for setting in settings]

    return default if default is not None else [1]


def add_notification_day(session, user: User, days_before: int) -> NotificationSetting:
    if days_before <= 0:
        raise ValueError("Количество дней должно быть больше 0.")

    existing = (
        session.query(NotificationSetting)
        .filter_by(user_id=user.id, days_before=days_before)
        .first()
    )
    if existing:
        raise ValueError("Такое уведомление уже существует.")

    setting = NotificationSetting(user_id=user.id, days_before=days_before)
    session.add(setting)
    session.flush()
    return setting


def remove_notification_day(session, user: User, days_before: int) -> bool:
    setting = (
        session.query(NotificationSetting)
        .filter_by(user_id=user.id, days_before=days_before)
        .first()
    )

    if not setting:
        return False

    session.delete(setting)
    session.flush()
    return True


def format_notification_days(days_list: list[int]) -> str:
    if not days_list:
        return "нет"

    return ", ".join(str(day) for day in sorted(days_list, reverse=True))