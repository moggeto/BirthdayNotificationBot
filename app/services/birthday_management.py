from app.database.models import Birthday, User


def split_name(full_name: str) -> tuple[str, str]:
    cleaned = full_name.strip()
    if not cleaned:
        raise ValueError("Имя не может быть пустым.")

    parts = cleaned.split(maxsplit=1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name


def get_birthdays_for_management(session, user: User) -> list[Birthday]:
    return (
        session.query(Birthday)
        .filter_by(user_id=user.id)
        .order_by(Birthday.first_name, Birthday.last_name, Birthday.month, Birthday.day)
        .all()
    )


def get_birthday_by_id_for_user(session, user: User, birthday_id: int) -> Birthday | None:
    return (
        session.query(Birthday)
        .filter_by(id=birthday_id, user_id=user.id)
        .first()
    )


def has_duplicate_except_self(
    session,
    user: User,
    birthday_id: int,
    first_name: str,
    last_name: str,
    day: int,
    month: int,
) -> bool:
    duplicate = (
        session.query(Birthday)
        .filter(
            Birthday.user_id == user.id,
            Birthday.first_name == first_name,
            Birthday.last_name == last_name,
            Birthday.day == day,
            Birthday.month == month,
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

    if has_duplicate_except_self(
        session=session,
        user=user,
        birthday_id=birthday.id,
        first_name=first_name,
        last_name=last_name,
        day=birthday.day,
        month=birthday.month,
    ):
        raise ValueError("Такая запись уже существует.")

    birthday.first_name = first_name
    birthday.last_name = last_name
    session.flush()
    return birthday


def update_birthday_date(session, user: User, birthday_id: int, day: int, month: int) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    if has_duplicate_except_self(
        session=session,
        user=user,
        birthday_id=birthday.id,
        first_name=birthday.first_name,
        last_name=birthday.last_name,
        day=day,
        month=month,
    ):
        raise ValueError("Такая запись уже существует.")

    birthday.day = day
    birthday.month = month
    session.flush()
    return birthday


def update_birthday_year(session, user: User, birthday_id: int, year: int | None) -> Birthday | None:
    if year is not None and year <= 0:
        raise ValueError("Год должен быть положительным числом.")

    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    birthday.year = year
    session.flush()
    return birthday


def update_birthday_description(session, user: User, birthday_id: int, description: str) -> Birthday | None:
    birthday = get_birthday_by_id_for_user(session, user, birthday_id)
    if not birthday:
        return None

    birthday.description = description.strip()
    session.flush()
    return birthday