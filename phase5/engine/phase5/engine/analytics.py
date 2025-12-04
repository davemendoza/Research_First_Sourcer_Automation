import pandas as pd

def role_distribution(df: pd.DataFrame) -> pd.Series:
    return df["primary_role"].value_counts().sort_values(ascending=False)

def tier_distribution(df: pd.DataFrame) -> pd.Series:
    return df["tier"].value_counts().sort_values(ascending=False)

def average_scores_by_role(df: pd.DataFrame) -> pd.Series:
    return df.groupby("primary_role")["signal_strength"].mean().sort_values(ascending=False)
