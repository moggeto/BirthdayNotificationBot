from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.database.models import Birthday, User
from app.services.notifications import get_notification_days_list


TZ = ZoneInfo("Asia/Jerusalem")


def build_birthday_date_for_year(birthday: Birthday, year: int) -> date | None:
    try:
        return date(year, birthday.month, birthday.day)
    except ValueError:
        return None


def get_next_birthday_date(birthday: Birthday, today: date) -> date | None:
    current_year_birthday = build_birthday_date_for_year(birthday, today.year)

    if current_year_birthday is None:
        return None

    if current_year_birthday >= today:
        return current_year_birthday

    return build_birthday_date_for_year(birthday, today.year + 1)


def format_birthday_text(birthday: Birthday) -> str:
    full_name = f"{birthday.first_name} {birthday.last_name}".strip()
    date_text = f"{birthday.day:02}.{birthday.month:02}"

    if birthday.year:
        return f"{full_name} — {date_text}.{birthday.year}"
    return f"{full_name} — {date_text}"


def get_upcoming_birthdays_for_user(
    session,
    user: User,
    today: date | None = None,
) -> dict[int, list[Birthday]]:
    if today is None:
        today = datetime.now(TZ).date()

    notify_days = get_notification_days_list(session, user, default=[1])

    birthdays = session.query(Birthday).filter_by(user_id=user.id).all()
    result: dict[int, list[Birthday]] = {days: [] for days in notify_days}

    for birthday in birthdays:
        if birthday.calendar_type != "gregorian":
            continue
        next_birthday = get_next_birthday_date(birthday, today)
        if next_birthday is None:
            continue

        days_left = (next_birthday - today).days
        if days_left in result:
            result[days_left].append(birthday)

    return result


def build_notification_message(birthdays: list[Birthday], days_before: int) -> str:
    if not birthdays:
        return ""

    if len(birthdays) == 1:
        return (
            f"Напоминание: через {days_before} дн. день рождения у:\n"
            f"{format_birthday_text(birthdays[0])}"
        )

    lines = [f"Напоминание: через {days_before} дн. дни рождения у:"]
    lines.extend(f"- {format_birthday_text(birthday)}" for birthday in birthdays)
    return "\n".join(lines)