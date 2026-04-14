from app.database.models import Birthday, BirthdayDate, CalendarType, User
from app.services.hebrew_dates import convert_gregorian_to_hebrew


def split_name(full_name: str) -> tuple[str, str]:
    cleaned = (full_name or "").strip()
    if not cleaned:
        raise ValueError("Имя не может быть пустым.")

    parts = cleaned.split(maxsplit=1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name


def create_birthday_with_gregorian(
    session,
    user: User,
    full_name: str,
    day: int,
    month: int,
    year: int | None,
    description: str,
) -> Birthday:
    first_name, last_name = split_name(full_name)

    existing = (
        session.query(Birthday)
        .filter_by(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
        )
        .first()
    )
    if existing:
        raise ValueError("Человек с таким именем уже существует.")

    birthday = Birthday(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        description=description or "",
    )
    session.add(birthday)
    session.flush()

    gregorian_date = BirthdayDate(
        birthday_id=birthday.id,
        calendar_type=CalendarType.gregorian,
        g_day=day,
        g_month=month,
        g_year=year,
    )
    session.add(gregorian_date)
    session.flush()

    if year is not None:
        hebrew_result = convert_gregorian_to_hebrew(
            day=day,
            month=month,
            year=year,
        )

        hebrew_date = BirthdayDate(
            birthday_id=birthday.id,
            calendar_type=CalendarType.hebrew,
            h_day=hebrew_result.day,
            h_month=hebrew_result.month,
            h_year=hebrew_result.year,
            adar_rule=hebrew_result.adar_rule,
        )
        session.add(hebrew_date)
        session.flush()

    return birthday


def create_birthday(
    session,
    user: User,
    full_name: str,
    day: int,
    month: int,
    year: int | None,
    description: str,
) -> Birthday:
    return create_birthday_with_gregorian(
        session=session,
        user=user,
        full_name=full_name,
        day=day,
        month=month,
        year=year,
        description=description,
    )