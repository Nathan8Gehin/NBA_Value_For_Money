import numpy as np
import pandas as pd


def compute_metrics(df):
    df = df.copy()

    # 1. Conversion numérique stricte
    cols = [
        "Points",
        "Assists",
        "Total_Rebounds",
        "Steals",
        "Blocks",
        "Turnovers",
        "Field_Goals_Made",
        "Field_Goals_Attempted",
        "Three_PT_Made",
        "FG_Percentage",
        "Three_PT_Percentage",
        "FT_Percentage",
        "Win_Pct",
        "Plus_Minus",
        "Minutes",
        "Salary",
    ]
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # 2. TS% (True Shooting - Efficacité Curry)
    ftm = np.maximum(
        0, df["Points"] - (2 * df["Field_Goals_Made"]) - df["Three_PT_Made"]
    )
    fta = np.where(df["FT_Percentage"] > 0, ftm / df["FT_Percentage"], ftm * 1.2)
    denom_ts = 2 * (df["Field_Goals_Attempted"] + 0.44 * fta)
    df["TS_Percentage"] = np.where(denom_ts > 0, df["Points"] / denom_ts, 0)
    df["TS_Percentage"] = np.clip(df["TS_Percentage"], 0, 1.0)

    # 3. Normalisation pour Performance Score
    max_v = df[cols].max()
    df["Perf_Points"] = df["Points"] / max_v.get("Points", 1)
    df["Perf_Assists"] = df["Assists"] / max_v.get("Assists", 1)
    df["Perf_Rebounds"] = df["Total_Rebounds"] / max_v.get("Total_Rebounds", 1)
    df["Perf_Steals"] = df["Steals"] / max_v.get("Steals", 1)
    df["Perf_Blocks"] = df["Blocks"] / max_v.get("Blocks", 1)

    pm_abs_max = np.max(np.abs(df["Plus_Minus"]))
    df["Perf_PlusMinus"] = df["Plus_Minus"] / (pm_abs_max + 1)
    df["Minutes_Factor"] = np.where(df["Minutes"] >= 26, 1.0, (df["Minutes"] / 26) ** 2)

    # 4. LEAGUE RANKING (Classement n°1, n°2...)
    df["Rank_Points"] = df["Points"].rank(ascending=False, method="min").astype(int)
    df["Rank_Assists"] = df["Assists"].rank(ascending=False, method="min").astype(int)
    df["Rank_Rebounds"] = (
        df["Total_Rebounds"].rank(ascending=False, method="min").astype(int)
    )
    # Defense Rank combine Steals + Blocks
    df["Rank_Defense"] = (
        (df["Steals"] + df["Blocks"]).rank(ascending=False, method="min").astype(int)
    )

    # 5. RECALCUL DES IMPACTS (Échelle 0-100 dynamique)
    # On normalise par rapport au maximum de la ligue pour éviter les zéros
    off_raw = (
        df["Perf_Points"] * 0.6 + df["Perf_Assists"] * 0.4 + df["TS_Percentage"] * 0.2
    )
    df["Offensive_Impact"] = np.floor((off_raw / off_raw.max()) * 100)

    def_raw = (
        df["Perf_Rebounds"] * 0.4 + df["Perf_Steals"] * 0.3 + df["Perf_Blocks"] * 0.3
    )
    df["Defensive_Impact"] = np.floor((def_raw / def_raw.max()) * 100)

    # 6. SCORE DE PERFORMANCE & SALAIRE (Inchangé)
    w = {
        "Points": 15.0,
        "TS_Perc": 10.0,
        "PlusMinus": 8.0,
        "Assists": 6.0,
        "Defense": 5.0,
        "Rebounds": 4.0,
        "Win": 2.0,
    }
    total_w = sum(w.values())
    prod_score = (
        df["Perf_Points"] * w["Points"]
        + df["TS_Percentage"] * w["TS_Perc"]
        + df["Perf_PlusMinus"] * w["PlusMinus"]
        + df["Perf_Assists"] * w["Assists"]
        + ((df["Perf_Steals"] + df["Perf_Blocks"]) / 2) * w["Defense"]
        + df["Perf_Rebounds"] * w["Rebounds"]
        + df["Win_Pct"] * w["Win"]
    ) / total_w

    df["Performance_Score"] = np.maximum(0, prod_score * df["Minutes_Factor"])
    max_p = df["Performance_Score"].max()
    target_max = max(df["Salary"].max(), 55700000)

    if max_p > 0:
        df["Salary_th"] = np.floor((df["Performance_Score"] / max_p) * target_max)
    else:
        df["Salary_th"] = 1157153

    df.loc[df["Salary_th"] < 1157153, "Salary_th"] = 1157153

    # 7. Formattage Final
    df["Salary_th_Format"] = [f"${int(x):,}" for x in df["Salary_th"]]
    df["Salary_Format"] = [f"${int(x):,}" for x in df["Salary"]]
    df["Indicateur"] = "🟡 Well paid"
    ratio = df["Salary_th"] / (df["Salary"] + 1)
    df.loc[ratio > 1.15, "Indicateur"] = "🟢 Underpaid"
    df.loc[ratio < 0.85, "Indicateur"] = "🔴 Overpaid"
    df.loc[df["Salary"] <= 0, "Indicateur"] = "Unknown"

    return df
