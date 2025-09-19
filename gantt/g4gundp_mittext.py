import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

df = pd.read_csv("C:/Users/pathto/datengantt.csv", encoding='cp1252')

def plot_combined_balken(df_prim, df_sec, prim_startg, prim_endg, prim_startp, prim_endp,
                         sec_startg, sec_endg, sec_startp, sec_endp, title):
    df_plot = df_prim.reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(20, len(df_plot) * 0.5 + 0.5))

    for i, row in df_plot.iterrows():
        nummer = row["Nummer"]

        # --- Primärdaten ---
        start1 = row[prim_startg]
        end1 = row[prim_endg]
        start2 = row[prim_startp]
        end2 = row[prim_endp]

        # Gesetzlich Primär
        if pd.notna(start1) and pd.notna(end1):
            ax.barh(i+0.2, (end1 - start1).days, left=start1, height=0.4,
                    color='bisque', edgecolor='black')
        elif pd.notna(start1) and pd.isna(end1):
            ax.text(start1, i+0.04, '[', va='center', ha='center',
                    fontsize=28, fontweight='normal', color='black')

        # Primäres Vorgespräch
        vorgespraech_datum = pd.to_datetime(row["Vorgespräch"], format='%d.%m.%y', errors='coerce')
        if pd.notna(vorgespraech_datum):
            ax.text(vorgespraech_datum, i+0.25, 'I', va='center', ha='center',
                    fontsize=16, fontweight='bold', color='darkgoldenrod')

        # Privat Primär
        if pd.notna(start2) and pd.notna(end2):
            ax.barh(i-0.2, (end2 - start2).days, left=start2, height=0.4,
                    color='steelblue', edgecolor='black')
        elif pd.notna(start2) and pd.isna(end2):
            ax.text(start2, i+0.04, '[', va='center', ha='center',
                    fontsize=28, fontweight='normal', color='black')

        # --- Sekundärdaten (alle Zeilen) ---
        matches = df_sec[df_sec["Nummer"] == nummer]
        if not matches.empty:
            for _, sec_row in matches.iterrows():
                sec_start_dateg = sec_row[sec_startg]
                sec_end_dateg = sec_row[sec_endg]
                sec_start_datep = sec_row[sec_startp]
                sec_end_datep = sec_row[sec_endp]

                # Gesetzlich Sekundär
                if pd.notna(sec_start_dateg) and pd.notna(sec_end_dateg):
                    ax.barh(i+0.2, (sec_end_dateg - sec_start_dateg).days, left=sec_start_dateg,
                            height=0.4, color='seagreen', edgecolor='black', alpha=0.3)
                elif pd.notna(sec_start_dateg) and pd.isna(sec_end_dateg):
                    ax.text(sec_start_dateg, i+0.04, '[', va='center', ha='center',
                            fontsize=28, fontweight='normal', color='black', alpha=0.5)

                # Sekundäres Vorgespräch
                vorgespraech_datum_sec = pd.to_datetime(sec_row["Vorgespräch"], format='%d.%m.%y', errors='coerce')
                if pd.notna(vorgespraech_datum_sec):
                    ax.text(vorgespraech_datum_sec, i+0.25, 'I', va='center', ha='center',
                            fontsize=16, fontweight='bold', color='green', alpha=0.3)

                # Privat Sekundär
                if pd.notna(sec_start_datep) and pd.notna(sec_end_datep):
                    ax.barh(i-0.2, (sec_end_datep - sec_start_datep).days, left=sec_start_datep,
                            height=0.4, color='steelblue', alpha=0.5)
                elif pd.notna(sec_start_datep) and pd.isna(sec_end_datep):
                    ax.text(sec_start_datep, i+0.04, '[', va='center', ha='center',
                            fontsize=28, fontweight='normal', color='black', alpha=0.5)

        # Optional: Text links anzeigen
        if "Text" in row and pd.notna(row["Text"]):
            ax.text(datetime(2025, 4, 6), i - 0.05, str(row["Text"]),
                    va='center', ha='left', linespacing=1, fontsize=15, color='black')


    ax.set_yticks(range(len(df_plot)))
    ax.set_yticklabels(df_plot["Nummer"], fontsize=18)
    ax.invert_yaxis()
    ax.set_xlim(datetime(2025, 4, 1), datetime(2026, 6, 5))
    # ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
    # Minor-Ticks: alle 7 Tage (oder was du willst)
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(interval=1))  # wöchentlich
    # Grid für Major- und Minor-Ticks
    ax.grid(axis='x', linestyle='--', alpha=0.5, which='major')
    ax.grid(axis='x', linestyle=':', alpha=0.3, which='minor')
    ax.tick_params(axis='x', labelsize=18)
    plt.xticks(rotation=30)
    ax.set_title(title, fontsize=20)
    ax.set_ylabel("Praxis #", fontsize=18)
    ax.set_xlabel("Zeitraum", fontsize=18)

    # Farbige Balken-Einträge
    privat_patch = mpatches.Patch(color='steelblue', label='Privat versichert, ⊂ P-Anfragen')
    gesetzlich_patch = mpatches.Patch(color='bisque', label='Gesetzlich versichert: Erstversuch')
    privat_patch_zweit = mpatches.Patch(color='steelblue', label='Privat versichert: Zweitversuch', alpha=0.5)
    gesetzlich_patch_zweit = mpatches.Patch(color='seagreen', label='Gesetzlich versichert: Zweitversuch', alpha=0.3)
    # Symbol-Einträge als Marker
    terminanfrage_line = mlines.Line2D([], [], color='black',
                                       marker='$[$', markersize=18,  # Größe größer = dicker
                                       linestyle='None', label='Terminanfrage')
    vorgespraech_line = mlines.Line2D([], [], color='darkgoldenrod',
                                     marker=r'$\mathrm{I}$', markersize=18,
                                     linestyle='None', label='Vorgespräch Erstversuch')
    vorgespraech_line_zweit = mlines.Line2D([], [], color='green',
                                           marker=r'$\mathrm{I}$', markersize=18,
                                           linestyle='None', label='Vorgespräch Zweitversuch', alpha=0.3)
    terminanfrage_line_zweit = mlines.Line2D([], [], color='black',
                                      marker='$[$', markersize=18,
                                      linestyle='None', label='Terminanfrage Zweitversuch', alpha=0.5)


    # Legende zusammensetzen
    ax.legend(handles=[privat_patch, gesetzlich_patch, privat_patch_zweit, gesetzlich_patch_zweit,
                       terminanfrage_line, vorgespraech_line, vorgespraech_line_zweit, terminanfrage_line_zweit],
              loc='upper right', fontsize=14)

    #bbox_to_anchor=(1, 1)

    plt.tight_layout()
    plt.savefig('ganttgandp4.png')
    plt.show()

# Datumsspalten parsen
for col in ["Gesetzlich Anfang", "Gesetzlich Ende"]:
    df[col] = pd.to_datetime(df[col], format='%d.%m.%y', errors='coerce')
for col in ["Privat Anfang", "Privat Ende"]:
    df[col] = pd.to_datetime(df[col], format='%d.%m.%y', errors='coerce')

# Nur das erste Vorkommen jeder Nummer
df_prim = df.loc[~df["Nummer"].duplicated(keep="first")]

# Nur das zweite Vorkommen jeder mehrfachen Nummer (zur Überlagerung)
duplikate = df["Nummer"].duplicated(keep=False)
erste = df["Nummer"].duplicated(keep="first")
df_sec = df.loc[duplikate & erste]

# Aufruf mit beiden DataFrames
plot_combined_balken(
    df_prim=df_prim,
    df_sec=df_sec,
    prim_startg="Gesetzlich Anfang",
    prim_endg="Gesetzlich Ende",
    prim_startp="Privat Anfang",
    prim_endp="Privat Ende",
    sec_startg="Gesetzlich Anfang",
    sec_endg="Gesetzlich Ende",
    sec_startp="Privat Anfang",
    sec_endp="Privat Ende",
    title="Ermittelte Wartezeiten"
)
