import pandas as pd
from sklearn.ensemble import IsolationForest


def create_features(df):

    features = pd.DataFrame()

    features["hour"] = \
        df["timestamp"].dt.hour.fillna(0)

    features["duration"] = \
        df["duration"].fillna(0)

    features["contact_frequency"] = \
        df.groupby(
            "contact"
        )["contact"].transform(
            "count"
        )

    gap = df[
        "timestamp"
    ].diff()

    features["time_gap"] = \
        gap.dt.total_seconds().fillna(0)

    features["night_activity"] = \
        (features["hour"] >= 22).astype(int)

    features["weekend_activity"] = \
        (
            df["timestamp"]
            .dt.dayofweek >= 5
        ).astype(int)

    features["communication_density"] = \
        df.groupby(
            "contact"
        )["contact"].transform(
            "count"
        )

    features["new_contact"] = \
        (~df["contact"].duplicated()).astype(int)

    return features.fillna(0)


def detect_anomaly(features):

    model = IsolationForest(

        contamination=0.15,

        random_state=42

    )

    return model.fit_predict(
        features
    )