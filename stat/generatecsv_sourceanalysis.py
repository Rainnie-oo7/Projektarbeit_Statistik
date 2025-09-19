import pandas as pd

# CSV laden
df = pd.read_csv(
    "C:/Users/pathto/wartezeiten_region1.csv",
    encoding='cp1252'
)

# Nummern in Integer konvertieren
df["Nummer"] = pd.to_numeric(df["Nummer"], errors="coerce").astype("Int64")

# Datumsfelder parsen
df["Gesetzlich Anfang"] = pd.to_datetime(df["Gesetzlich Anfang"], format='%d.%m.%y', errors='coerce')
df["Gesetzlich Ende"] = pd.to_datetime(df["Gesetzlich Ende"], format='%d.%m.%y', errors='coerce')
df["Privat Anfang"] = pd.to_datetime(df["Privat Anfang"], format='%d.%m.%y', errors='coerce')
df["Privat Ende"] = pd.to_datetime(df["Privat Ende"], format='%d.%m.%y', errors='coerce')
df["Vorgespräch"] = pd.to_datetime(df["Vorgespräch"], format='%d.%m.%y', errors='coerce')

# Primär- und Sekundärbalken für jede Nummer
df_prim = df.loc[~df["Nummer"].duplicated(keep="first")]
duplikate = df["Nummer"].duplicated(keep=False)
erste = df["Nummer"].duplicated(keep="first")
df_sec = df.loc[duplikate & erste]

# Neues DataFrame vorbereiten
praxisnummern = df["Nummer"].unique()
df_wartezeiten = pd.DataFrame(columns=[
    "Nummer",
    "Gesetzlich_Wartezeit_min", "Gesetzlich_Wartezeit_max",
    "Vorgespräch_Wartezeit_min", "Vorgespräch_Wartezeit_max",
    "Privat_Wartezeit_min", "Privat_Wartezeit_max"
])

for nummer in praxisnummern:
    gesetzlich_values = []
    privat_values = []
    vorgespraech_values = []

    # Funktion zur Berechnung der Wartezeit (Enddatum oder Vorgespräch fallback)
    def berechne_wartezeit(start, ende, vorgespraech):
        if pd.notna(start):
            if pd.notna(ende):
                return (ende - start).days
            elif pd.notna(vorgespraech):
                return (vorgespraech - start).days
            else:
                return pd.NA
        else:
            return pd.NA

    # Alle Einträge (Primär + Sekundär) prüfen
    alle_reihen = pd.concat([
        df_prim[df_prim["Nummer"] == nummer],
        df_sec[df_sec["Nummer"] == nummer]
    ])

    for _, row in alle_reihen.iterrows():
        # Gesetzlich
        gesetzlich_values.append(berechne_wartezeit(row["Gesetzlich Anfang"], row["Gesetzlich Ende"], row["Vorgespräch"]))
        # Privat
        privat_values.append(berechne_wartezeit(row.get("Privat Anfang"), row.get("Privat Ende"), row["Vorgespräch"]))
        # Vorgespräch
        if pd.notna(row["Vorgespräch"]) and pd.notna(row["Gesetzlich Anfang"]):
            vorgespraech_values.append((row["Vorgespräch"] - row["Gesetzlich Anfang"]).days)
        else:
            vorgespraech_values.append(pd.NA)

    # Min/Max berechnen, nur gültige Werte
    gesetzlich_min = min([v for v in gesetzlich_values if pd.notna(v)], default=pd.NA)
    gesetzlich_max = max([v for v in gesetzlich_values if pd.notna(v)], default=pd.NA)
    privat_min = min([v for v in privat_values if pd.notna(v)], default=pd.NA)
    privat_max = max([v for v in privat_values if pd.notna(v)], default=pd.NA)
    vorgespraech_min = min([v for v in vorgespraech_values if pd.notna(v)], default=pd.NA)
    vorgespraech_max = max([v for v in vorgespraech_values if pd.notna(v)], default=pd.NA)

    # In DataFrame eintragen
    df_wartezeiten.loc[len(df_wartezeiten)] = [
        nummer,
        gesetzlich_min, gesetzlich_max,
        vorgespraech_min, vorgespraech_max,
        privat_min, privat_max
    ]

# CSV speichern
df_wartezeiten.to_csv("wartezeiten_min_max_vorgespr_region1.csv", index=False, encoding='utf-8-sig')
print("CSV 'wartezeiten_min_max_vorgespräch_alle.csv' erstellt.")
print(df_wartezeiten)
