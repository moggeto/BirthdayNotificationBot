from datetime import date

from app.database.models import SentNotification


def was_sent(
    session,
    user_id: int,
    birthday_date_id: int,
    today: date,
    days_before: int,
) -> bool:
    return (
        session.query(SentNotification)
        .filter_by(
            user_id=user_id,
            birthday_date_id=birthday_date_id,
            date_sent=today,
            days_before=days_before,
        )
        .first()
        is not None
    )


def mark_as_sent(
    session,
    user_id: int,
    birthday_date_id: int,
    today: date,
    days_before: int,
):
    record = SentNotification(
        user_id=user_id,
        birthday_date_id=birthday_date_id,
        date_sent=today,
        days_before=days_before,
    )
    session.add(record)
    session.flush()