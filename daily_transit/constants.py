from typing import List, Tuple, Dict

DEFAULT_PLANETS: List[Tuple[str, str]] = [
    ("Sun", "\u2609"),
    ("Moon", "\u263d"),
    ("Mercury", "\u263f"),
    ("Venus", "\u2640"),
    ("Mars", "\u2642"),
    ("Jupiter", "\u2643"),
    ("Saturn", "\u2644"),
    ("Uranus", "\u2645"),
    ("Neptune", "\u2646"),
    ("Pluto", "\u2647"),
]

ZODIAC_SIGNS: List[Tuple[str, str]] = [
    ("Aries", "\u2648"),
    ("Taurus", "\u2649"),
    ("Gemini", "\u264a"),
    ("Cancer", "\u264b"),
    ("Leo", "\u264c"),
    ("Virgo", "\u264d"),
    ("Libra", "\u264e"),
    ("Scorpio", "\u264f"),
    ("Sagittarius", "\u2650"),
    ("Capricorn", "\u2651"),
    ("Aquarius", "\u2652"),
    ("Pisces", "\u2653"),
]

ASPECT_SYMBOLS: Dict[str, str] = {
    "Conjunction": "\u260c",
    "Opposition": "\u260d",
    "Trine": "\u25b3",
    "Square": "\u25a1",
    "Sextile": "\u26b9",
    "Quincunx": "\u267b",
    "Semisextile": "\u26fa",
    "Semisquare": "\u2220",
    "Sesquiquadrate": "\u26bc",
    "Quintile": "\u235b",
    "Biquintile": "\u2359",
}

ASCII_PLANET_LABELS: Dict[str, str] = {
    "Sun": "Su",
    "Moon": "Mo",
    "Mercury": "Me",
    "Venus": "Ve",
    "Mars": "Ma",
    "Jupiter": "Ju",
    "Saturn": "Sa",
    "Uranus": "Ur",
    "Neptune": "Ne",
    "Pluto": "Pl",
}

ASCII_ASPECT_SYMBOLS: Dict[str, str] = {
    "Conjunction": "CONJ",
    "Opposition": "OPP",
    "Trine": "TRI",
    "Square": "SQR",
    "Sextile": "SEX",
    "Quincunx": "QNC",
    "Semisextile": "SSEX",
    "Semisquare": "SSQR",
    "Sesquiquadrate": "SESQ",
    "Quintile": "QUIN",
    "Biquintile": "BIQ",
}

ASCII_ZODIAC_SIGNS: Dict[str, str] = {
    "Aries": "Ar",
    "Taurus": "Ta",
    "Gemini": "Ge",
    "Cancer": "Cn",
    "Leo": "Le",
    "Virgo": "Vi",
    "Libra": "Li",
    "Scorpio": "Sc",
    "Sagittarius": "Sg",
    "Capricorn": "Cp",
    "Aquarius": "Aq",
    "Pisces": "Pi",
}

LUNAR_PHASES: Dict[int, Tuple[str, str]] = {
    0: ("New Moon", "\U0001F311"),
    1: ("First Quarter", "\U0001F313"),
    2: ("Full Moon", "\U0001F315"),
    3: ("Last Quarter", "\U0001F317"),
}

ASCII_LUNAR_PHASE_LABELS: Dict[int, str] = {
    0: "New Moon",
    1: "First Quarter",
    2: "Full Moon",
    3: "Last Quarter",
}

LUNAR_PHASE_MEANINGS: Dict[int, str] = {
    0: "Time for intention-setting, fresh starts, and inward focus.",
    1: "Push through challenges, make decisions, and take visible action.",
    2: "Celebrate culmination, clarity, and heightened awareness.",
    3: "Release, reflect, and prepare the ground for the next cycle.",
}

CULTURAL_FULL_MOON_NAMES: Dict[int, str] = {
    1: "Wolf",
    2: "Snow",
    3: "Worm",
    4: "Pink",
    5: "Flower",
    6: "Strawberry",
    7: "Buck",
    8: "Sturgeon",
    9: "Harvest",
    10: "Hunter's",
    11: "Beaver",
    12: "Cold",
}

EPHEMERIS_NAME_MAP: Dict[str, str] = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars barycenter",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter",
    "Neptune": "neptune barycenter",
    "Pluto": "pluto barycenter",
}
