def generate_story(df):

    report = ""

    suspicious = df[
        df["anomaly"] == -1
    ]

    for _, row in suspicious.iterrows():

        report += f"""

Time:
{row['timestamp']}

Contact:
{row['contact']}

Risk:
{row['risk_score']}

Reason:
{row['reason']}

--------------------

"""

    return report