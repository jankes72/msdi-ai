import csv
import shutil
import os

from datetime import datetime


PLIK = "./danePomocnicze/oferta_Popularne_wynik.csv"


PLIK_DZIS = "./dane/database_Popularne_dzisiaj.csv"

PLIK_LIGA = "./dane/liga_Popularne_dzisiaj.csv"


ARCHIWUM = "./archiwa/DataBase/"





def archiwizuj_plik(plik, nazwa):


    if not os.path.exists(plik):

        print(
            "Brak pliku do archiwizacji:",
            plik
        )

        return



    os.makedirs(
        ARCHIWUM,
        exist_ok=True
    )



    plik_archiwum = (
        ARCHIWUM
        +
        nazwa
    )



    shutil.copy2(
        plik,
        plik_archiwum
    )



    print(
        "Archiwum zapisane:",
        plik_archiwum
    )









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



                # pomijamy mecze zakończone

                if data_meczu < teraz:

                    continue





                # mecze dzisiejsze

                if data_meczu.date() == dzisiaj:

                    mecze_dzisiaj.append(
                        row
                    )





                # wszystkie przyszłe

                mecze_przyszle.append(
                    row
                )



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
                row[2],   # mecz
                row[0],   # liga
                row[1]    # data godzina
            ]
        )



    zapisz(
        wynik,
        plik
    )









# =========================
# START PROGRAMU
# =========================



# katalog danych

os.makedirs(
    "./dane/",
    exist_ok=True
)





# =========================
# ARCHIWIZACJA
# =========================



data = datetime.now().strftime(
    "%Y-%m-%d"
)



# baza popularna z datą

archiwizuj_plik(
    PLIK,
    "dataBase_futbol_popularne" + data + ".csv"
)



# baza liga popularna bez daty

archiwizuj_plik(
    PLIK_LIGA,
    "liga_popularne.csv"
)







# =========================
# FILTROWANIE
# =========================



dzisiejsze, przyszle = filtruj_oferte()







# zapis dzisiejszych meczów

zapisz(
    dzisiejsze,
    PLIK_DZIS
)







# aktualizacja głównej bazy

zapisz(
    przyszle,
    PLIK
)







# aktualizacja ligi popularnej

zapisz_database_liga(
    dzisiejsze,
    PLIK_LIGA
)








print("========================")


print(
    "Aktualny czas:",
    datetime.now().strftime(
        "%d-%m-%Y %H:%M"
    )
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
import shutil
import os

from datetime import datetime


PLIK = "./danePomocnicze/oferta_wynik.csv"


PLIK_DZIS = "./dane/database_dzisiaj.csv"

PLIK_LIGA = "./dane/liga_dzisiaj.csv"


ARCHIWUM = "./archiwa/DataBase/"





def archiwizuj_baze(plik):

    if not os.path.exists(plik):

        print(
            "Nie znaleziono pliku:",
            plik
        )

        return



    os.makedirs(
        ARCHIWUM,
        exist_ok=True
    )


    data = datetime.now().strftime(
        "%Y-%m-%d"
    )


    nazwa = (
        "dataBase_futbol"
        + data
        + ".csv"
    )


    plik_archiwum = (
        ARCHIWUM
        + nazwa
    )


    shutil.copy2(
        plik,
        plik_archiwum
    )


    print(
        "Utworzono archiwum:",
        plik_archiwum
    )







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



                # pomijamy mecze, które już się odbyły

                if data_meczu < teraz:

                    continue





                # zapis dzisiejszych meczów

                if data_meczu.date() == dzisiaj:

                    mecze_dzisiaj.append(
                        row
                    )





                # wszystkie przyszłe mecze

                mecze_przyszle.append(
                    row
                )



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
                row[2],   # mecz
                row[0],   # liga
                row[1]    # data,godzina
            ]
        )



    zapisz(
        wynik,
        plik
    )









# =========================
# START PROGRAMU
# =========================


# tworzenie katalogu dane

os.makedirs(
    "./dane/",
    exist_ok=True
)



# tworzenie kopii starej bazy

archiwizuj_baze(
    PLIK
)





# filtracja oferty

dzisiejsze, przyszle = filtruj_oferte()






# zapis dzisiejszych meczów

zapisz(
    dzisiejsze,
    PLIK_DZIS
)






# aktualizacja głównej bazy

zapisz(
    przyszle,
    PLIK
)






# zapis bazy ligowej

zapisz_database_liga(
    dzisiejsze,
    PLIK_LIGA
)







print("========================")

print(
    "Aktualny czas:",
    datetime.now().strftime(
        "%d-%m-%Y %H:%M"
    )
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