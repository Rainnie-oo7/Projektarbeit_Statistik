import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Daten laden (achte auf korrektes Encoding)

df = pd.read_csv("C:/Users/pathto/daten.csv", encoding='cp1252')

# Nur gesetzlich plotten, mit Überlagerung gleicher "Nummer"
def plot_combined_balken(df_prim, df_sec, prim_start, prim_end, sec_start, sec_end, title):
    df_plot = df_prim.reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(20, len(df_plot) * 0.5 + 0.5))

    for i, row in df_plot.iterrows():
        nummer = row["Nummer"]

        # Primärdaten
        start1 = row[prim_start]
        end1 = row[prim_end]

        # Primärbalken
        if pd.notna(start1) and pd.notna(end1):
            ax.barh(i, (end1 - start1).days, left=start1, height=0.7,
                    color='steelblue', edgecolor='black')
        elif pd.notna(start1) and pd.isna(end1):
            ax.text(start1, i, '[', va='center', ha='center', fontsize=18,
                    fontweight='bold', color='black')

        # Sekundärdaten nur aus df_sec (zweites Vorkommen mit gleicher Nummer)
        match = df_sec[df_sec["Nummer"] == nummer]
        if not match.empty:
            sec_row = match.iloc[0]
            sec_start_date = sec_row[sec_start]
            sec_end_date = sec_row[sec_end]

            if pd.notna(sec_start_date) and pd.notna(sec_end_date):
                ax.barh(i, (sec_end_date - sec_start_date).days, left=sec_start_date,
                        height=0.7, color='orange', edgecolor='black', alpha=0.3)

        # Text links anzeigen
        if "Text" in row and pd.notna(row["Text"]):
            ax.text(datetime(2025, 4, 6), i - 0.05, str(row["Text"]), va='center', ha='left', linespacing=1, fontsize=17, color='black')

    # Achsen
    ax.set_yticks(range(len(df_plot)))
    ax.set_yticklabels(df_plot["Nummer"], fontsize=18)
    ax.invert_yaxis()
    ax.set_xlim(datetime(2025, 4, 1), datetime(2026, 4, 30))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', labelsize=18)
    plt.xticks(rotation=30)
    ax.set_title(title, fontsize=20)
    ax.set_ylabel("Praxis #", fontsize=18)
    ax.set_xlabel("Zeitraum", fontsize=18)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('ganttp.png')
    plt.show()

# Datumsspalten parsen
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
    prim_start="Privat Anfang",
    prim_end="Privat Ende",
    sec_start="Privat Anfang",
    sec_end="Privat Ende",
    title="Ermittelte Wartezeiten für Privatversicherte"
)
