import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np

# CSV laden
df = pd.read_csv(
    "C:/Users/pathto/daten.csv",
    encoding='cp1252'
)

# Nummern in Integer konvertieren
df["Nummer"] = pd.to_numeric(df["Nummer"], errors="coerce").astype("Int64")

# Datumsfelder parsen
datum_spalten = ["Gesetzlich Anfang", "Gesetzlich Ende", "Vorgespräch", "Privat Anfang", "Privat Ende"]
for sp in datum_spalten:
    df[sp] = pd.to_datetime(df[sp], format='%d.%m.%y', errors='coerce')

# Alle Praxisnummern von 1 bis 33
praxisnummern = list(range(1, 34))

# Dicts für gemittelte Wartezeiten pro Nummer
mittel_gesetzlich = {}
mittel_privat = {}

for nummer in praxisnummern:
    rows = df[df["Nummer"] == nummer]

    # --- Gesetzlich ---
    gesetzlich_list = []
    for _, row in rows.iterrows():
        if pd.notna(row["Gesetzlich Anfang"]) and pd.notna(row["Gesetzlich Ende"]):
            gesetzlich_list.append(max((row["Gesetzlich Ende"] - row["Gesetzlich Anfang"]).days, 0))
    if gesetzlich_list:
        mittel_gesetzlich[nummer] = np.mean(gesetzlich_list)
    else:
        mittel_gesetzlich[nummer] = np.nan

    # --- Privat ---
    privat_list = []
    for _, row in rows.iterrows():
        if pd.notna(row["Privat Anfang"]) and pd.notna(row["Privat Ende"]):
            privat_list.append(max((row["Privat Ende"] - row["Privat Anfang"]).days, 0))
    if privat_list:
        mittel_privat[nummer] = np.mean(privat_list)
    else:
        mittel_privat[nummer] = np.nan

# --- Optional: als DataFrame für Export ---
df_mittel = pd.DataFrame({
    "Nummer": praxisnummern,
    "Mittel_Gesetzlich": [mittel_gesetzlich[n] for n in praxisnummern],
    "Mittel_Privat": [mittel_privat[n] for n in praxisnummern]
})

df_mittel.to_csv("mittelwerte_pro_praxis.csv", sep=";", index=False)
print(df_mittel)

# --- Plot ---
fig, ax = plt.subplots(figsize=(14, 6))
x_pos = np.arange(len(praxisnummern))
width = 0.35

ax.bar(x_pos - width / 2, df_mittel["Mittel_Gesetzlich"], width, color="darkgoldenrod", label="Gesetzlich")
ax.bar(x_pos + width / 2, df_mittel["Mittel_Privat"], width, color="steelblue", label="Privat")

ax.set_xticks(x_pos)
ax.set_xticklabels(praxisnummern)
ax.set_xlabel("Praxisnummer")
ax.set_ylabel("Mittlere Wartezeit (Tage)")
ax.set_title("Mittlere Wartezeit pro Praxisnummer")
ax.legend()
plt.tight_layout()
plt.show()
import pandas as pd
import numpy as np

# CSV laden, das wir vorher erstellt haben
df_mittel = pd.read_csv("mittelwerte_pro_praxis.csv", sep=";")

# --- Deskriptive Statistik Gesetzlich ---
print("\n--- Deskriptive Statistik: Gesetzlich ---")
gesetzlich = df_mittel["Mittel_Gesetzlich"].dropna()
desc_gesetzlich = {
    "Anzahl": gesetzlich.count(),
    "Mittelwert": gesetzlich.mean(),
    "Standardabweichung": gesetzlich.std(),
    "Varianz": gesetzlich.var(),
    "Minimum": gesetzlich.min(),
    "25%-Quartil": gesetzlich.quantile(0.25),
    "Median": gesetzlich.median(),
    "75%-Quartil": gesetzlich.quantile(0.75),
    "Maximum": gesetzlich.max()
}
for k, v in desc_gesetzlich.items():
    print(f"{k}: {v:.2f}")

# --- Deskriptive Statistik Privat ---
print("\n--- Deskriptive Statistik: Privat ---")
privat = df_mittel["Mittel_Privat"].dropna()
desc_privat = {
    "Anzahl": privat.count(),
    "Mittelwert": privat.mean(),
    "Standardabweichung": privat.std(),
    "Varianz": privat.var(),
    "Minimum": privat.min(),
    "25%-Quartil": privat.quantile(0.25),
    "Median": privat.median(),
    "75%-Quartil": privat.quantile(0.75),
    "Maximum": privat.max()
}
for k, v in desc_privat.items():
    print(f"{k}: {v:.2f}")
