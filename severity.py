symptoms = {
    "headache": 1,
    "anxiety": 2,
    "sweating": 2,
    "nausea": 2,
    "vomiting": 3,
    "tremors": 3,
    "hallucinations": 5,
    "seizures": 6
}

def detect_severity(text):
    score = 0
    text = text.lower()

    for symptom, value in symptoms.items():
        if symptom in text:
            score += value

    if score <= 4:
        return "Mild"
    elif score <= 8:
        return "Moderate"
    else:
        return "Severe"
