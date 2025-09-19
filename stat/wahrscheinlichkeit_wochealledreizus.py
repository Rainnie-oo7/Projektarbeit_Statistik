import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# === Einstellungen ===
spalten = [
    "Gesetzlich_bis_Beh_Wartezeit_mean",
    "Gesetzlich_bis_Vorgespräch_Wartezeit_mean",
    "Vorgespräch_bis_Beh_mean",
    "Privat_Wartezeit_mean",
]

max_days = 316
max_weeks = max_days // 7  # ≈ 45 Wochen
# Intervalle bis 16 Wochen in 4er-Schritten
intervalle = [(0, 4), (4, 8), (8, 12), (12, 16)]
# Letztes Intervall = 16 bis max_weeks
intervalle.append((16, max_weeks))

# Kandidatenmodelle (mit fixem floc=0)
cands = [
    ("lognorm", stats.lognorm, dict(floc=0)),
    ("gamma", stats.gamma, dict(floc=0)),
    ("weibull", stats.weibull_min, dict(floc=0)),
]

# === Hilfsfunktion ===
def berechne_intervall_wahrscheinlichkeiten(x, intervals, max_days=316):
    """Berechne Wahrscheinlichkeiten pro Intervall für alle Modelle"""
    results = []
    for name, dist, kw in cands:
        try:
            params = dist.fit(x, **kw)
            probs = []
            for a, b in intervals:
                a_days = a * 7
                b_days = b * 7

                if b_days > max_days:
                    b_days = max_days  # Deckeln bei 316 Tagen
                    intervall_name = f"{a}-{b} Wochen (gedeckelt)"
                else:
                    intervall_name = f"{a}-{b} Wochen"

                pa = dist.cdf(b_days, *params) - dist.cdf(a_days, *params)
                probs.append((intervall_name, pa))

            results.append((name, dict(probs)))
        except Exception as e:
            print(f"Fehler bei {name}: {e}")
    return results


# === CSV einlesen ===
df = pd.read_csv("warten_min_max_vorgespr_means_only.csv", sep=",")
df.columns = df.columns.str.strip()

ergebnis = []

for _, row in df.iterrows():
    nummer = row.get("Nummer", None)
    for spalte in spalten:
        x = df[spalte].dropna().values
        if len(x) < 3:
            continue
        model_results = berechne_intervall_wahrscheinlichkeiten(x, intervalle)

        # jetzt alle drei Modelle zusammenfassen
        intervall_names = model_results[0][1].keys()
        for intervall in intervall_names:
            probs = [res[1][intervall] for res in model_results]
            mean_prob = np.mean(probs)
            ergebnis.append({
                "Nummer": nummer,
                "Spalte": spalte,
                "Intervall": intervall,
                "Wahrscheinlichkeit_Mittel": mean_prob
            })

# === Neue CSV schreiben ===
df_out = pd.DataFrame(ergebnis)
df_out.to_csv("wartezeiten_wahrscheinlichkeitenalledreizusm.csv", sep=";", index=False)
print("Fertig: wartezeiten_wahrscheinlichkeitenalledreizusm.csv")


# === Plot Beispiel: eine Spalte visualisieren ===
def plot_spalte(spalte):
    plt.figure(figsize=(10, 6))
    subset = df_out[df_out["Spalte"] == spalte]
    intervals = list(dict.fromkeys(subset["Intervall"]))
    x_pos = np.arange(len(intervals))

    y = [subset[subset["Intervall"] == iv]["Wahrscheinlichkeit_Mittel"].mean() for iv in intervals]
    plt.bar(x_pos, y, width=0.5, color="steelblue", alpha=0.7)

    plt.xticks(x_pos, intervals, rotation=45)
    plt.ylabel("Wahrscheinlichkeit (Mittelwert der Modelle)")
    plt.title(f"Wahrscheinlichkeiten je Intervall - Privat - Von Kontaktaufnahme bis Behandlung")
    plt.tight_layout()
    plt.show()


# Beispielplot
# plot_spalte("Gesetzlich_bis_Beh_Wartezeit_mean")
# plot_spalte("Gesetzlich_bis_Vorgespräch_Wartezeit_mean")
# plot_spalte("Vorgespräch_bis_Beh_mean")
plot_spalte("Privat_Wartezeit_mean")