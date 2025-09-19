import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# --- Einstellungen ---
spalten = [
    "Gesetzlich_bis_Beh_Wartezeit_mean",
    "Gesetzlich_bis_Vorgespräch_Wartezeit_mean",
    "Vorgespräch_bis_Beh_mean",
    "Privat_Wartezeit_mean"
]

qs = np.array([0.50, 0.85, 0.90, 0.95])   # gewünschte Quantile
B = 2000  # Bootstrap-Replikate

# Kandidatenmodelle
cands = [
    ("lognorm", stats.lognorm, dict(floc=0)),
    ("gamma",   stats.gamma,   dict(floc=0)),
    ("weibull", stats.weibull_min, dict(floc=0))
]

# --- Hilfsfunktionen ---
def model_quantiles(dist, params, qs):
    return dist.ppf(qs, *params)

def process_file(path, region_label):
    df = pd.read_csv(path, sep=";")
    rows = []
    for sp in spalten:
        x = df[sp].dropna().values
        n = len(x)
        if n < 3:
            continue
        for name, dist, kw in cands:
            try:
                params = dist.fit(x, **kw)
                qhat = model_quantiles(dist, params, qs)
                part = pd.DataFrame({
                    "Spalte": sp,
                    "Region": region_label,
                    "Modell": name,
                    "q": qs,
                    "Q_modell": qhat
                })
                rows.append(part)
            except Exception:
                pass
    return pd.concat(rows, ignore_index=True)

# --- Daten beider Regionen verarbeiten ---
res1 = process_file("warten_mittelwerte_reg1.csv", "Region1")
res2 = process_file("warten_mittelwerte_reg2.csv", "Region2")

# --- Zusammenführen ---
combined = pd.concat([res1, res2], ignore_index=True)

# --- Pivot für direkten Vergleich ---
pivoted = combined.pivot_table(
    index=["Spalte", "Modell", "q"],
    columns="Region",
    values="Q_modell"
).reset_index()

# --- Verhältnis berechnen ---
pivoted["Verhältnis_R2_R1"] = pivoted["Region2"] / pivoted["Region1"]

# --- Ausgabe in Datei ---
with open("quantil_vergleich_regionenr2r1_mittelwert.txt", "w", encoding="utf-8") as f:
    for _, row in pivoted.iterrows():
        f.write(
            f"{row['Spalte']} – q={row['q']} – Modell={row['Modell']}: "
            f"Region2 ist {row['Verhältnis_R2_R1']:.2f}-mal so groß wie Region1\n"
        )

# --- Konsolen-Ausgabe ---
print(pivoted.round(2).to_string(index=False))

# Pivoted DataFrame 'pivoted' liegt bereits vor (aus vorherigem Skript)

# --- Plot ---
plt.figure(figsize=(12, 6))
sns.barplot(
    data=pivoted,
    x="Spalte",
    y="Verhältnis_R2_R1",
    hue="q",
    palette="viridis",
    dodge=True
)

# Referenzlinie bei 1
plt.axhline(1.0, color="red", linestyle="--", linewidth=1)

# Achsenbeschriftungen
plt.ylabel("Verhältnis Region2 / Region1")
plt.title("Vergleich der Quantile zwischen Region2 und Region1")

# Legende anpassen
plt.legend(title="Quantil")

# Schönere x-Ticks
plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()