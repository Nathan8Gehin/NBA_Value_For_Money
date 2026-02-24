import os
import sys
import unicodedata

import pandas as pd

# Path setup for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def clean_name(text):
    """Normalisation ultime : pas d'accents, pas de ponctuation, pas de suffixes."""
    if not isinstance(text, str):
        return ""
    # Passage en minuscule et retrait ponctuation
    text = text.lower().replace(".", "").replace("-", " ").replace("'", " ").strip()
    # Retrait des accents (Dončić -> Doncic)
    text = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    # Retrait des suffixes Jr, Sr, II, III, IV
    words = text.split()
    suffixes = {"jr", "sr", "ii", "iii", "iv"}
    words = [w for w in words if w not in suffixes]
    return " ".join(words)


def refresh_nba_data():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stats_path = os.path.join(BASE_DIR, "data", "NBA_Stat.xlsx")
    salary_path = os.path.join(BASE_DIR, "data", "NBA_Salary.xlsx")
    output_path = os.path.join(BASE_DIR, "data", "nba_data.xlsx")

    df_stats = pd.read_excel(stats_path)
    df_salary = pd.read_excel(salary_path)

    # Création d'un dictionnaire de recherche normalisé
    # Clé = nom nettoyé, Valeur = (Salaire, Type, Nom Original)
    salary_dict = {}
    for _, row in df_salary.iterrows():
        orig_name = str(row["Player"])
        salary_dict[clean_name(orig_name)] = {
            "val": row["Salary"],
            "type": row.get("Contract_Type", "Standard"),
            "first": clean_name(orig_name).split()[0]
            if len(clean_name(orig_name).split()) > 0
            else "",
        }

    final_salaries = []
    final_types = []

    for _, row in df_stats.iterrows():
        name = str(row["Player"])
        c_name = clean_name(name)
        parts = c_name.split()

        found_sal = 0
        found_type = "Standard"

        # 1. Match Direct Normalisé (KAT, Michael Porter Jr, Trey Murphy III)
        if c_name in salary_dict:
            found_sal = salary_dict[c_name]["val"]
            found_type = salary_dict[c_name]["type"]

        # 2. Match par Initiales (V. Wembanyama -> Victor Wembanyama)
        else:
            for norm_key, data in salary_dict.items():
                key_parts = norm_key.split()
                if len(parts) >= 2 and len(key_parts) >= 2:
                    # On compare le Nom de famille et l'initiale du prénom
                    if parts[-1] == key_parts[-1] and parts[0][0] == key_parts[0][0]:
                        # SECURITÉ HOMONYMES : Si le prénom complet est présent et différent, on ignore
                        # (Ex: Bronny vs LeBron : l'initiale 'b' != 'l', donc pas de match)
                        if (
                            len(parts[0]) > 1
                            and len(key_parts[0]) > 1
                            and parts[0] != key_parts[0]
                        ):
                            continue
                        found_sal = data["val"]
                        found_type = data["type"]
                        break

        final_salaries.append(found_sal)
        final_types.append(found_type)

    df_stats["Salary"] = final_salaries
    df_stats["Contract_Type"] = final_types

    # Calcul des métriques
    from Scripts.utils_nba import compute_metrics

    df_final = compute_metrics(df_stats)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_final.to_excel(writer, sheet_name="Analyse_NBA", index=False)

    print("Files created")


if __name__ == "__main__":
    refresh_nba_data()
