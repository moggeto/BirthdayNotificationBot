from app.database.models import NotificationSetting, User


def get_notification_days_list(session, user: User, default: list[int] | None = None) -> list[int]:
    settings = (
        session.query(NotificationSetting)
        .filter(NotificationSetting.user_id == user.id)
        .order_by(NotificationSetting.days_before.asc())
        .all()
    )

    if settings:
        return [item.days_before for item in settings]

    if default:
        created = []
        for day in sorted(set(default)):
            setting = NotificationSetting(user_id=user.id, days_before=day)
            session.add(setting)
            created.append(day)

        session.flush()
        return created

    return []


def add_notification_day(session, user: User, days_before: int) -> None:
    if days_before <= 0:
        raise ValueError("Количество дней должно быть больше 0.")

    existing = (
        session.query(NotificationSetting)
        .filter_by(user_id=user.id, days_before=days_before)
        .first()
    )
    if existing:
        raise ValueError(f"Уведомление за {days_before} дн. уже существует.")

    session.add(NotificationSetting(user_id=user.id, days_before=days_before))
    session.flush()


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
        return "не настроено"
    return ", ".join(str(day) for day in sorted(days_list))