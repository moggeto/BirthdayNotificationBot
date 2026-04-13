from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import UniqueConstraint
from sqlalchemy import Date


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)

    birthdays = relationship(
        "Birthday",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    notification_setting = relationship(
        "NotificationSetting",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Birthday(Base):
    __tablename__ = "birthdays"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False, default="")
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=True)
    description = Column(String, nullable=False, default="")

    user = relationship("User", back_populates="birthdays")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "first_name",
            "last_name",
            "day",
            "month",
            name="uq_user_birthday",
        ),
    )


class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    notify_before = Column(Integer, nullable=False, default=1)

    user = relationship("User", back_populates="notification_setting")


class SentNotification(Base):
    __tablename__ = "sent_notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    birthday_id = Column(Integer, nullable=False)
    date_sent = Column(Date, nullable=False)