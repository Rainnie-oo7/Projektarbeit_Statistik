import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# CSV laden
df = pd.read_csv(
    "C:/Users/pathto/daten.csv",
    encoding='cp1252'
)

# Nummern in Integer konvertieren
df["Nummer"] = pd.to_numeric(df["Nummer"], errors="coerce").astype("Int64")

# Datumsfelder parsen
df["Privat Anfang"] = pd.to_datetime(df["Privat Anfang"], format='%d.%m.%y', errors='coerce')
df["Privat Ende"] = pd.to_datetime(df["Privat Ende"], format='%d.%m.%y', errors='coerce')

# Wartezeiten berechnen
df["Wartezeit"] = (df["Privat Ende"] - df["Privat Anfang"]).dt.days

# Mittelwerte je Praxisnummer
mean_waits = df.groupby("Nummer")["Wartezeit"].mean().sort_values()

# Nach Mittelwert sortierte Liste der Praxisnummern
sorted_praxen = mean_waits.index.tolist()

# Plot vorbereiten
fig, ax = plt.subplots(figsize=(14, 6))

for rank, nummer in enumerate(sorted_praxen, start=1):
    rows = df[df["Nummer"] == nummer]

    for i, row in rows.iterrows():
        if pd.notna(row["Wartezeit"]):
            # Primär vs. Sekundär
            if i == rows.index[0]:
                color = "steelblue"
                alpha = 1.0
                label_text = str(int(row["Wartezeit"]))
                ax.bar(rank, row["Wartezeit"], color=color, edgecolor="black", alpha=alpha)
                ax.text(rank, row["Wartezeit"] + 0.5, label_text,
                        ha="center", va="bottom", fontsize=9, color="black")
            else:
                color = "steelblue"
                alpha = 0.5
                label_text = str(int(row["Wartezeit"]))
                ax.bar(rank, row["Wartezeit"], color=color, edgecolor="black", alpha=alpha)
                ax.text(rank, row["Wartezeit"] + 0.5, label_text,
                        ha="center", va="bottom", fontsize=9, color="cornflowerblue")

    # Praxisnummer als Label unten anzeigen
    ax.text(rank, -5, str(nummer), ha="center", va="top", fontsize=8, rotation=90)

# Achsenbeschriftung & Layout
ax.set_ylabel("Wartezeit in Tagen", fontsize=14)
ax.set_title("Wartezeiten (sortiert nach mittlerer Wartezeit)", fontsize=16)

# X-Achse auf sortierte Reihenfolge
ax.set_xticks(range(1, len(sorted_praxen)+1))
ax.set_xticklabels([""]*len(sorted_praxen))  # keine Nummern direkt als xtick

# Farbige Balken-Einträge
privat_patch = mpatches.Patch(color='steelblue', label='Privatversichert: Erstversuch')
privat_patch_zweit = mpatches.Patch(color='steelblue', alpha=0.5, label='Privatversichert: Zweit-/Drittversuch')

# Legende zusammensetzen
ax.legend(handles=[privat_patch, privat_patch_zweit],
          loc='upper left', bbox_to_anchor=(0.55, -0.05),
          ncol=2, fontsize=8)

plt.tight_layout()
plt.savefig('balken_sortiertp.png', dpi=300)
plt.show()
