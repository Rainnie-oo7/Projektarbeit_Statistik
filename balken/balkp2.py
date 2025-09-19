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

# Datumsfelder parsen (nur privat + Vorgespräch)
df["Privat Anfang"] = pd.to_datetime(df["Privat Anfang"], format='%d.%m.%y', errors='coerce')
df["Privat Ende"] = pd.to_datetime(df["Privat Ende"], format='%d.%m.%y', errors='coerce')
df["Vorgespräch"] = pd.to_datetime(df["Vorgespräch"], format='%d.%m.%y', errors='coerce')

# Primärbalken = erstes Vorkommen jeder Nummer
df_prim = df.loc[~df["Nummer"].duplicated(keep="first")]

# Plot vorbereiten
fig, ax = plt.subplots(figsize=(14, 6))

# Alle Praxisnummern von 1 bis 33
praxisnummern = list(range(1, 34))

for nummer in praxisnummern:
    # Primärdaten
    row = df_prim[df_prim["Nummer"] == nummer]
    if not row.empty:
        row = row.iloc[0]
        start = row["Privat Anfang"]
        end = row["Privat Ende"]

        if pd.notna(start) and pd.notna(end):
            wartezeit = (end - start).days
            ax.bar(nummer, wartezeit, color='steelblue', edgecolor='black')

            # Beschriftung oben (Primär)
            ax.text(nummer, wartezeit + 0.5, str(wartezeit),
                    ha='center', va='bottom', fontsize=10, color="black")

            # Text Privat nur anzeigen, wenn er nicht leer/nan ist
            privat_text = row.get("Text Privat", "")
            if isinstance(privat_text, str) and privat_text.strip() != "":
                ax.text(nummer, 205, privat_text,
                        ha='center', va='bottom', fontsize=8, rotation=90, color='black')
        else:
            ax.bar(nummer, 0, color='steelblue', edgecolor='black')
            privat_text = row.get("Text Privat", "")
            if isinstance(privat_text, str) and privat_text.strip() != "":
                ax.text(nummer, 205, privat_text,
                        ha='center', va='bottom', fontsize=8, rotation=90, color='black')

        # Sekundär-/Drittversuche suchen → ALLE weiteren Zeilen dieser Nummer
        repeats = df[df["Nummer"] == nummer].iloc[1:]  # alle außer der ersten
        for i, sec_row in repeats.iterrows():
            sec_start = sec_row["Privat Anfang"]
            sec_end = sec_row["Privat Ende"]
            if pd.notna(sec_start) and pd.notna(sec_end):
                sec_wartezeit = (sec_end - sec_start).days
                ax.bar(nummer, sec_wartezeit,
                       color='steelblue', alpha=0.5, edgecolor='black')

                # Wartezeit-Beschriftung direkt auf diesem Balken
                ax.text(nummer, sec_wartezeit + 0.5, str(sec_wartezeit),
                        ha='center', va='bottom', fontsize=10, color="cornflowerblue")

    else:
        # Weder Primär- noch Sekundärdaten -> leerer Balken
        ax.bar(nummer, 0, color='white', edgecolor='black')

# Achsenbeschriftung & Layout
ax.set_xlabel("Praxisnummer", fontsize=14)
ax.set_ylabel("Wartezeit in Tagen", fontsize=14)
ax.set_title("Wartezeiten (nur privat)", fontsize=16)

# X-Achse fix 1–33
ax.set_xticks(praxisnummern)
ax.set_xticklabels(praxisnummern, rotation=0, fontsize=12)
ax.tick_params(axis='y', labelsize=12)

# Farbige Balken-Einträge
privat_patch = mpatches.Patch(color='steelblue', label='Privatversichert: Erstversuch')
privat_patch_zweit = mpatches.Patch(color='steelblue', label='Privatversichert: Zweit-/Drittversuch', alpha=0.5)


# Legende zusammensetzen
ax.legend(handles=[privat_patch, privat_patch_zweit],
          loc='upper left', bbox_to_anchor=(0.558, -0.051),
          ncol=2, fontsize=8)

plt.tight_layout()
plt.savefig('balkp.png', dpi=300)
plt.show()
