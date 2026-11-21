NUMBER_MEANINGS = {
    1: {"theme": "initiative and independence", "strength": "initiative",
        "watchout": "impatience", "colour": "red or orange", "day": "Sunday"},
    2: {"theme": "cooperation and sensitivity", "strength": "diplomacy",
        "watchout": "indecision", "colour": "white or cream", "day": "Monday"},
    3: {"theme": "learning and expression", "strength": "communication",
        "watchout": "scattered attention", "colour": "yellow", "day": "Thursday"},
    4: {"theme": "structure and unconventional thinking", "strength": "practical problem-solving",
        "watchout": "rigidity", "colour": "smoky blue or grey", "day": "Saturday"},
    5: {"theme": "adaptability and curiosity", "strength": "versatility",
        "watchout": "restlessness", "colour": "green", "day": "Wednesday"},
    6: {"theme": "care and responsibility", "strength": "supportiveness",
        "watchout": "taking on too much", "colour": "pink or light blue", "day": "Friday"},
    7: {"theme": "reflection and analysis", "strength": "thoughtfulness",
        "watchout": "overthinking", "colour": "white or sea green", "day": "Monday"},
    8: {"theme": "discipline and persistence", "strength": "organisation",
        "watchout": "being overly strict", "colour": "navy or dark blue", "day": "Saturday"},
    9: {"theme": "courage and action", "strength": "determination",
        "watchout": "acting too quickly", "colour": "red", "day": "Tuesday"},
}

def get_number_meaning(number: int) -> dict:
    return NUMBER_MEANINGS[number]

def build_combined_summary(profile: dict) -> list[str]:
    m = profile["mulank"]
    b = profile["bhagyank"]
    n = profile["name_root"]
    return [
        f"Birth-day theme ({m}): {NUMBER_MEANINGS[m]['theme']}.",
        f"Birth-date total ({b}): {NUMBER_MEANINGS[b]['theme']}.",
        f"Chaldean name root ({n}): {NUMBER_MEANINGS[n]['theme']}.",
        "Read these as three separate traditional lenses, not as a fixed personality diagnosis.",
    ]
