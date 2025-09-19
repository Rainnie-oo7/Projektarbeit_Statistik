import pandas as pd

# CSV laden
df = pd.read_csv(
    "C:/Users/pathto/daten.csv",
    encoding='cp1252'
)

df["Nummer"] = pd.to_numeric(df["Nummer"], errors="coerce").astype("Int64")

# Datumsfelder parsen
for col in ["Gesetzlich Anfang", "Gesetzlich Ende", "Privat Anfang", "Privat Ende", "Vorgespräch"]:
    df[col] = pd.to_datetime(df[col], format='%d.%m.%y', errors='coerce')

# Primär + Sekundär
df_prim = df.loc[~df["Nummer"].duplicated(keep="first")]
duplikate = df["Nummer"].duplicated(keep=False)
erste = df["Nummer"].duplicated(keep="first")
df_sec = df.loc[duplikate & erste]

praxisnummern = df["Nummer"].unique()
df_wartezeiten = pd.DataFrame(columns=[
    "Nummer",
    "Gesetzlich_bis_Beh_Wartezeit_min", "Gesetzlich_bis_Beh_Wartezeit_max",
    "Gesetzlich_bis_Vorgespräch_Wartezeit_min", "Gesetzlich_bis_Vorgespräch_Wartezeit_max",
    "Vorgespräch_bis_Beh_min", "Vorgespräch_bis_Beh_max",
    "Privat_Wartezeit_min", "Privat_Wartezeit_max"
])

for nummer in praxisnummern:
    alle_reihen = pd.concat([
        df_prim[df_prim["Nummer"] == nummer],
        df_sec[df_sec["Nummer"] == nummer]
    ])

    wartezeiten = []
    vorgespraeche = []
    tel_bis_vorgespraech = []
    privat = []

    for _, row in alle_reihen.iterrows():
        # Gesetzlich
        if pd.notna(row["Gesetzlich Anfang"]) and pd.notna(row["Gesetzlich Ende"]):
            wartezeiten.append((row["Gesetzlich Ende"] - row["Gesetzlich Anfang"]).days)
        else:
            wartezeiten.append(pd.NA)

        # Privat
        if pd.notna(row.get("Privat Anfang")) and pd.notna(row.get("Privat Ende")):
            privat.append((row["Privat Ende"] - row["Privat Anfang"]).days)
        else:
            privat.append(pd.NA)

        # Vorgespräch
        if pd.notna(row["Vorgespräch"]) and pd.notna(row["Gesetzlich Anfang"]):
            vorgespraeche.append((row["Vorgespräch"] - row["Gesetzlich Anfang"]).days)
        else:
            vorgespraeche.append(pd.NA)

        # Tel bis Vorgespräch
        if pd.notna(row["Vorgespräch"]) and pd.notna(row["Gesetzlich Ende"]):
            tel_bis_vorgespraech.append((row["Gesetzlich Ende"] - row["Vorgespräch"]).days)
        else:
            tel_bis_vorgespraech.append(pd.NA)

    # Fehlende Werte anhand des relativen Bruchteils schätzen
    # Wenn Vorgespräch fehlt, versucht, den Bruch von einem anderen Versuch zu übernehmen und
    # daraus einen erwarteten/geschätzen Vorgesprächstermin zu bauen.
    for i in range(len(wartezeiten)):
        if pd.isna(vorgespraeche[i]) and pd.notna(wartezeiten[i]):
            # Falls es einen anderen Satz mit Vorgespräch gibt
            for j in range(len(wartezeiten)):
                if i != j and pd.notna(vorgespraeche[j]) and pd.notna(wartezeiten[j]):
                    bruch = vorgespraeche[j] / wartezeiten[j]
                    vorgespraeche[i] = round(bruch * wartezeiten[i])
                    break  # nur einmal schätzen

        if pd.isna(tel_bis_vorgespraech[i]) and pd.notna(wartezeiten[i]) and pd.notna(vorgespraeche[i]):
            tel_bis_vorgespraech[i] = wartezeiten[i] - vorgespraeche[i]

    # Min/Max bilden
    gesetzlich_min = min([w for w in wartezeiten if pd.notna(w)], default=pd.NA)
    gesetzlich_max = max([w for w in wartezeiten if pd.notna(w)], default=pd.NA)
    vorgespraech_min = min([v for v in vorgespraeche if pd.notna(v)], default=pd.NA)
    vorgespraech_max = max([v for v in vorgespraeche if pd.notna(v)], default=pd.NA)
    tel_bis_vorgespraech_min = min([t for t in tel_bis_vorgespraech if pd.notna(t)], default=pd.NA)
    tel_bis_vorgespraech_max = max([t for t in tel_bis_vorgespraech if pd.notna(t)], default=pd.NA)
    privat_min = min([p for p in privat if pd.notna(p)], default=pd.NA)
    privat_max = max([p for p in privat if pd.notna(p)], default=pd.NA)

    df_wartezeiten.loc[len(df_wartezeiten)] = [
        nummer,
        gesetzlich_min, gesetzlich_max,
        vorgespraech_min, vorgespraech_max,
        tel_bis_vorgespraech_min, tel_bis_vorgespraech_max,
        privat_min, privat_max
    ]

df_wartezeiten.to_csv("warten_min_max_vorgespr.csv", index=False, encoding='utf-8-sig')
print("CSV erstellt.")
print(df_wartezeiten)
