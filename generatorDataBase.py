

import csv
from datetime import datetime


PLIK = "oferta_Popularne_wynik.csv"

PLIK_DZIS = "./typerBetAi/database_Popularne_dzisiaj.csv"

PLIK_LIGA = "./typerBetAi/liga_Popularne_dzisiaj.csv"





def filtruj_oferte():

    teraz = datetime.now()
    dzisiaj = teraz.date()

    mecze_dzisiaj = []
    mecze_przyszle = []


    with open(
        PLIK,
        "r",
        encoding="utf-8"
    ) as f:


        reader = csv.reader(
            f,
            delimiter=";"
        )


        for row in reader:


            if len(row) < 3:
                continue


            try:

                data_godzina = row[1].strip()


                data_meczu = datetime.strptime(
                    data_godzina,
                    "%d-%m-%Y,%H:%M"
                )


                # mecze, które już się odbyły
                # pomijamy

                if data_meczu < teraz:
                    continue



                # tylko dzisiejsze do database_dzisiaj

                if data_meczu.date() == dzisiaj:

                    mecze_dzisiaj.append(row)



                # wszystkie przyszłe zostają w ofercie

                mecze_przyszle.append(row)



            except Exception as e:

                print(
                    "Błąd:",
                    row,
                    e
                )


    return mecze_dzisiaj, mecze_przyszle




def zapisz(dane, plik):

    with open(
        plik,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:


        writer = csv.writer(
            f,
            delimiter=";"
        )


        writer.writerows(
            dane
        )




def zapisz_database_liga(dane, plik):

    wynik = []


    for row in dane:

        if len(row) < 3:
            continue


        wynik.append(
            [
                row[2],  # mecz
                row[0],  # liga
                row[1]   # data,godzina
            ]
        )


    zapisz(
        wynik,
        plik
    )





# =========================
# START
# =========================


dzisiejsze, przyszle = filtruj_oferte()



# tylko dzisiejsze mecze

zapisz(
    dzisiejsze,
    PLIK_DZIS
)



# cała baza bez zakończonych

zapisz(
    przyszle,
    PLIK
)



# baza liga tylko dzisiejsze

zapisz_database_liga(
    dzisiejsze,
    PLIK_LIGA
)



print("========================")
print(
    "Aktualny czas:",
    datetime.now().strftime("%d-%m-%Y %H:%M")
)
print(
    "Dzisiejsze mecze:",
    len(dzisiejsze)
)
print(
    "Pozostałe przyszłe:",
    len(przyszle)
)
print("========================")


import csv
from datetime import datetime


PLIK = "oferta_wynik.csv"

PLIK_DZIS = "./typerBetAi/database_dzisiaj.csv"

PLIK_LIGA = "./typerBetAi/liga_dzisiaj.csv"





def filtruj_oferte():

    teraz = datetime.now()
    dzisiaj = teraz.date()

    mecze_dzisiaj = []
    mecze_przyszle = []


    with open(
        PLIK,
        "r",
        encoding="utf-8"
    ) as f:


        reader = csv.reader(
            f,
            delimiter=";"
        )


        for row in reader:


            if len(row) < 3:
                continue


            try:

                data_godzina = row[1].strip()


                data_meczu = datetime.strptime(
                    data_godzina,
                    "%d-%m-%Y,%H:%M"
                )


                # mecze, które już się odbyły
                # pomijamy

                if data_meczu < teraz:
                    continue



                # tylko dzisiejsze do database_dzisiaj

                if data_meczu.date() == dzisiaj:

                    mecze_dzisiaj.append(row)



                # wszystkie przyszłe zostają w ofercie

                mecze_przyszle.append(row)



            except Exception as e:

                print(
                    "Błąd:",
                    row,
                    e
                )


    return mecze_dzisiaj, mecze_przyszle




def zapisz(dane, plik):

    with open(
        plik,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:


        writer = csv.writer(
            f,
            delimiter=";"
        )


        writer.writerows(
            dane
        )




def zapisz_database_liga(dane, plik):

    wynik = []


    for row in dane:

        if len(row) < 3:
            continue


        wynik.append(
            [
                row[2],  # mecz
                row[0],  # liga
                row[1]   # data,godzina
            ]
        )


    zapisz(
        wynik,
        plik
    )





# =========================
# START
# =========================


dzisiejsze, przyszle = filtruj_oferte()



# tylko dzisiejsze mecze

zapisz(
    dzisiejsze,
    PLIK_DZIS
)



# cała baza bez zakończonych

zapisz(
    przyszle,
    PLIK
)



# baza liga tylko dzisiejsze

zapisz_database_liga(
    dzisiejsze,
    PLIK_LIGA
)



print("========================")
print(
    "Aktualny czas:",
    datetime.now().strftime("%d-%m-%Y %H:%M")
)
print(
    "Dzisiejsze mecze:",
    len(dzisiejsze)
)
print(
    "Pozostałe przyszłe:",
    len(przyszle)
)
print("========================")