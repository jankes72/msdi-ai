import csv
import time
import pyperclip

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains



def pobierz_strone(driver, url):

    driver.get(url)

    time.sleep(3)

    print("TYTUŁ:", driver.title)
    print("URL:", driver.current_url)


    # zaznacz wszystko
    ActionChains(driver)\
        .key_down(Keys.CONTROL)\
        .send_keys('a')\
        .key_up(Keys.CONTROL)\
        .perform()


    time.sleep(1)


    # kopiuj
    ActionChains(driver)\
        .key_down(Keys.CONTROL)\
        .send_keys('c')\
        .key_up(Keys.CONTROL)\
        .perform()


    time.sleep(1)


    tekst = pyperclip.paste()


    print(
        "Pobrano znaków:",
        len(tekst)
    )


    return tekst



def podziel_oferte(tekst):

    popularne = ""
    najblizsze = ""


    start_pop = tekst.find("Popularne mecze")
    start_naj = tekst.find("Najbliższe mecze")


    if start_pop != -1 and start_naj != -1:


        # Popularne od początku do Najbliższe
        popularne = tekst[start_pop:start_naj]


        # Oferta od Najbliższe do końca
        najblizsze = tekst[start_naj:]



    else:

        print("Nie znaleziono znaczników")


    return popularne, najblizsze




def zapisz_csv(nazwa, url, dane):

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
                "html"
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

    chrome_options = Options()

    chrome_options.add_argument(
        "--start-maximized"
    )


    service = Service(
        ChromeDriverManager().install()
    )


    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )


    url = "https://www.bukmacherzy.com/oferta/"


    # pobranie całej strony
    tekst = pobierz_strone(
        driver,
        url
    )


    # podział
    popularne, najblizsze = podziel_oferte(
        tekst
    )



    # zapis popularnych
    zapisz_csv(
        "./oferta_Popularne.csv",
        url,
        popularne
    )


    # zapis najbliższych
    zapisz_csv(
        "./oferta.csv",
        url,
        najblizsze
    )


    driver.quit()



if __name__ == "__main__":
    main()





import re
import csv
import time
import os


PLIK_WYNIK = "oferta_wynik.csv"



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
    "oferta.csv",
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





import re
import csv
import time
import os


PLIK_WYNIK = "oferta_Popularne_wynik.csv"



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
    "oferta_Popularne.csv",
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



