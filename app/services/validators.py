from datetime import date


def validate_day_month(day: int, month: int):
    try:
        date(2000, month, day)  # 2000 — високосный год
    except ValueError:
        raise ValueError("Такой даты не существует.")