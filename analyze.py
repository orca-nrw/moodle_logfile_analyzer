import csv
import os
import re
from datetime import datetime

DATUM_FORMAT = "%d. %B %Y, %H:%M:%S"
MONATE = {
    "Januar": "January", "Februar": "February", "März": "March",
    "April": "April", "Mai": "May", "Juni": "June",
    "Juli": "July", "August": "August", "September": "September",
    "Oktober": "October", "November": "November", "Dezember": "December"
}
BLACKLIST = {""}
#directory for the logfiles 
PFAD = "2/"

def ersetze_monat(datum_str):
    for de, en in MONATE.items():
        if de in datum_str:
            return datum_str.replace(de, en)
    return datum_str

def verarbeite_datei(dateipfad):
    gaeste_ips = set()
    nutzer = set()
    kursname = ""
    fruehestes_datum = None

    with open(dateipfad, encoding='utf8') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)  # Kopfzeile überspringen

        for row in reader:
            if len(row) <= 2:
                continue

            # Datum extrahieren und vergleichen
            datum_str = ersetze_monat(row[0])
            try:
                aktuelles_datum = datetime.strptime(datum_str, DATUM_FORMAT)
                if fruehestes_datum is None or aktuelles_datum < fruehestes_datum:
                    fruehestes_datum = aktuelles_datum
            except Exception:
                pass  # Fehlerhafte Zeile ignorieren

            # Kursname extrahieren
            if not kursname and 'Kurs:' in row[3]:
                kursname = row[3].replace("Kurs:", "").strip()

            # Gäste und Nutzer*innen zählen
            if 'Gast' in row[1]:
                gaeste_ips.add(row[8])
            else:
                loginname = row[1]
                match=re.search(r"The user with id '(\d+)'", row[6])
                if match:
                    userid = match.group(1)
                    if loginname not in BLACKLIST:
                        nutzer.add(userid)

    return fruehestes_datum, kursname, len(gaeste_ips), len(nutzer)

def main():
    with open('export.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for dateiname in os.listdir(PFAD):
            dateipfad = os.path.join(PFAD, dateiname)
            datum, kurs, gaeste, nutzer = verarbeite_datei(dateipfad)
            print(f"{dateiname}: Gäste={gaeste}, Nutzer={nutzer}")
            writer.writerow([datum, kurs, gaeste, nutzer])

if __name__ == "__main__":
    main()
