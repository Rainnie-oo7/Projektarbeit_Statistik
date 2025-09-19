import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === CSV einlesen ===
df = pd.read_csv("mittelwerte_sorten_pro_praxis.csv", sep=";")
df.columns = df.columns.str.strip()

# Spalten, die ausgewertet werden sollen
spalten = [
    "Gesetzlich_bis_Beh_Wartezeit_mean",
    "Gesetzlich_bis_Vorgespräch_Wartezeit_mean",
    "Vorgespräch_bis_Beh_mean",
    "Privat_Wartezeit_mean",
]

# Wochenintervalle (bis 16 Wochen in 4er-Schritten, letztes Intervall = 16+)
max_days = 316
max_weeks = max_days // 7
intervalle = [(0, 4), (4, 8), (8, 12), (12, 16), (16, max_weeks)]

# === Hilfsfunktion: empirische Wahrscheinlichkeit pro Intervall ===
def berechne_empirische_wahrscheinlichkeiten(x, intervals):
    probs = {}
    for a, b in intervals:
        a_days = a * 7
        b_days = b * 7
        intervall_name = f"{a}-{b} Wochen" if b_days < max_days else f"{a}-{b} Wochen (16+)"
        # Anteil der Werte, die in dieses Intervall fallen
        pa = np.sum((x >= a_days) & (x < b_days)) / len(x)
        probs[intervall_name] = pa
    return probs

# === Berechne Wahrscheinlichkeiten pro Spalte ===
ergebnis = []

for spalte in spalten:
    x = df[spalte].dropna().values
    if len(x) == 0:
        continue

    probs = berechne_empirische_wahrscheinlichkeiten(x, intervalle)
    for intervall, p in probs.items():
        ergebnis.append({
            "Spalte": spalte,
            "Intervall": intervall,
            "Empirische_Wahrscheinlichkeit": p
        })

df_out = pd.DataFrame(ergebnis)
df_out.to_csv("empirische_wahrscheinlichkeiten.csv", sep=";", index=False)
print("Fertig: empirische_wahrscheinlichkeiten.csv")

# === Plot Beispiel: eine Spalte ===
def plot_spalte(spalte):
    subset = df_out[df_out["Spalte"] == spalte]
    intervals = list(subset["Intervall"])
    y = subset["Empirische_Wahrscheinlichkeit"].values

    plt.figure(figsize=(10, 6))
    plt.bar(np.arange(len(intervals)), y, width=0.5, color="steelblue", alpha=0.7)
    plt.xticks(np.arange(len(intervals)), intervals, rotation=45)
    plt.ylabel("Empirische Wahrscheinlichkeit")
    # plt.title(f"Wahrscheinlichkeiten je Intervall - Gesetzlich - Von Kontaktaufnahme bis Behandlung")
    # plt.title(f"Wahrscheinlichkeiten je Intervall - Gesetzlich - Von Kontaktaufnahme bis Vorgespräch")
    plt.title(f"Wahrscheinlichkeiten je Intervall - Gesetzlich - Von Vorgespräch bis Behandlung")
    # plt.title(f"Wahrscheinlichkeiten je Intervall - Privat - Von Kontaktaufnahme bis Behandlung")
    plt.tight_layout()
    plt.show()

# Beispielplot für die privat-Spalte
# plot_spalte("Privat_Wartezeit_mean")
# plot_spalte("Gesetzlich_bis_Beh_Wartezeit_mean")
# plot_spalte("Gesetzlich_bis_Vorgespräch_Wartezeit_mean")
plot_spalte("Vorgespräch_bis_Beh_mean")

