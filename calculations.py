import math

CLASS_HOURS = 1.5

def calculate_metrics(attended, conducted, medical=0, extra=0, remaining=0):
    """
    Calculates attendance metrics.

    Claims reduce the 'conducted' count (excused absences),
    so the effective denominator shrinks.

    attended   - raw classes attended
    conducted  - raw classes conducted
    medical    - medical leave claims (reduce denominator)
    extra      - extracurricular claims (reduce denominator)
    remaining  - classes yet to be held this semester
    """

    claims = medical + extra

    # Effective conducted = conducted minus approved claims (floor at 1)
    effective_conducted = max(conducted - claims, 1)

    if effective_conducted == 0:
        percentage = 0.0
    else:
        percentage = round((attended / effective_conducted) * 100, 2)

    # Cap display at 100 %
    display_percentage = min(percentage, 100.0)

    total_hours    = round(effective_conducted * CLASS_HOURS, 1)
    attended_hours = round(attended            * CLASS_HOURS, 1)

    # Classes still needed to reach 85 %
    # Solve: (attended + x) / (effective_conducted + x) = 0.85
    # => x = (0.85 * effective_conducted - attended) / (1 - 0.85)
    if percentage >= 85:
        needed = 0
    else:
        raw = (0.85 * effective_conducted - attended) / (1 - 0.85)
        needed = max(math.ceil(raw), 0)

    # Can't attend more future classes than there are remaining
    possible_recovery = min(needed, remaining) if remaining > 0 else needed

    return {
        "percentage":        percentage,
        "display_percentage": display_percentage,
        "total_hours":        total_hours,
        "attended_hours":     attended_hours,
        "needed":             needed,
        "possible_recovery":  possible_recovery,
        "effective_conducted": effective_conducted,
    }