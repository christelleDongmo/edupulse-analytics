def risk_level(x):
    if x < 10:
        return "Faible"
    elif x < 13:
        return "Moyen"
    else:
        return "Fort"


def stress_interpret(stress):
    if stress >= 7:
        return "⚠️ Stress élevé → risque de baisse de performance"
    return "✔ Stress normal"


def sleep_interpret(sleep):
    if sleep < 5:
        return "⚠️ Sommeil insuffisant"
    return "✔ Sommeil correct"