from datetime import date


def validate_day_month(day: int, month: int):
    try:
        date(2000, month, day)  # 2000 — високосный год
    except ValueError:
        raise ValueError("Такой даты не существует.")


def validate_year(year: int):
    if year <= 0:
        raise ValueError("Год должен быть положительным числом.")

    if year > 9999:
        raise ValueError("Год слишком большой.")


def parse_date_with_optional_year(text: str) -> tuple[int, int, int | None]:
    raw = (text or "").strip()
    parts = raw.split(".")

    if len(parts) not in (2, 3):
        raise ValueError("Формат: ДД.ММ или ДД.ММ.ГГГГ")

    if not all(part.isdigit() for part in parts):
        raise ValueError("Дата должна содержать только числа и точки.")

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2]) if len(parts) == 3 else None

    if year is None:
        validate_day_month(day, month)
        return day, month, year

    validate_year(year)

    try:
        date(year, month, day)
    except ValueError:
        raise ValueError("Такой даты не существует.")

    return day, month, year