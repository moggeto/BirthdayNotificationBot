from app.database.models import NotificationSetting, User


def set_notification_days(session, user: User, notify_before: int) -> NotificationSetting:
    if notify_before <= 0:
        raise ValueError("Количество дней должно быть больше 0.")

    setting = session.query(NotificationSetting).filter_by(user_id=user.id).first()

    if setting:
        setting.notify_before = notify_before
        return setting

    setting = NotificationSetting(user_id=user.id, notify_before=notify_before)
    session.add(setting)
    session.flush()
    return setting


def get_notification_setting(session, user: User) -> NotificationSetting | None:
    return session.query(NotificationSetting).filter_by(user_id=user.id).first()


def get_notification_days(session, user: User, default: int = 1) -> int:
    setting = get_notification_setting(session, user)
    return setting.notify_before if setting else default


def get_all_notification_settings(session) -> list[NotificationSetting]:
    return session.query(NotificationSetting).all()