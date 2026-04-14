from sqlalchemy.orm import selectinload

from app.database.models import (
    Birthday,
    BirthdayDate,
    CalendarType,
    NotificationCalendarMode,
    User,
    HebrewMonth,
    AdarRule,
)
from app.services.birthdays import (
    split_name,
    get_date_by_type,
    add_gregorian_date_to_birthday,
    add_hebrew_date_to_birthday,
    sync_derived_hebrew_from_gregorian,
)
from app.services.hebrew_dates import validate_hebrew_date


def get_birthdays_for_management(session, user: User) -> list[Birthday]:
    birthdays = (
        session.query(Birthday)
        .options(selectinload(Birthday.dates))
        .filter_by(user_id=user.id)
        .all()
    )

    def sort_key(item: Birthday):
        gregorian = get_date_by_type(item, CalendarType.gregorian)
        month = gregorian.g_month if gregorian and gregorian.g_month else 99
        day = gregorian.g_day if gregorian and gregorian.g_day else 99
        return (
            item.first_name.lower(),
            item.last_name.lower(),
            month,
            day,
        )

    return sorted(birthdays, key=sort_key)


def get_birthday_by_id_for_user(session, user: User, birthday_id: int) -> Birthday | None:
    return (
        session.query(Birthday)
        .options(selectinload(Birthday.dates))
        .filter_by(id=birthday_id, user_id=user.id)
        .first()
    )


def has_duplicate_name_except_self(
    session,
    user: User,
    birthday_id: int,
    first_name: str,
    last_name: str,
) -> bool:
    duplicate = (
        session.query(Birthday)
        .filter(
            Birthday.user_id == user.id,
            Birthday.first_name == first_name,
            Birthday.last_name == last_name,
            Birthday.id != birthday_id,
        )
        .first()
    )
    return duplicate is not None


def delete_birthday_by_id(session, user: User, birthday_id: int) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    session.delete(birthday)
    session.flush()
    return birthday


def delete_birthday_date(
    session,
    user: User,
    birthday_id: int,
    calendar_type: CalendarType,
) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    date_item = get_date_by_type(birthday, calendar_type)
    if not date_item:
        raise ValueError("Дата этого типа не найдена.")

    session.delete(date_item)
    session.flush()

    refreshed = get_birthday_by_id_for_user(session, user, birthday_id)
    if not refreshed:
        return None

    if not refreshed.dates:
        session.delete(refreshed)
        session.flush()
        return None

    if refreshed.notification_calendar_mode == NotificationCalendarMode.both and len(refreshed.dates) == 1:
        remaining = refreshed.dates[0]
        refreshed.notification_calendar_mode = remaining.calendar_type.value

    elif refreshed.notification_calendar_mode == calendar_type.value:
        remaining = refreshed.dates[0]
        refreshed.notification_calendar_mode = remaining.calendar_type.value

    session.flush()
    return get_birthday_by_id_for_user(session, user, birthday_id)


def update_birthday_name(session, user: User, birthday_id: int, full_name: str) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    first_name, last_name = split_name(full_name)

    if has_duplicate_name_except_self(
        session=session,
        user=user,
        birthday_id=birthday.id,
        first_name=first_name,
        last_name=last_name,
    ):
        raise ValueError("Такая запись уже существует.")

    birthday.first_name = first_name
    birthday.last_name = last_name
    session.flush()
    return get_birthday_by_id_for_user(session, user, birthday_id)


def update_birthday_description(session, user: User, birthday_id: int, description: str) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    birthday.description = (description or "").strip()
    session.flush()
    return get_birthday_by_id_for_user(session, user, birthday_id)


def update_notification_calendar_mode(
    session,
    user: User,
    birthday_id: int,
    mode: NotificationCalendarMode,
) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    has_gregorian = get_date_by_type(birthday, CalendarType.gregorian) is not None
    has_hebrew = get_date_by_type(birthday, CalendarType.hebrew) is not None

    if mode == NotificationCalendarMode.gregorian and not has_gregorian:
        raise ValueError("Нельзя выбрать григорианские уведомления: такой даты нет.")

    if mode == NotificationCalendarMode.hebrew and not has_hebrew:
        raise ValueError("Нельзя выбрать еврейские уведомления: такой даты нет.")

    if mode == NotificationCalendarMode.both and not (has_gregorian and has_hebrew):
        raise ValueError("Режим both доступен только когда у записи есть обе даты.")

    birthday.notification_calendar_mode = mode
    session.flush()
    return get_birthday_by_id_for_user(session, user, birthday_id)


def add_gregorian_date(
    session,
    user: User,
    birthday_id: int,
    day: int,
    month: int,
    year: int | None,
    *,
    auto_create_hebrew_if_possible: bool = False,
) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    add_gregorian_date_to_birthday(session, birthday, day, month, year)

    if auto_create_hebrew_if_possible and year is not None and not get_date_by_type(birthday, CalendarType.hebrew):
        sync_derived_hebrew_from_gregorian(session, birthday)

    session.flush()
    return get_birthday_by_id_for_user(session, user, birthday_id)


def add_hebrew_date(
    session,
    user: User,
    birthday_id: int,
    day: int,
    month: HebrewMonth,
    year: int | None,
    *,
    adar_rule: AdarRule = AdarRule.regular_to_adar_ii,
    is_derived: bool = False,
) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    validate_hebrew_date(day, month, year)
    add_hebrew_date_to_birthday(
        session=session,
        birthday=birthday,
        day=day,
        month=month,
        year=year,
        adar_rule=adar_rule,
        is_derived=is_derived,
    )

    session.flush()
    return get_birthday_by_id_for_user(session, user, birthday_id)


def update_gregorian_date(
    session,
    user: User,
    birthday_id: int,
    day: int,
    month: int,
) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    gregorian = get_date_by_type(birthday, CalendarType.gregorian)
    if not gregorian:
        raise ValueError("У записи нет григорианской даты.")

    gregorian.g_day = day
    gregorian.g_month = month
    session.flush()

    sync_derived_hebrew_from_gregorian(session, birthday)
    return get_birthday_by_id_for_user(session, user, birthday_id)


def update_gregorian_year(
    session,
    user: User,
    birthday_id: int,
    year: int | None,
) -> Birthday | None:
    if year is not None and year <= 0:
        raise ValueError("Год должен быть положительным.")

    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    gregorian = get_date_by_type(birthday, CalendarType.gregorian)
    if not gregorian:
        raise ValueError("У записи нет григорианской даты.")

    gregorian.g_year = year
    session.flush()

    sync_derived_hebrew_from_gregorian(session, birthday)
    return get_birthday_by_id_for_user(session, user, birthday_id)


def update_hebrew_date(
    session,
    user: User,
    birthday_id: int,
    day: int,
    month: HebrewMonth,
    year: int | None,
    *,
    adar_rule: AdarRule = AdarRule.regular_to_adar_ii,
) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    hebrew = get_date_by_type(birthday, CalendarType.hebrew)
    if not hebrew:
        raise ValueError("У записи нет еврейской даты.")

    validate_hebrew_date(day, month, year)

    hebrew.h_day = day
    hebrew.h_month = month
    hebrew.h_year = year
    hebrew.adar_rule = adar_rule
    hebrew.is_derived = False

    session.flush()
    return get_birthday_by_id_for_user(session, user, birthday_id)