from app.database.models import CalendarType, DateDisplayFormat, HebrewMonth


HEBREW_MONTH_LABELS = {
    HebrewMonth.tishrei: "Тишрей",
    HebrewMonth.cheshvan: "Хешван",
    HebrewMonth.kislev: "Кислев",
    HebrewMonth.tevet: "Тевет",
    HebrewMonth.shevat: "Шват",
    HebrewMonth.adar: "Адар",
    HebrewMonth.adar_i: "Адар I",
    HebrewMonth.adar_ii: "Адар II",
    HebrewMonth.nisan: "Нисан",
    HebrewMonth.iyar: "Ияр",
    HebrewMonth.sivan: "Сиван",
    HebrewMonth.tammuz: "Таммуз",
    HebrewMonth.av: "Ав",
    HebrewMonth.elul: "Элул",
}


def get_gregorian(birthday):
    for d in birthday.dates:
        if d.calendar_type == CalendarType.gregorian:
            return d
    return None


def get_hebrew(birthday):
    for d in birthday.dates:
        if d.calendar_type == CalendarType.hebrew:
            return d
    return None


def format_gregorian(d):
    if not d or not d.g_day or not d.g_month:
        return "не указана"

    text = f"{d.g_day:02}.{d.g_month:02}"
    if d.g_year:
        text += f".{d.g_year}"
    return text


def format_hebrew(d):
    if not d or not d.h_day or not d.h_month:
        return "не указана"

    month = HEBREW_MONTH_LABELS.get(d.h_month, str(d.h_month))
    text = f"{d.h_day} {month}"
    if d.h_year:
        text += f" {d.h_year}"
    return text


def format_full(birthday, display_format: DateDisplayFormat):
    g = get_gregorian(birthday)
    h = get_hebrew(birthday)

    if display_format == DateDisplayFormat.gregorian:
        return format_gregorian(g)

    if display_format == DateDisplayFormat.hebrew:
        return format_hebrew(h)

    return f"{format_gregorian(g)} | {format_hebrew(h)}"