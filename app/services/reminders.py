from datetime import date, datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import selectinload

from app.database.models import (
    Birthday,
    BirthdayDate,
    CalendarType,
    NotificationCalendarMode,
    User,
)
from app.services.birthdays import get_date_by_type
from app.services.hebrew_dates import get_next_gregorian_for_hebrew
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


def get_next_hebrew_occurrence(birthday_date: BirthdayDate, today: date) -> date | None:
    if not birthday_date.h_day or not birthday_date.h_month:
        return None

    return get_next_gregorian_for_hebrew(
        h_day=birthday_date.h_day,
        h_month=birthday_date.h_month,
        h_year=birthday_date.h_year,
        today=today,
    )


def format_birthday_text(birthday: Birthday, date_item: BirthdayDate) -> str:
    full_name = f"{birthday.first_name} {birthday.last_name}".strip()

    if date_item.calendar_type == CalendarType.gregorian:
        date_text = f"{date_item.g_day:02}.{date_item.g_month:02}"
        if date_item.g_year:
            date_text += f".{date_item.g_year}"
        return f"{full_name} — {date_text}"

    month_text = date_item.h_month.value if date_item.h_month else "?"
    date_text = f"{date_item.h_day} {month_text}"
    if date_item.h_year:
        date_text += f" {date_item.h_year}"
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
        mode = birthday.notification_calendar_mode

        date_items: list[BirthdayDate] = []

        gregorian = get_date_by_type(session, birthday.id, CalendarType.gregorian)
        hebrew = get_date_by_type(session, birthday.id, CalendarType.hebrew)

        if mode == NotificationCalendarMode.gregorian:
            if gregorian:
                date_items.append(gregorian)

        elif mode == NotificationCalendarMode.hebrew:
            if hebrew:
                date_items.append(hebrew)

        elif mode == NotificationCalendarMode.both:
            if gregorian:
                date_items.append(gregorian)
            if hebrew:
                date_items.append(hebrew)

        for date_item in date_items:
            if date_item.calendar_type == CalendarType.gregorian:
                next_birthday = get_next_gregorian_occurrence(date_item, today)
            else:
                next_birthday = get_next_hebrew_occurrence(date_item, today)

            if next_birthday is None:
                continue

            days_left = (next_birthday - today).days
            if days_left in result:
                result[days_left].append((birthday, date_item))

    return result


def build_notification_message(
    birthday_items: list[tuple[Birthday, BirthdayDate]],
    days_before: int,
) -> str:
    if not birthday_items:
        return ""

    if len(birthday_items) == 1:
        birthday, date_item = birthday_items[0]
        return (
            f"Напоминание: через {days_before} дн. день рождения у:\n"
            f"{format_birthday_text(birthday, date_item)}"
        )

    lines = [f"Напоминание: через {days_before} дн. дни рождения у:"]
    lines.extend(
        f"- {format_birthday_text(birthday, date_item)}"
        for birthday, date_item in birthday_items
    )
    return "\n".join(lines)