import pandas as pd
import matplotlib.pyplot as plt

# CSV laden
df = pd.read_csv(
    "C:/Users/pathto/daten.csv",
    encoding='cp1252'
)

# Nummern in Integer konvertieren
df["Nummer"] = pd.to_numeric(df["Nummer"], errors="coerce").astype("Int64")

# Erste Zeile pro Nummer behalten
df_unique = df.loc[~df["Nummer"].duplicated(keep="first")]

# Alle Praxisnummern 1–33
praxisnummern = list(range(1, 34))

fig, ax = plt.subplots(figsize=(14, 2))

# Y-Achse ausschalten, Rahmen ausblenden
ax.get_yaxis().set_visible(False)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='x', bottom=False, top=False)
ax.set_xlim(0.5, 33.5)

# Texte (Dringlichkeitscodes) direkt oberhalb der Ticks platzieren
for nummer in praxisnummern:
    row = df_unique[df_unique["Nummer"] == nummer]
    text = str(row.iloc[0].get("Dringlichkeitscode", "")) if not row.empty else ""
    if text == "TSS":
        ax.annotate(
            text,
            xy=(nummer, 0), xycoords=ax.get_xaxis_transform(),
            xytext=(0, 6), textcoords="offset points",  # 6 pt ≈ 2 mm
            ha="center", va="bottom", fontsize=9, rotation=90, color="black"
        )
    else:
        # Annotate nutzt Transform: (x, 0) = Tick-Position, plus Pixel-Offset
        ax.annotate(
            text,
            xy=(nummer, 0), xycoords=ax.get_xaxis_transform(),
            xytext=(0, 6), textcoords="offset points",  # 6 pt ≈ 2 mm
            ha="center", va="bottom", fontsize=9, rotation=0, color="black"
        )

ax.set_xticks(praxisnummern)
ax.set_xticklabels(praxisnummern, fontsize=10)

plt.tight_layout()
plt.savefig("dring2.png", dpi=300, transparent=True)
plt.show()
