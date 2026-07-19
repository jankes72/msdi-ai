import csv
import math
import statistics
import os

def normalize(value, min_val, max_val):
    if max_val - min_val == 0:
        return 0.5
    return max(0, min(1, (value - min_val) / (max_val - min_val)))

def oblicz_cechy_3kursy_rozszerzone(bloki):
    kurs_1 = [b[0] for b in bloki]
    kurs_X = [b[1] for b in bloki]
    kurs_2 = [b[2] for b in bloki]
    czasy = [b[3] for b in bloki]

    start_1, start_X, start_2 = kurs_1[0], kurs_X[0], kurs_2[0]
    koniec_1, koniec_X, koniec_2 = kurs_1[-1], kurs_X[-1], kurs_2[-1]

    zmiana_1 = ((start_1 - koniec_1) / start_1) * 100 if start_1 else 0
    zmiana_X = ((start_X - koniec_X) / start_X) * 100 if start_X else 0
    zmiana_2 = ((start_2 - koniec_2) / start_2) * 100 if start_2 else 0

    amplituda_1 = ((max(kurs_1) - min(kurs_1)) / start_1) * 100 if start_1 else 0
    amplituda_X = ((max(kurs_X) - min(kurs_X)) / start_X) * 100 if start_X else 0
    amplituda_2 = ((max(kurs_2) - min(kurs_2)) / start_2) * 100 if start_2 else 0

    czas_trwania = max(czasy) - min(czasy) if czasy else 1
    czas_h = czas_trwania / 3600
    tempo_1 = zmiana_1 / czas_h if czas_h else 0
    tempo_X = zmiana_X / czas_h if czas_h else 0
    tempo_2 = zmiana_2 / czas_h if czas_h else 0

    synchronizacja = 1 if ((zmiana_1 > 0 and zmiana_X > 0 and zmiana_2 > 0) or
                           (zmiana_1 < 0 and zmiana_X < 0 and zmiana_2 < 0)) else 0

    max_wahanie_1 = max(abs(kurs_1[i+1] - kurs_1[i]) for i in range(len(kurs_1)-1))
    max_wahanie_X = max(abs(kurs_X[i+1] - kurs_X[i]) for i in range(len(kurs_X)-1))
    max_wahanie_2 = max(abs(kurs_2[i+1] - kurs_2[i]) for i in range(len(kurs_2)-1))

    start_1_raw = normalize(start_1, 1.01, 10.0)
    start_X_raw = normalize(start_X, 1.01, 10.0)
    start_2_raw = normalize(start_2, 1.01, 10.0)
    koniec_1_raw = normalize(koniec_1, 1.01, 10.0)
    koniec_X_raw = normalize(koniec_X, 1.01, 10.0)
    koniec_2_raw = normalize(koniec_2, 1.01, 10.0)

    log_start_1 = normalize(math.log(start_1), math.log(1.01), math.log(10.0))
    log_start_X = normalize(math.log(start_X), math.log(1.01), math.log(10.0))
    log_start_2 = normalize(math.log(start_2), math.log(1.01), math.log(10.0))
    log_koniec_1 = normalize(math.log(koniec_1), math.log(1.01), math.log(10.0))
    log_koniec_X = normalize(math.log(koniec_X), math.log(1.01), math.log(10.0))
    log_koniec_2 = normalize(math.log(koniec_2), math.log(1.01), math.log(10.0))

    ratio_1X_start = start_1 / start_X if start_X else 1
    ratio_1_2_start = start_1 / start_2 if start_2 else 1
    ratio_X2_start = start_X / start_2 if start_2 else 1
    ratio_1X_koniec = koniec_1 / koniec_X if koniec_X else 1
    ratio_1_2_koniec = koniec_1 / koniec_2 if koniec_2 else 1
    ratio_X2_koniec = koniec_X / koniec_2 if koniec_2 else 1

    stat_mean = [statistics.mean(kurs_1), statistics.mean(kurs_X), statistics.mean(kurs_2)]
    stat_median = [statistics.median(kurs_1), statistics.median(kurs_X), statistics.median(kurs_2)]
    stat_stdev = [
        statistics.stdev(kurs_1) if len(kurs_1)>1 else 0,
        statistics.stdev(kurs_X) if len(kurs_X)>1 else 0,
        statistics.stdev(kurs_2) if len(kurs_2)>1 else 0
    ]

    features = [
        normalize(zmiana_1, -100, 100), normalize(zmiana_X, -100, 100), normalize(zmiana_2, -100, 100),
        normalize(amplituda_1, 0, 100), normalize(amplituda_X, 0, 100), normalize(amplituda_2, 0, 100),
        normalize(tempo_1, -50, 50), normalize(tempo_X, -50, 50), normalize(tempo_2, -50, 50),
        synchronizacja,
        max_wahanie_1, max_wahanie_X, max_wahanie_2,
        start_1_raw, start_X_raw, start_2_raw,
        koniec_1_raw, koniec_X_raw, koniec_2_raw,
        log_start_1, log_start_X, log_start_2,
        log_koniec_1, log_koniec_X, log_koniec_2,
        normalize(ratio_1X_start, 0, 10), normalize(ratio_1_2_start, 0, 10), normalize(ratio_X2_start, 0, 10),
        normalize(ratio_1X_koniec, 0, 10), normalize(ratio_1_2_koniec, 0, 10), normalize(ratio_X2_koniec, 0, 10),
        normalize(stat_mean[0],1,10), normalize(stat_mean[1],1,10), normalize(stat_mean[2],1,10),
        normalize(stat_median[0],1,10), normalize(stat_median[1],1,10), normalize(stat_median[2],1,10),
        normalize(stat_stdev[0],0,5), normalize(stat_stdev[1],0,5), normalize(stat_stdev[2],0,5),
        czas_h
    ]
    return features

def przetworz_plik_3kursy_rozszerzone(nazwa_pliku, nazwa_wyjsciowa):
    if not os.path.exists(nazwa_pliku):
        print(f"⚠️ Plik nie istnieje, pomijam: {nazwa_pliku}")
        return
    try:
        with open(nazwa_pliku, "r", encoding="utf-8") as f, \
             open(nazwa_wyjsciowa, "w", encoding="utf-8", newline="") as out:

            reader = csv.reader(f, delimiter=";")
            writer = csv.writer(out, delimiter=";")

            header = ["id_meczu",
                      "zmiana_1","zmiana_X","zmiana_2",
                      "amplituda_1","amplituda_X","amplituda_2",
                      "tempo_1","tempo_X","tempo_2",
                      "synchronizacja",
                      "max_wahanie_1","max_wahanie_X","max_wahanie_2",
                      "start_1_raw","start_X_raw","start_2_raw",
                      "koniec_1_raw","koniec_X_raw","koniec_2_raw",
                      "log_start_1","log_start_X","log_start_2",
                      "log_koniec_1","log_koniec_X","log_koniec_2",
                      "ratio_1X_start","ratio_1_2_start","ratio_X2_start",
                      "ratio_1X_koniec","ratio_1_2_koniec","ratio_X2_koniec",
                      "mean_1","mean_X","mean_2",
                      "median_1","median_X","median_2",
                      "stdev_1","stdev_X","stdev_2",
                      "czas_h"
                     ]
            writer.writerow(header)

            for row in reader:
                if not row:
                    continue
                try:
                    id_meczu = row[0]
                    mecz = row[2]
                except IndexError:
                    continue

                bloki = []
                for i in range(3, len(row), 4):
                    try:
                        k1 = float(row[i])
                        kX = float(row[i+1])
                        k2 = float(row[i+2])
                        czas = int(row[i+3])
                        bloki.append((k1,kX,k2,czas))
                    except (ValueError, IndexError):
                        continue

                if len(bloki) < 2:
                    continue

                cechy = oblicz_cechy_3kursy_rozszerzone(bloki)
                writer.writerow([mecz]+[round(c,5) for c in cechy])
        print(f"✅ Zapisano: {nazwa_wyjsciowa}")
    except Exception as e:
        print(f"❌ Błąd przy przetwarzaniu '{nazwa_pliku}': {e}")


# Uruchomienie
pliki = [
    ("database_popularne_dzisiaj.csv","dataBase_futbol_popularne_trend.csv"),
    ("database_dzisiaj.csv","dataBase_futbol_trend.csv")
]

for plik_in, plik_out in pliki:
    przetworz_plik_3kursy_rozszerzone(plik_in, plik_out)
    print(f"Zapisano: {plik_out}")









import csv

plik_wej = "dataBase_futbol_trend.csv"
plik_wyj = "dataBase_futbol_trend_klasyfikator.csv"


# indeksy danych do zachowania
wybrane_indeksy = [
    0,   # id_meczu
    21,  # log_start_1
    22,  # log_start_X
    23,  # log_start_2
    24,  # log_koniec_1
    25,  # log_koniec_X
    26   # log_koniec_2
]


# nowy nagłówek
nowy_naglowek = [
    "id_meczu",
    "log_start_1",
    "log_start_X",
    "log_start_2",
    "log_koniec_1",
    "log_koniec_X",
    "log_koniec_2"
]


with open(plik_wej, "r", encoding="utf-8", newline="") as f_in, \
     open(plik_wyj, "w", encoding="utf-8", newline="") as f_out:

    reader = csv.reader(f_in, delimiter=";")
    writer = csv.writer(f_out, delimiter=";")

    # zapis nowego nagłówka
    writer.writerow(nowy_naglowek)

    # pomijamy stary nagłówek
    next(reader)

    for rekord in reader:
        if len(rekord) >= 27:
            nowy_rekord = [
                rekord[i] for i in wybrane_indeksy
            ]

            writer.writerow(nowy_rekord)


print("Gotowe.")
print("Utworzono:", plik_wyj)

import csv

plik_wej = "kod_dataBase_futbol_trend.csv"
plik_wyj = "kod_dataBase_futbol_trend_klasyfikator.csv"


# indeksy danych do zachowania
wybrane_indeksy = [
    0,   # id_meczu
    21,  # log_start_1
    22,  # log_start_X
    23,  # log_start_2
    24,  # log_koniec_1
    25,  # log_koniec_X
    26   # log_koniec_2
]


# nowy nagłówek
nowy_naglowek = [
    "id_meczu",
    "log_start_1",
    "log_start_X",
    "log_start_2",
    "log_koniec_1",
    "log_koniec_X",
    "log_koniec_2",
    "wynik"
]


with open(plik_wej, "r", encoding="utf-8", newline="") as f_in, \
     open(plik_wyj, "w", encoding="utf-8", newline="") as f_out:

    reader = csv.reader(f_in, delimiter=";")
    writer = csv.writer(f_out, delimiter=";")

    # zapis nowego nagłówka
    writer.writerow(nowy_naglowek)

    # pomijamy stary nagłówek
    next(reader)

    for rekord in reader:

        # musi mieć minimum 27 kolumn + ostatnią z wynikiem
        if len(rekord) >= 28:

            nowy_rekord = [
                rekord[i] for i in wybrane_indeksy
            ]

            # dodajemy ostatni indeks (wynik meczu)
            nowy_rekord.append(rekord[-1])

            writer.writerow(nowy_rekord)


print("Gotowe.")
print("Utworzono:", plik_wyj)






import csv
import math
from collections import defaultdict


# ==========================================
# PLIKI
# ==========================================

plik_predykcja_klasyfikator = "dataBase_futbol_trend_klasyfikator.csv"

plik_historia_klasyfikator = "kod_dataBase_futbol_trend_klasyfikator.csv"

plik_historia_pelna = "kod_dataBase_futbol_trend.csv"

plik_wyj = "dopasowane_trendy_historyczne.csv"

plik_wagi = "wagi_dopasowania.csv"



# ==========================================
# PARAMETR PODOBIEŃSTWA
# ==========================================

PROG = 0.03



# ==========================================
# 6 CECH DO PORÓWNANIA
# ==========================================

LOG_INDEXY_KLASYFIKATOR = [
    1,
    2,
    3,
    4,
    5,
    6
]



# ==========================================
# FUNKCJE
# ==========================================

def liczba(x):

    try:
        return float(x)

    except:
        return 0.0



def odleglosc(a,b):

    suma = 0

    for x,y in zip(a,b):

        suma += (x-y)**2


    return math.sqrt(suma)



def wynik_liczbowy(wynik):

    try:

        g1,g2 = wynik.split(":")

        g1=int(g1)
        g2=int(g2)


        if g1>g2:
            return 1

        elif g1==g2:
            return 0

        else:
            return -1

    except:

        return 0



# ==========================================
# PEŁNA HISTORIA
# ==========================================

pelna_historia = {}


with open(
    plik_historia_pelna,
    "r",
    encoding="utf-8",
    newline=""
) as f:


    reader = csv.reader(
        f,
        delimiter=";"
    )


    for rekord in reader:


        if len(rekord) < 42:
            continue


        pelna_historia[rekord[0]] = rekord



print(
    "Pełna baza:",
    len(pelna_historia)
)



# ==========================================
# HISTORIA KLASYFIKATOR
# ==========================================

historia_klasyfikator=[]


with open(
    plik_historia_klasyfikator,
    "r",
    encoding="utf-8",
    newline=""
) as f:


    reader=csv.reader(
        f,
        delimiter=";"
    )


    next(reader)


    for rekord in reader:


        if len(rekord)<8:
            continue



        profil=[

            liczba(rekord[i])

            for i in LOG_INDEXY_KLASYFIKATOR

        ]



        historia_klasyfikator.append(

            {
                "id":rekord[0],
                "profil":profil,
                "wynik":rekord[-1]
            }

        )



print(
    "Historia klasyfikator:",
    len(historia_klasyfikator)
)



# ==========================================
# OTWARCIE PLIKÓW
# ==========================================

with open(
    plik_predykcja_klasyfikator,
    "r",
    encoding="utf-8",
    newline=""
) as f_in,\
open(
    plik_wyj,
    "w",
    encoding="utf-8",
    newline=""
) as f_out,\
open(
    plik_wagi,
    "w",
    encoding="utf-8",
    newline=""
) as f_wagi:



    reader=csv.reader(
        f_in,
        delimiter=";"
    )


    writer=csv.writer(
        f_out,
        delimiter=";"
    )


    writer_wagi=csv.writer(
        f_wagi,
        delimiter=";"
    )



    next(reader)



    # nagłówek pełnej bazy

    naglowek_hist = [

        "id_meczu",
        "zmiana_1",
        "zmiana_X",
        "zmiana_2",
        "amplituda_1",
        "amplituda_X",
        "amplituda_2",
        "tempo_1",
        "tempo_X",
        "tempo_2",
        "synchronizacja",
        "max_wahanie_1",
        "max_wahanie_X",
        "max_wahanie_2",
        "start_1_raw",
        "start_X_raw",
        "start_2_raw",
        "koniec_1_raw",
        "koniec_X_raw",
        "koniec_2_raw",
        "log_start_1",
        "log_start_X",
        "log_start_2",
        "log_koniec_1",
        "log_koniec_X",
        "log_koniec_2",
        "ratio_1X_start",
        "ratio_1_2_start",
        "ratio_X2_start",
        "ratio_1X_koniec",
        "ratio_1_2_koniec",
        "ratio_X2_koniec",
        "mean_1",
        "mean_X",
        "mean_2",
        "median_1",
        "median_X",
        "median_2",
        "stdev_1",
        "stdev_X",
        "stdev_2",
        "czas_h",
        "wynik"
    ]



    writer.writerow(

        [
            "id_meczu_predykcja",
            "odleglosc"
        ]

        +

        naglowek_hist

    )



    writer_wagi.writerow(

        [
            "id_meczu_predykcja",
            "liczba_dopasowanych",
            "sredni_wynik"
        ]

    )



    licznik_globalny=0



    # ======================================
    # MECZE PREDYKCYJNE
    # ======================================

    for mecz_pred in reader:


        profil_pred=[

            liczba(mecz_pred[i])

            for i in LOG_INDEXY_KLASYFIKATOR

        ]


        znalezone=[]



        for historia in historia_klasyfikator:


            dystans=odleglosc(

                profil_pred,
                historia["profil"]

            )


            if dystans <= PROG:

                znalezone.append(

                    (
                        dystans,
                        historia["id"],
                        historia["wynik"]

                    )

                )



        print(
            mecz_pred[0],
            "->",
            len(znalezone)
        )



        suma_wynikow=0



        for dystans,id_historyczny,wynik in znalezone:


            if id_historyczny in pelna_historia:


                rekord=pelna_historia[id_historyczny]


                writer.writerow(

                    [
                        mecz_pred[0],
                        round(dystans,8)

                    ]

                    +

                    rekord

                )


                suma_wynikow += wynik_liczbowy(wynik)


                licznik_globalny+=1




        # zapis pomocniczy

        if len(znalezone)>0:

            sredni = round(
                suma_wynikow / len(znalezone),
                4
            )

        else:

            sredni = 0



        writer_wagi.writerow(

            [
                mecz_pred[0],
                len(znalezone),
                sredni
            ]

        )



print()
print("==============================")
print("Gotowe")
print("Dane:",plik_wyj)
print("Wagi:",plik_wagi)
print("Rekordy:",licznik_globalny)
print("==============================")





import pandas as pd
import numpy as np
import csv
import math

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score
)


# =================================================
# PLIKI
# =================================================

plik_dane = "dopasowane_trendy_historyczne.csv"

plik_wagi = "wagi_dopasowania.csv"


plik_korelacja = "analiza_korelacji_cech.csv"

plik_rf = "random_forest_waznosc_cech.csv"

plik_ranking = "ranking_cech.csv"

plik_syntetyczne = "syntetyczne_trendy_historyczne.csv"

plik_poisson = "analiza_poisson_dixon.csv"



# =================================================
# PARAMETRY
# =================================================

LICZBA_SYNTH = 3

KROK = 0.02

MAX_GOLE = 8

RHO_DIXON = -0.1



# =================================================
# WCZYTANIE
# =================================================


df = pd.read_csv(
    plik_dane,
    sep=";"
)


df_wagi = pd.read_csv(
    plik_wagi,
    sep=";"
)



print(
    "Dane:",
    len(df)
)



# =================================================
# DODANIE WAG
# =================================================


df = df.merge(

    df_wagi,

    on="id_meczu_predykcja",

    how="left"

)


df["liczba_dopasowanych"] = (

    df["liczba_dopasowanych"]

    .fillna(1)

)



# =================================================
# ANALIZA WYNIKU
# =================================================


def rozbij_wynik(x):

    try:

        a,b = x.split(":")

        return int(a), int(b)


    except:

        return 0,0



def wynik_1x2(x):

    a,b = rozbij_wynik(x)


    if a>b:

        return 1


    elif a==b:

        return 0


    else:

        return 2



def wynik_gole(x):

    a,b = rozbij_wynik(x)

    return a+b




df["gole_dom"] = df["wynik"].apply(

    lambda x:
    rozbij_wynik(x)[0]

)


df["gole_wyj"] = df["wynik"].apply(

    lambda x:
    rozbij_wynik(x)[1]

)



df["gole"] = df["wynik"].apply(

    wynik_gole

)



df["klasa"] = df["wynik"].apply(

    wynik_1x2

)



# =================================================
# FUNKCJE POISSON
# =================================================


def poisson(k, lam):

    if lam <= 0:

        return 0


    try:

        return (

            math.exp(-lam)

            *

            (lam ** k)

            /

            math.factorial(k)

        )


    except:

        return 0




# =================================================
# DIXON COLES
# =================================================


def dixon_coles(

        gole_dom,

        gole_wyj,

        lambda_dom,

        lambda_wyj,

        rho=RHO_DIXON

):


    korekta = 1



    if gole_dom == 0 and gole_wyj == 0:


        korekta = (

            1

            -

            lambda_dom

            *

            lambda_wyj

            *

            rho

        )



    elif gole_dom == 1 and gole_wyj == 0:


        korekta = (

            1

            +

            lambda_wyj

            *

            rho

        )



    elif gole_dom == 0 and gole_wyj == 1:


        korekta = (

            1

            +

            lambda_dom

            *

            rho

        )



    elif gole_dom == 1 and gole_wyj == 1:


        korekta = (

            1

            -

            rho

        )



    return max(

        korekta,

        0

    )



# =================================================
# ŚREDNIE BRAMKI
# =================================================


srednia_dom = (

    df["gole_dom"]

    .mean()

)


srednia_wyj = (

    df["gole_wyj"]

    .mean()

)



print(
    "Średnia gole dom:",
    srednia_dom
)


print(
    "Średnia gole wyjazd:",
    srednia_wyj
)



# =================================================
# POISSON + DIXON COLES
# =================================================


def policz_dc(row):


    gd = row["gole_dom"]

    gw = row["gole_wyj"]



    p_dom = poisson(

        gd,

        srednia_dom

    )



    p_wyj = poisson(

        gw,

        srednia_wyj

    )



    dc = dixon_coles(

        gd,

        gw,

        srednia_dom,

        srednia_wyj

    )



    return (

        p_dom

        *

        p_wyj

        *

        dc

    )




df["prawdopodobienstwo_dc"] = df.apply(

    policz_dc,

    axis=1

)



print(
    "Poisson + Dixon-Coles gotowy"
)

# =================================================
# ZAPIS ANALIZY POISSON + DIXON COLES
# =================================================


df_poisson = df[

    [

        "id_meczu_predykcja",

        "wynik",

        "gole_dom",

        "gole_wyj",

        "gole",

        "prawdopodobienstwo_dc"

    ]

]


df_poisson.to_csv(

    plik_poisson,

    sep=";",

    index=False,

    encoding="utf-8"

)



print(
    "Analiza Poisson Dixon zapisana"
)



# =================================================
# PRZYGOTOWANIE CECH
# =================================================


usun = [

    "id_meczu_predykcja",

    "id_meczu",

    "wynik",

    "klasa",

    "gole",

    "gole_dom",

    "gole_wyj",

    "prawdopodobienstwo_dc"

]



X = df.drop(

    columns=usun,

    errors="ignore"

)



X = X.apply(

    pd.to_numeric,

    errors="coerce"

)



X = X.fillna(0)



# =================================================
# CEL MODELU
# =================================================
# gole ważone prawdopodobieństwem
# wynik bardziej realistyczny według modelu


df["wynik_modelowy"] = (

    df["gole"]

    *

    df["prawdopodobienstwo_dc"]

)



# =================================================
# KORELACJA POISSON + DIXON
# =================================================


wyniki_korelacji = []



for cecha in X.columns:


    try:


        korelacja = X[cecha].corr(

            df["wynik_modelowy"]

        )


    except:


        korelacja = 0



    wyniki_korelacji.append(

        {


            "cecha": cecha,


            "korelacja_dc": korelacja


        }

    )



df_kor = pd.DataFrame(

    wyniki_korelacji

)



df_kor.to_csv(

    plik_korelacja,

    sep=";",

    index=False,

    encoding="utf-8"

)



print(
    "Korelacja Poisson+Dixon gotowa"
)



# =================================================
# RANDOM FOREST CLASSIFIER
# =================================================


X_train, X_test, y_train, y_test = train_test_split(

    X,

    df["klasa"],

    test_size=0.2,

    random_state=42

)



rf = RandomForestClassifier(

    n_estimators=300,

    random_state=42,

    class_weight="balanced"

)



rf.fit(

    X_train,

    y_train

)



pred = rf.predict(

    X_test

)



print(

    "RF accuracy:",

    accuracy_score(

        y_test,

        pred

    )

)



# =================================================
# WAŻNOŚĆ CECH RF
# =================================================


df_rf = pd.DataFrame(

    {


        "cecha": X.columns,


        "RF": rf.feature_importances_


    }

)



df_rf.to_csv(

    plik_rf,

    sep=";",

    index=False,

    encoding="utf-8"

)



print(
    "Random Forest ważność cech gotowa"
)

# =================================================
# POŁĄCZENIE KORELACJI + RANDOM FOREST + DIXON
# =================================================


ranking = df_kor.merge(

    df_rf,

    on="cecha",

    how="inner"

)



# średnia wiarygodność wyników
# według Poisson + Dixon-Coles


srednia_dc = (

    df["prawdopodobienstwo_dc"]

    .mean()

)



ranking["DC"] = srednia_dc



# końcowa siła cechy


ranking["sila"] = (

    abs(

        ranking["korelacja_dc"]

    )

    *

    ranking["RF"]

    *

    ranking["DC"]

)



ranking = ranking.sort_values(

    "sila",

    ascending=False

)



ranking.to_csv(

    plik_ranking,

    sep=";",

    index=False,

    encoding="utf-8"

)



print(
    "Ranking cech gotowy"
)



# =================================================
# NAJLEPSZE CECHY DO SYNTEZY
# =================================================


najlepsze = dict(

    zip(

        ranking["cecha"],

        ranking["korelacja_dc"]

    )

)



# =================================================
# GENEROWANIE DANYCH SYNTHETYCZNYCH
# =================================================


with open(

    plik_syntetyczne,

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

            "typ_danych"

        ]

        +

        list(df.columns)

    )



    for _, row in df.iterrows():



        # ---------------------------------
        # ORYGINAŁ
        # ---------------------------------


        writer.writerow(

            [

                "oryginal"

            ]

            +

            list(row)

        )



        # ---------------------------------
        # SYNTH
        # ---------------------------------


        for nr in range(

            1,

            LICZBA_SYNTH + 1

        ):



            nowy = row.copy()



            for cecha, korelacja in najlepsze.items():



                if cecha not in nowy:

                    continue



                try:


                    wartosc = float(

                        nowy[cecha]

                    )


                except:


                    continue



                if korelacja > 0:


                    wartosc += (

                        KROK

                        *

                        nr

                    )



                elif korelacja < 0:


                    wartosc -= (

                        KROK

                        *

                        nr

                    )



                nowy[cecha] = wartosc



            writer.writerow(

                [

                    f"syntetyczny_{nr}"

                ]

                +

                list(nowy)

            )



print(
    "Dane syntetyczne gotowe"
)



# =================================================
# PODSUMOWANIE
# =================================================


print()

print("==============================")

print(" KONIEC ANALIZY ")

print("==============================")

print()


print(
    "Liczba meczów:",
    len(df)
)


print()


print(
    "Średnia bramek gospodarze:",
    round(
        srednia_dom,
        3
    )
)


print(
    "Średnia bramek goście:",
    round(
        srednia_wyj,
        3
    )
)


print()


print(
    "Średnie prawdopodobieństwo",
    "Poisson+Dixon:",
    round(
        srednia_dc,
        5
    )
)


print()


print(
    "Najważniejsze pliki:"
)


print()

print(
    "1.",
    plik_poisson
)


print(
    "2.",
    plik_korelacja
)


print(
    "3.",
    plik_rf
)


print(
    "4.",
    plik_ranking
)


print(
    "5.",
    plik_syntetyczne
)


print()

print("==============================")



import pandas as pd
import numpy as np
import math
import csv


# =================================================
# PLIKI
# =================================================

plik_wejscie = "dopasowane_trendy_historyczne.csv"

plik_wynik = "predykcja_poisson_dc_v2.csv"


# =================================================
# PARAMETRY
# =================================================

MAX_GOLE = 8

RHO_DIXON = -0.1



# =================================================
# WCZYTANIE
# =================================================


df = pd.read_csv(

    plik_wejscie,

    sep=";"

)


print()

print("==============================")

print(" MODEL POISSON DC V2 ")

print("==============================")

print()

print(

    "Liczba meczów:",

    len(df)

)



# =================================================
# ROZBICIE WYNIKU
# =================================================


def rozbij_wynik(x):

    try:

        a,b = x.split(":")

        return int(a), int(b)

    except:

        return 0,0



df["gole_dom"] = df["wynik"].apply(

    lambda x:

    rozbij_wynik(x)[0]

)



df["gole_wyj"] = df["wynik"].apply(

    lambda x:

    rozbij_wynik(x)[1]

)



# =================================================
# WYDOBYCIE DRUŻYN
# =================================================


def pobierz_druzyny(x):

    try:

        if "-" in x:

            a,b = x.split("-")

            return (

                a.strip(),

                b.strip()

            )


        elif " vs " in x:

            a,b = x.split(" vs ")

            return (

                a.strip(),

                b.strip()

            )


    except:

        pass


    return (

        "DOM",

        "WYJAZD"

    )



kolumna_mecz = None


for k in [

    "id_mecz",

    "id_meczu",

    "id_meczu_predykcja"

]:

    if k in df.columns:

        kolumna_mecz = k

        break



if kolumna_mecz is None:

    raise Exception(

        "Brak kolumny z nazwą meczu"

    )



df["gospodarz"] = df[kolumna_mecz].apply(

    lambda x:

    pobierz_druzyny(str(x))[0]

)



df["gosc"] = df[kolumna_mecz].apply(

    lambda x:

    pobierz_druzyny(str(x))[1]

)



# =================================================
# SIŁA ATAKU
# =================================================


srednia_goli = (

    df["gole_dom"]

    .mean()

)



srednia_goli_wyj = (

    df["gole_wyj"]

    .mean()

)



atak_dom = (

    df.groupby("gospodarz")

    ["gole_dom"]

    .mean()

    /

    srednia_goli

)



atak_wyj = (

    df.groupby("gosc")

    ["gole_wyj"]

    .mean()

    /

    srednia_goli_wyj

)



# =================================================
# SIŁA OBRONY
# =================================================


obrona_dom = (

    df.groupby("gospodarz")

    ["gole_wyj"]

    .mean()

    /

    srednia_goli_wyj

)



obrona_wyj = (

    df.groupby("gosc")

    ["gole_dom"]

    .mean()

    /

    srednia_goli

)



# =================================================
# POISSON
# =================================================


def poisson(k, lam):

    if lam <= 0:

        return 0


    return (

        math.exp(-lam)

        *

        lam**k

        /

        math.factorial(k)

    )



# =================================================
# DIXON COLES
# =================================================


def dixon_coles(

        gd,

        gw,

        ld,

        lw

):


    rho = RHO_DIXON


    if gd==0 and gw==0:

        return 1 - ld*lw*rho


    if gd==1 and gw==0:

        return 1 + lw*rho


    if gd==0 and gw==1:

        return 1 + ld*rho


    if gd==1 and gw==1:

        return 1-rho


    return 1



# =================================================
# MACIERZ WYNIKÓW
# =================================================


def macierz_wynikow(ld,lw):


    wyniki=[]


    for gd in range(MAX_GOLE+1):

        for gw in range(MAX_GOLE+1):


            p=(

                poisson(gd,ld)

                *

                poisson(gw,lw)

                *

                dixon_coles(

                    gd,

                    gw,

                    ld,

                    lw

                )

            )


            wyniki.append(

                (

                    gd,

                    gw,

                    p

                )

            )


    return sorted(

        wyniki,

        key=lambda x:x[2],

        reverse=True

    )



# =================================================
# PREDYKCJA
# =================================================


wyniki=[]


for _,row in df.iterrows():


    dom=row["gospodarz"]

    gosc=row["gosc"]



    attack_dom = atak_dom.get(

        dom,

        1

    )


    attack_gosc = atak_wyj.get(

        gosc,

        1

    )


    defence_gosc = obrona_wyj.get(

        gosc,

        1

    )


    defence_dom = obrona_dom.get(

        dom,

        1

    )


    lambda_dom = (

        srednia_goli

        *

        attack_dom

        *

        defence_gosc

    )



    lambda_wyj = (

        srednia_goli_wyj

        *

        attack_gosc

        *

        defence_dom

    )



    tabela = macierz_wynikow(

        lambda_dom,

        lambda_wyj

    )


    najlepszy=tabela[0]



    gd,gw,p=najlepszy



    if gd>gw:

        typ="1"


    elif gd==gw:

        typ="X"


    else:

        typ="2"



    wyniki.append(

        {

        "mecz":row[kolumna_mecz],

        "lambda_dom":round(lambda_dom,3),

        "lambda_wyj":round(lambda_wyj,3),

        "wynik_model":f"{gd}:{gw}",

        "prawdopodobienstwo":round(p,5),

        "typ":typ

        }

    )



# =================================================
# ZAPIS
# =================================================


df_out=pd.DataFrame(

    wyniki

)



df_out.to_csv(

    plik_wynik,

    sep=";",

    index=False,

    encoding="utf-8"

)



print()

print(

    "Zapisano:",

    plik_wynik

)


print()

print("==============================")

print(" KONIEC MODEL V2 ")

print("==============================")
import csv
import pandas as pd


# ==========================================
# PLIKI
# ==========================================

plik_wej = "dataBase_futbol_Stare.csv"

plik_wyj = "kursy_historyczne_przygotowane.csv"


# ==========================================
# ODCZYT PLIKU
# ==========================================

wyniki = []


with open(
    plik_wej,
    "r",
    encoding="utf-8",
    newline=""
) as f:


    reader = csv.reader(
        f,
        delimiter=";"
    )


    for nr, row in enumerate(reader):


        try:


            # pomijanie pustych lub uszkodzonych wierszy

            if len(row) < 8:
                continue



            # ==================================
            # STRUKTURA DANYCH
            # ==================================

            # indeks 2 - nazwa meczu

            mecz = row[2]



            # kursy początkowe

            kurs_1_start = row[3]

            kurs_X_start = row[4]

            kurs_2_start = row[5]



            # kursy końcowe

            # ostatnia wartość = Unix

            # przedostatnia = kurs 2

            # trzecia od końca = kurs X

            # czwarta od końca = kurs 1


            kurs_2_koniec = row[-2]

            kurs_X_koniec = row[-3]

            kurs_1_koniec = row[-4]



            wyniki.append(


                {

                    "mecz": mecz,

                    "kurs_1_start": kurs_1_start,

                    "kurs_X_start": kurs_X_start,

                    "kurs_2_start": kurs_2_start,

                    "kurs_1_koniec": kurs_1_koniec,

                    "kurs_X_koniec": kurs_X_koniec,

                    "kurs_2_koniec": kurs_2_koniec

                }


            )



        except Exception as e:


            print(
                "Błąd w wierszu:",
                nr,
                e
            )



# ==========================================
# DATAFRAME
# ==========================================


df = pd.DataFrame(
    wyniki
)



# zamiana kursów na liczby

kolumny_kursow = [

    "kurs_1_start",

    "kurs_X_start",

    "kurs_2_start",

    "kurs_1_koniec",

    "kurs_X_koniec",

    "kurs_2_koniec"

]


for kol in kolumny_kursow:


    df[kol] = pd.to_numeric(

        df[kol],

        errors="coerce"

    )



# ==========================================
# DODATKOWE CECHY ZMIANY KURSU
# ==========================================


df["zmiana_kurs_1"] = (

    df["kurs_1_koniec"]

    -

    df["kurs_1_start"]

)



df["zmiana_kurs_X"] = (

    df["kurs_X_koniec"]

    -

    df["kurs_X_start"]

)



df["zmiana_kurs_2"] = (

    df["kurs_2_koniec"]

    -

    df["kurs_2_start"]

)



# procentowa zmiana kursów


df["procent_kurs_1"] = (

    df["zmiana_kurs_1"]

    /

    df["kurs_1_start"]

)



df["procent_kurs_X"] = (

    df["zmiana_kurs_X"]

    /

    df["kurs_X_start"]

)



df["procent_kurs_2"] = (

    df["zmiana_kurs_2"]

    /

    df["kurs_2_start"]

)



# ==========================================
# ZAPIS
# ==========================================


df.to_csv(

    plik_wyj,

    sep=";",

    index=False,

    encoding="utf-8"

)



print()
print("==============================")
print("KONIEC")
print("==============================")
print()

print(
    "Liczba meczów:",
    len(df)
)

print()

print(
    "Zapisano:",
    plik_wyj
)

print()

print(
    df.head()
)