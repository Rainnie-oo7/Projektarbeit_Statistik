import csv
import os.path as osp

def read_csv_as_set(filepath):
    with open(filepath, newline='', encoding='latin1') as f:
        reader = csv.reader(f)
        rows = list(reader)
    header = rows[0]
    data = set(tuple(row) for row in rows[1:])  # Zeilen als Tupel in ein Set (ohne Header)
    return header, data

def compare_csv_files(file1, file2):
    header1, data1 = read_csv_as_set(file1)
    header2, data2 = read_csv_as_set(file2)

    if header1 != header2:
        print("Fehlerr Unterschiedliche Header.")
        return

    if data1 == data2:
        print("Ja Die Dateien sind identisch (unabhängig von der Zeilenreihenfolge).")
    else:
        missing_in_file2 = data1 - data2
        missing_in_file1 = data2 - data1

        if missing_in_file2:
            print("Fehler Diese Zeilen fehlen in Datei 2:")
            for row in missing_in_file2:
                print(row)
        if missing_in_file1:
            print("Fehler Diese Zeilen fehlen in Datei 1:")
            for row in missing_in_file1:
                print(row)

BASE_DIRECTORY = "C:/Users/XXXXX/Downloads"
FILENAME1 = "Koln_inngast129.csv"  # Wesel #Koln_inn_sp_gast Essen_inn_sp_gast Wesel_inn_sp_gast
FILENAME2 = "Essen_inngast129.csv"  
filepath1 = osp.join(BASE_DIRECTORY, FILENAME1)
filepath2 = osp.join(BASE_DIRECTORY, FILENAME2)
# Beispiel-Aufruf
compare_csv_files(filepath1, filepath2)
