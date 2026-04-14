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
from app.services.hebrew_dates import convert_gregorian_to_hebrew, validate_hebrew_date


def split_name(full_name: str) -> tuple[str, str]:
    cleaned = (full_name or "").strip()
    if not cleaned:
        raise ValueError("Имя не может быть пустым.")

    parts = cleaned.split(maxsplit=1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name


def get_birthday_with_dates(session, birthday_id: int) -> Birthday:
    birthday = (
        session.query(Birthday)
        .options(selectinload(Birthday.dates))
        .filter(Birthday.id == birthday_id)
        .first()
    )
    if not birthday:
        raise ValueError("Запись не найдена.")
    return birthday


def ensure_unique_person(session, user: User, first_name: str, last_name: str) -> None:
    existing = (
        session.query(Birthday)
        .filter_by(user_id=user.id, first_name=first_name, last_name=last_name)
        .first()
    )
    if existing:
        raise ValueError("Человек с таким именем уже существует.")


def create_empty_birthday_card(
    session,
    user: User,
    full_name: str,
    description: str,
    notification_calendar_mode: NotificationCalendarMode,
) -> Birthday:
    first_name, last_name = split_name(full_name)
    ensure_unique_person(session, user, first_name, last_name)

    birthday = Birthday(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        description=description or "",
        notification_calendar_mode=notification_calendar_mode,
    )
    session.add(birthday)
    session.flush()
    return birthday


def get_date_by_type(birthday: Birthday, calendar_type: CalendarType) -> BirthdayDate | None:
    for item in birthday.dates:
        if item.calendar_type == calendar_type:
            return item
    return None


def ensure_missing_date_type(birthday: Birthday, calendar_type: CalendarType) -> None:
    if get_date_by_type(birthday, calendar_type):
        raise ValueError("Дата этого типа уже существует у записи.")


def add_gregorian_date_to_birthday(
    session,
    birthday: Birthday,
    day: int,
    month: int,
    year: int | None,
    *,
    is_derived: bool = False,
) -> BirthdayDate:
    birthday = get_birthday_with_dates(session, birthday.id)
    ensure_missing_date_type(birthday, CalendarType.gregorian)

    date_item = BirthdayDate(
        birthday_id=birthday.id,
        calendar_type=CalendarType.gregorian,
        is_derived=is_derived,
        g_day=day,
        g_month=month,
        g_year=year,
    )
    session.add(date_item)
    session.flush()
    return date_item


def add_hebrew_date_to_birthday(
    session,
    birthday: Birthday,
    day: int,
    month: HebrewMonth,
    year: int | None,
    *,
    adar_rule: AdarRule = AdarRule.regular_to_adar_ii,
    is_derived: bool = False,
) -> BirthdayDate:
    birthday = get_birthday_with_dates(session, birthday.id)
    validate_hebrew_date(day, month, year)
    ensure_missing_date_type(birthday, CalendarType.hebrew)

    date_item = BirthdayDate(
        birthday_id=birthday.id,
        calendar_type=CalendarType.hebrew,
        is_derived=is_derived,
        h_day=day,
        h_month=month,
        h_year=year,
        adar_rule=adar_rule,
    )
    session.add(date_item)
    session.flush()
    return date_item


def sync_derived_hebrew_from_gregorian(session, birthday: Birthday) -> None:
    # ВАЖНО: всегда заново читаем карточку с датами из БД/сессии
    birthday = get_birthday_with_dates(session, birthday.id)

    gregorian = get_date_by_type(birthday, CalendarType.gregorian)
    hebrew = get_date_by_type(birthday, CalendarType.hebrew)

    if not gregorian:
        return

    if not gregorian.g_year:
        if hebrew and hebrew.is_derived:
            session.delete(hebrew)
            session.flush()
        return

    result = convert_gregorian_to_hebrew(
        day=gregorian.g_day,
        month=gregorian.g_month,
        year=gregorian.g_year,
    )

    if hebrew:
        if hebrew.is_derived:
            hebrew.h_day = result.day
            hebrew.h_month = result.month
            hebrew.h_year = result.year
            hebrew.adar_rule = result.adar_rule
            session.flush()
        return

    derived_hebrew = BirthdayDate(
        birthday_id=birthday.id,
        calendar_type=CalendarType.hebrew,
        is_derived=True,
        h_day=result.day,
        h_month=result.month,
        h_year=result.year,
        adar_rule=result.adar_rule,
    )
    session.add(derived_hebrew)
    session.flush()


def create_birthday_gregorian(
    session,
    user: User,
    full_name: str,
    day: int,
    month: int,
    year: int | None,
    description: str,
    *,
    notification_calendar_mode: NotificationCalendarMode = NotificationCalendarMode.gregorian,
    auto_create_hebrew: bool = True,
) -> Birthday:
    birthday = create_empty_birthday_card(
        session=session,
        user=user,
        full_name=full_name,
        description=description,
        notification_calendar_mode=notification_calendar_mode,
    )

    add_gregorian_date_to_birthday(
        session=session,
        birthday=birthday,
        day=day,
        month=month,
        year=year,
    )

    if auto_create_hebrew and year is not None:
        sync_derived_hebrew_from_gregorian(session, birthday)

    return get_birthday_with_dates(session, birthday.id)


def create_birthday_hebrew(
    session,
    user: User,
    full_name: str,
    day: int,
    month: HebrewMonth,
    year: int | None,
    description: str,
    *,
    adar_rule: AdarRule = AdarRule.regular_to_adar_ii,
    notification_calendar_mode: NotificationCalendarMode = NotificationCalendarMode.hebrew,
) -> Birthday:
    birthday = create_empty_birthday_card(
        session=session,
        user=user,
        full_name=full_name,
        description=description,
        notification_calendar_mode=notification_calendar_mode,
    )

    add_hebrew_date_to_birthday(
        session=session,
        birthday=birthday,
        day=day,
        month=month,
        year=year,
        adar_rule=adar_rule,
        is_derived=False,
    )

    return get_birthday_with_dates(session, birthday.id)


def create_birthday_both(
    session,
    user: User,
    full_name: str,
    description: str,
    *,
    g_day: int,
    g_month: int,
    g_year: int | None,
    notification_calendar_mode: NotificationCalendarMode = NotificationCalendarMode.gregorian,
    auto_create_hebrew: bool = False,
    h_day: int | None = None,
    h_month: HebrewMonth | None = None,
    h_year: int | None = None,
    adar_rule: AdarRule = AdarRule.regular_to_adar_ii,
) -> Birthday:
    birthday = create_empty_birthday_card(
        session=session,
        user=user,
        full_name=full_name,
        description=description,
        notification_calendar_mode=notification_calendar_mode,
    )

    add_gregorian_date_to_birthday(
        session=session,
        birthday=birthday,
        day=g_day,
        month=g_month,
        year=g_year,
    )

    if auto_create_hebrew:
        if g_year is None:
            raise ValueError("Для автоконвертации в еврейскую дату нужен год.")
        sync_derived_hebrew_from_gregorian(session, birthday)
        return get_birthday_with_dates(session, birthday.id)

    if h_day is None or h_month is None:
        raise ValueError("Для ручного создания обеих дат нужно заполнить еврейскую дату.")

    add_hebrew_date_to_birthday(
        session=session,
        birthday=birthday,
        day=h_day,
        month=h_month,
        year=h_year,
        adar_rule=adar_rule,
        is_derived=False,
    )

    return get_birthday_with_dates(session, birthday.id)


def create_birthday(
    session,
    user: User,
    full_name: str,
    day: int,
    month: int,
    year: int | None,
    description: str,
) -> Birthday:
    return create_birthday_gregorian(
        session=session,
        user=user,
        full_name=full_name,
        day=day,
        month=month,
        year=year,
        description=description,
        notification_calendar_mode=NotificationCalendarMode.gregorian,
        auto_create_hebrew=True,
    )