
from datetime import date

CHALDEAN = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
    "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3,
    "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5,
    "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7,
    "F": 8, "P": 8
}

PLANETS = {
    1: "Sun", 2: "Moon", 3: "Jupiter",
    4: "Rahu", 5: "Mercury", 6: "Venus",
    7: "Ketu", 8: "Saturn", 9: "Mars"
}

def reduce_number(number):
    while number > 9:
        number = sum(int(x) for x in str(number))
    return number

def generate_profile(name, dob):
    mulank = reduce_number(dob.day)

    digits = dob.strftime("%d%m%Y")
    bhagyank = reduce_number(sum(int(x) for x in digits))

    compound = sum(CHALDEAN.get(c, 0) for c in name.upper())
    name_number = reduce_number(compound)

    year = date.today().year
    personal_year = reduce_number(
        dob.day + dob.month + sum(int(x) for x in str(year))
    )

    return {
        "name": name,
        "dob": dob.isoformat(),
        "mulank": mulank,
        "bhagyank": bhagyank,
        "name_number": name_number,
        "name_compound": compound,
        "personal_year": personal_year,
        "planet": PLANETS[mulank],
        "destiny_planet": PLANETS[bhagyank]
    }
