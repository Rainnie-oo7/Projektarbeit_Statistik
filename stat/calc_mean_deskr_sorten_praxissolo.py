import pandas as pd
import numpy as np

# CSV einlesen
df = pd.read_csv(
    "C:/Users/pathto/daten.csv",
    encoding='cp1252'
)

# Nummern in Integer konvertieren
df["Nummer"] = pd.to_numeric(df["Nummer"], errors="coerce").astype("Int64")

# Datumsfelder parsen
df["Gesetzlich Anfang"] = pd.to_datetime(df["Gesetzlich Anfang"], format='%d.%m.%y', errors='coerce')
df["Gesetzlich Ende"] = pd.to_datetime(df["Gesetzlich Ende"], format='%d.%m.%y', errors='coerce')
df["Vorgespräch"] = pd.to_datetime(df["Vorgespräch"], format='%d.%m.%y', errors='coerce')
df["Privat Anfang"] = pd.to_datetime(df["Privat Anfang"], format='%d.%m.%y', errors='coerce')
df["Privat Ende"] = pd.to_datetime(df["Privat Ende"], format='%d.%m.%y', errors='coerce')

# Wartezeiten in Tagen berechnen, nur wenn beide Daten vorhanden sind
df["Gesetzlich_bis_Beh_Wartezeit"] = (df["Gesetzlich Ende"] - df["Gesetzlich Anfang"]).dt.days
df["Gesetzlich_bis_Vorgespräch_Wartezeit"] = (df["Vorgespräch"] - df["Gesetzlich Anfang"]).dt.days
df["Vorgespräch_bis_Beh_Wartezeit"] = (df["Gesetzlich Ende"] - df["Vorgespräch"]).dt.days
df["Privat_Wartezeit"] = (df["Privat Ende"] - df["Privat Anfang"]).dt.days

# Spalten, die gemittelt werden sollen
spalten = [
    "Gesetzlich_bis_Beh_Wartezeit",
    "Gesetzlich_bis_Vorgespräch_Wartezeit",
    "Vorgespräch_bis_Beh_Wartezeit",
    "Privat_Wartezeit"
]

# Mittelwerte pro Praxisnummer berechnen
df_mittel = df.groupby("Nummer")[spalten].mean().reset_index()

# Spaltennamen anpassen (mit "_mean")
df_mittel.rename(columns={
    "Gesetzlich_bis_Beh_Wartezeit": "Gesetzlich_bis_Beh_Wartezeit_mean",
    "Gesetzlich_bis_Vorgespräch_Wartezeit": "Gesetzlich_bis_Vorgespräch_Wartezeit_mean",
    "Vorgespräch_bis_Beh_Wartezeit": "Vorgespräch_bis_Beh_mean",
    "Privat_Wartezeit": "Privat_Wartezeit_mean"
}, inplace=True)

# In CSV exportieren
df_mittel.to_csv("C:/Users/mathq/Nextcloud/Projektarbeit Gastroenterologie/mittelwerte_sorten_pro_praxis.csv",
                 sep=";", index=False)

print("Fertig: mittelwerte_sorten_pro_praxis.csv")
