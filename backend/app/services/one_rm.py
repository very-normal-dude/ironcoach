"""One-rep-max (1RM) estimation.

Formulas lose accuracy as reps go up (they are most reliable at about 1-10 reps),
so the API caps reps at 30.
"""


def epley(weight_kg: float, reps: int) -> float:
    return weight_kg * (1 + reps / 30)


def brzycki(weight_kg: float, reps: int) -> float:
    if reps >= 37:
        raise ValueError("Brzycki formula is undefined for 37 or more reps")
    return weight_kg * 36 / (37 - reps)


def estimate_1rm(weight_kg: float, reps: int, formula: str = "epley") -> float:
    if weight_kg <= 0:
        raise ValueError("weight_kg must be positive")
    if reps < 1:
        raise ValueError("reps must be at least 1")
    if reps == 1:
        return round(weight_kg, 1)  # one rep IS your max for that weight

    if formula == "epley":
        value = epley(weight_kg, reps)
    elif formula == "brzycki":
        value = brzycki(weight_kg, reps)
    else:
        raise ValueError("formula must be 'epley' or 'brzycki'")
    return round(value, 1)
