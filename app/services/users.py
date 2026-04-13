from app.database.models import User


def get_or_create_user(session, telegram_id: int, name: str) -> User:
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user:
        if user.name != name:
            user.name = name
        return user

    user = User(telegram_id=telegram_id, name=name)
    session.add(user)
    session.flush()
    return user


def get_user_by_telegram_id(session, telegram_id: int) -> User | None:
    return session.query(User).filter_by(telegram_id=telegram_id).first()