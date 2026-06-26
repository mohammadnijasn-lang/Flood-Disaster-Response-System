def predict_future_flood(

    flood_percent,
    rainfall

):

    probability = (

        flood_percent * 5

        +

        rainfall * 2

    )

    probability = min(
        100,
        probability
    )

    if probability < 30:

        severity = "LOW"

    elif probability < 60:

        severity = "MEDIUM"

    elif probability < 80:

        severity = "HIGH"

    else:

        severity = "CRITICAL"

    return {

        "probability": probability,

        "severity": severity
    }