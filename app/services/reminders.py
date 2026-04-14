from datetime import date, datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import selectinload

from app.database.models import Birthday, BirthdayDate, CalendarType, User
from app.services.notifications import get_notification_days_list


TZ = ZoneInfo("Asia/Jerusalem")


def build_gregorian_date_for_year(birthday_date: BirthdayDate, year: int) -> date | None:
    if not birthday_date.g_day or not birthday_date.g_month:
        return None

    try:
        return date(year, birthday_date.g_month, birthday_date.g_day)
    except ValueError:
        return None


def get_next_gregorian_occurrence(birthday_date: BirthdayDate, today: date) -> date | None:
    current_year_birthday = build_gregorian_date_for_year(birthday_date, today.year)

    if current_year_birthday is None:
        return None

    if current_year_birthday >= today:
        return current_year_birthday

    return build_gregorian_date_for_year(birthday_date, today.year + 1)


def get_gregorian_date(birthday: Birthday) -> BirthdayDate | None:
    for item in birthday.dates:
        if item.calendar_type == CalendarType.gregorian:
            return item
    return None


def format_birthday_text(birthday: Birthday, birthday_date: BirthdayDate) -> str:
    full_name = f"{birthday.first_name} {birthday.last_name}".strip()
    date_text = f"{birthday_date.g_day:02}.{birthday_date.g_month:02}"

    if birthday_date.g_year:
        return f"{full_name} — {date_text}.{birthday_date.g_year}"
    return f"{full_name} — {date_text}"


def get_upcoming_birthdays_for_user(
    session,
    user: User,
    today: date | None = None,
) -> dict[int, list[tuple[Birthday, BirthdayDate]]]:
    if today is None:
        today = datetime.now(TZ).date()

    notify_days = get_notification_days_list(session, user, default=[1])

    birthdays = (
        session.query(Birthday)
        .options(selectinload(Birthday.dates))
        .filter_by(user_id=user.id)
        .all()
    )

    result: dict[int, list[tuple[Birthday, BirthdayDate]]] = {
        days: [] for days in notify_days
    }

    for birthday in birthdays:
        gregorian_date = get_gregorian_date(birthday)
        if not gregorian_date:
            continue

        next_birthday = get_next_gregorian_occurrence(gregorian_date, today)
        if next_birthday is None:
            continue

        days_left = (next_birthday - today).days
        if days_left in result:
            result[days_left].append((birthday, gregorian_date))

    return result


def build_notification_message(
    birthday_items: list[tuple[Birthday, BirthdayDate]],
    days_before: int,
) -> str:
    if not birthday_items:
        return ""

    if len(birthday_items) == 1:
        birthday, birthday_date = birthday_items[0]
        return (
            f"Напоминание: через {days_before} дн. день рождения у:\n"
            f"{format_birthday_text(birthday, birthday_date)}"
        )

    lines = [f"Напоминание: через {days_before} дн. дни рождения у:"]
    lines.extend(
        f"- {format_birthday_text(birthday, birthday_date)}"
        for birthday, birthday_date in birthday_items
    )
    return "\n".join(lines)