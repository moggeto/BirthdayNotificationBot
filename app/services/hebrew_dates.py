from dataclasses import dataclass

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


def map_pyluach_month_to_enum(month_number: int, year: int) -> HebrewMonth:
    """
    В pyluach месяцы нумеруются по еврейскому календарю.
    В невисокосный год 12 = Adar.
    В високосный год 12 = Adar I, 13 = Adar II.
    """
    if month_number == 12:
        if is_hebrew_leap_year(year):
            return HebrewMonth.adar_i
        return HebrewMonth.adar

    mapped = PYLUACH_MONTH_TO_ENUM.get(month_number)
    if mapped is None:
        raise ValueError(f"Неизвестный номер еврейского месяца: {month_number}")

    return mapped


def is_hebrew_leap_year(year: int) -> bool:
    # 7 високосных лет в 19-летнем цикле: 3, 6, 8, 11, 14, 17, 19
    return year % 19 in {0, 3, 6, 8, 11, 14, 17}


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