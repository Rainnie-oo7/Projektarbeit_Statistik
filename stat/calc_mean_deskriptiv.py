import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np

# CSV laden
df = pd.read_csv(
    "C:/Users/pathto/pathto/daten.csv",
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

# Listen für Wartezeiten sammeln
gesetzlich_wartezeiten = []
privat_wartezeiten = []

# Plot vorbereiten
fig, ax = plt.subplots(figsize=(14, 6))

# Gruppieren nach Praxisnummer
for nummer in praxisnummern:
    rows = df[df["Nummer"] == nummer].reset_index(drop=True)

    if rows.empty:
        ax.bar(nummer, 0, color='white', edgecolor='black')
        continue

    for i, row in rows.iterrows():
        # --- Wartezeiten berechnen, nur wenn beide Felder vorhanden ---
        gesetzlich_wartezeit = None
        privat_wartezeit = None

        if pd.notna(row["Gesetzlich Anfang"]) and pd.notna(row["Gesetzlich Ende"]):
            gesetzlich_wartezeit = max((row["Gesetzlich Ende"] - row["Gesetzlich Anfang"]).days, 0)
            gesetzlich_wartezeiten.append(gesetzlich_wartezeit)

            ax.bar(nummer, gesetzlich_wartezeit, color="bisque" if i == 0 else "seagreen",
                   alpha=1.0 if i == 0 else 0.3, edgecolor='black')
            ax.text(nummer, gesetzlich_wartezeit + 0.5, str(gesetzlich_wartezeit),
                    ha='center', va='bottom', fontsize=10, color="darkgoldenrod" if i == 0 else "green")

        if pd.notna(row["Privat Anfang"]) and pd.notna(row["Privat Ende"]):
            privat_wartezeit = max((row["Privat Ende"] - row["Privat Anfang"]).days, 0)
            privat_wartezeiten.append(privat_wartezeit)
            ax.bar(nummer, privat_wartezeit, color="steelblue", alpha=0.7, edgecolor='black')

        # --- Vorgespräch markieren ---
        if pd.notna(row["Vorgespräch"]) and pd.notna(row["Gesetzlich Anfang"]):
            y_pos = max((row["Vorgespräch"] - row["Gesetzlich Anfang"]).days, 0)
            ax.text(nummer, y_pos, "I", ha='center', va='center', rotation=90,
                    fontsize=14, fontweight='bold', color="darkgoldenrod" if i == 0 else "green", alpha=1.0 if i == 0 else 0.3)
            ax.text(nummer + 0.12, y_pos, str(i+1), ha='left', va='center', fontsize=8,
                    color="darkgoldenrod" if i == 0 else "green", alpha=1.0 if i == 0 else 0.3)

        # Text immer anzeigen
        if pd.notna(row.get("Text", None)):
            ax.text(nummer, 170, row["Text"], ha='center', va='bottom', fontsize=8, rotation=90, color='black')

# Achsenbeschriftung & Layout
ax.set_xlabel("Praxisnummer", fontsize=14)
ax.set_ylabel("Wartezeit in Tagen", fontsize=14)
ax.set_title("Wartezeiten (gesetzlich & privat)", fontsize=16)
ax.set_xticks(praxisnummern)
ax.set_xticklabels(praxisnummern, rotation=0, fontsize=12)
ax.tick_params(axis='y', labelsize=12)

# Legende
patch_gesetzlich = mpatches.Patch(color='bisque', label='Gesetzlich: Erstversuch')
patch_gesetzlich_zweit = mpatches.Patch(color='seagreen', alpha=0.3, label='Gesetzlich: Zweit-/Drittversuch')
patch_priv = mpatches.Patch(color='steelblue', label='Privat')

vorg_line = mlines.Line2D([], [], color='darkgoldenrod', marker=r'$\mathrm{I}$', markersize=10, linestyle='None', label='Vorgespräch Erstversuch')
vorg_line_zweit = mlines.Line2D([], [], color='green', marker=r'$\mathrm{I}$', markersize=10, linestyle='None', label='Vorgespräch Zweitversuch')

ax.legend(handles=[patch_gesetzlich, patch_gesetzlich_zweit, patch_priv, vorg_line, vorg_line_zweit],
          loc='upper left', bbox_to_anchor=(0.558, -0.051), ncol=2, fontsize=8)

plt.tight_layout()
plt.savefig('balkg2_angepasst.png', dpi=300)
plt.show()

# =========================
# Deskriptive Statistik berechnen
# =========================
def beschreibung(wartezeiten, name):
    arr = np.array(wartezeiten)
    print(f"\n{name}:")
    print(f"Anzahl: {len(arr)}")
    print(f"Mittelwert: {np.mean(arr):.2f}")
    print(f"Standardabweichung: {np.std(arr, ddof=1):.2f}")
    print(f"Varianz: {np.var(arr, ddof=1):.2f}")
    print(f"Minimum: {np.min(arr)}")
    print(f"Maximum: {np.max(arr)}")

beschreibung(gesetzlich_wartezeiten, "Gesetzlich Wartezeiten")
beschreibung(privat_wartezeiten, "Privat Wartezeiten")
