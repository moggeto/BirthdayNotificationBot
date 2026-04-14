from datetime import date

from app.database.models import HebrewMonth


HEBREW_MONTH_INPUT_MAP = {
    "Тишрей": HebrewMonth.tishrei,
    "Хешван": HebrewMonth.cheshvan,
    "Кислев": HebrewMonth.kislev,
    "Тевет": HebrewMonth.tevet,
    "Шват": HebrewMonth.shevat,
    "Адар": HebrewMonth.adar,
    "Адар I": HebrewMonth.adar_i,
    "Адар II": HebrewMonth.adar_ii,
    "Нисан": HebrewMonth.nisan,
    "Ияр": HebrewMonth.iyar,
    "Сиван": HebrewMonth.sivan,
    "Таммуз": HebrewMonth.tammuz,
    "Ав": HebrewMonth.av,
    "Элул": HebrewMonth.elul,
}


def validate_day_month(day: int, month: int):
    try:
        date(2000, month, day)
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


def parse_positive_day(text: str) -> int:
    raw = (text or "").strip()
    if not raw.isdigit():
        raise ValueError("День должен быть числом.")
    day = int(raw)
    if day <= 0 or day > 30:
        raise ValueError("Введите день от 1 до 30.")
    return day


def parse_optional_positive_year(text: str) -> int | None:
    raw = (text or "").strip()
    if raw == "-":
        return None
    if not raw.isdigit():
        raise ValueError("Год должен быть положительным числом или '-'.")
    year = int(raw)
    if year <= 0:
        raise ValueError("Год должен быть положительным числом.")
    return year


def parse_hebrew_month(text: str) -> HebrewMonth:
    month = HEBREW_MONTH_INPUT_MAP.get((text or "").strip())
    if not month:
        raise ValueError("Выбери еврейский месяц кнопкой.")
    return month