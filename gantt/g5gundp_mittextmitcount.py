import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
from math import ceil
from PIL import Image

df = pd.read_csv("C:/Users/pathto/datengantt.csv", encoding='cp1252')

def plot_combined_balken(df_prim, df_sec, prim_startg, prim_endg, prim_startp, prim_endp,
                         sec_startg, sec_endg, sec_startp, sec_endp, title):

    df_plot = df_prim.reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(20, len(df_plot) * 0.5 + 0.5))

    # Dictionary für Mittelwerte (pro Nummer: privat/gesetzlich)
    mean_durations = {nummer: {"gesetzlich": [], "privat": []} for nummer in df_plot["Nummer"]}

    for i, row in df_plot.iterrows():
        nummer = row["Nummer"]

        # --- Primärdaten ---
        start1 = row[prim_startg]
        end1 = row[prim_endg]
        start2 = row[prim_startp]
        end2 = row[prim_endp]

        # Gesetzlich Primär
        if pd.notna(start1) and pd.notna(end1):
            dauer = (end1 - start1).days
            mean_durations[nummer]["gesetzlich"].append(dauer)
            ax.barh(i+0.2, dauer, left=start1, height=0.4,
                    color='bisque', edgecolor='black')
        elif pd.notna(start1) and pd.isna(end1):
            ax.text(start1, i+0.04, '[', va='center', ha='center',
                    fontsize=28, fontweight='normal', color='black')

        # Privat Primär
        if pd.notna(start2) and pd.notna(end2):
            dauer = (end2 - start2).days
            mean_durations[nummer]["privat"].append(dauer)
            ax.barh(i-0.2, dauer, left=start2, height=0.4,
                    color='steelblue', edgecolor='black')
        elif pd.notna(start2) and pd.isna(end2):
            ax.text(start2, i+0.04, '[', va='center', ha='center',
                    fontsize=28, fontweight='normal', color='black')

        # --- Sekundärdaten ---
        matches = df_sec[df_sec["Nummer"] == nummer]
        if not matches.empty:
            for _, sec_row in matches.iterrows():
                sec_start_dateg = sec_row[sec_startg]
                sec_end_dateg = sec_row[sec_endg]
                sec_start_datep = sec_row[sec_startp]
                sec_end_datep = sec_row[sec_endp]

                if pd.notna(sec_start_dateg) and pd.notna(sec_end_dateg):
                    dauer = (sec_end_dateg - sec_start_dateg).days
                    mean_durations[nummer]["gesetzlich"].append(dauer)
                    ax.barh(i+0.2, dauer, left=sec_start_dateg,
                            height=0.4, color='seagreen', edgecolor='black', alpha=0.3)

                if pd.notna(sec_start_datep) and pd.notna(sec_end_datep):
                    dauer = (sec_end_datep - sec_start_datep).days
                    mean_durations[nummer]["privat"].append(dauer)
                    ax.barh(i-0.2, dauer, left=sec_start_datep,
                            height=0.4, color='steelblue', alpha=0.5)

    # --- Achsen-Setup ---
    ax.set_yticks(range(len(df_plot)))
    ax.set_yticklabels(df_plot["Nummer"], fontsize=18)
    ax.invert_yaxis()
    ax.set_xlim(datetime(2025, 4, 1), datetime(2026, 6, 5))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(interval=1))
    ax.grid(axis='x', linestyle='--', alpha=0.5, which='major')
    ax.grid(axis='x', linestyle=':', alpha=0.3, which='minor')
    ax.tick_params(axis='x', labelsize=18)
    plt.xticks(rotation=30)
    ax.set_title(title, fontsize=20)
    ax.set_ylabel("Praxis #", fontsize=18)
    ax.set_xlabel("Zeitraum", fontsize=18)

    plt.tight_layout()
    plt.savefig('gantt_links.png')
    plt.close(fig)

    # --- Mittelwerte berechnen + Plot ---
    fig2, ax2 = plt.subplots(figsize=(3, len(df_plot) * 0.43 - 0.15))

    for i, nummer in enumerate(df_plot["Nummer"]):
        g_vals = mean_durations[nummer]["gesetzlich"]
        p_vals = mean_durations[nummer]["privat"]
        if g_vals:
        #     print(nummer, str(ceil(np.mean(g_vals))))
            mean_g = ceil(np.mean(g_vals))
            ax2.text(0.5, i + 0.2, str(mean_g), color="darkgoldenrod",
                     ha="center", va="center", weight="bold", fontsize=14)

        if p_vals:
            # print(nummer, str(ceil(np.mean(p_vals))))
            mean_p = ceil(np.mean(p_vals))
            ax2.text(0.5, i - 0.2, str(mean_p), color="cornflowerblue",
                     ha="center", va="center", weight="bold", fontsize=14)

    ax2.set_yticks(range(len(df_plot)))
    ax2.set_yticklabels(df_plot["Nummer"], fontsize=18)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 1)
    ax2.set_xticks([])


    # Rahmenlinien entfernen
    for spine in ax2.spines.values():
        spine.set_visible(False)

    # Tick-Marken entfernen (nur Zahlen behalten)
    ax2.tick_params(left=False, right=False, top=False, bottom=False)

    plt.tight_layout()
    plt.savefig("gantt_rechts.png", bbox_inches="tight", pad_inches=0)
    plt.close(fig2)

    # --- Beide Bilder kombinieren ---
    img1 = Image.open("gantt_links.png")
    img2 = Image.open("gantt_rechts.png")

    new_width = img1.width + img2.width
    new_height = max(img1.height, img2.height)

    new_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))
    new_img.paste(img1, (0, 0))
    new_img.paste(img2, (img1.width, 0))

    new_img.save("gantt_merged0.png")
    new_img.show()

# Datumsspalten parsen
for col in ["Gesetzlich Anfang", "Gesetzlich Ende"]:
    df[col] = pd.to_datetime(df[col], format='%d.%m.%y', errors='coerce')
for col in ["Privat Anfang", "Privat Ende"]:
    df[col] = pd.to_datetime(df[col], format='%d.%m.%y', errors='coerce')

df_prim = df.loc[~df["Nummer"].duplicated(keep="first")]
duplikate = df["Nummer"].duplicated(keep=False)
erste = df["Nummer"].duplicated(keep="first")
df_sec = df.loc[duplikate & erste]

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
