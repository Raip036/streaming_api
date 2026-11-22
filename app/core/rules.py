from datetime import date


def age_on(dob: date, today: date) -> int:
    """Whole years between a date of birth and a given day."""
    years = today.year - dob.year
    birthday_still_to_come = (today.month, today.day) < (dob.month, dob.day)
    if birthday_still_to_come:
        years -= 1
    return years


def is_adult(dob: date, today: date, minimum_age: int = 18) -> bool:
    return age_on(dob, today) >= minimum_age

