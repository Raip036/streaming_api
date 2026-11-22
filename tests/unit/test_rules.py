from datetime import date

import pytest
from app.core.rules import age_on, is_adult

@pytest.mark.parametrize(
    ("dob", "today", "expected_age"),
    [
        (date(2008, 11, 20), date(2026, 11, 20), 18),  # 18th birthday is today
        (date(2008, 11, 21), date(2026, 11, 20), 17),  # 18th birthday is tomorrow
        (date(2008, 11, 19), date(2026, 11, 20), 18),  # 18th birthday was yesterday
        (date(2008, 2, 29), date(2026, 2, 28), 17),  # leap-day birthday, not yet reached
        (date(2008, 2, 29), date(2026, 3, 1), 18),  # leap-day birthday, reached
        (date(1990, 1, 1), date(2026, 11, 20), 36),
    ],
)

def test_age_on_counts_whole_years(dob, today, expected_age):
    assert age_on(dob, today) == expected_age

def test_is_adult_on_the_18th_birthday():
    assert is_adult(date(2008, 11, 20), today=date(2026, 11, 20))


def test_is_not_adult_the_day_before_the_18th_birthday():
    assert not is_adult(date(2008, 11, 21), today=date(2026, 11, 20))


def test_minimum_age_can_be_changed():
    assert not is_adult(date(2008, 11, 20), today=date(2026, 11, 20), minimum_age=21)