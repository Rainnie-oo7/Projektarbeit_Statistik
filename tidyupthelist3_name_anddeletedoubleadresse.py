import pandas as pd
import os.path as osp

# Pfade
BASE_DIRECTORY = "C:/Users/XXXXX/Downloads"
FILENAME1 = "Koln_inngast129.csv"  # Koln_inngast129.csv  Koln_inn_schwerp141.csv"Koln_inngast129.csv"  # Wesel #Koln_inn_sp_gast Essen_inn_sp_gast Wesel_inn_sp_gast
FILENAME2 = "Koln_inn_schwerp141.csv"
filepath1 = osp.join(BASE_DIRECTORY, FILENAME1)
filepath2 = osp.join(BASE_DIRECTORY, FILENAME2)

print("Pfad zur Datei:", filepath1)
print("Pfad zur Datei:", filepath2)
print("Existiert?", osp.exists(filepath1))
print("Existiert?", osp.exists(filepath2))

# Einlesen
df = pd.read_csv(filepath2, encoding='latin1')

#  Adresse zusammenbauen
df['Adresse, Tel., Kontakt PLZ Ort'] = (
    df['Adresse, Tel., Kontakt PLZ Ort'].astype(str) + "\n" +
    df['Straße Nr.'].astype(str) + "\n" +
    df['PLZ'].astype(str) + ", " +
    df['Ort'].astype(str)
)

# Nur gültige Adressen
df_valid = df[df['Straße Nr.'].notna() & (df['Straße Nr.'].astype(str).str.strip() != '')].copy()

# Aggregierfunktion für alle Spalten
def custom_agg(series):
    if pd.api.types.is_numeric_dtype(series):
        return series.sum()
    else:
        s = series.dropna().astype(str).str.strip()
        s = s[s != '']
        s = s[s != 'nan']
        s = s[s != 'None']
        return '\n'.join(sorted(set(s))) if not s.empty else ''

# gruppieren nach Straße Nr.
df_grouped = df_valid.groupby('Straße Nr.', as_index=False).agg(custom_agg)

# Optional: Leere Adressen wieder anhängen
df_empty = df[df['Straße Nr.'].isna() | (df['Straße Nr.'].astype(str).str.strip() == '')]
df_final = pd.concat([df_grouped, df_empty], ignore_index=True)

# Ergebnis
print(df_final)
df_final.to_csv("ergebnis_inn_schwerp141.csv", index=False) # Koln_inngast129.csv Koln_inn_schwerp141.csv  # Wesel_inn_sp_gast #Koln_inn_sp_gast Essen_inn_sp_gast

