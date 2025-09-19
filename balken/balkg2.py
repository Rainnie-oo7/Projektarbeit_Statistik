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

# Datumsfelder parsen (nur gesetzlich + Vorgespräch)
df["Gesetzlich Anfang"] = pd.to_datetime(df["Gesetzlich Anfang"], format='%d.%m.%y', errors='coerce')
df["Gesetzlich Ende"] = pd.to_datetime(df["Gesetzlich Ende"], format='%d.%m.%y', errors='coerce')
df["Vorgespräch"] = pd.to_datetime(df["Vorgespräch"], format='%d.%m.%y', errors='coerce')

# Alle Praxisnummern von 1 bis 33
praxisnummern = list(range(1, 34))

# Plot vorbereiten
fig, ax = plt.subplots(figsize=(14, 6))

# Gruppieren nach Praxisnummer, damit man beliebig viele Versuche abarbeiten kann
for nummer in praxisnummern:
    rows = df[df["Nummer"] == nummer].reset_index(drop=True)

    if rows.empty:
        # Falls keine Daten -> leerer Balken
        ax.bar(nummer, 0, color='white', edgecolor='black')
        continue

    for i, row in rows.iterrows():
        start = row["Gesetzlich Anfang"]
        end = row["Gesetzlich Ende"]
        vorgespraech = row["Vorgespräch"]

        # Farben/Alpha abhängig vom Versuch
        if i == 0:
            color = "bisque"
            alpha = 1.0
            label_suffix = "Erstversuch"
            text_color = "darkgoldenrod"
        else:
            color = "seagreen"
            alpha = 0.3
            label_suffix = f"{i+1}. Versuch"
            text_color = "green"

        if pd.notna(start) and pd.notna(end):
            wartezeit = (end - start).days
            ax.bar(nummer, wartezeit, color=color, alpha=alpha, edgecolor='black')

            # Wartezeit-Beschriftung über Balken
            ax.text(nummer, wartezeit + 0.5, str(wartezeit),
                    ha='center', va='bottom', fontsize=10, color=text_color)

            # Vorgespräch markieren

        else:
            # Kein Balken, aber Text
            ax.bar(nummer, 0, color=color, alpha=alpha, edgecolor='black')

        if pd.notna(vorgespraech) and pd.notna(start):
            if start <= vorgespraech:
                y_pos = (vorgespraech - start).days
            else:
                y_pos = 0
            ax.text(nummer, y_pos, "I",
                    ha='center', va='center', rotation=90,
                    fontsize=14, fontweight='bold', color=text_color, alpha=alpha)

            # Kleine Indexzahl (1,2,3) daneben
            ax.text(nummer + 0.12, y_pos, str(i+1),
                    ha='left', va='center', fontsize=8, color=text_color, alpha=alpha)

        # Text IMMER anzeigen (egal ob Balken vorhanden)
        if pd.notna(row.get("Text", None)):
            ax.text(nummer, 170, row["Text"],
                    ha='center', va='bottom', fontsize=8, rotation=90, color='black')

# Achsenbeschriftung & Layout
ax.set_xlabel("Praxisnummer", fontsize=14)
ax.set_ylabel("Wartezeit in Tagen", fontsize=14)
ax.set_title("Wartezeiten (nur gesetzlich)", fontsize=16)

# X-Achse fix 1–33
ax.set_xticks(praxisnummern)
ax.set_xticklabels(praxisnummern, rotation=0, fontsize=12)
ax.tick_params(axis='y', labelsize=12)

# Farbige Balken-Einträge
gesetzlich_patch = mpatches.Patch(color='bisque', label='Gesetzlich: Erstversuch')
gesetzlich_patch_zweit = mpatches.Patch(color='seagreen', alpha=0.3, label='Gesetzlich: Zweit-/Drittversuch')

# Symbol-Einträge für Vorgespräch
vorgespraech_line_erst = mlines.Line2D([], [], color='darkgoldenrod',
                                 marker=r'$\mathrm{I}$', markersize=10,
                                 linestyle='None', label='Vorgespräch (Index zeigt Versuch)')

vorgespraech_line_zweitdritt = mlines.Line2D([], [], color='seagreen',
                                 marker=r'$\mathrm{I}$', markersize=10,
                                 linestyle='None', label='Vorgespräch Zweitversuch (Index zeigt Versuch)')
# Legende zusammensetzen
ax.legend(handles=[gesetzlich_patch, gesetzlich_patch_zweit, vorgespraech_line_erst, vorgespraech_line_zweitdritt],
          loc='upper left', bbox_to_anchor=(0.558, -0.051),
          ncol=2, fontsize=8)

plt.tight_layout()
plt.savefig('balkg2.png', dpi=300)
plt.show()
