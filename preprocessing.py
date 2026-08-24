import pandas as pd


def standardize_columns(df):

    rename_map = {}

    for col in df.columns:

        c = col.lower().strip()

        if c in [
            "timestamp",
            "time",
            "date",
            "datetime"
        ]:

            rename_map[col] = "timestamp"

        elif c in [
            "contact",
            "number",
            "phone",
            "person",
            "receiver"
        ]:

            rename_map[col] = "contact"

        elif c in [
            "duration",
            "call duration",
            "length"
        ]:

            rename_map[col] = "duration"

        elif c in [
            "message",
            "text",
            "chat"
        ]:

            rename_map[col] = "message"

    df = df.rename(
        columns=rename_map
    )

    return df


def load_calls(uploaded_file):

    calls = pd.read_csv(
        uploaded_file
    )

    calls = standardize_columns(
        calls
    )

    if "timestamp" not in calls.columns:

        raise ValueError(
            "CSV needs time/date column"
        )

    calls["timestamp"] = pd.to_datetime(

        calls["timestamp"],

        errors="coerce"

    )

    if "contact" not in calls.columns:

        calls["contact"] = "Unknown"

    if "duration" not in calls.columns:

        calls["duration"] = 0

    calls["message"] = ""

    calls["event"] = "call"

    return calls


def load_chats(uploaded_file):

    if uploaded_file.name.endswith(".csv"):

        chats = pd.read_csv(
            uploaded_file
        )

    else:

        text = uploaded_file.read()

        text = text.decode(
            "utf-8"
        )

        rows = []

        for line in text.splitlines():

            rows.append(
                line.split(",")
            )

        chats = pd.DataFrame(

            rows,

            columns=[
                "timestamp",
                "contact",
                "message"
            ]

        )

    chats = standardize_columns(
        chats
    )

    chats["timestamp"] = pd.to_datetime(

        chats["timestamp"],

        errors="coerce"

    )

    if "contact" not in chats.columns:

        chats["contact"] = "Unknown"

    if "message" not in chats.columns:

        chats["message"] = ""

    chats["duration"] = 0

    chats["event"] = "chat"

    return chats


def create_timeline(
    calls,
    chats
):

    timeline = pd.concat(

        [calls, chats],

        ignore_index=True

    )

    timeline = timeline.sort_values(
        "timestamp"
    )

    timeline = timeline.reset_index(
        drop=True
    )

    return timeline