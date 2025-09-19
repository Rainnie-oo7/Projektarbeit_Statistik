import pandas as pd

# CSV laden
df = pd.read_csv(
    "C:/Users/pathto/wartezeiten_region2.csv",
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
    gesetzlich_values = []
    privat_values = []
    vorgespraech_values = []
    tel_bis_vorgespraech_values = []
    alle_reihen = pd.concat([
        df_prim[df_prim["Nummer"] == nummer],
        df_sec[df_sec["Nummer"] == nummer]
    ])

    for _, row in alle_reihen.iterrows():
        # Gesetzlich: nur wenn Anfang & Ende vorhanden
        if pd.notna(row["Gesetzlich Anfang"]) and pd.notna(row["Gesetzlich Ende"]):
            gesetzlich_values.append((row["Gesetzlich Ende"] - row["Gesetzlich Anfang"]).days)
        # Privat: nur wenn Anfang & Ende vorhanden
        if pd.notna(row.get("Privat Anfang")) and pd.notna(row.get("Privat Ende")):
            privat_values.append((row["Privat Ende"] - row["Privat Anfang"]).days)
        # Vorgespräch: nur wenn vorhanden & Anfang vorhanden
        if pd.notna(row["Vorgespräch"]) and pd.notna(row["Gesetzlich Anfang"]):
            vorgespraech_values.append((row["Vorgespräch"] - row["Gesetzlich Anfang"]).days)
        if pd.notna(row["Vorgespräch"]) and pd.notna(row["Gesetzlich Ende"]):
            tel_bis_vorgespraech_values.append((row["Gesetzlich Ende"] - row["Vorgespräch"]).days)



    gesetzlich_min = min(gesetzlich_values, default=pd.NA)
    gesetzlich_max = max(gesetzlich_values, default=pd.NA)
    privat_min = min(privat_values, default=pd.NA)
    privat_max = max(privat_values, default=pd.NA)
    vorgespraech_min = min(vorgespraech_values, default=pd.NA)
    vorgespraech_max = max(vorgespraech_values, default=pd.NA)
    tel_bis_vorgespraech_values_min = min(tel_bis_vorgespraech_values, default=pd.NA)
    tel_bis_vorgespraech_values_max = max(tel_bis_vorgespraech_values, default=pd.NA)

    df_wartezeiten.loc[len(df_wartezeiten)] = [
        nummer,
        gesetzlich_min, gesetzlich_max,
        vorgespraech_min, vorgespraech_max,
        tel_bis_vorgespraech_values_min, tel_bis_vorgespraech_values_max,
        privat_min, privat_max
    ]

df_wartezeiten.to_csv("wartezeiten_min_max_vorgespr_region1_2.csv", index=False, encoding='utf-8-sig')
print("CSV erstellt.")
print(df_wartezeiten)
