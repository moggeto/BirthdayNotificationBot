from app.database.models import DateDisplayFormat, User


def get_date_display_format(session, user: User) -> DateDisplayFormat:
    if not user.date_display_format:
        user.date_display_format = DateDisplayFormat.gregorian
        session.flush()

    return user.date_display_format


def set_date_display_format(session, user: User, value: DateDisplayFormat) -> DateDisplayFormat:
    user.date_display_format = value
    session.flush()
    return user.date_display_format


def format_date_display_label(value: DateDisplayFormat) -> str:
    mapping = {
        DateDisplayFormat.gregorian: "Только григорианская",
        DateDisplayFormat.hebrew: "Только еврейская",
        DateDisplayFormat.both: "Обе даты",
    }
    return mapping[value]