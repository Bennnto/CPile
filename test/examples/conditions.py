def grade(score: int) -> int:
    if score >= 90:
        return 4
    elif score >= 80:
        return 3
    elif score >= 70:
        return 2
    else:
        return 1
