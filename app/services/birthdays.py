from app.database.models import Birthday, BirthdayDate, CalendarType, User


def split_name(full_name: str):
    parts = full_name.strip().split(maxsplit=1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def create_birthday_with_gregorian(
    session,
    user: User,
    full_name: str,
    day: int,
    month: int,
    year: int | None,
    description: str,
):
    first_name, last_name = split_name(full_name)

    birthday = Birthday(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        day=day,
        month=month,
        year=year,
        description=description,
        calendar_type="gregorian",
    )
    session.add(birthday)
    session.flush()

    date = BirthdayDate(
        birthday_id=birthday.id,
        calendar_type=CalendarType.gregorian,
        g_day=day,
        g_month=month,
        g_year=year,
    )

    session.add(date)
    session.flush()

    return birthday