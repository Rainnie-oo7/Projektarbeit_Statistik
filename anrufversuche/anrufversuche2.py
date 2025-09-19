import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# Hauptdatei
df = pd.read_csv("C:/Users/pathto/datengantt.csv", encoding='cp1252')

# Datei mit Anrufversuchen
df_calls = pd.read_csv("C:/Users/mathq/Nextcloud/Projektarbeit Gastroenterologie/datenanrufversuchee.csv", encoding="cp1252")
df_calls["Datum"] = pd.to_datetime(df_calls["Datum"], format="%d.%m.%y", errors="coerce")
df_calls["Nummer"] = pd.to_numeric(df_calls["Nummer"], errors="coerce").astype("Int64")
if "Online" not in df_calls.columns:
    df_calls["Online"] = ""
else:
    df_calls["Online"] = df_calls["Online"].fillna("").astype(str).str.lower()


def plot_combined_balken(df_prim, df_sec, df_calls,
                         prim_startg, prim_endg, prim_startp, prim_endp,
                         sec_startg, sec_endg, sec_startp, sec_endp,
                         title):
    df_plot = df_prim.reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(20, len(df_plot) * 0.5 + 0.5))

    for i, row in df_plot.iterrows():
        nummer = row["Nummer"]

        # --- Primärbalken ---
        start1 = row[prim_startg]
        end1 = row[prim_endg]
        start2 = row[prim_startp]
        end2 = row[prim_endp]

        # Gesetzlich Primär
        if pd.notna(start1) and pd.notna(end1):
            ax.barh(i+0.2, (end1 - start1).days, left=start1, height=0.4,
                    color='bisque', edgecolor='black', alpha=0.7)
        elif pd.notna(start1) and pd.isna(end1):
            ax.text(start1, i+0.04, '[', va='center', ha='center', fontsize=28,
                    fontweight='normal', color='black', alpha=0.7)

        # Privat Primär
        if pd.notna(start2) and pd.notna(end2):
            ax.barh(i-0.2, (end2 - start2).days, left=start2, height=0.4,
                    color='steelblue', edgecolor='black', alpha=0.7)
        elif pd.notna(start2) and pd.isna(end2):
            ax.text(start2, i+0.04, '[', va='center', ha='center', fontsize=28,
                    fontweight='normal', color='black', alpha=0.7)

        # Primäres Vorgespräch
        if "Vorgespräch" in row:
            vorgespraech_datum = pd.to_datetime(row["Vorgespräch"], format='%d.%m.%y', errors='coerce')
            if pd.notna(vorgespraech_datum):
                ax.text(vorgespraech_datum, i + 0.25, 'I', va='center', ha='center',
                        fontsize=16, fontweight='bold', color='darkgoldenrod')

        # Primäres Vorgespräch
        if "Vorgespräch" in row:
            vorgespraech_datum = pd.to_datetime(row["Vorgespräch"], format='%d.%m.%y', errors='coerce')
            if pd.notna(vorgespraech_datum):
                ax.text(vorgespraech_datum, i+0.25, 'I', va='center', ha='center',
                        fontsize=16, fontweight='bold', color='darkgoldenrod')
        # --- Sekundärbalken ---
        match = df_sec[df_sec["Nummer"] == nummer]
        if not match.empty:
            for _, sec_row in match.iterrows():
                sec_start_dateg = sec_row[sec_startg]
                sec_end_dateg = sec_row[sec_endg]
                sec_start_datep = sec_row[sec_startp]
                sec_end_datep = sec_row[sec_endp]

                # Gesetzlich Sekundär
                if pd.notna(sec_start_dateg) and pd.notna(sec_end_dateg):
                    ax.barh(i + 0.2, (sec_end_dateg - sec_start_dateg).days, left=sec_start_dateg,
                            height=0.4, color='seagreen', edgecolor='black', alpha=0.3)
                elif pd.notna(sec_start_dateg) and pd.isna(sec_end_dateg):
                    ax.text(sec_start_dateg, i + 0.04, '[', va='center', ha='center', fontsize=28,
                            fontweight='normal', color='black', alpha=0.5)

                # Privat Sekundär
                if pd.notna(sec_start_datep) and pd.notna(sec_end_datep):
                    ax.barh(i - 0.2, (sec_end_datep - sec_start_datep).days, left=sec_start_datep,
                            height=0.4, color='steelblue', alpha=0.3)
                elif pd.notna(sec_start_datep) and pd.isna(sec_end_datep):
                    ax.text(sec_start_datep, i + 0.04, '[', va='center', ha='center', fontsize=28,
                            fontweight='normal', color='black', alpha=0.5)

                # Sekundäres Vorgespräch
                if "Vorgespräch" in sec_row:
                    vorgespraech_datum_sec = pd.to_datetime(sec_row["Vorgespräch"], format='%d.%m.%y', errors='coerce')
                    if pd.notna(vorgespraech_datum_sec):
                        ax.text(vorgespraech_datum_sec, i + 0.25, 'I', va='center', ha='center',
                                fontsize=16, fontweight='bold', color='green', alpha=0.3)

        # --- Sekundärbalken ---
        # match = df_sec[df_sec["Nummer"] == nummer]
        # if not match.empty:
        #     sec_row = match.iloc[0]
        #     sec_start_dateg = sec_row[sec_startg]
        #     sec_end_dateg = sec_row[sec_endg]
        #     sec_start_datep = sec_row[sec_startp]
        #     sec_end_datep = sec_row[sec_endp]
        #
        #     # Gesetzlich Sekundär
        #     if pd.notna(sec_start_dateg) and pd.notna(sec_end_dateg):
        #         ax.barh(i+0.2, (sec_end_dateg - sec_start_dateg).days, left=sec_start_dateg,
        #                 height=0.4, color='seagreen', edgecolor='black', alpha=0.3)
        #     elif pd.notna(sec_start_dateg) and pd.isna(sec_end_dateg):
        #         ax.text(sec_start_dateg, i+0.04, '[', va='center', ha='center', fontsize=28,
        #                 fontweight='normal', color='black', alpha=0.5)
        #
        #     # Privat Sekundär
        #     if pd.notna(sec_start_datep) and pd.notna(sec_end_datep):
        #         ax.barh(i-0.2, (sec_end_datep - sec_start_datep).days, left=sec_start_datep,
        #                 height=0.4, color='steelblue', alpha=0.3)
        #     elif pd.notna(sec_start_datep) and pd.isna(sec_end_datep):
        #         ax.text(sec_start_datep, i+0.04, '[', va='center', ha='center', fontsize=28,
        #                 fontweight='normal', color='black', alpha=0.5)
        #
        #     # Sekundäres Vorgespräch
        #     if "Vorgespräch" in sec_row:
        #         vorgespraech_datum_sec = pd.to_datetime(sec_row["Vorgespräch"], format='%d.%m.%y', errors='coerce')
        #         if pd.notna(vorgespraech_datum_sec):
        #             ax.text(vorgespraech_datum_sec, i+0.25, 'I', va='center', ha='center',
        #                     fontsize=16, fontweight='bold', color='green', alpha=0.3)

        # --- Anrufversuche und Online ---
        calls = df_calls[df_calls["Nummer"] == nummer]
        if not calls.empty:
            grouped = calls.groupby("Datum")
            for datum, group in grouped:
                if pd.isna(datum):
                    continue
                total_at_date = len(group)
                online_group = group[group["Online"] == "online"]
                online_count = len(online_group)
                offline_count = total_at_date - online_count

                offset_days = 0.35
                # beide Typen
                if online_count > 0 and offline_count > 0:
                    ax.text(datum - timedelta(days=offset_days), i, "ı",
                            ha="center", va="center", fontsize=12, fontweight="bold", color="red")
                    if offline_count > 1:
                        ax.annotate(str(offline_count), xy=(datum - timedelta(days=offset_days), i),
                                    xytext=(4, 0), textcoords="offset points", ha="left", va="center",
                                    fontsize=8, color="red")
                    ax.text(datum + timedelta(days=offset_days), i, "i",
                            ha="center", va="center", fontsize=12, fontweight="normal", color="green")
                    if online_count > 1:
                        ax.annotate(str(online_count), xy=(datum + timedelta(days=offset_days), i),
                                    xytext=(4, 0), textcoords="offset points", ha="left", va="center",
                                    fontsize=8, color="green")
                else:
                    if online_count > 0:
                        ax.text(datum, i, "i", ha="center", va="center",
                                fontsize=12, fontweight="normal", color="green")
                        if online_count > 1:
                            ax.annotate(str(online_count), xy=(datum, i), xytext=(4,0),
                                        textcoords="offset points", ha="left", va="center",
                                        fontsize=8, color="green")
                    elif offline_count > 0:
                        ax.text(datum, i, "ı", ha="center", va="center",
                                fontsize=12, fontweight="bold", color="red")
                        if offline_count > 1:
                            ax.annotate(str(offline_count), xy=(datum, i), xytext=(4,0),
                                        textcoords="offset points", ha="left", va="center",
                                        fontsize=8, color="red")

        # --- Gesamtanzahl rechts ---
        total_calls = len(calls)
        if total_calls > 0:
            ax.text(1.01, i, str(total_calls),
                    transform=ax.get_yaxis_transform(), ha='left', va='center',
                    fontsize=12, color='blue', clip_on=False)

    # --- Achsen ---
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

    # --- Legende ---
    privat_patch = mpatches.Patch(color='steelblue', label='Privat (Erstversuch)', alpha=0.7)
    gesetzlich_patch = mpatches.Patch(color='bisque', label='Gesetzlich (Erstversuch)', alpha=0.7)
    privat_patch_zweit = mpatches.Patch(color='steelblue', label='Privat (Zweitversuch)', alpha=0.3)
    gesetzlich_patch_zweit = mpatches.Patch(color='seagreen', label='Gesetzlich (Zweitversuch)', alpha=0.3)
    call_marker = mlines.Line2D([], [], color='red', marker='$\mathregular{ı}$', markersize=7,
                                linestyle='None', label='Anrufversuch (Telefon)')
    online_marker = mlines.Line2D([], [], color='green', marker='$\mathregular{i}$', markersize=7,
                                  linestyle='None', label='Anrufversuch (Online)')
    count_numbers = mlines.Line2D([], [], color='blue', marker='$\mathregular{3}$', markersize=7,
                                  linestyle='None', label='Anzahl Kontaktierungen')

    ax.legend(handles=[privat_patch, gesetzlich_patch, privat_patch_zweit,
                       gesetzlich_patch_zweit, call_marker, online_marker, count_numbers],
              loc='upper right', fontsize=12)

    plt.tight_layout()
    plt.savefig('ganttgandp_calls_online4.png')
    plt.show()


# --- Datumsspalten parsen ---
for col in ["Gesetzlich Anfang", "Gesetzlich Ende",
            "Privat Anfang", "Privat Ende"]:
    df[col] = pd.to_datetime(df[col], format='%d.%m.%y', errors='coerce')
df["Nummer"] = pd.to_numeric(df["Nummer"], errors="coerce").astype("Int64")

# Primär / Sekundär
df_prim = df.loc[~df["Nummer"].duplicated(keep="first")]
duplikate = df["Nummer"].duplicated(keep=False)
erste = df["Nummer"].duplicated(keep="first")
df_sec = df.loc[duplikate & erste]

# --- Plot ---
plot_combined_balken(
    df_prim=df_prim,
    df_sec=df_sec,
    df_calls=df_calls,
    prim_startg="Gesetzlich Anfang",
    prim_endg="Gesetzlich Ende",
    prim_startp="Privat Anfang",
    prim_endp="Privat Ende",
    sec_startg="Gesetzlich Anfang",
    sec_endg="Gesetzlich Ende",
    sec_startp="Privat Anfang",
    sec_endp="Privat Ende",
    title="Ermittelte Wartezeiten mit Anrufversuchen"
)
