import pandas as pd
import numpy as np

# --- CSV laden ---
df = pd.read_csv("warten_min_max_vorgespr.csv")

# --- Spalten und Quantile ---
spalten = [
    "Gesetzlich_bis_Beh_Wartezeit_min", "Gesetzlich_bis_Beh_Wartezeit_max",
    "Gesetzlich_bis_Vorgespräch_Wartezeit_min", "Gesetzlich_bis_Vorgespräch_Wartezeit_max",
    "Vorgespräch_bis_Beh_min", "Vorgespräch_bis_Beh_max",
    "Privat_Wartezeit_min", "Privat_Wartezeit_max"
]

qs = np.array([0.10, 0.50, 0.70, 0.80, 0.90, 0.95])

# --- Ergebnisse sammeln ---
rows = []

for sp in spalten:
    x = df[sp].dropna().values
    if len(x) < 1:
        continue
    # Empirische Quantile berechnen
    q_emp = np.quantile(x, qs, method="linear")
    part = pd.DataFrame({
        "Spalte": sp,
        "Modell": "empirisch",
        "q": qs,
        "Q_modell": q_emp,
        "CI_low": np.nan,
        "CI_high": np.nan
    })
    rows.append(part)

# --- Alle zusammenführen ---
parametrisch_tab_emp = pd.concat(rows, ignore_index=True)

# --- In TXT speichern ---
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
with open("empirische_perzentile_region2.txt", "w", encoding="utf-8") as f:
    f.write("--- EMPIRISCHE PERZENTILE für ALLE SPALTEN ---\n\n")
    f.write(parametrisch_tab_emp.round(2).to_string(index=False))

# --- Konsolen-Ausgabe ---
print("--- EMPIRISCHE PERZENTILE für ALLE SPALTEN ---")
print(parametrisch_tab_emp.round(2).to_string(index=False))
