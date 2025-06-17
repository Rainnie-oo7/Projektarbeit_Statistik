import pandas as pd
import os.path as osp
# --- Datei-Pfade ---
BASE_DIRECTORY = "C:/Users/mathq/Downloads"
FILENAME1 = 'ergebnis_inngast129_98.csv'    # ergebnis_inngast129_98.csv
FILENAME2 = 'ergebnis_inn_schwerp141_108.csv' #ergebnis_inn_schwerp141_108.csv
file1 = osp.join(BASE_DIRECTORY, FILENAME1)
file2 = osp.join(BASE_DIRECTORY, FILENAME2)

# --- Einlesen ---
df1 = pd.read_csv(file1, encoding='utf-8-sig')
df2 = pd.read_csv(file2, encoding='utf-8-sig')

# --- Nur gültige Adressen ---
def clean(df):
    return df[df['StrasseNr'].notna() & (df['StrasseNr'].astype(str).str.strip() != '')].copy()

df1 = clean(df1)
df2 = clean(df2)

# --- Funktion zur Aggregation: Zahlen summieren, Strings zusammenfassen ---
def custom_agg(series):
    if pd.api.types.is_numeric_dtype(series):
        return series.sum()
    else:
        s = series.dropna().astype(str).str.strip()
        s = s[s != '']
        s = s[s != 'nan']
        return '\n'.join(sorted(set(s))) if not s.empty else ''

# --- Gruppieren innerhalb der einzelnen Dateien ---
agg1 = df1.groupby('StrasseNr', as_index=False).agg(custom_agg)
agg2 = df2.groupby('StrasseNr', as_index=False).agg(custom_agg)

# --- Zusammenführen auf Basis gemeinsamer Straße Nr. ---
merged = pd.merge(agg1, agg2, on='StrasseNr', how='outer', suffixes=('_1', '_2'))

# --- Jetzt pro Spalte beide Varianten zusammenführen ---
# Ergebnis-DataFrame vorbereiten
result = pd.DataFrame()
result['StrasseNr'] = merged['StrasseNr']

# Alle Spalten außer "Straße Nr." automatisch verarbeiten
for col in merged.columns:
    if col.endswith('_1') and col != 'Straße Nr._1':
        base = col[:-2]
        col1 = col
        col2 = base + '_2'
        if col2 in merged:
            # Strings zusammenführen (mit Zeilenumbruch), Zahlen summieren
            if pd.api.types.is_numeric_dtype(merged[col1]) and pd.api.types.is_numeric_dtype(merged[col2]):
                result[base] = merged[col1] + merged[col2]
            else:
                def combine_strs(a, b):
                    s = pd.Series([a, b])
                    s = s.dropna().astype(str).str.strip()
                    s = s[s != '']
                    return '\n'.join(sorted(set(s)))
                result[base] = merged.apply(lambda row: combine_strs(row[col1], row[col2]), axis=1)

# --- Ausgabe ---
result.to_csv('aggregiertes_ergebnis_outer.csv', index=False)
print("✅ Aggregation abgeschlossen: aggregiertes_ergebnis.csv")
