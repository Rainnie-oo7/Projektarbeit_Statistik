# import pandas as pd
#
# # Eingabedatei
# infile = "warten_min_max_vorgespr_reg2.csv"
# outfile = "warten_mittelwerte_reg2.csv"
#
# # CSV laden
# df = pd.read_csv(infile, sep="\t")  # falls Trennung Komma ist: sep="," anpassen
#
# # Spaltenpaare (min/max)
# spalten_paare = [
#     ("Gesetzlich_bis_Beh_Wartezeit_min", "Gesetzlich_bis_Beh_Wartezeit_max", "Gesetzlich_bis_Beh_Wartezeit_mean"),
#     ("Gesetzlich_bis_Vorgespräch_Wartezeit_min", "Gesetzlich_bis_Vorgespräch_Wartezeit_max", "Gesetzlich_bis_Vorgespräch_Wartezeit_mean"),
#     ("Vorgespräch_bis_Beh_min", "Vorgespräch_bis_Beh_max", "Vorgespräch_bis_Beh_mean"),
#     ("Privat_Wartezeit_min", "Privat_Wartezeit_max", "Privat_Wartezeit_mean"),
# ]
#
# # Mittelwerte berechnen
# for min_col, max_col, mean_col in spalten_paare:
#     if min_col in df.columns and max_col in df.columns:
#         df[mean_col] = (df[min_col] + df[max_col]) / 2
#
# # Neue CSV speichern
# df.to_csv(outfile, sep="\t", index=False, encoding="utf-8")
#
# print(f"Neue Datei mit Mittelwerten gespeichert: {outfile}")


#!/usr/bin/env python3
"""
compute_means.py

Liest eine CSV (automatisch Delimiter-Erkennung), berechnet Mittelwerte aus
jeweils *_min und *_max für die bekannten Wartezeit-Paare und schreibt:
- <infile>_means_full.csv (Original + mean-Spalten)
- <infile>_means_only.csv (Nummer + nur mean-Spalten)
"""

import pandas as pd
import unicodedata
import csv
import sys
import os

# ---------- Einstellungen ----------
INFILE = "warten_min_max_vorgespr.csv"   # anpassen: Dateiname deiner CSV
OUT_FULL = os.path.splitext(INFILE)[0] + "_means_full.csv"
OUT_MEANS = os.path.splitext(INFILE)[0] + "_means_only.csv"

# Kanonische Ausgabespalten (wie du sie willst)
pairs_spec = [
    (["gesetzlich", "beh"], "Gesetzlich_bis_Beh_Wartezeit_mean"),
    (["gesetzlich", "vorgesprach"], "Gesetzlich_bis_Vorgespräch_Wartezeit_mean"),
    (["vorgesprach", "beh"], "Vorgespräch_bis_Beh_mean"),
    (["privat"], "Privat_Wartezeit_mean")
]

# ---------- Helfer ----------
def normalize(s):
    """Unicode normalisieren, Diakritika entfernen, lowercase, whitespace->underscore"""
    if s is None:
        return ""
    s2 = unicodedata.normalize("NFKD", str(s))
    s2 = s2.encode("ascii", "ignore").decode("ascii")  # entfernt ä/ö/ü -> ae/oe/ue weg
    s2 = s2.lower().strip().replace(" ", "_")
    # zusätzlich einige nicht-alphanumerische Zeichen entfernen
    s2 = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in s2)
    # zusammengezogene Unterstriche
    while "__" in s2:
        s2 = s2.replace("__", "_")
    return s2.strip("_")

def detect_delimiter(path):
    """Versucht das Delimiter mit csv.Sniffer zu erkennen. Falls nicht möglich → None."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            sample = f.read(4096)
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
        return dialect.delimiter
    except Exception:
        return None

def read_csv_auto(path):
    """Versucht verschiedene Encodings und Delimiter automatisch."""
    tried = []
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            delim = detect_delimiter(path)
            if delim:
                df = pd.read_csv(path, encoding=enc, sep=delim)
            else:
                # pandas automatische Trennzeichen-Erkennung über engine='python'
                df = pd.read_csv(path, encoding=enc, sep=None, engine="python")
            return df, enc, delim or "auto"
        except Exception as e:
            tried.append((enc, str(e)))
    raise RuntimeError(f"Konnte Datei nicht lesen. Versuchte Encodings: {tried}")

# ---------- Main ----------
def main(infile):
    print("Lese Datei:", infile)
    df, used_enc, used_delim = read_csv_auto(infile)
    print(f"-> erfolgreich gelesen (encoding={used_enc}, delimiter={used_delim})")
    # Spalten cleanup
    df.columns = df.columns.str.strip()
    norm_map = {normalize(c): c for c in df.columns}  # normalized_name -> original_name

    # Wenn 'Nummer' fehlt, eine erzeugen (Index-basiert), damit die MEANS-Datei eine ID hat
    if "Nummer" not in df.columns:
        print("Hinweis: Spalte 'Nummer' nicht gefunden. Erzeuge 'Nummer' als 1..N")
        df.insert(0, "Nummer", range(1, len(df) + 1))

    mean_cols = []
    found_any = False

    for keywords, outname in pairs_spec:
        # Suche min und max Spalten: prüfen ob in irgendeiner normalized colname alle keywords + 'min'/'max' vorkommen
        min_col = None
        max_col = None
        for nname, orig in norm_map.items():
            if all(k in nname for k in keywords) and "min" in nname:
                min_col = orig
                break
        for nname, orig in norm_map.items():
            if all(k in nname for k in keywords) and "max" in nname:
                max_col = orig
                break

        if min_col is None or max_col is None:
            print(f"WARNING: Paar für {outname} nicht vollständig gefunden. min={min_col}, max={max_col}")
            continue

        print(f"Gefunden für {outname}: min='{min_col}', max='{max_col}'")
        # numerisch konvertieren (NaNs bleiben erhalten)
        a = pd.to_numeric(df[min_col], errors="coerce")
        b = pd.to_numeric(df[max_col], errors="coerce")
        mean_series = (a + b) / 2.0
        df[outname] = mean_series
        mean_cols.append(outname)
        found_any = True

    if not found_any:
        print("Keine Mittelwerte berechnet (keine passenden min/max Paare gefunden).")
    else:
        # Vollständige Datei (Original + mean-Spalten)
        df.to_csv(OUT_FULL, index=False, encoding="utf-8")
        # Nur Nummer + mean-Spalten
        cols_to_write = ["Nummer"] + mean_cols
        df[cols_to_write].to_csv(OUT_MEANS, index=False, encoding="utf-8")
        print(f"Dateien geschrieben:\n - {OUT_FULL}\n - {OUT_MEANS}")
        print("Beispiel-Ausgabe (erste 5 Zeilen):")
        print(df[cols_to_write].head().to_string(index=False))

if __name__ == "__main__":
    infile = INFILE
    if len(sys.argv) > 1:
        infile = sys.argv[1]
    try:
        main(infile)
    except Exception as e:
        print("Fehler:", e)
        raise
