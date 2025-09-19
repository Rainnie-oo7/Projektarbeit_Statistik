import pandas as pd

# === CSV einlesen ===
df = pd.read_csv("mittelwerte_sorten_pro_praxis.csv", sep=";")
df.columns = df.columns.str.strip()

# Spalten, die ausgewertet werden sollen
spalten = [
    "Gesetzlich_bis_Beh_Wartezeit_mean",
    "Gesetzlich_bis_Vorgespräch_Wartezeit_mean",
    "Vorgespräch_bis_Beh_mean",
    "Privat_Wartezeit_mean"
]

# Deskriptive Statistik berechnen
deskriptiv = df[spalten].describe().T  # Transponiert für bessere Lesbarkeit

# Zusätzliche Kennzahlen: Varianz
deskriptiv['varianz'] = df[spalten].var().values

# Median (50%-Quantil) ist schon enthalten, aber explizit
deskriptiv['median'] = df[spalten].median().values

# Ausgabe
print("\n--- Deskriptive Statistik ---\n")
print(deskriptiv)

# Optional: als CSV speichern
deskriptiv.to_csv("warten_mittelwerte_beidereg_sorten_pro_praxis.csv", sep=";")
print("\nFertig: warten_mittelwerte_beidereg_sorten_pro_praxis.csv")
