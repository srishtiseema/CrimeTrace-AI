def explain(row):

    reasons = []

    if row["hour"] >= 22:

        reasons.append(
            "Late-night activity"
        )

    if row[
        "contact_frequency"
    ] > 3:

        reasons.append(
            "High communication frequency"
        )

    if row[
        "time_gap"
    ] > 100000:

        reasons.append(
            "Long inactivity"
        )

    if row[
        "duration"
    ] > 250:

        reasons.append(
            "Long interaction"
        )

    if row[
        "new_contact"
    ]:

        reasons.append(
            "New contact detected"
        )

    if row[
        "weekend_activity"
    ]:

        reasons.append(
            "Weekend activity"
        )

    if row["anomaly"] == -1:

        reasons.append(
            "ML anomaly detected"
        )

    if len(reasons) == 0:

        reasons.append(
            "Normal behavior"
        )

    return ", ".join(
        reasons
    )