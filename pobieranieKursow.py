import csv
import requests
from bs4 import BeautifulSoup



def pobierz_strone(url):

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }


    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )


    response.raise_for_status()


    print(
        "Kod strony:",
        response.status_code
    )


    print(
        "Pobrano znaków:",
        len(response.text)
    )


    return response.text





def html_na_tekst(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    tekst = soup.get_text(
        "\n",
        strip=True
    )


    return tekst





def podziel_oferte(tekst):

    popularne = ""
    najblizsze = ""


    start_pop = tekst.find(
        "Popularne mecze"
    )


    start_naj = tekst.find(
        "Najbliższe mecze"
    )


    if start_pop != -1 and start_naj != -1:


        popularne = tekst[
            start_pop:start_naj
        ]


        najblizsze = tekst[
            start_naj:
        ]


    else:

        print(
            "Nie znaleziono znaczników"
        )


    return popularne, najblizsze





def zapisz_csv(
        nazwa,
        url,
        dane
):

    with open(
        nazwa,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:


        writer = csv.writer(
            f,
            delimiter=";"
        )


        writer.writerow(
            [
                "url",
                "dane"
            ]
        )


        writer.writerow(
            [
                url,
                dane
            ]
        )


    print(
        "Zapisano:",
        nazwa,
        "znaki:",
        len(dane)
    )






def main():


    url = (
        "https://www.bukmacherzy.com/oferta/"
    )


    html = pobierz_strone(
        url
    )


    tekst = html_na_tekst(
        html
    )


    popularne, najblizsze = podziel_oferte(
        tekst
    )



    zapisz_csv(
        "./danePomocnicze/oferta_Popularne.csv",
        url,
        popularne
    )


    zapisz_csv(
        "./danePomocnicze/oferta.csv",
        url,
        najblizsze
    )





if __name__ == "__main__":

    main()

import re
import csv
import time
import os


# =====================================
# Sprawdzenie kursu
# =====================================

def czy_kurs(wartosc):

    return bool(
        re.fullmatch(
            r"\d+\.\d+",
            wartosc
        )
    )



# =====================================
# Parser oferty
#
# Schemat:
#
# Oferta Liga
# Data
# Godzina
# Drużyna - Drużyna
# Kurs 1
# Kurs X
# Kurs 2
#
# =====================================

def parsuj_oferte(tekst):

    wynik = []

    aktualna_liga = ""
    aktualna_data = ""


    linie = [
        x.strip()
        for x in tekst.splitlines()
        if x.strip()
    ]


    i = 0


    while i < len(linie):

        linia = linie[i]



        # =========================
        # Liga
        # =========================

        if linia.startswith("Oferta"):


            aktualna_liga = linia.replace(
                "Oferta",
                ""
            ).strip()


            i += 1
            continue




        # =========================
        # Data
        # =========================

        data = re.search(
            r"\d{2}-\d{2}-\d{4}",
            linia
        )


        if data:

            aktualna_data = data.group()

            i += 1
            continue





        # =========================
        # Godzina
        # =========================

        if re.fullmatch(
            r"\d{2}:\d{2}",
            linia
        ):



            godzina = linia



            # sprawdzamy kolejny układ:
            #
            # godzina
            # mecz
            # kurs1
            # kursX
            # kurs2


            if i + 4 < len(linie):


                mecz = linie[i+1]

                kurs1 = linie[i+2]

                kursX = linie[i+3]

                kurs2 = linie[i+4]




                # =====================
                # Walidacja meczu
                # =====================

                poprawny_mecz = (

                    " - " in mecz

                    and

                    len(
                        mecz.split(" - ")
                    ) == 2

                )




                # =====================
                # Walidacja kursów
                # =====================

                poprawne_kursy = (

                    czy_kurs(kurs1)

                    and

                    czy_kurs(kursX)

                    and

                    czy_kurs(kurs2)

                )





                if (

                    poprawny_mecz

                    and

                    poprawne_kursy

                ):


                    czas_unix = int(
                        time.time()
                    )



                    wynik.append(
                        [

                            aktualna_liga
                            if aktualna_liga
                            else "BRAK_LIGI",


                            f"{aktualna_data},{godzina}",


                            mecz,


                            kurs1,


                            kursX,


                            kurs2,


                            czas_unix

                        ]
                    )



                    i += 5
                    continue




        i += 1



    return wynik







# =====================================
# Aktualizacja historii
# =====================================

def aktualizuj_historie(
        nowe_dane,
        plik
):


    baza = {}



    # =========================
    # Wczytanie starej historii
    # =========================

    if os.path.exists(plik):


        with open(
            plik,
            "r",
            encoding="utf-8"
        ) as f:


            reader = csv.reader(
                f,
                delimiter=";"
            )


            for row in reader:


                if len(row) >= 3:

                    baza[row[2]] = row





    # =========================
    # Aktualizacja
    # =========================

    for nowy in nowe_dane:


        mecz = nowy[2]



        if mecz in baza:


            stary = baza[mecz]


            stary.extend(
                [

                    nowy[3],

                    nowy[4],

                    nowy[5],

                    nowy[6]

                ]
            )



        else:


            baza[mecz] = nowy





    # =========================
    # Zapis
    # =========================

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
            baza.values()
        )





# =====================================
# Obsługa dwóch plików
# =====================================

pliki = [

    (
        "./danePomocnicze/oferta.csv",
        "./danePomocnicze/oferta_wynik.csv"
    ),


    (
        "./danePomocnicze/oferta_Popularne.csv",
        "./danePomocnicze/oferta_Popularne_wynik.csv"
    )

]




for plik_wejscia, plik_wyjscia in pliki:


    if not os.path.exists(
        plik_wejscia
    ):

        print(
            "Brak pliku:",
            plik_wejscia
        )

        continue




    with open(
        plik_wejscia,
        "r",
        encoding="utf-8"
    ) as f:


        tekst = f.read()





    dane = parsuj_oferte(
        tekst
    )





    aktualizuj_historie(
        dane,
        plik_wyjscia
    )





    print(
        "Przetworzono:",
        plik_wejscia,
        "Dodano:",
        len(dane)
    )



import re
import csv
import time
import os


PLIK_WYNIK = "./danePomocnicze/oferta_Popularne_wynik.csv"



def parsuj_oferte(tekst):

    wynik = []

    aktualna_data = ""
    aktualna_liga = ""

    linie = tekst.splitlines()


    for linia in linie:

        # czyszczenie znaków
        linia = linia.strip()

        if not linia:
            continue


        # =========================
        # Wykrywanie ligi
        # =========================

        if re.search(r"»\s*Oferta", linia):

            aktualna_liga = re.split(
                r"Oferta",
                linia,
                maxsplit=1
            )[1].strip()


            aktualna_liga = aktualna_liga.replace(
                "»",
                ""
            ).strip()


            continue






        # =========================
        # Wykrywanie daty
        # =========================

        if re.match(
            r"^(Poniedziałek|Wtorek|Środa|Czwartek|Piątek|Sobota|Niedziela)",
            linia
        ):


            aktualna_data = linia.replace(
                "1X2",
                ""
            ).strip()



            if "," in aktualna_data:

                aktualna_data = aktualna_data.split(
                    ",",
                    1
                )[1].strip()



            continue






        # =========================
        # Wykrywanie meczu
        # =========================

        if re.match(
            r"^\d{2}:\d{2}",
            linia
        ):



            godzina = linia[:5]

            reszta = linia[5:].strip()




            kursy = re.search(
                r"([0-9]+\.[0-9]{2})([0-9]+\.[0-9]{2})([0-9]+\.[0-9]{2})(\+[0-9]+)$",
                reszta
            )



            if kursy:



                mecz = reszta[:kursy.start()].strip()



                kurs1 = kursy.group(1)
                kursX = kursy.group(2)
                kurs2 = kursy.group(3)



                czas_unix = int(
                    time.time()
                )



                wynik.append(
                    [
                        aktualna_liga if aktualna_liga else "BRAK_LIGI",
                        f"{aktualna_data},{godzina}",
                        mecz,
                        kurs1,
                        kursX,
                        kurs2,
                        czas_unix
                    ]
                )



    return wynik






def aktualizuj_historie(nowe_dane, plik):


    baza = {}



    # =========================
    # Wczytanie historii
    # =========================

    if os.path.exists(plik):


        with open(
            plik,
            "r",
            encoding="utf-8"
        ) as f:


            reader = csv.reader(
                f,
                delimiter=";"
            )


            for row in reader:


                if len(row) >= 3:


                    baza[row[2]] = row






    # =========================
    # Aktualizacja danych
    # =========================

    for nowy in nowe_dane:


        nazwa_meczu = nowy[2]



        if nazwa_meczu in baza:



            stary = baza[nazwa_meczu]



            stary.extend(
                [
                    nowy[3],
                    nowy[4],
                    nowy[5],
                    nowy[6]
                ]
            )



        else:


            baza[nazwa_meczu] = nowy






    # =========================
    # Zapis
    # =========================

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
            baza.values()
        )








# =========================
# START
# =========================


with open(
    "./danePomocnicze/oferta_Popularne.csv",
    "r",
    encoding="utf-8"
) as f:


    tekst = f.read()




dane = parsuj_oferte(
    tekst
)



aktualizuj_historie(
    dane,
    PLIK_WYNIK
)



print(
    "Dodano aktualizację meczów:",
    len(dane)
)



