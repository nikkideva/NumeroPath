from datetime import date
import re
import unicodedata

CHALDEAN = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
    "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3,
    "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5,
    "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7,
    "F": 8, "P": 8,
}

PLANETS = {
    1: "Sun (Surya)", 2: "Moon (Chandra)",
    3: "Jupiter (Guru)", 4: "Rahu",
    5: "Mercury (Budh)", 6: "Venus (Shukra)",
    7: "Ketu", 8: "Saturn (Shani)", 9: "Mars (Mangal)",
}

def digit_sum(value: int) -> int:
    return sum(int(ch) for ch in str(abs(value)))

def reduce_to_single_digit(value: int) -> int:
    """Traditional 1-9 reduction used by this app; no master-number exception."""
    if value == 0:
        return 0
    while value > 9:
        value = digit_sum(value)
    return value

def normalize_name(name: str) -> str:
    """Remove accents and keep A-Z letters; users should enter Roman spelling."""
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z]", "", ascii_name).upper()

def calculate_chaldean_name(name: str) -> dict:
    letters = normalize_name(name)
    if not letters:
        raise ValueError("Enter a name containing Roman alphabet letters A-Z.")
    total = sum(CHALDEAN[letter] for letter in letters)
    return {
        "normalized_name": letters,
        "compound": total,
        "root": reduce_to_single_digit(total),
    }

def calculate_mulank(dob: date) -> int:
    return reduce_to_single_digit(dob.day)

def calculate_bhagyank(dob: date) -> int:
    return reduce_to_single_digit(sum(int(ch) for ch in dob.strftime("%d%m%Y")))

def calculate_personal_year(dob: date, year: int | None = None) -> int:
    year = year or date.today().year
    total = dob.day + dob.month + digit_sum(year)
    return reduce_to_single_digit(total)

def calculate_personal_month(dob: date, year: int | None = None,
                             month: int | None = None) -> int:
    year = year or date.today().year
    month = month or date.today().month
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12.")
    personal_year = calculate_personal_year(dob, year)
    return reduce_to_single_digit(personal_year + month)

def calculate_profile(name: str, dob: date, year: int | None = None) -> dict:
    name_data = calculate_chaldean_name(name)
    mulank = calculate_mulank(dob)
    bhagyank = calculate_bhagyank(dob)
    name_root = name_data["root"]
    personal_year = calculate_personal_year(dob, year)

    # Transparent app-defined ranking heuristic, not a canonical numerology rule.
    weights = {mulank: 3, bhagyank: 2, name_root: 2}
    ranked = sorted(weights.items(), key=lambda item: (-item[1], item[0]))
    lucky_candidates = [number for number, _ in ranked]

    return {
        "name": name.strip(),
        "dob": dob.isoformat(),
        "mulank": mulank,
        "bhagyank": bhagyank,
        "name_compound": name_data["compound"],
        "name_root": name_root,
        "mulank_planet": PLANETS[mulank],
        "bhagyank_planet": PLANETS[bhagyank],
        "personal_year": personal_year,
        "personal_month": calculate_personal_month(dob, year),
        "profile_numbers": [mulank, bhagyank, name_root],
        "lucky_candidates": lucky_candidates,
        "ranking_note": (
            "App-defined ranking: Mulank weight 3, Bhagyank weight 2, "
            "and Chaldean name root weight 2. This is a transparent "
            "product rule, not a universally accepted numerology formula."
        ),
    }
