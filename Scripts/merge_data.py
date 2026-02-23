import os
import re
import sys
import unicodedata

import pandas as pd
from utils_nba import apply_style, compute_metrics

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS_FILE = os.path.join(BASE_DIR, "data", "NBA_Stat.xlsx")
SALARY_FILE = os.path.join(BASE_DIR, "data", "NBA_Salary.xlsx")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "nba_data.xlsx")


def normalize_name(name):
    """
    Nettoie le nom pour la fusion :
    - Enlève les accents (Dončić -> Doncic) pour le matching
    - Enlève les points (V. -> V)
    - Retourne le dernier mot (Nom de famille)
    """
    if pd.isna(name):
        return ""

    # Suppression des accents pour la comparaison technique
    name = str(name)
    name = "".join(
        c for c in unicodedata.normalize("NFD", name) if unicodedata.category(c) != "Mn"
    )

    # Nettoyage ponctuation et mise en minuscule
    name = name.replace(".", "").replace("-", " ").lower().strip()

    # Extraction du dernier mot (Nom de famille)
    parts = name.split()
    return parts[-1] if parts else ""


def run_merge():
    # Vérification de l'existence des dossiers/fichiers
    if not os.path.exists(STATS_FILE) or not os.path.exists(SALARY_FILE):
        print(f" Erreur : Fichiers introuvables dans {os.path.join(BASE_DIR, 'data')}")
        return

    df_stats = pd.read_excel(STATS_FILE)
    df_salaries = pd.read_excel(SALARY_FILE)

    df_stats["Player"] = df_stats["Player"].str.strip()

    # On crée une clé technique invisible pour la fusion
    df_stats["join_key"] = df_stats["Player"].apply(normalize_name)
    df_salaries["join_key"] = df_salaries["Player"].apply(normalize_name)

    df_merged = pd.merge(
        df_stats, df_salaries.drop(columns=["Player"]), on="join_key", how="left"
    )
    df_merged = df_merged.drop_duplicates(subset=["Player"], keep="first")
    df_merged = df_merged.drop(columns=["join_key"])

    df_final = compute_metrics(df_merged)

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        df_final.to_excel(writer, sheet_name="Analyse_NBA", index=False)
        # Application du design Excel
        apply_style(writer.sheets["Analyse_NBA"], df_final)

    print("Fichier créé")


if __name__ == "__main__":
    run_merge()
