from dataclasses import dataclass
from datetime import date

from pyluach import dates as pyluach_dates

from app.database.models import HebrewMonth, AdarRule


@dataclass(slots=True)
class HebrewDateConversionResult:
    day: int
    month: HebrewMonth
    year: int
    adar_rule: AdarRule


PYLUACH_MONTH_TO_ENUM = {
    7: HebrewMonth.tishrei,
    8: HebrewMonth.cheshvan,
    9: HebrewMonth.kislev,
    10: HebrewMonth.tevet,
    11: HebrewMonth.shevat,
    12: HebrewMonth.adar,
    13: HebrewMonth.adar_ii,
    1: HebrewMonth.nisan,
    2: HebrewMonth.iyar,
    3: HebrewMonth.sivan,
    4: HebrewMonth.tammuz,
    5: HebrewMonth.av,
    6: HebrewMonth.elul,
}


ENUM_TO_PYLUACH_MONTH = {
    HebrewMonth.tishrei: 7,
    HebrewMonth.cheshvan: 8,
    HebrewMonth.kislev: 9,
    HebrewMonth.tevet: 10,
    HebrewMonth.shevat: 11,
    HebrewMonth.adar: 12,
    HebrewMonth.adar_i: 12,
    HebrewMonth.adar_ii: 13,
    HebrewMonth.nisan: 1,
    HebrewMonth.iyar: 2,
    HebrewMonth.sivan: 3,
    HebrewMonth.tammuz: 4,
    HebrewMonth.av: 5,
    HebrewMonth.elul: 6,
}


def is_hebrew_leap_year(year: int) -> bool:
    return year % 19 in {0, 3, 6, 8, 11, 14, 17}


def map_pyluach_month_to_enum(month_number: int, year: int) -> HebrewMonth:
    if month_number == 12:
        return HebrewMonth.adar_i if is_hebrew_leap_year(year) else HebrewMonth.adar

    mapped = PYLUACH_MONTH_TO_ENUM.get(month_number)
    if mapped is None:
        raise ValueError(f"Неизвестный номер еврейского месяца: {month_number}")
    return mapped


def map_enum_month_to_pyluach(month: HebrewMonth, year: int) -> int:
    if month == HebrewMonth.adar:
        return 12

    if month == HebrewMonth.adar_i:
        if not is_hebrew_leap_year(year):
            raise ValueError("Adar I существует только в високосном еврейском году.")
        return 12

    if month == HebrewMonth.adar_ii:
        if not is_hebrew_leap_year(year):
            raise ValueError("Adar II существует только в високосном еврейском году.")
        return 13

    mapped = ENUM_TO_PYLUACH_MONTH.get(month)
    if mapped is None:
        raise ValueError("Неизвестный еврейский месяц.")
    return mapped


def validate_hebrew_date(day: int, month: HebrewMonth, year: int | None) -> None:
    if day <= 0:
        raise ValueError("День должен быть положительным числом.")

    if year is not None and year <= 0:
        raise ValueError("Год должен быть положительным числом.")

    if year is None:
        return

    pyluach_month = map_enum_month_to_pyluach(month, year)
    try:
        pyluach_dates.HebrewDate(year, pyluach_month, day)
    except ValueError:
        raise ValueError("Такой еврейской даты не существует.")


def convert_gregorian_to_hebrew(day: int, month: int, year: int) -> HebrewDateConversionResult:
    gregorian_date = pyluach_dates.GregorianDate(year, month, day)
    hebrew_date = gregorian_date.to_heb()

    hebrew_month = map_pyluach_month_to_enum(hebrew_date.month, hebrew_date.year)

    return HebrewDateConversionResult(
        day=hebrew_date.day,
        month=hebrew_month,
        year=hebrew_date.year,
        adar_rule=AdarRule.regular_to_adar_ii,
    )


def get_next_gregorian_for_hebrew(
    h_day: int,
    h_month: HebrewMonth,
    h_year: int | None,
    today: date,
) -> date:
    """
    Возвращает ближайшую григорианскую дату наступления еврейской даты,
    начиная от today.

    h_year не используется как ограничение для поиска следующего наступления,
    он хранится только как исходный год рождения.
    """
    current_hebrew = pyluach_dates.GregorianDate(
        today.year,
        today.month,
        today.day,
    ).to_heb()

    # Проверяем текущий и следующий еврейский год
    for hebrew_year in (current_hebrew.year, current_hebrew.year + 1):
        try:
            pyluach_month = map_enum_month_to_pyluach(h_month, hebrew_year)
            candidate = pyluach_dates.HebrewDate(hebrew_year, pyluach_month, h_day).to_greg()
            candidate_date = date(candidate.year, candidate.month, candidate.day)

            if candidate_date >= today:
                return candidate_date
        except ValueError:
            continue

    raise ValueError("Не удалось вычислить ближайшую григорианскую дату для еврейского дня рождения.")