from sqlalchemy import Column, Integer, String, ForeignKey, Enum, UniqueConstraint, Date
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class CalendarType(str, enum.Enum):
    gregorian = "gregorian"
    hebrew = "hebrew"


class HebrewMonth(str, enum.Enum):
    tishrei = "tishrei"
    cheshvan = "cheshvan"
    kislev = "kislev"
    tevet = "tevet"
    shevat = "shevat"
    adar = "adar"
    adar_i = "adar_i"
    adar_ii = "adar_ii"
    nisan = "nisan"
    iyar = "iyar"
    sivan = "sivan"
    tammuz = "tammuz"
    av = "av"
    elul = "elul"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)

    birthdays = relationship("Birthday", back_populates="user", cascade="all, delete-orphan")
    notification_settings = relationship("NotificationSetting", back_populates="user", cascade="all, delete-orphan")


class Birthday(Base):
    __tablename__ = "birthdays"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # тип даты
    calendar_type = Column(String, nullable=False, default="gregorian")

    # еврейская дата
    hebrew_day = Column(Integer, nullable=True)
    hebrew_month = Column(Enum(HebrewMonth), nullable=True)
    hebrew_year = Column(Integer, nullable=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False, default="")
    description = Column(String, nullable=False, default="")

    user = relationship("User", back_populates="birthdays")
    dates = relationship("BirthdayDate", back_populates="birthday", cascade="all, delete-orphan")


class BirthdayDate(Base):
    __tablename__ = "birthday_dates"

    id = Column(Integer, primary_key=True)
    birthday_id = Column(Integer, ForeignKey("birthdays.id"), nullable=False)

    calendar_type = Column(Enum(CalendarType), nullable=False)

    # Gregorian
    g_day = Column(Integer, nullable=True)
    g_month = Column(Integer, nullable=True)
    g_year = Column(Integer, nullable=True)

    # Hebrew
    h_day = Column(Integer, nullable=True)
    h_month = Column(Enum(HebrewMonth), nullable=True)
    h_year = Column(Integer, nullable=True)

    birthday = relationship("Birthday", back_populates="dates")

    __table_args__ = (
        UniqueConstraint(
            "birthday_id",
            "calendar_type",
            name="uq_birthday_one_type",
        ),
    )


class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    days_before = Column(Integer, nullable=False)

    user = relationship("User", back_populates="notification_settings")

    __table_args__ = (
        UniqueConstraint("user_id", "days_before", name="uq_user_notification_day"),
    )


class SentNotification(Base):
    __tablename__ = "sent_notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    birthday_date_id = Column(Integer, nullable=False)
    date_sent = Column(Date, nullable=False)
    days_before = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "birthday_date_id",
            "date_sent",
            "days_before",
            name="uq_sent_notification_once_per_day",
        ),
    )
