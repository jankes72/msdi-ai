import csv
import requests
import re
import os
import shutil

from datetime import datetime, timedelta
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





def czy_druzyna(nazwa):


    if len(nazwa) < 3:

        return False



    # odrzucamy linie zawierające cyfry
    if re.search(r"\d", nazwa):

        return False



    odrzucone = [

        "Koniec",
        "Odwołany",
        "Live",
        "LIVE"

    ]



    for slowo in odrzucone:

        if slowo.lower() in nazwa.lower():

            return False



    return True





def wyciagnij_wyniki(tekst):


    linie = [

        x.strip()

        for x in tekst.split("\n")

        if x.strip()

    ]



    mecze = []



    for i in range(1, len(linie)-1):


        wynik = linie[i]



        # szukamy tylko wyników np. 4-6, 0-0, 2-1

        if re.fullmatch(

            r"\d+-\d+",

            wynik

        ):



            druzyna1 = linie[i-1]

            druzyna2 = linie[i+1]



            if (

                czy_druzyna(druzyna1)

                and

                czy_druzyna(druzyna2)

            ):



                wynik = wynik.replace(

                    "-",

                    ":"

                )



                mecze.append(

                    [

                        druzyna1,

                        druzyna2,

                        wynik

                    ]

                )



    return mecze





def zapisz_csv(mecze):


    plik = "./dane/wyniki.csv"



    # ============================
    # GŁÓWNY PLIK BEZ NAGŁÓWKÓW
    # ============================


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



        for mecz in mecze:



            nazwa = (

                mecz[0]

                +

                " - "

                +

                mecz[1]

            )



            writer.writerow(

                [

                    nazwa,

                    mecz[2]

                ]

            )



    print(

        "Zapisano meczów:",

        len(mecze)

    )





    # ============================
    # KOPIA HISTORYCZNA
    # DATA = WCZORAJ
    # ============================


    folder = "archiwa/wyniki"



    if not os.path.exists(folder):

        os.makedirs(folder)



    data_wczoraj = (

        datetime.now()

        -

        timedelta(days=1)

    ).strftime(

        "%Y-%m-%d"

    )



    kopia = (

        folder

        +

        "/wyniki"

        +

        data_wczoraj

        +

        ".csv"

    )



    shutil.copy(

        plik,

        kopia

    )



    print(

        "Utworzono kopię:",

        kopia

    )





def main():


    url = (

        "https://www.bukmacherzy.com/wyniki/wczoraj/"

    )



    html = pobierz_strone(

        url

    )



    tekst = html_na_tekst(

        html

    )



    mecze = wyciagnij_wyniki(

        tekst

    )



    print()

    print(

        "Znalezione mecze:"

    )



    for mecz in mecze:


        print(

            mecz[0],

            "-",

            mecz[1],

            mecz[2]

        )



    zapisz_csv(

        mecze

    )





if __name__ == "__main__":

    main()