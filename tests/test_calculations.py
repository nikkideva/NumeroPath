from datetime import date
from numerology.calculations import (
    calculate_mulank, calculate_bhagyank,
    calculate_chaldean_name, calculate_personal_year,
)

def test_mulank():
    assert calculate_mulank(date(1992, 8, 15)) == 6

def test_bhagyank():
    assert calculate_bhagyank(date(1992, 8, 15)) == 8

def test_chaldean_name():
    result = calculate_chaldean_name("Asha")
    assert result["compound"] == 1 + 3 + 5 + 1
    assert result["root"] == 1

def test_personal_year():
    assert calculate_personal_year(date(1992, 8, 15), 2026) == 6
