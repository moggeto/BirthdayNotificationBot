from app.database.models import Birthday, User


def split_name(full_name: str) -> tuple[str, str]:
    cleaned = full_name.strip()
    if not cleaned:
        raise ValueError("Имя не может быть пустым.")

    parts = cleaned.split(maxsplit=1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name


def find_duplicate_birthday(
    session,
    user: User,
    first_name: str,
    last_name: str,
    day: int,
    month: int,
) -> Birthday | None:
    return (
        session.query(Birthday)
        .filter_by(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            day=day,
            month=month,
        )
        .first()
    )


def create_birthday(
    session,
    user: User,
    full_name: str,
    day: int,
    month: int,
    year: int | None = None,
) -> Birthday:
    first_name, last_name = split_name(full_name)

    duplicate = find_duplicate_birthday(
        session=session,
        user=user,
        first_name=first_name,
        last_name=last_name,
        day=day,
        month=month,
    )
    if duplicate:
        raise ValueError("Такая запись уже существует.")

    birthday = Birthday(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        day=day,
        month=month,
        year=year,
    )
    session.add(birthday)
    session.flush()
    return birthday


def get_user_birthdays(session, user: User, sort_by: str = "name") -> list[Birthday]:
    query = session.query(Birthday).filter_by(user_id=user.id)

    if sort_by == "date":
        query = query.order_by(Birthday.month, Birthday.day, Birthday.first_name, Birthday.last_name)
    else:
        query = query.order_by(Birthday.first_name, Birthday.last_name)

    return query.all()