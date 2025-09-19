import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# CSV laden
df = pd.read_csv(
    "C:/Users/pathto/daten.csv",
    encoding='cp1252'
)

# Nummern in Integer konvertieren
df["Nummer"] = pd.to_numeric(df["Nummer"], errors="coerce").astype("Int64")

# Datumsfelder parsen
df["Gesetzlich Anfang"] = pd.to_datetime(df["Gesetzlich Anfang"], format='%d.%m.%y', errors='coerce')
df["Gesetzlich Ende"] = pd.to_datetime(df["Gesetzlich Ende"], format='%d.%m.%y', errors='coerce')
df["Vorgespräch"] = pd.to_datetime(df["Vorgespräch"], format='%d.%m.%y', errors='coerce')

# Wartezeiten berechnen
df["Wartezeit"] = (df["Gesetzlich Ende"] - df["Gesetzlich Anfang"]).dt.days

# Mittelwerte je Praxisnummer
mean_waits = df.groupby("Nummer")["Wartezeit"].mean().sort_values()

# Nach Mittelwert sortierte Liste der Praxisnummern
sorted_praxen = mean_waits.index.tolist()

# Plot vorbereiten
fig, ax = plt.subplots(figsize=(14, 6))

for rank, nummer in enumerate(sorted_praxen, start=1):
    rows = df[df["Nummer"] == nummer].reset_index(drop=True)

    if rows.empty:
        ax.bar(rank, 0, color='white', edgecolor='black')
        continue

    for i, row in rows.iterrows():
        start = row["Gesetzlich Anfang"]
        end = row["Gesetzlich Ende"]
        vorgespraech = row["Vorgespräch"]

        # Farben/Alpha abhängig vom Versuch
        if i == 0:
            color = "bisque"
            alpha = 1.0
            text_color = "darkgoldenrod"
        else:
            color = "seagreen"
            alpha = 0.3
            text_color = "green"

        # Balken zeichnen
        if pd.notna(start) and pd.notna(end):
            wartezeit = (end - start).days
            ax.bar(rank, wartezeit, color=color, alpha=alpha, edgecolor='black')
            ax.text(rank, wartezeit + 0.5, str(wartezeit),
                    ha='center', va='bottom', fontsize=10, color=text_color)
        else:
            ax.bar(rank, 0, color=color, alpha=alpha, edgecolor='black')

        # Vorgespräch markieren
        if pd.notna(vorgespraech) and pd.notna(start):
            y_pos = max((vorgespraech - start).days, 0)
            ax.text(rank, y_pos, "I",
                    ha='center', va='center', rotation=90,
                    fontsize=14, fontweight='bold', color=text_color, alpha=alpha)
            # Indexzahl daneben
            ax.text(rank + 0.12, y_pos, str(i+1),
                    ha='left', va='center', fontsize=8, color=text_color, alpha=alpha)

        # Text immer anzeigen
        if pd.notna(row.get("Text", None)):
            ax.text(rank, 170, row["Text"],
                    ha='center', va='bottom', fontsize=8, rotation=90, color='black')

    # Praxisnummer als Text unten anzeigen
    ax.text(rank, -5, str(nummer), ha='center', va='top', fontsize=8, rotation=90)

# Achsenbeschriftung & Layout
ax.set_ylabel("Wartezeit in Tagen", fontsize=14)
ax.set_title("Wartezeiten (nur gesetzlich, sortiert nach mittlerer Wartezeit)", fontsize=16)

# X-Achse: nur Positionen, keine Labels
ax.set_xticks(range(1, len(sorted_praxen)+1))
ax.set_xticklabels([""]*len(sorted_praxen))
ax.tick_params(axis='y', labelsize=12)

# Legende
gesetzlich_patch = mpatches.Patch(color='bisque', label='Gesetzlich: Erstversuch')
gesetzlich_patch_zweit = mpatches.Patch(color='seagreen', alpha=0.3, label='Gesetzlich: Zweit-/Drittversuch')

vorgespraech_line_erst = mlines.Line2D([], [], color='darkgoldenrod',
                                 marker=r'$\mathrm{I}$', markersize=10,
                                 linestyle='None', label='Vorgespräch Erstversuch')
vorgespraech_line_zweitdritt = mlines.Line2D([], [], color='seagreen',
                                 marker=r'$\mathrm{I}$', markersize=10,
                                 linestyle='None', label='Vorgespräch Zweit-/Drittversuch')

ax.legend(handles=[gesetzlich_patch, gesetzlich_patch_zweit, vorgespraech_line_erst, vorgespraech_line_zweitdritt],
          loc='upper left', bbox_to_anchor=(0.558, -0.051),
          ncol=2, fontsize=8)

plt.tight_layout()
plt.savefig('balkg_sortiertg.png', dpi=300)
plt.show()
