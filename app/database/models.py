from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False, unique=True)
    name = Column(String, nullable=False)

class Birthday(Base):
    __tablename__ = "birthdays"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    first_name = Column(String, nullable=False)  # Добавлено
    last_name = Column(String, nullable=False)   # Добавлено
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

class NotificationSetting(Base):
    __tablename__ = "notification_settings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False, unique=True)
    notify_before = Column(Integer, nullable=False, default=1)  # Уведомление за N дней до ДР
