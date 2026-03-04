def calculate_risk(data):
    score = 0
    reasons = []
    missing = []

    # Vitals
    if data.get("spo2") is not None:
        if data["spo2"] < 92:
            score += 30
            reasons.append("Low oxygen saturation")
    else:
        missing.append("SpO₂")

    if data.get("heart_rate") is not None:
        if data["heart_rate"] > 120 or data["heart_rate"] < 50:
            score += 20
            reasons.append("Abnormal heart rate")
    else:
        missing.append("Heart Rate")

    if data.get("bp") is not None:
        if data["bp"] > 180 or data["bp"] < 90:
            score += 20
            reasons.append("Abnormal blood pressure")
    else:
        missing.append("Blood Pressure")

    if data.get("temperature") is not None:
        if data["temperature"] > 39:
            score += 10
            reasons.append("High fever")
    else:
        missing.append("Temperature")

    # Symptoms
    if data["symptom"] == "Chest Pain":
        score += 25
        reasons.append("Chest pain reported")

    if data["symptom"] == "Breathlessness":
        score += 25
        reasons.append("Breathlessness reported")

    # Pain
    if data["pain"] >= 7:
        score += 15
        reasons.append("Severe pain")

    # Age factor
    if data["age"] > 65:
        score += 10
        reasons.append("Elderly patient")

    # Priority
    if score >= 61:
        priority = "High"
    elif score >= 31:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "score": score,
        "priority": priority,
        "reasons": reasons,
        "missing": missing
    }