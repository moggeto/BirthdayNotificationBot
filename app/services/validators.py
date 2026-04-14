from datetime import date


def validate_day_month(day: int, month: int):
    try:
        date(2000, month, day)  # 2000 — високосный год
    except ValueError:
        raise ValueError("Такой даты не существует.")


def parse_date_with_optional_year(text: str):
    parts = text.strip().split(".")

    if len(parts) not in (2, 3):
        raise ValueError("Формат: ДД.ММ или ДД.ММ.ГГГГ")

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2]) if len(parts) == 3 else None

    return day, month, year