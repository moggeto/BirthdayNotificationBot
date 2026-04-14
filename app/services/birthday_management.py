from sqlalchemy.orm import selectinload

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


def get_gregorian_date(birthday: Birthday) -> BirthdayDate | None:
    for item in birthday.dates:
        if item.calendar_type == CalendarType.gregorian:
            return item
    return None


def get_hebrew_date(birthday: Birthday) -> BirthdayDate | None:
    for item in birthday.dates:
        if item.calendar_type == CalendarType.hebrew:
            return item
    return None


def sync_hebrew_date(session, birthday: Birthday):
    """
    Главная функция:
    - если есть год → пересчитать Hebrew
    - если нет года → удалить Hebrew
    """

    gregorian = get_gregorian_date(birthday)
    hebrew = get_hebrew_date(birthday)

    if not gregorian:
        return

    # если года нет → удаляем Hebrew
    if not gregorian.g_year:
        if hebrew:
            session.delete(hebrew)
            session.flush()
        return

    # если год есть → пересчитываем
    result = convert_gregorian_to_hebrew(
        day=gregorian.g_day,
        month=gregorian.g_month,
        year=gregorian.g_year,
    )

    if hebrew:
        # обновляем существующую
        hebrew.h_day = result.day
        hebrew.h_month = result.month
        hebrew.h_year = result.year
        hebrew.adar_rule = result.adar_rule
    else:
        # создаём новую
        hebrew = BirthdayDate(
            birthday_id=birthday.id,
            calendar_type=CalendarType.hebrew,
            h_day=result.day,
            h_month=result.month,
            h_year=result.year,
            adar_rule=result.adar_rule,
        )
        session.add(hebrew)

    session.flush()


def get_birthdays_for_management(session, user: User) -> list[Birthday]:
    birthdays = (
        session.query(Birthday)
        .options(selectinload(Birthday.dates))
        .filter_by(user_id=user.id)
        .all()
    )

    def sort_key(item: Birthday):
        gregorian = get_gregorian_date(item)
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
    session.refresh(birthday)
    return get_birthday_by_id_for_user(session, user, birthday_id)


def update_birthday_date(session, user: User, birthday_id: int, day: int, month: int) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    gregorian = get_gregorian_date(birthday)
    if not gregorian:
        raise ValueError("Нет григорианской даты.")

    gregorian.g_day = day
    gregorian.g_month = month

    session.flush()

    # ВАЖНО
    sync_hebrew_date(session, birthday)

    return get_birthday_by_id_for_user(session, user, birthday_id)


def update_birthday_year(session, user: User, birthday_id: int, year: int | None) -> Birthday | None:
    if year is not None and year <= 0:
        raise ValueError("Год должен быть положительным.")

    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    gregorian = get_gregorian_date(birthday)
    if not gregorian:
        raise ValueError("Нет григорианской даты.")

    gregorian.g_year = year

    session.flush()

    # ВАЖНО
    sync_hebrew_date(session, birthday)

    return get_birthday_by_id_for_user(session, user, birthday_id)


def update_birthday_description(session, user: User, birthday_id: int, description: str) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    birthday.description = (description or "").strip()
    session.flush()
    return get_birthday_by_id_for_user(session, user, birthday_id)