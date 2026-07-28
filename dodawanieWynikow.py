# -*- coding: utf-8 -*-

import csv
import os
import sys

csv.field_size_limit(sys.maxsize)


plik_wyniki = "./dane/wyniki.csv"


pliki = [
    (
        "./dane/dataBase_futbol_popularne_trend.csv",
        "./dane/kod_dataBase_futbol_popularne_trend.csv"
    ),
    (
        "./dane/dataBase_futbol_trend.csv",
        "./dane/kod_dataBase_futbol_trend.csv"
    ),

    (
        "./dane/analizaKursowDni_dataBase_futbol.csv",
        "./dane/mozg_analizaKursowDni_dataBase_futbol.csv"
    ),

    (
        "./dane/kursy_popularne_przygotowane.csv",
        "./dane/mozg_kursy_popularne_przygotowane.csv"
    ),

    (
        "./dane/kursy_przygotowane.csv",
        "./dane/mozg_kursy_przygotowane_wynik.csv"
    )

]



# -----------------------------
# WYNIKI
# klucz = indeks 0
# wartość = indeks 1
# -----------------------------

wyniki = {}


with open(
    plik_wyniki,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    reader = csv.reader(
        f,
        delimiter=";"
    )

    for row in reader:

        if len(row) >= 2:

            wyniki[row[0].strip()] = row[1].strip()



print("Wyników:", len(wyniki))



# -----------------------------
# ŁĄCZENIE
# -----------------------------

for plik_in, plik_out in pliki:


    licznik = 0


    with open(
        plik_in,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as fin, open(
        plik_out,
        "a",
        encoding="utf-8",
        newline=""
    ) as fout:


        reader = csv.reader(
            fin,
            delimiter=";"
        )


        writer = csv.writer(
            fout,
            delimiter=";"
        )


        for row in reader:


            if not row:
                continue


            klucz = row[0].strip()


            if klucz in wyniki:

                row.append(
                    wyniki[klucz]
                )


                writer.writerow(row)

                licznik += 1



    print(
        plik_out,
        "dodano:",
        licznik
    )


print("Gotowe")