from datetime import date
from app.database.models import SentNotification


def was_sent(session, user_id: int, birthday_id: int, today: date) -> bool:
    return (
        session.query(SentNotification)
        .filter_by(user_id=user_id, birthday_id=birthday_id, date_sent=today)
        .first()
        is not None
    )


def mark_as_sent(session, user_id: int, birthday_id: int, today: date):
    record = SentNotification(
        user_id=user_id,
        birthday_id=birthday_id,
        date_sent=today,
    )
    session.add(record)