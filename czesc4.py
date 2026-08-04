


# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime

from tensorflow.keras.models import load_model



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_08_log_koniec"


PLIK_PREDYKCJI = r"dane\dataBase_futbol_trend.csv"


PLIK_HISTORIA = r"dane\kod_dataBase_futbol_trend.csv"



KATALOG_OBSERWACJI = os.path.join(
    KATALOG_MODELU,
    "obserwacja"
)


KATALOG_PREDYKCJI = os.path.join(
    KATALOG_MODELU,
    "predykcje"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_OBSERWACJI,
    "pamiec_obserwacji.json"
)



PLIK_OCENA = os.path.join(
    KATALOG_OBSERWACJI,
    "ocena.json"
)



os.makedirs(
    KATALOG_OBSERWACJI,
    exist_ok=True
)



os.makedirs(
    KATALOG_PREDYKCJI,
    exist_ok=True
)





# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "metadata.json"
    ),

    encoding="utf-8"

) as f:

    metadata = json.load(f)



CECHY = metadata["cechy"]


NAZWA_MODELU = metadata["nazwa"]





# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "klasy.json"
    ),

    encoding="utf-8"

) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v): k

    for k,v in klasy.items()

}





# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================


df_pred = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



INDEX_MAP = {


    kolumna:index

    for index,kolumna

    in enumerate(df_pred.columns)

}



print("MAPA CECH")

print(INDEX_MAP)





# =====================================================
# CECHY MODELU
# =====================================================


INDEX_CECH = []



for cecha in CECHY:


    if cecha not in INDEX_MAP:


        raise Exception(

            f"Brak cechy modelu: {cecha}"

        )


    INDEX_CECH.append(

        INDEX_MAP[cecha]

    )



print(

    "Cechy modelu:",

    INDEX_CECH

)





# =====================================================
# AKTUALNE MECZE DO PREDYKCJI
# =====================================================


NAZWY_PREDYKCJI = (

    df_pred["id_meczu"]

    .astype(str)

    .tolist()

)



X_PREDYKCJA = df_pred.iloc[

    :,

    INDEX_CECH

]



X_PREDYKCJA = np.nan_to_num(

    X_PREDYKCJA.values

)





# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


hist = pd.read_csv(

    PLIK_HISTORIA,

    sep=";",

    header=None,

    encoding="utf-8"

)



NAZWY_HISTORIA = hist.iloc[:,0].astype(str)



X_HISTORIA = hist.iloc[

    :,

    INDEX_CECH

]



Y_HISTORIA = hist.iloc[:,-1]



X_HISTORIA = np.nan_to_num(

    X_HISTORIA.values

)





# =====================================================
# WCZYTANIE MODELU
# =====================================================


model = load_model(

    os.path.join(

        KATALOG_MODELU,

        "model.h5"

    )

)





# =====================================================
# PREDYKCJA HISTORII
# =====================================================


print(
    "Analiza historii..."
)



pred_hist = model.predict(

    X_HISTORIA

)



klasy_pred_hist = np.argmax(

    pred_hist,

    axis=1

)





# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================


print(

    "Analiza aktualnych meczów..."

)



pred = model.predict(

    X_PREDYKCJA

)



klasy_pred = np.argmax(

    pred,

    axis=1

)





# =====================================================
# WCZYTANIE PAMIĘCI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:


        pamiec_obserwacji = json.load(f)



else:


    pamiec_obserwacji = {}





# =====================================================
# WCZYTANIE OCENY
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:


        ocena = json.load(f)



else:


    ocena = {


        "model":

        NAZWA_MODELU,


        "ocena_ogolna":

        {

            "ilosc":

            0,


            "trafienia":

            0

        },


        "ocena_wynikow":

        {}

    }





# =====================================================
# STRUKTURY SESJI
# =====================================================


czas = datetime.now().strftime(

    "%Y-%m-%d %H:%M:%S"

)



nowe_obserwacje = []


nowe_predykcje = []


nowa_historia = []




analiza = {}



for wynik in klasy.keys():


    analiza[wynik] = {


        "ilosc_wystapien":0,


        "trafienia":0,


        "bledy":{}

    }




print(

    "Przygotowano dane."

)
# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 2/2
# =====================================================



# =====================================================
# ANALIZA HISTORII Z WYNIKAMI
# =====================================================


for i,p in enumerate(klasy_pred_hist):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    real_wynik = str(
        Y_HISTORIA.iloc[i]
    )


    nazwa_meczu = str(
        NAZWY_HISTORIA.iloc[i]
    )


    pewnosc = float(
        np.max(pred_hist[i])
    )


    trafienie = (
        pred_wynik == real_wynik
    )



    obserwacja = {


        "data":

        czas,


        "model":

        NAZWA_MODELU,


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "predykcja":

        pred_wynik,


        "wynik_rzeczywisty":

        real_wynik,


        "pewnosc":

        pewnosc,


        "trafienie":

        trafienie

    }





    # =========================================
    # AKTUALIZACJA PAMIĘCI MECZU
    # =========================================


    if nazwa_meczu not in pamiec_obserwacji:


        pamiec_obserwacji[nazwa_meczu] = []



        obserwacja["pierwsza_obserwacja"] = True



    else:


        ostatnia = pamiec_obserwacji[nazwa_meczu][-1]



        if ostatnia["predykcja"] != pred_wynik:


            obserwacja["zmiana_predykcji"] = {


                "stara":

                ostatnia["predykcja"],


                "nowa":

                pred_wynik

            }



        if ostatnia["pewnosc"] != pewnosc:


            obserwacja["zmiana_pewnosci"] = {


                "stara":

                ostatnia["pewnosc"],


                "nowa":

                pewnosc

            }





    pamiec_obserwacji[nazwa_meczu].append(

        obserwacja

    )



    nowe_obserwacje.append(

        obserwacja

    )





    # statystyka klasy


    analiza[pred_wynik]["ilosc_wystapien"] += 1



    if trafienie:


        analiza[pred_wynik]["trafienia"] += 1


    else:


        if real_wynik not in analiza[pred_wynik]["bledy"]:


            analiza[pred_wynik]["bledy"][real_wynik] = 0



        analiza[pred_wynik]["bledy"][real_wynik] += 1







# =====================================================
# AKTUALNE MECZE BEZ WYNIKU
# =====================================================


for i,p in enumerate(klasy_pred):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    nazwa_meczu = str(

        NAZWY_PREDYKCJI[i]

    )


    pewnosc = float(

        np.max(pred[i])

    )



    predykcja = {


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "wynik_predykcji":

        pred_wynik,


        "pewnosc":

        pewnosc

    }



    nowe_predykcje.append(

        predykcja

    )







# =====================================================
# AKTUALIZACJA OCENY MODELU
# =====================================================


ilosc_globalna = 0

trafienia_globalne = 0



ocena_wynikow = {}



for wynik,dane in analiza.items():


    ilosc = dane["ilosc_wystapien"]


    trafienia = dane["trafienia"]



    ilosc_globalna += ilosc


    trafienia_globalne += trafienia



    ocena_wynikow[wynik] = {


        "ilosc_predykcji":

        ilosc,


        "trafienia":

        trafienia,


        "skutecznosc":

        (

            trafienia / ilosc

            if ilosc > 0

            else 0

        ),


        "bledy":

        dane["bledy"]

    }





ocena = {


    "model":

    NAZWA_MODELU,


    "data":

    czas,


    "ocena_ogolna":{


        "ilosc_meczow":

        ilosc_globalna,


        "trafienia":

        trafienia_globalne,


        "skutecznosc":

        (

            trafienia_globalne /

            ilosc_globalna

            if ilosc_globalna > 0

            else 0

        )

    },


    "ocena_wynikow":

    ocena_wynikow

}







# =====================================================
# ZAPIS PAMIĘCI
# =====================================================


with open(

    PLIK_PAMIEC,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        pamiec_obserwacji,

        f,

        indent=4,

        ensure_ascii=False

    )





# =====================================================
# ZAPIS OCENY
# =====================================================


with open(

    PLIK_OCENA,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        ocena,

        f,

        indent=4,

        ensure_ascii=False

    )







# =====================================================
# ZAPIS AKTUALNEJ PREDYKCJI
# =====================================================


pd.DataFrame(

    nowe_predykcje

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







# =====================================================
# ZAPIS HISTORII Z WYNIKAMI
# =====================================================


historia_csv = []



for mecz,lista in pamiec_obserwacji.items():


    ostatnia = lista[-1]


    historia_csv.append(


        {


            "id_meczu":

            mecz,


            "id_grupy":

            ostatnia["id_grupy"],


            "wynik_predykcji":

            ostatnia["predykcja"],


            "pewnosc":

            ostatnia["pewnosc"],


            "wynik_rzeczywisty":

            ostatnia["wynik_rzeczywisty"]

        }

    )







pd.DataFrame(

    historia_csv

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







print()

print("================================")

print("ZAKOŃCZONO")

print("================================")



print(

    "Pamięć:",

    PLIK_PAMIEC

)



print(

    "Ocena:",

    PLIK_OCENA

)



print(

    "Predykcje:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    )

)



print(

    "Historia:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    )

)
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = (
    r"modele_dataBase_futbol_trend"
    r"\siec_08_log_koniec"
)


NAZWA_BAZY = "dataBase_futbol_trend"


NAZWA_MODELU = os.path.basename(
    KATALOG_MODELU
)



# =====================================================
# LABORATORIUM
# =====================================================


KATALOG_LABORATORIUM = os.path.join(
    "laboratorium",
    NAZWA_BAZY,
    NAZWA_MODELU
)



os.makedirs(
    KATALOG_LABORATORIUM,
    exist_ok=True
)



# =====================================================
# PLIKI WEJŚCIOWE
# =====================================================


PLIK_KLASY = os.path.join(
    KATALOG_MODELU,
    "klasy.json"
)



PLIK_PRED_WYNIK = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_z_wynikiem.csv"
)



PLIK_PRED_GRUPY = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_grupy.csv"
)



PLIK_OCENA = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "ocena.json"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "pamiec_obserwacji.json"
)




# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(
    PLIK_KLASY,
    encoding="utf-8"
) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v):k

    for k,v in klasy.items()

}



print(
    "Załadowano klas:",
    len(ID_NA_WYNIK)
)



# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


df_historia = pd.read_csv(

    PLIK_PRED_WYNIK,

    sep=";",

    encoding="utf-8"

)



print(
    "Historia:",
    len(df_historia)
)



# =====================================================
# WCZYTANIE AKTUALNYCH PREDYKCJI
# =====================================================


df_predykcja = pd.read_csv(

    PLIK_PRED_GRUPY,

    sep=";",

    encoding="utf-8"

)



print(
    "Aktualne predykcje:",
    len(df_predykcja)
)



# =====================================================
# WCZYTANIE OCENY MODELU
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:

        ocena_modelu = json.load(f)


else:


    ocena_modelu = {}




# =====================================================
# WCZYTANIE PAMIĘCI OBSERWACJI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:

        pamiec_obserwacji = json.load(f)


else:


    pamiec_obserwacji = {}




print(
    "Pamięć obserwacji:",
    len(pamiec_obserwacji)
)




# =====================================================
# ANALIZA KLAS
# =====================================================


analiza_klas = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    ilosc = len(dane)



    if ilosc == 0:


        analiza_klas[str(id_grupy)] = {


            "wynik":

            wynik,


            "ilosc_predykcji":

            0,


            "trafienia":

            0,


            "skutecznosc":

            0,


            "rzeczywisty_rozkład":

            {}

        }


        continue




    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()




    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )




    analiza_klas[str(id_grupy)] = {


        "wynik":

        wynik,


        "ilosc_predykcji":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        ),



        "rzeczywisty_rozkład":

        rozklad

    }




# =====================================================
# ANALIZA PEWNOŚCI DYNAMICZNA
# =====================================================


analiza_pewnosci = {}




df_historia = df_historia.sort_values(
    "pewnosc"
)




# 10 równych grup według ilości danych

df_historia["koszyk_pewnosci"] = pd.qcut(

    df_historia["pewnosc"],

    q=10,

    duplicates="drop"

)




for koszyk, dane in df_historia.groupby(

    "koszyk_pewnosci",

    observed=True

):


    ilosc = len(dane)



    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()



    analiza_pewnosci[str(koszyk)] = {


        "ilosc":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        )

    }




# =====================================================
# ANALIZA PEWNOŚCI DLA KAŻDEJ KLASY
# =====================================================


analiza_pewnosci_klasy = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane_klasy = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    if len(dane_klasy) == 0:

        continue




    dane_klasy = dane_klasy.copy()



    dane_klasy["koszyk"] = pd.qcut(

        dane_klasy["pewnosc"],

        q=10,

        duplicates="drop"

    )



    koszyki = {}



    for koszyk,dane in dane_klasy.groupby(

        "koszyk",

        observed=True

    ):



        ilosc = len(dane)



        trafienia = (

            dane["wynik_predykcji"]

            ==

            dane["wynik_rzeczywisty"]

        ).sum()



        koszyki[str(koszyk)] = {


            "ilosc":

            int(ilosc),


            "trafienia":

            int(trafienia),


            "skutecznosc":

            float(

                trafienia / ilosc

            )

        }




    analiza_pewnosci_klasy[str(id_grupy)] = {


        "wynik":

        wynik,


        "progi_pewnosci":

        koszyki

    }




# KONIEC FRAGMENTU 1/2
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 2/2
# =====================================================


# =====================================================
# ANALIZA ODCHYLEŃ
# (CO SIEĆ TYPOWAŁA VS CO FAKTYCZNIE WYPADŁO)
# =====================================================


analiza_odchylen = {}



for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]


    if len(dane) == 0:

        continue



    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )



    uporzadkowane = sorted(

        rozklad.items(),

        key=lambda x:x[1],

        reverse=True

    )



    analiza_odchylen[str(id_grupy)] = {


        "wynik_typowany":

        wynik,


        "ilosc":

        int(len(dane)),


        "najczestsze_wyniki_rzeczywiste":

        dict(uporzadkowane[:10]),


        "czy_odwrócony_wzorzec":

        (
            uporzadkowane[0][0] != wynik
            if len(uporzadkowane)>0
            else False
        )

    }




# =====================================================
# ANALIZA PAMIĘCI OBSERWACJI
# =====================================================


analiza_pamieci = {


    "ilosc_meczow":

    len(pamiec_obserwacji),


    "zmiany_predykcji":0,


    "pierwsze_obserwacje":0

}



for mecz, obserwacje in pamiec_obserwacji.items():


    for obs in obserwacje:


        if obs.get(
            "pierwsza_obserwacja"
        ):

            analiza_pamieci[
                "pierwsze_obserwacje"
            ] += 1



        if obs.get(
            "zmiana_predykcji"
        ):

            analiza_pamieci[
                "zmiany_predykcji"
            ] += 1




# =====================================================
# ANALIZA AKTUALNYCH PREDYKCJI
# =====================================================


analiza_przyszlych = []



for _,mecz in df_predykcja.iterrows():


    id_grupy = int(
        mecz["id_grupy"]
    )


    wynik = str(
        mecz["wynik_predykcji"]
    )


    pewnosc = float(
        mecz["pewnosc"]
    )



    wiedza = analiza_klas.get(

        str(id_grupy),

        {}

    )



    pewnosc_klasy = analiza_pewnosci_klasy.get(

        str(id_grupy),

        {}

    )



    odchylenie = analiza_odchylen.get(

        str(id_grupy),

        {}

    )


    analiza_przyszlych.append(


        {


            "id_meczu":

            mecz["id_meczu"],



            "id_grupy":

            id_grupy,



            "wynik_predykcji":

            wynik,



            "pewnosc":

            pewnosc,



            "historyczna_skutecznosc_klasy":

            wiedza.get(

                "skutecznosc",

                0

            ),



            "najczestszy_realny_wynik":

            (
                max(

                    wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ),

                    key=wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ).get

                )

                if wiedza.get(

                    "rzeczywisty_rozkład"

                )

                else None
            ),



            "czy_odwrócony_wzorzec":

            odchylenie.get(

                "czy_odwrócony_wzorzec",

                False

            )

        }

    )




df_analiza_predykcji = pd.DataFrame(

    analiza_przyszlych

)



df_analiza_predykcji.to_csv(


    os.path.join(

        KATALOG_LABORATORIUM,

        "analiza_przyszlych_predykcji.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)




# =====================================================
# KOLEKTOR WIEDZY
# =====================================================


kolektor_wiedzy = {


    "model":

    NAZWA_MODELU,



    "data":

    datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    ),



    "ocena_modelu":

    ocena_modelu,



    "analiza_klas":

    analiza_klas,



    "analiza_pewnosci":

    analiza_pewnosci,



    "analiza_pewnosci_klasy":

    analiza_pewnosci_klasy,



    "analiza_odchylen":

    analiza_odchylen,



    "analiza_pamieci":

    analiza_pamieci

}




# =====================================================
# ZAPIS JSON
# =====================================================


pliki_json = {


    "analiza_klas.json":

    analiza_klas,


    "analiza_pewnosci.json":

    analiza_pewnosci,


    "analiza_pewnosci_klasy.json":

    analiza_pewnosci_klasy,


    "analiza_odchylen.json":

    analiza_odchylen,


    "analiza_pamieci.json":

    analiza_pamieci,


    "kolektor_wiedzy.json":

    kolektor_wiedzy

}




for nazwa,dane in pliki_json.items():


    with open(

        os.path.join(

            KATALOG_LABORATORIUM,

            nazwa

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            dane,

            f,

            indent=4,

            ensure_ascii=False

        )




# =====================================================
# RAPORT KOŃCOWY
# =====================================================


print()
print("======================================")
print("LABORATORIUM V2 ZAKOŃCZONE")
print("======================================")


print(
    "Model:",
    NAZWA_MODELU
)


print(
    "Katalog:",
    KATALOG_LABORATORIUM
)


print(
    "Analizowane mecze:",
    len(df_historia)
)


print(
    "Przyszłe predykcje:",
    len(df_predykcja)
)


print(
    "Pamięć:",
    len(pamiec_obserwacji)
)


print()
print("Utworzono:")

for plik in pliki_json:

    print(
        "-",
        plik
    )


print(
    "- analiza_przyszlych_predykcji.csv"
)

print()
print("======================================")






# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime

from tensorflow.keras.models import load_model



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_09_ratio_start"


PLIK_PREDYKCJI = r"dane\dataBase_futbol_trend.csv"


PLIK_HISTORIA = r"dane\kod_dataBase_futbol_trend.csv"



KATALOG_OBSERWACJI = os.path.join(
    KATALOG_MODELU,
    "obserwacja"
)


KATALOG_PREDYKCJI = os.path.join(
    KATALOG_MODELU,
    "predykcje"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_OBSERWACJI,
    "pamiec_obserwacji.json"
)



PLIK_OCENA = os.path.join(
    KATALOG_OBSERWACJI,
    "ocena.json"
)



os.makedirs(
    KATALOG_OBSERWACJI,
    exist_ok=True
)



os.makedirs(
    KATALOG_PREDYKCJI,
    exist_ok=True
)





# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "metadata.json"
    ),

    encoding="utf-8"

) as f:

    metadata = json.load(f)



CECHY = metadata["cechy"]


NAZWA_MODELU = metadata["nazwa"]





# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "klasy.json"
    ),

    encoding="utf-8"

) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v): k

    for k,v in klasy.items()

}





# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================


df_pred = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



INDEX_MAP = {


    kolumna:index

    for index,kolumna

    in enumerate(df_pred.columns)

}



print("MAPA CECH")

print(INDEX_MAP)





# =====================================================
# CECHY MODELU
# =====================================================


INDEX_CECH = []



for cecha in CECHY:


    if cecha not in INDEX_MAP:


        raise Exception(

            f"Brak cechy modelu: {cecha}"

        )


    INDEX_CECH.append(

        INDEX_MAP[cecha]

    )



print(

    "Cechy modelu:",

    INDEX_CECH

)





# =====================================================
# AKTUALNE MECZE DO PREDYKCJI
# =====================================================


NAZWY_PREDYKCJI = (

    df_pred["id_meczu"]

    .astype(str)

    .tolist()

)



X_PREDYKCJA = df_pred.iloc[

    :,

    INDEX_CECH

]



X_PREDYKCJA = np.nan_to_num(

    X_PREDYKCJA.values

)





# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


hist = pd.read_csv(

    PLIK_HISTORIA,

    sep=";",

    header=None,

    encoding="utf-8"

)



NAZWY_HISTORIA = hist.iloc[:,0].astype(str)



X_HISTORIA = hist.iloc[

    :,

    INDEX_CECH

]



Y_HISTORIA = hist.iloc[:,-1]



X_HISTORIA = np.nan_to_num(

    X_HISTORIA.values

)





# =====================================================
# WCZYTANIE MODELU
# =====================================================


model = load_model(

    os.path.join(

        KATALOG_MODELU,

        "model.h5"

    )

)





# =====================================================
# PREDYKCJA HISTORII
# =====================================================


print(
    "Analiza historii..."
)



pred_hist = model.predict(

    X_HISTORIA

)



klasy_pred_hist = np.argmax(

    pred_hist,

    axis=1

)





# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================


print(

    "Analiza aktualnych meczów..."

)



pred = model.predict(

    X_PREDYKCJA

)



klasy_pred = np.argmax(

    pred,

    axis=1

)





# =====================================================
# WCZYTANIE PAMIĘCI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:


        pamiec_obserwacji = json.load(f)



else:


    pamiec_obserwacji = {}





# =====================================================
# WCZYTANIE OCENY
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:


        ocena = json.load(f)



else:


    ocena = {


        "model":

        NAZWA_MODELU,


        "ocena_ogolna":

        {

            "ilosc":

            0,


            "trafienia":

            0

        },


        "ocena_wynikow":

        {}

    }





# =====================================================
# STRUKTURY SESJI
# =====================================================


czas = datetime.now().strftime(

    "%Y-%m-%d %H:%M:%S"

)



nowe_obserwacje = []


nowe_predykcje = []


nowa_historia = []




analiza = {}



for wynik in klasy.keys():


    analiza[wynik] = {


        "ilosc_wystapien":0,


        "trafienia":0,


        "bledy":{}

    }




print(

    "Przygotowano dane."

)
# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 2/2
# =====================================================



# =====================================================
# ANALIZA HISTORII Z WYNIKAMI
# =====================================================


for i,p in enumerate(klasy_pred_hist):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    real_wynik = str(
        Y_HISTORIA.iloc[i]
    )


    nazwa_meczu = str(
        NAZWY_HISTORIA.iloc[i]
    )


    pewnosc = float(
        np.max(pred_hist[i])
    )


    trafienie = (
        pred_wynik == real_wynik
    )



    obserwacja = {


        "data":

        czas,


        "model":

        NAZWA_MODELU,


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "predykcja":

        pred_wynik,


        "wynik_rzeczywisty":

        real_wynik,


        "pewnosc":

        pewnosc,


        "trafienie":

        trafienie

    }





    # =========================================
    # AKTUALIZACJA PAMIĘCI MECZU
    # =========================================


    if nazwa_meczu not in pamiec_obserwacji:


        pamiec_obserwacji[nazwa_meczu] = []



        obserwacja["pierwsza_obserwacja"] = True



    else:


        ostatnia = pamiec_obserwacji[nazwa_meczu][-1]



        if ostatnia["predykcja"] != pred_wynik:


            obserwacja["zmiana_predykcji"] = {


                "stara":

                ostatnia["predykcja"],


                "nowa":

                pred_wynik

            }



        if ostatnia["pewnosc"] != pewnosc:


            obserwacja["zmiana_pewnosci"] = {


                "stara":

                ostatnia["pewnosc"],


                "nowa":

                pewnosc

            }





    pamiec_obserwacji[nazwa_meczu].append(

        obserwacja

    )



    nowe_obserwacje.append(

        obserwacja

    )





    # statystyka klasy


    analiza[pred_wynik]["ilosc_wystapien"] += 1



    if trafienie:


        analiza[pred_wynik]["trafienia"] += 1


    else:


        if real_wynik not in analiza[pred_wynik]["bledy"]:


            analiza[pred_wynik]["bledy"][real_wynik] = 0



        analiza[pred_wynik]["bledy"][real_wynik] += 1







# =====================================================
# AKTUALNE MECZE BEZ WYNIKU
# =====================================================


for i,p in enumerate(klasy_pred):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    nazwa_meczu = str(

        NAZWY_PREDYKCJI[i]

    )


    pewnosc = float(

        np.max(pred[i])

    )



    predykcja = {


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "wynik_predykcji":

        pred_wynik,


        "pewnosc":

        pewnosc

    }



    nowe_predykcje.append(

        predykcja

    )







# =====================================================
# AKTUALIZACJA OCENY MODELU
# =====================================================


ilosc_globalna = 0

trafienia_globalne = 0



ocena_wynikow = {}



for wynik,dane in analiza.items():


    ilosc = dane["ilosc_wystapien"]


    trafienia = dane["trafienia"]



    ilosc_globalna += ilosc


    trafienia_globalne += trafienia



    ocena_wynikow[wynik] = {


        "ilosc_predykcji":

        ilosc,


        "trafienia":

        trafienia,


        "skutecznosc":

        (

            trafienia / ilosc

            if ilosc > 0

            else 0

        ),


        "bledy":

        dane["bledy"]

    }





ocena = {


    "model":

    NAZWA_MODELU,


    "data":

    czas,


    "ocena_ogolna":{


        "ilosc_meczow":

        ilosc_globalna,


        "trafienia":

        trafienia_globalne,


        "skutecznosc":

        (

            trafienia_globalne /

            ilosc_globalna

            if ilosc_globalna > 0

            else 0

        )

    },


    "ocena_wynikow":

    ocena_wynikow

}







# =====================================================
# ZAPIS PAMIĘCI
# =====================================================


with open(

    PLIK_PAMIEC,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        pamiec_obserwacji,

        f,

        indent=4,

        ensure_ascii=False

    )





# =====================================================
# ZAPIS OCENY
# =====================================================


with open(

    PLIK_OCENA,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        ocena,

        f,

        indent=4,

        ensure_ascii=False

    )







# =====================================================
# ZAPIS AKTUALNEJ PREDYKCJI
# =====================================================


pd.DataFrame(

    nowe_predykcje

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







# =====================================================
# ZAPIS HISTORII Z WYNIKAMI
# =====================================================


historia_csv = []



for mecz,lista in pamiec_obserwacji.items():


    ostatnia = lista[-1]


    historia_csv.append(


        {


            "id_meczu":

            mecz,


            "id_grupy":

            ostatnia["id_grupy"],


            "wynik_predykcji":

            ostatnia["predykcja"],


            "pewnosc":

            ostatnia["pewnosc"],


            "wynik_rzeczywisty":

            ostatnia["wynik_rzeczywisty"]

        }

    )







pd.DataFrame(

    historia_csv

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







print()

print("================================")

print("ZAKOŃCZONO")

print("================================")



print(

    "Pamięć:",

    PLIK_PAMIEC

)



print(

    "Ocena:",

    PLIK_OCENA

)



print(

    "Predykcje:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    )

)



print(

    "Historia:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    )

)
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = (
    r"modele_dataBase_futbol_trend"
    r"\siec_09_ratio_start"
)


NAZWA_BAZY = "dataBase_futbol_trend"


NAZWA_MODELU = os.path.basename(
    KATALOG_MODELU
)



# =====================================================
# LABORATORIUM
# =====================================================


KATALOG_LABORATORIUM = os.path.join(
    "laboratorium",
    NAZWA_BAZY,
    NAZWA_MODELU
)



os.makedirs(
    KATALOG_LABORATORIUM,
    exist_ok=True
)



# =====================================================
# PLIKI WEJŚCIOWE
# =====================================================


PLIK_KLASY = os.path.join(
    KATALOG_MODELU,
    "klasy.json"
)



PLIK_PRED_WYNIK = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_z_wynikiem.csv"
)



PLIK_PRED_GRUPY = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_grupy.csv"
)



PLIK_OCENA = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "ocena.json"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "pamiec_obserwacji.json"
)




# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(
    PLIK_KLASY,
    encoding="utf-8"
) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v):k

    for k,v in klasy.items()

}



print(
    "Załadowano klas:",
    len(ID_NA_WYNIK)
)



# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


df_historia = pd.read_csv(

    PLIK_PRED_WYNIK,

    sep=";",

    encoding="utf-8"

)



print(
    "Historia:",
    len(df_historia)
)



# =====================================================
# WCZYTANIE AKTUALNYCH PREDYKCJI
# =====================================================


df_predykcja = pd.read_csv(

    PLIK_PRED_GRUPY,

    sep=";",

    encoding="utf-8"

)



print(
    "Aktualne predykcje:",
    len(df_predykcja)
)



# =====================================================
# WCZYTANIE OCENY MODELU
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:

        ocena_modelu = json.load(f)


else:


    ocena_modelu = {}




# =====================================================
# WCZYTANIE PAMIĘCI OBSERWACJI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:

        pamiec_obserwacji = json.load(f)


else:


    pamiec_obserwacji = {}




print(
    "Pamięć obserwacji:",
    len(pamiec_obserwacji)
)




# =====================================================
# ANALIZA KLAS
# =====================================================


analiza_klas = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    ilosc = len(dane)



    if ilosc == 0:


        analiza_klas[str(id_grupy)] = {


            "wynik":

            wynik,


            "ilosc_predykcji":

            0,


            "trafienia":

            0,


            "skutecznosc":

            0,


            "rzeczywisty_rozkład":

            {}

        }


        continue




    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()




    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )




    analiza_klas[str(id_grupy)] = {


        "wynik":

        wynik,


        "ilosc_predykcji":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        ),



        "rzeczywisty_rozkład":

        rozklad

    }




# =====================================================
# ANALIZA PEWNOŚCI DYNAMICZNA
# =====================================================


analiza_pewnosci = {}




df_historia = df_historia.sort_values(
    "pewnosc"
)




# 10 równych grup według ilości danych

df_historia["koszyk_pewnosci"] = pd.qcut(

    df_historia["pewnosc"],

    q=10,

    duplicates="drop"

)




for koszyk, dane in df_historia.groupby(

    "koszyk_pewnosci",

    observed=True

):


    ilosc = len(dane)



    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()



    analiza_pewnosci[str(koszyk)] = {


        "ilosc":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        )

    }




# =====================================================
# ANALIZA PEWNOŚCI DLA KAŻDEJ KLASY
# =====================================================


analiza_pewnosci_klasy = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane_klasy = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    if len(dane_klasy) == 0:

        continue




    dane_klasy = dane_klasy.copy()



    dane_klasy["koszyk"] = pd.qcut(

        dane_klasy["pewnosc"],

        q=10,

        duplicates="drop"

    )



    koszyki = {}



    for koszyk,dane in dane_klasy.groupby(

        "koszyk",

        observed=True

    ):



        ilosc = len(dane)



        trafienia = (

            dane["wynik_predykcji"]

            ==

            dane["wynik_rzeczywisty"]

        ).sum()



        koszyki[str(koszyk)] = {


            "ilosc":

            int(ilosc),


            "trafienia":

            int(trafienia),


            "skutecznosc":

            float(

                trafienia / ilosc

            )

        }




    analiza_pewnosci_klasy[str(id_grupy)] = {


        "wynik":

        wynik,


        "progi_pewnosci":

        koszyki

    }




# KONIEC FRAGMENTU 1/2
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 2/2
# =====================================================


# =====================================================
# ANALIZA ODCHYLEŃ
# (CO SIEĆ TYPOWAŁA VS CO FAKTYCZNIE WYPADŁO)
# =====================================================


analiza_odchylen = {}



for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]


    if len(dane) == 0:

        continue



    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )



    uporzadkowane = sorted(

        rozklad.items(),

        key=lambda x:x[1],

        reverse=True

    )



    analiza_odchylen[str(id_grupy)] = {


        "wynik_typowany":

        wynik,


        "ilosc":

        int(len(dane)),


        "najczestsze_wyniki_rzeczywiste":

        dict(uporzadkowane[:10]),


        "czy_odwrócony_wzorzec":

        (
            uporzadkowane[0][0] != wynik
            if len(uporzadkowane)>0
            else False
        )

    }




# =====================================================
# ANALIZA PAMIĘCI OBSERWACJI
# =====================================================


analiza_pamieci = {


    "ilosc_meczow":

    len(pamiec_obserwacji),


    "zmiany_predykcji":0,


    "pierwsze_obserwacje":0

}



for mecz, obserwacje in pamiec_obserwacji.items():


    for obs in obserwacje:


        if obs.get(
            "pierwsza_obserwacja"
        ):

            analiza_pamieci[
                "pierwsze_obserwacje"
            ] += 1



        if obs.get(
            "zmiana_predykcji"
        ):

            analiza_pamieci[
                "zmiany_predykcji"
            ] += 1




# =====================================================
# ANALIZA AKTUALNYCH PREDYKCJI
# =====================================================


analiza_przyszlych = []



for _,mecz in df_predykcja.iterrows():


    id_grupy = int(
        mecz["id_grupy"]
    )


    wynik = str(
        mecz["wynik_predykcji"]
    )


    pewnosc = float(
        mecz["pewnosc"]
    )



    wiedza = analiza_klas.get(

        str(id_grupy),

        {}

    )



    pewnosc_klasy = analiza_pewnosci_klasy.get(

        str(id_grupy),

        {}

    )



    odchylenie = analiza_odchylen.get(

        str(id_grupy),

        {}

    )


    analiza_przyszlych.append(


        {


            "id_meczu":

            mecz["id_meczu"],



            "id_grupy":

            id_grupy,



            "wynik_predykcji":

            wynik,



            "pewnosc":

            pewnosc,



            "historyczna_skutecznosc_klasy":

            wiedza.get(

                "skutecznosc",

                0

            ),



            "najczestszy_realny_wynik":

            (
                max(

                    wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ),

                    key=wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ).get

                )

                if wiedza.get(

                    "rzeczywisty_rozkład"

                )

                else None
            ),



            "czy_odwrócony_wzorzec":

            odchylenie.get(

                "czy_odwrócony_wzorzec",

                False

            )

        }

    )




df_analiza_predykcji = pd.DataFrame(

    analiza_przyszlych

)



df_analiza_predykcji.to_csv(


    os.path.join(

        KATALOG_LABORATORIUM,

        "analiza_przyszlych_predykcji.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)




# =====================================================
# KOLEKTOR WIEDZY
# =====================================================


kolektor_wiedzy = {


    "model":

    NAZWA_MODELU,



    "data":

    datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    ),



    "ocena_modelu":

    ocena_modelu,



    "analiza_klas":

    analiza_klas,



    "analiza_pewnosci":

    analiza_pewnosci,



    "analiza_pewnosci_klasy":

    analiza_pewnosci_klasy,



    "analiza_odchylen":

    analiza_odchylen,



    "analiza_pamieci":

    analiza_pamieci

}




# =====================================================
# ZAPIS JSON
# =====================================================


pliki_json = {


    "analiza_klas.json":

    analiza_klas,


    "analiza_pewnosci.json":

    analiza_pewnosci,


    "analiza_pewnosci_klasy.json":

    analiza_pewnosci_klasy,


    "analiza_odchylen.json":

    analiza_odchylen,


    "analiza_pamieci.json":

    analiza_pamieci,


    "kolektor_wiedzy.json":

    kolektor_wiedzy

}




for nazwa,dane in pliki_json.items():


    with open(

        os.path.join(

            KATALOG_LABORATORIUM,

            nazwa

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            dane,

            f,

            indent=4,

            ensure_ascii=False

        )




# =====================================================
# RAPORT KOŃCOWY
# =====================================================


print()
print("======================================")
print("LABORATORIUM V2 ZAKOŃCZONE")
print("======================================")


print(
    "Model:",
    NAZWA_MODELU
)


print(
    "Katalog:",
    KATALOG_LABORATORIUM
)


print(
    "Analizowane mecze:",
    len(df_historia)
)


print(
    "Przyszłe predykcje:",
    len(df_predykcja)
)


print(
    "Pamięć:",
    len(pamiec_obserwacji)
)


print()
print("Utworzono:")

for plik in pliki_json:

    print(
        "-",
        plik
    )


print(
    "- analiza_przyszlych_predykcji.csv"
)

print()
print("======================================")






# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime

from tensorflow.keras.models import load_model



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_10_ratio_koniec"


PLIK_PREDYKCJI = r"dane\dataBase_futbol_trend.csv"


PLIK_HISTORIA = r"dane\kod_dataBase_futbol_trend.csv"



KATALOG_OBSERWACJI = os.path.join(
    KATALOG_MODELU,
    "obserwacja"
)


KATALOG_PREDYKCJI = os.path.join(
    KATALOG_MODELU,
    "predykcje"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_OBSERWACJI,
    "pamiec_obserwacji.json"
)



PLIK_OCENA = os.path.join(
    KATALOG_OBSERWACJI,
    "ocena.json"
)



os.makedirs(
    KATALOG_OBSERWACJI,
    exist_ok=True
)



os.makedirs(
    KATALOG_PREDYKCJI,
    exist_ok=True
)





# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "metadata.json"
    ),

    encoding="utf-8"

) as f:

    metadata = json.load(f)



CECHY = metadata["cechy"]


NAZWA_MODELU = metadata["nazwa"]





# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "klasy.json"
    ),

    encoding="utf-8"

) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v): k

    for k,v in klasy.items()

}





# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================


df_pred = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



INDEX_MAP = {


    kolumna:index

    for index,kolumna

    in enumerate(df_pred.columns)

}



print("MAPA CECH")

print(INDEX_MAP)





# =====================================================
# CECHY MODELU
# =====================================================


INDEX_CECH = []



for cecha in CECHY:


    if cecha not in INDEX_MAP:


        raise Exception(

            f"Brak cechy modelu: {cecha}"

        )


    INDEX_CECH.append(

        INDEX_MAP[cecha]

    )



print(

    "Cechy modelu:",

    INDEX_CECH

)





# =====================================================
# AKTUALNE MECZE DO PREDYKCJI
# =====================================================


NAZWY_PREDYKCJI = (

    df_pred["id_meczu"]

    .astype(str)

    .tolist()

)



X_PREDYKCJA = df_pred.iloc[

    :,

    INDEX_CECH

]



X_PREDYKCJA = np.nan_to_num(

    X_PREDYKCJA.values

)





# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


hist = pd.read_csv(

    PLIK_HISTORIA,

    sep=";",

    header=None,

    encoding="utf-8"

)



NAZWY_HISTORIA = hist.iloc[:,0].astype(str)



X_HISTORIA = hist.iloc[

    :,

    INDEX_CECH

]



Y_HISTORIA = hist.iloc[:,-1]



X_HISTORIA = np.nan_to_num(

    X_HISTORIA.values

)





# =====================================================
# WCZYTANIE MODELU
# =====================================================


model = load_model(

    os.path.join(

        KATALOG_MODELU,

        "model.h5"

    )

)





# =====================================================
# PREDYKCJA HISTORII
# =====================================================


print(
    "Analiza historii..."
)



pred_hist = model.predict(

    X_HISTORIA

)



klasy_pred_hist = np.argmax(

    pred_hist,

    axis=1

)





# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================


print(

    "Analiza aktualnych meczów..."

)



pred = model.predict(

    X_PREDYKCJA

)



klasy_pred = np.argmax(

    pred,

    axis=1

)





# =====================================================
# WCZYTANIE PAMIĘCI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:


        pamiec_obserwacji = json.load(f)



else:


    pamiec_obserwacji = {}





# =====================================================
# WCZYTANIE OCENY
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:


        ocena = json.load(f)



else:


    ocena = {


        "model":

        NAZWA_MODELU,


        "ocena_ogolna":

        {

            "ilosc":

            0,


            "trafienia":

            0

        },


        "ocena_wynikow":

        {}

    }





# =====================================================
# STRUKTURY SESJI
# =====================================================


czas = datetime.now().strftime(

    "%Y-%m-%d %H:%M:%S"

)



nowe_obserwacje = []


nowe_predykcje = []


nowa_historia = []




analiza = {}



for wynik in klasy.keys():


    analiza[wynik] = {


        "ilosc_wystapien":0,


        "trafienia":0,


        "bledy":{}

    }




print(

    "Przygotowano dane."

)
# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 2/2
# =====================================================



# =====================================================
# ANALIZA HISTORII Z WYNIKAMI
# =====================================================


for i,p in enumerate(klasy_pred_hist):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    real_wynik = str(
        Y_HISTORIA.iloc[i]
    )


    nazwa_meczu = str(
        NAZWY_HISTORIA.iloc[i]
    )


    pewnosc = float(
        np.max(pred_hist[i])
    )


    trafienie = (
        pred_wynik == real_wynik
    )



    obserwacja = {


        "data":

        czas,


        "model":

        NAZWA_MODELU,


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "predykcja":

        pred_wynik,


        "wynik_rzeczywisty":

        real_wynik,


        "pewnosc":

        pewnosc,


        "trafienie":

        trafienie

    }





    # =========================================
    # AKTUALIZACJA PAMIĘCI MECZU
    # =========================================


    if nazwa_meczu not in pamiec_obserwacji:


        pamiec_obserwacji[nazwa_meczu] = []



        obserwacja["pierwsza_obserwacja"] = True



    else:


        ostatnia = pamiec_obserwacji[nazwa_meczu][-1]



        if ostatnia["predykcja"] != pred_wynik:


            obserwacja["zmiana_predykcji"] = {


                "stara":

                ostatnia["predykcja"],


                "nowa":

                pred_wynik

            }



        if ostatnia["pewnosc"] != pewnosc:


            obserwacja["zmiana_pewnosci"] = {


                "stara":

                ostatnia["pewnosc"],


                "nowa":

                pewnosc

            }





    pamiec_obserwacji[nazwa_meczu].append(

        obserwacja

    )



    nowe_obserwacje.append(

        obserwacja

    )





    # statystyka klasy


    analiza[pred_wynik]["ilosc_wystapien"] += 1



    if trafienie:


        analiza[pred_wynik]["trafienia"] += 1


    else:


        if real_wynik not in analiza[pred_wynik]["bledy"]:


            analiza[pred_wynik]["bledy"][real_wynik] = 0



        analiza[pred_wynik]["bledy"][real_wynik] += 1







# =====================================================
# AKTUALNE MECZE BEZ WYNIKU
# =====================================================


for i,p in enumerate(klasy_pred):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    nazwa_meczu = str(

        NAZWY_PREDYKCJI[i]

    )


    pewnosc = float(

        np.max(pred[i])

    )



    predykcja = {


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "wynik_predykcji":

        pred_wynik,


        "pewnosc":

        pewnosc

    }



    nowe_predykcje.append(

        predykcja

    )







# =====================================================
# AKTUALIZACJA OCENY MODELU
# =====================================================


ilosc_globalna = 0

trafienia_globalne = 0



ocena_wynikow = {}



for wynik,dane in analiza.items():


    ilosc = dane["ilosc_wystapien"]


    trafienia = dane["trafienia"]



    ilosc_globalna += ilosc


    trafienia_globalne += trafienia



    ocena_wynikow[wynik] = {


        "ilosc_predykcji":

        ilosc,


        "trafienia":

        trafienia,


        "skutecznosc":

        (

            trafienia / ilosc

            if ilosc > 0

            else 0

        ),


        "bledy":

        dane["bledy"]

    }





ocena = {


    "model":

    NAZWA_MODELU,


    "data":

    czas,


    "ocena_ogolna":{


        "ilosc_meczow":

        ilosc_globalna,


        "trafienia":

        trafienia_globalne,


        "skutecznosc":

        (

            trafienia_globalne /

            ilosc_globalna

            if ilosc_globalna > 0

            else 0

        )

    },


    "ocena_wynikow":

    ocena_wynikow

}







# =====================================================
# ZAPIS PAMIĘCI
# =====================================================


with open(

    PLIK_PAMIEC,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        pamiec_obserwacji,

        f,

        indent=4,

        ensure_ascii=False

    )





# =====================================================
# ZAPIS OCENY
# =====================================================


with open(

    PLIK_OCENA,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        ocena,

        f,

        indent=4,

        ensure_ascii=False

    )







# =====================================================
# ZAPIS AKTUALNEJ PREDYKCJI
# =====================================================


pd.DataFrame(

    nowe_predykcje

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







# =====================================================
# ZAPIS HISTORII Z WYNIKAMI
# =====================================================


historia_csv = []



for mecz,lista in pamiec_obserwacji.items():


    ostatnia = lista[-1]


    historia_csv.append(


        {


            "id_meczu":

            mecz,


            "id_grupy":

            ostatnia["id_grupy"],


            "wynik_predykcji":

            ostatnia["predykcja"],


            "pewnosc":

            ostatnia["pewnosc"],


            "wynik_rzeczywisty":

            ostatnia["wynik_rzeczywisty"]

        }

    )







pd.DataFrame(

    historia_csv

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







print()

print("================================")

print("ZAKOŃCZONO")

print("================================")



print(

    "Pamięć:",

    PLIK_PAMIEC

)



print(

    "Ocena:",

    PLIK_OCENA

)



print(

    "Predykcje:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    )

)



print(

    "Historia:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    )

)
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = (
    r"modele_dataBase_futbol_trend"
    r"\siec_10_ratio_koniec"
)


NAZWA_BAZY = "dataBase_futbol_trend"


NAZWA_MODELU = os.path.basename(
    KATALOG_MODELU
)



# =====================================================
# LABORATORIUM
# =====================================================


KATALOG_LABORATORIUM = os.path.join(
    "laboratorium",
    NAZWA_BAZY,
    NAZWA_MODELU
)



os.makedirs(
    KATALOG_LABORATORIUM,
    exist_ok=True
)



# =====================================================
# PLIKI WEJŚCIOWE
# =====================================================


PLIK_KLASY = os.path.join(
    KATALOG_MODELU,
    "klasy.json"
)



PLIK_PRED_WYNIK = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_z_wynikiem.csv"
)



PLIK_PRED_GRUPY = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_grupy.csv"
)



PLIK_OCENA = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "ocena.json"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "pamiec_obserwacji.json"
)




# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(
    PLIK_KLASY,
    encoding="utf-8"
) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v):k

    for k,v in klasy.items()

}



print(
    "Załadowano klas:",
    len(ID_NA_WYNIK)
)



# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


df_historia = pd.read_csv(

    PLIK_PRED_WYNIK,

    sep=";",

    encoding="utf-8"

)



print(
    "Historia:",
    len(df_historia)
)



# =====================================================
# WCZYTANIE AKTUALNYCH PREDYKCJI
# =====================================================


df_predykcja = pd.read_csv(

    PLIK_PRED_GRUPY,

    sep=";",

    encoding="utf-8"

)



print(
    "Aktualne predykcje:",
    len(df_predykcja)
)



# =====================================================
# WCZYTANIE OCENY MODELU
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:

        ocena_modelu = json.load(f)


else:


    ocena_modelu = {}




# =====================================================
# WCZYTANIE PAMIĘCI OBSERWACJI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:

        pamiec_obserwacji = json.load(f)


else:


    pamiec_obserwacji = {}




print(
    "Pamięć obserwacji:",
    len(pamiec_obserwacji)
)




# =====================================================
# ANALIZA KLAS
# =====================================================


analiza_klas = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    ilosc = len(dane)



    if ilosc == 0:


        analiza_klas[str(id_grupy)] = {


            "wynik":

            wynik,


            "ilosc_predykcji":

            0,


            "trafienia":

            0,


            "skutecznosc":

            0,


            "rzeczywisty_rozkład":

            {}

        }


        continue




    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()




    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )




    analiza_klas[str(id_grupy)] = {


        "wynik":

        wynik,


        "ilosc_predykcji":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        ),



        "rzeczywisty_rozkład":

        rozklad

    }




# =====================================================
# ANALIZA PEWNOŚCI DYNAMICZNA
# =====================================================


analiza_pewnosci = {}




df_historia = df_historia.sort_values(
    "pewnosc"
)




# 10 równych grup według ilości danych

df_historia["koszyk_pewnosci"] = pd.qcut(

    df_historia["pewnosc"],

    q=10,

    duplicates="drop"

)




for koszyk, dane in df_historia.groupby(

    "koszyk_pewnosci",

    observed=True

):


    ilosc = len(dane)



    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()



    analiza_pewnosci[str(koszyk)] = {


        "ilosc":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        )

    }




# =====================================================
# ANALIZA PEWNOŚCI DLA KAŻDEJ KLASY
# =====================================================


analiza_pewnosci_klasy = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane_klasy = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    if len(dane_klasy) == 0:

        continue




    dane_klasy = dane_klasy.copy()



    dane_klasy["koszyk"] = pd.qcut(

        dane_klasy["pewnosc"],

        q=10,

        duplicates="drop"

    )



    koszyki = {}



    for koszyk,dane in dane_klasy.groupby(

        "koszyk",

        observed=True

    ):



        ilosc = len(dane)



        trafienia = (

            dane["wynik_predykcji"]

            ==

            dane["wynik_rzeczywisty"]

        ).sum()



        koszyki[str(koszyk)] = {


            "ilosc":

            int(ilosc),


            "trafienia":

            int(trafienia),


            "skutecznosc":

            float(

                trafienia / ilosc

            )

        }




    analiza_pewnosci_klasy[str(id_grupy)] = {


        "wynik":

        wynik,


        "progi_pewnosci":

        koszyki

    }




# KONIEC FRAGMENTU 1/2
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 2/2
# =====================================================


# =====================================================
# ANALIZA ODCHYLEŃ
# (CO SIEĆ TYPOWAŁA VS CO FAKTYCZNIE WYPADŁO)
# =====================================================


analiza_odchylen = {}



for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]


    if len(dane) == 0:

        continue



    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )



    uporzadkowane = sorted(

        rozklad.items(),

        key=lambda x:x[1],

        reverse=True

    )



    analiza_odchylen[str(id_grupy)] = {


        "wynik_typowany":

        wynik,


        "ilosc":

        int(len(dane)),


        "najczestsze_wyniki_rzeczywiste":

        dict(uporzadkowane[:10]),


        "czy_odwrócony_wzorzec":

        (
            uporzadkowane[0][0] != wynik
            if len(uporzadkowane)>0
            else False
        )

    }




# =====================================================
# ANALIZA PAMIĘCI OBSERWACJI
# =====================================================


analiza_pamieci = {


    "ilosc_meczow":

    len(pamiec_obserwacji),


    "zmiany_predykcji":0,


    "pierwsze_obserwacje":0

}



for mecz, obserwacje in pamiec_obserwacji.items():


    for obs in obserwacje:


        if obs.get(
            "pierwsza_obserwacja"
        ):

            analiza_pamieci[
                "pierwsze_obserwacje"
            ] += 1



        if obs.get(
            "zmiana_predykcji"
        ):

            analiza_pamieci[
                "zmiany_predykcji"
            ] += 1




# =====================================================
# ANALIZA AKTUALNYCH PREDYKCJI
# =====================================================


analiza_przyszlych = []



for _,mecz in df_predykcja.iterrows():


    id_grupy = int(
        mecz["id_grupy"]
    )


    wynik = str(
        mecz["wynik_predykcji"]
    )


    pewnosc = float(
        mecz["pewnosc"]
    )



    wiedza = analiza_klas.get(

        str(id_grupy),

        {}

    )



    pewnosc_klasy = analiza_pewnosci_klasy.get(

        str(id_grupy),

        {}

    )



    odchylenie = analiza_odchylen.get(

        str(id_grupy),

        {}

    )


    analiza_przyszlych.append(


        {


            "id_meczu":

            mecz["id_meczu"],



            "id_grupy":

            id_grupy,



            "wynik_predykcji":

            wynik,



            "pewnosc":

            pewnosc,



            "historyczna_skutecznosc_klasy":

            wiedza.get(

                "skutecznosc",

                0

            ),



            "najczestszy_realny_wynik":

            (
                max(

                    wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ),

                    key=wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ).get

                )

                if wiedza.get(

                    "rzeczywisty_rozkład"

                )

                else None
            ),



            "czy_odwrócony_wzorzec":

            odchylenie.get(

                "czy_odwrócony_wzorzec",

                False

            )

        }

    )




df_analiza_predykcji = pd.DataFrame(

    analiza_przyszlych

)



df_analiza_predykcji.to_csv(


    os.path.join(

        KATALOG_LABORATORIUM,

        "analiza_przyszlych_predykcji.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)




# =====================================================
# KOLEKTOR WIEDZY
# =====================================================


kolektor_wiedzy = {


    "model":

    NAZWA_MODELU,



    "data":

    datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    ),



    "ocena_modelu":

    ocena_modelu,



    "analiza_klas":

    analiza_klas,



    "analiza_pewnosci":

    analiza_pewnosci,



    "analiza_pewnosci_klasy":

    analiza_pewnosci_klasy,



    "analiza_odchylen":

    analiza_odchylen,



    "analiza_pamieci":

    analiza_pamieci

}




# =====================================================
# ZAPIS JSON
# =====================================================


pliki_json = {


    "analiza_klas.json":

    analiza_klas,


    "analiza_pewnosci.json":

    analiza_pewnosci,


    "analiza_pewnosci_klasy.json":

    analiza_pewnosci_klasy,


    "analiza_odchylen.json":

    analiza_odchylen,


    "analiza_pamieci.json":

    analiza_pamieci,


    "kolektor_wiedzy.json":

    kolektor_wiedzy

}




for nazwa,dane in pliki_json.items():


    with open(

        os.path.join(

            KATALOG_LABORATORIUM,

            nazwa

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            dane,

            f,

            indent=4,

            ensure_ascii=False

        )




# =====================================================
# RAPORT KOŃCOWY
# =====================================================


print()
print("======================================")
print("LABORATORIUM V2 ZAKOŃCZONE")
print("======================================")


print(
    "Model:",
    NAZWA_MODELU
)


print(
    "Katalog:",
    KATALOG_LABORATORIUM
)


print(
    "Analizowane mecze:",
    len(df_historia)
)


print(
    "Przyszłe predykcje:",
    len(df_predykcja)
)


print(
    "Pamięć:",
    len(pamiec_obserwacji)
)


print()
print("Utworzono:")

for plik in pliki_json:

    print(
        "-",
        plik
    )


print(
    "- analiza_przyszlych_predykcji.csv"
)

print()
print("======================================")






# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime

from tensorflow.keras.models import load_model



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_11_statystyka"


PLIK_PREDYKCJI = r"dane\dataBase_futbol_trend.csv"


PLIK_HISTORIA = r"dane\kod_dataBase_futbol_trend.csv"



KATALOG_OBSERWACJI = os.path.join(
    KATALOG_MODELU,
    "obserwacja"
)


KATALOG_PREDYKCJI = os.path.join(
    KATALOG_MODELU,
    "predykcje"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_OBSERWACJI,
    "pamiec_obserwacji.json"
)



PLIK_OCENA = os.path.join(
    KATALOG_OBSERWACJI,
    "ocena.json"
)



os.makedirs(
    KATALOG_OBSERWACJI,
    exist_ok=True
)



os.makedirs(
    KATALOG_PREDYKCJI,
    exist_ok=True
)





# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "metadata.json"
    ),

    encoding="utf-8"

) as f:

    metadata = json.load(f)



CECHY = metadata["cechy"]


NAZWA_MODELU = metadata["nazwa"]





# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "klasy.json"
    ),

    encoding="utf-8"

) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v): k

    for k,v in klasy.items()

}





# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================


df_pred = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



INDEX_MAP = {


    kolumna:index

    for index,kolumna

    in enumerate(df_pred.columns)

}



print("MAPA CECH")

print(INDEX_MAP)





# =====================================================
# CECHY MODELU
# =====================================================


INDEX_CECH = []



for cecha in CECHY:


    if cecha not in INDEX_MAP:


        raise Exception(

            f"Brak cechy modelu: {cecha}"

        )


    INDEX_CECH.append(

        INDEX_MAP[cecha]

    )



print(

    "Cechy modelu:",

    INDEX_CECH

)





# =====================================================
# AKTUALNE MECZE DO PREDYKCJI
# =====================================================


NAZWY_PREDYKCJI = (

    df_pred["id_meczu"]

    .astype(str)

    .tolist()

)



X_PREDYKCJA = df_pred.iloc[

    :,

    INDEX_CECH

]



X_PREDYKCJA = np.nan_to_num(

    X_PREDYKCJA.values

)





# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


hist = pd.read_csv(

    PLIK_HISTORIA,

    sep=";",

    header=None,

    encoding="utf-8"

)



NAZWY_HISTORIA = hist.iloc[:,0].astype(str)



X_HISTORIA = hist.iloc[

    :,

    INDEX_CECH

]



Y_HISTORIA = hist.iloc[:,-1]



X_HISTORIA = np.nan_to_num(

    X_HISTORIA.values

)





# =====================================================
# WCZYTANIE MODELU
# =====================================================


model = load_model(

    os.path.join(

        KATALOG_MODELU,

        "model.h5"

    )

)





# =====================================================
# PREDYKCJA HISTORII
# =====================================================


print(
    "Analiza historii..."
)



pred_hist = model.predict(

    X_HISTORIA

)



klasy_pred_hist = np.argmax(

    pred_hist,

    axis=1

)





# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================


print(

    "Analiza aktualnych meczów..."

)



pred = model.predict(

    X_PREDYKCJA

)



klasy_pred = np.argmax(

    pred,

    axis=1

)





# =====================================================
# WCZYTANIE PAMIĘCI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:


        pamiec_obserwacji = json.load(f)



else:


    pamiec_obserwacji = {}





# =====================================================
# WCZYTANIE OCENY
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:


        ocena = json.load(f)



else:


    ocena = {


        "model":

        NAZWA_MODELU,


        "ocena_ogolna":

        {

            "ilosc":

            0,


            "trafienia":

            0

        },


        "ocena_wynikow":

        {}

    }





# =====================================================
# STRUKTURY SESJI
# =====================================================


czas = datetime.now().strftime(

    "%Y-%m-%d %H:%M:%S"

)



nowe_obserwacje = []


nowe_predykcje = []


nowa_historia = []




analiza = {}



for wynik in klasy.keys():


    analiza[wynik] = {


        "ilosc_wystapien":0,


        "trafienia":0,


        "bledy":{}

    }




print(

    "Przygotowano dane."

)
# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 2/2
# =====================================================



# =====================================================
# ANALIZA HISTORII Z WYNIKAMI
# =====================================================


for i,p in enumerate(klasy_pred_hist):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    real_wynik = str(
        Y_HISTORIA.iloc[i]
    )


    nazwa_meczu = str(
        NAZWY_HISTORIA.iloc[i]
    )


    pewnosc = float(
        np.max(pred_hist[i])
    )


    trafienie = (
        pred_wynik == real_wynik
    )



    obserwacja = {


        "data":

        czas,


        "model":

        NAZWA_MODELU,


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "predykcja":

        pred_wynik,


        "wynik_rzeczywisty":

        real_wynik,


        "pewnosc":

        pewnosc,


        "trafienie":

        trafienie

    }





    # =========================================
    # AKTUALIZACJA PAMIĘCI MECZU
    # =========================================


    if nazwa_meczu not in pamiec_obserwacji:


        pamiec_obserwacji[nazwa_meczu] = []



        obserwacja["pierwsza_obserwacja"] = True



    else:


        ostatnia = pamiec_obserwacji[nazwa_meczu][-1]



        if ostatnia["predykcja"] != pred_wynik:


            obserwacja["zmiana_predykcji"] = {


                "stara":

                ostatnia["predykcja"],


                "nowa":

                pred_wynik

            }



        if ostatnia["pewnosc"] != pewnosc:


            obserwacja["zmiana_pewnosci"] = {


                "stara":

                ostatnia["pewnosc"],


                "nowa":

                pewnosc

            }





    pamiec_obserwacji[nazwa_meczu].append(

        obserwacja

    )



    nowe_obserwacje.append(

        obserwacja

    )





    # statystyka klasy


    analiza[pred_wynik]["ilosc_wystapien"] += 1



    if trafienie:


        analiza[pred_wynik]["trafienia"] += 1


    else:


        if real_wynik not in analiza[pred_wynik]["bledy"]:


            analiza[pred_wynik]["bledy"][real_wynik] = 0



        analiza[pred_wynik]["bledy"][real_wynik] += 1







# =====================================================
# AKTUALNE MECZE BEZ WYNIKU
# =====================================================


for i,p in enumerate(klasy_pred):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    nazwa_meczu = str(

        NAZWY_PREDYKCJI[i]

    )


    pewnosc = float(

        np.max(pred[i])

    )



    predykcja = {


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "wynik_predykcji":

        pred_wynik,


        "pewnosc":

        pewnosc

    }



    nowe_predykcje.append(

        predykcja

    )







# =====================================================
# AKTUALIZACJA OCENY MODELU
# =====================================================


ilosc_globalna = 0

trafienia_globalne = 0



ocena_wynikow = {}



for wynik,dane in analiza.items():


    ilosc = dane["ilosc_wystapien"]


    trafienia = dane["trafienia"]



    ilosc_globalna += ilosc


    trafienia_globalne += trafienia



    ocena_wynikow[wynik] = {


        "ilosc_predykcji":

        ilosc,


        "trafienia":

        trafienia,


        "skutecznosc":

        (

            trafienia / ilosc

            if ilosc > 0

            else 0

        ),


        "bledy":

        dane["bledy"]

    }





ocena = {


    "model":

    NAZWA_MODELU,


    "data":

    czas,


    "ocena_ogolna":{


        "ilosc_meczow":

        ilosc_globalna,


        "trafienia":

        trafienia_globalne,


        "skutecznosc":

        (

            trafienia_globalne /

            ilosc_globalna

            if ilosc_globalna > 0

            else 0

        )

    },


    "ocena_wynikow":

    ocena_wynikow

}







# =====================================================
# ZAPIS PAMIĘCI
# =====================================================


with open(

    PLIK_PAMIEC,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        pamiec_obserwacji,

        f,

        indent=4,

        ensure_ascii=False

    )





# =====================================================
# ZAPIS OCENY
# =====================================================


with open(

    PLIK_OCENA,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        ocena,

        f,

        indent=4,

        ensure_ascii=False

    )







# =====================================================
# ZAPIS AKTUALNEJ PREDYKCJI
# =====================================================


pd.DataFrame(

    nowe_predykcje

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







# =====================================================
# ZAPIS HISTORII Z WYNIKAMI
# =====================================================


historia_csv = []



for mecz,lista in pamiec_obserwacji.items():


    ostatnia = lista[-1]


    historia_csv.append(


        {


            "id_meczu":

            mecz,


            "id_grupy":

            ostatnia["id_grupy"],


            "wynik_predykcji":

            ostatnia["predykcja"],


            "pewnosc":

            ostatnia["pewnosc"],


            "wynik_rzeczywisty":

            ostatnia["wynik_rzeczywisty"]

        }

    )







pd.DataFrame(

    historia_csv

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







print()

print("================================")

print("ZAKOŃCZONO")

print("================================")



print(

    "Pamięć:",

    PLIK_PAMIEC

)



print(

    "Ocena:",

    PLIK_OCENA

)



print(

    "Predykcje:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    )

)



print(

    "Historia:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    )

)
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = (
    r"modele_dataBase_futbol_trend"
    r"\siec_11_statystyka"
)


NAZWA_BAZY = "dataBase_futbol_trend"


NAZWA_MODELU = os.path.basename(
    KATALOG_MODELU
)



# =====================================================
# LABORATORIUM
# =====================================================


KATALOG_LABORATORIUM = os.path.join(
    "laboratorium",
    NAZWA_BAZY,
    NAZWA_MODELU
)



os.makedirs(
    KATALOG_LABORATORIUM,
    exist_ok=True
)



# =====================================================
# PLIKI WEJŚCIOWE
# =====================================================


PLIK_KLASY = os.path.join(
    KATALOG_MODELU,
    "klasy.json"
)



PLIK_PRED_WYNIK = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_z_wynikiem.csv"
)



PLIK_PRED_GRUPY = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_grupy.csv"
)



PLIK_OCENA = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "ocena.json"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "pamiec_obserwacji.json"
)




# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(
    PLIK_KLASY,
    encoding="utf-8"
) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v):k

    for k,v in klasy.items()

}



print(
    "Załadowano klas:",
    len(ID_NA_WYNIK)
)



# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


df_historia = pd.read_csv(

    PLIK_PRED_WYNIK,

    sep=";",

    encoding="utf-8"

)



print(
    "Historia:",
    len(df_historia)
)



# =====================================================
# WCZYTANIE AKTUALNYCH PREDYKCJI
# =====================================================


df_predykcja = pd.read_csv(

    PLIK_PRED_GRUPY,

    sep=";",

    encoding="utf-8"

)



print(
    "Aktualne predykcje:",
    len(df_predykcja)
)



# =====================================================
# WCZYTANIE OCENY MODELU
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:

        ocena_modelu = json.load(f)


else:


    ocena_modelu = {}




# =====================================================
# WCZYTANIE PAMIĘCI OBSERWACJI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:

        pamiec_obserwacji = json.load(f)


else:


    pamiec_obserwacji = {}




print(
    "Pamięć obserwacji:",
    len(pamiec_obserwacji)
)




# =====================================================
# ANALIZA KLAS
# =====================================================


analiza_klas = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    ilosc = len(dane)



    if ilosc == 0:


        analiza_klas[str(id_grupy)] = {


            "wynik":

            wynik,


            "ilosc_predykcji":

            0,


            "trafienia":

            0,


            "skutecznosc":

            0,


            "rzeczywisty_rozkład":

            {}

        }


        continue




    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()




    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )




    analiza_klas[str(id_grupy)] = {


        "wynik":

        wynik,


        "ilosc_predykcji":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        ),



        "rzeczywisty_rozkład":

        rozklad

    }




# =====================================================
# ANALIZA PEWNOŚCI DYNAMICZNA
# =====================================================


analiza_pewnosci = {}




df_historia = df_historia.sort_values(
    "pewnosc"
)




# 10 równych grup według ilości danych

df_historia["koszyk_pewnosci"] = pd.qcut(

    df_historia["pewnosc"],

    q=10,

    duplicates="drop"

)




for koszyk, dane in df_historia.groupby(

    "koszyk_pewnosci",

    observed=True

):


    ilosc = len(dane)



    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()



    analiza_pewnosci[str(koszyk)] = {


        "ilosc":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        )

    }




# =====================================================
# ANALIZA PEWNOŚCI DLA KAŻDEJ KLASY
# =====================================================


analiza_pewnosci_klasy = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane_klasy = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    if len(dane_klasy) == 0:

        continue




    dane_klasy = dane_klasy.copy()



    dane_klasy["koszyk"] = pd.qcut(

        dane_klasy["pewnosc"],

        q=10,

        duplicates="drop"

    )



    koszyki = {}



    for koszyk,dane in dane_klasy.groupby(

        "koszyk",

        observed=True

    ):



        ilosc = len(dane)



        trafienia = (

            dane["wynik_predykcji"]

            ==

            dane["wynik_rzeczywisty"]

        ).sum()



        koszyki[str(koszyk)] = {


            "ilosc":

            int(ilosc),


            "trafienia":

            int(trafienia),


            "skutecznosc":

            float(

                trafienia / ilosc

            )

        }




    analiza_pewnosci_klasy[str(id_grupy)] = {


        "wynik":

        wynik,


        "progi_pewnosci":

        koszyki

    }




# KONIEC FRAGMENTU 1/2
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 2/2
# =====================================================


# =====================================================
# ANALIZA ODCHYLEŃ
# (CO SIEĆ TYPOWAŁA VS CO FAKTYCZNIE WYPADŁO)
# =====================================================


analiza_odchylen = {}



for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]


    if len(dane) == 0:

        continue



    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )



    uporzadkowane = sorted(

        rozklad.items(),

        key=lambda x:x[1],

        reverse=True

    )



    analiza_odchylen[str(id_grupy)] = {


        "wynik_typowany":

        wynik,


        "ilosc":

        int(len(dane)),


        "najczestsze_wyniki_rzeczywiste":

        dict(uporzadkowane[:10]),


        "czy_odwrócony_wzorzec":

        (
            uporzadkowane[0][0] != wynik
            if len(uporzadkowane)>0
            else False
        )

    }




# =====================================================
# ANALIZA PAMIĘCI OBSERWACJI
# =====================================================


analiza_pamieci = {


    "ilosc_meczow":

    len(pamiec_obserwacji),


    "zmiany_predykcji":0,


    "pierwsze_obserwacje":0

}



for mecz, obserwacje in pamiec_obserwacji.items():


    for obs in obserwacje:


        if obs.get(
            "pierwsza_obserwacja"
        ):

            analiza_pamieci[
                "pierwsze_obserwacje"
            ] += 1



        if obs.get(
            "zmiana_predykcji"
        ):

            analiza_pamieci[
                "zmiany_predykcji"
            ] += 1




# =====================================================
# ANALIZA AKTUALNYCH PREDYKCJI
# =====================================================


analiza_przyszlych = []



for _,mecz in df_predykcja.iterrows():


    id_grupy = int(
        mecz["id_grupy"]
    )


    wynik = str(
        mecz["wynik_predykcji"]
    )


    pewnosc = float(
        mecz["pewnosc"]
    )



    wiedza = analiza_klas.get(

        str(id_grupy),

        {}

    )



    pewnosc_klasy = analiza_pewnosci_klasy.get(

        str(id_grupy),

        {}

    )



    odchylenie = analiza_odchylen.get(

        str(id_grupy),

        {}

    )


    analiza_przyszlych.append(


        {


            "id_meczu":

            mecz["id_meczu"],



            "id_grupy":

            id_grupy,



            "wynik_predykcji":

            wynik,



            "pewnosc":

            pewnosc,



            "historyczna_skutecznosc_klasy":

            wiedza.get(

                "skutecznosc",

                0

            ),



            "najczestszy_realny_wynik":

            (
                max(

                    wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ),

                    key=wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ).get

                )

                if wiedza.get(

                    "rzeczywisty_rozkład"

                )

                else None
            ),



            "czy_odwrócony_wzorzec":

            odchylenie.get(

                "czy_odwrócony_wzorzec",

                False

            )

        }

    )




df_analiza_predykcji = pd.DataFrame(

    analiza_przyszlych

)



df_analiza_predykcji.to_csv(


    os.path.join(

        KATALOG_LABORATORIUM,

        "analiza_przyszlych_predykcji.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)




# =====================================================
# KOLEKTOR WIEDZY
# =====================================================


kolektor_wiedzy = {


    "model":

    NAZWA_MODELU,



    "data":

    datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    ),



    "ocena_modelu":

    ocena_modelu,



    "analiza_klas":

    analiza_klas,



    "analiza_pewnosci":

    analiza_pewnosci,



    "analiza_pewnosci_klasy":

    analiza_pewnosci_klasy,



    "analiza_odchylen":

    analiza_odchylen,



    "analiza_pamieci":

    analiza_pamieci

}




# =====================================================
# ZAPIS JSON
# =====================================================


pliki_json = {


    "analiza_klas.json":

    analiza_klas,


    "analiza_pewnosci.json":

    analiza_pewnosci,


    "analiza_pewnosci_klasy.json":

    analiza_pewnosci_klasy,


    "analiza_odchylen.json":

    analiza_odchylen,


    "analiza_pamieci.json":

    analiza_pamieci,


    "kolektor_wiedzy.json":

    kolektor_wiedzy

}




for nazwa,dane in pliki_json.items():


    with open(

        os.path.join(

            KATALOG_LABORATORIUM,

            nazwa

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            dane,

            f,

            indent=4,

            ensure_ascii=False

        )




# =====================================================
# RAPORT KOŃCOWY
# =====================================================


print()
print("======================================")
print("LABORATORIUM V2 ZAKOŃCZONE")
print("======================================")


print(
    "Model:",
    NAZWA_MODELU
)


print(
    "Katalog:",
    KATALOG_LABORATORIUM
)


print(
    "Analizowane mecze:",
    len(df_historia)
)


print(
    "Przyszłe predykcje:",
    len(df_predykcja)
)


print(
    "Pamięć:",
    len(pamiec_obserwacji)
)


print()
print("Utworzono:")

for plik in pliki_json:

    print(
        "-",
        plik
    )


print(
    "- analiza_przyszlych_predykcji.csv"
)

print()
print("======================================")




































# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime

from tensorflow.keras.models import load_model



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = r"modele_kursy_przygotowane\siec_01_start_kursow"


PLIK_PREDYKCJI = r"dane\kursy_przygotowane.csv"


PLIK_HISTORIA = r"dane\mozg_kursy_przygotowane.csv"



KATALOG_OBSERWACJI = os.path.join(
    KATALOG_MODELU,
    "obserwacja"
)


KATALOG_PREDYKCJI = os.path.join(
    KATALOG_MODELU,
    "predykcje"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_OBSERWACJI,
    "pamiec_obserwacji.json"
)



PLIK_OCENA = os.path.join(
    KATALOG_OBSERWACJI,
    "ocena.json"
)



os.makedirs(
    KATALOG_OBSERWACJI,
    exist_ok=True
)



os.makedirs(
    KATALOG_PREDYKCJI,
    exist_ok=True
)





# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "metadata.json"
    ),

    encoding="utf-8"

) as f:

    metadata = json.load(f)



CECHY = metadata["cechy"]


NAZWA_MODELU = metadata["nazwa"]





# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "klasy.json"
    ),

    encoding="utf-8"

) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v): k

    for k,v in klasy.items()

}





# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================


df_pred = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



INDEX_MAP = {


    kolumna:index

    for index,kolumna

    in enumerate(df_pred.columns)

}



print("MAPA CECH")

print(INDEX_MAP)





# =====================================================
# CECHY MODELU
# =====================================================


INDEX_CECH = []



for cecha in CECHY:


    if cecha not in INDEX_MAP:


        raise Exception(

            f"Brak cechy modelu: {cecha}"

        )


    INDEX_CECH.append(

        INDEX_MAP[cecha]

    )



print(

    "Cechy modelu:",

    INDEX_CECH

)





# =====================================================
# AKTUALNE MECZE DO PREDYKCJI
# =====================================================


NAZWY_PREDYKCJI = (

    df_pred["mecz"]

    .astype(str)

    .tolist()

)



X_PREDYKCJA = df_pred.iloc[

    :,

    INDEX_CECH

]



X_PREDYKCJA = np.nan_to_num(

    X_PREDYKCJA.values

)





# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


hist = pd.read_csv(

    PLIK_HISTORIA,

    sep=";",

    header=None,

    encoding="utf-8"

)



NAZWY_HISTORIA = hist.iloc[:,0].astype(str)



X_HISTORIA = hist.iloc[

    :,

    INDEX_CECH

]



Y_HISTORIA = hist.iloc[:,-1]



X_HISTORIA = np.nan_to_num(

    X_HISTORIA.values

)





# =====================================================
# WCZYTANIE MODELU
# =====================================================


model = load_model(

    os.path.join(

        KATALOG_MODELU,

        "model.h5"

    )

)





# =====================================================
# PREDYKCJA HISTORII
# =====================================================


print(
    "Analiza historii..."
)



pred_hist = model.predict(

    X_HISTORIA

)



klasy_pred_hist = np.argmax(

    pred_hist,

    axis=1

)





# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================


print(

    "Analiza aktualnych meczów..."

)



pred = model.predict(

    X_PREDYKCJA

)



klasy_pred = np.argmax(

    pred,

    axis=1

)





# =====================================================
# WCZYTANIE PAMIĘCI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:


        pamiec_obserwacji = json.load(f)



else:


    pamiec_obserwacji = {}





# =====================================================
# WCZYTANIE OCENY
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:


        ocena = json.load(f)



else:


    ocena = {


        "model":

        NAZWA_MODELU,


        "ocena_ogolna":

        {

            "ilosc":

            0,


            "trafienia":

            0

        },


        "ocena_wynikow":

        {}

    }





# =====================================================
# STRUKTURY SESJI
# =====================================================


czas = datetime.now().strftime(

    "%Y-%m-%d %H:%M:%S"

)



nowe_obserwacje = []


nowe_predykcje = []


nowa_historia = []




analiza = {}



for wynik in klasy.keys():


    analiza[wynik] = {


        "ilosc_wystapien":0,


        "trafienia":0,


        "bledy":{}

    }




print(

    "Przygotowano dane."

)
# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 2/2
# =====================================================



# =====================================================
# ANALIZA HISTORII Z WYNIKAMI
# =====================================================


for i,p in enumerate(klasy_pred_hist):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    real_wynik = str(
        Y_HISTORIA.iloc[i]
    )


    nazwa_meczu = str(
        NAZWY_HISTORIA.iloc[i]
    )


    pewnosc = float(
        np.max(pred_hist[i])
    )


    trafienie = (
        pred_wynik == real_wynik
    )



    obserwacja = {


        "data":

        czas,


        "model":

        NAZWA_MODELU,


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "predykcja":

        pred_wynik,


        "wynik_rzeczywisty":

        real_wynik,


        "pewnosc":

        pewnosc,


        "trafienie":

        trafienie

    }





    # =========================================
    # AKTUALIZACJA PAMIĘCI MECZU
    # =========================================


    if nazwa_meczu not in pamiec_obserwacji:


        pamiec_obserwacji[nazwa_meczu] = []



        obserwacja["pierwsza_obserwacja"] = True



    else:


        ostatnia = pamiec_obserwacji[nazwa_meczu][-1]



        if ostatnia["predykcja"] != pred_wynik:


            obserwacja["zmiana_predykcji"] = {


                "stara":

                ostatnia["predykcja"],


                "nowa":

                pred_wynik

            }



        if ostatnia["pewnosc"] != pewnosc:


            obserwacja["zmiana_pewnosci"] = {


                "stara":

                ostatnia["pewnosc"],


                "nowa":

                pewnosc

            }





    pamiec_obserwacji[nazwa_meczu].append(

        obserwacja

    )



    nowe_obserwacje.append(

        obserwacja

    )





    # statystyka klasy


    analiza[pred_wynik]["ilosc_wystapien"] += 1



    if trafienie:


        analiza[pred_wynik]["trafienia"] += 1


    else:


        if real_wynik not in analiza[pred_wynik]["bledy"]:


            analiza[pred_wynik]["bledy"][real_wynik] = 0



        analiza[pred_wynik]["bledy"][real_wynik] += 1







# =====================================================
# AKTUALNE MECZE BEZ WYNIKU
# =====================================================


for i,p in enumerate(klasy_pred):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    nazwa_meczu = str(

        NAZWY_PREDYKCJI[i]

    )


    pewnosc = float(

        np.max(pred[i])

    )



    predykcja = {


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "wynik_predykcji":

        pred_wynik,


        "pewnosc":

        pewnosc

    }



    nowe_predykcje.append(

        predykcja

    )







# =====================================================
# AKTUALIZACJA OCENY MODELU
# =====================================================


ilosc_globalna = 0

trafienia_globalne = 0



ocena_wynikow = {}



for wynik,dane in analiza.items():


    ilosc = dane["ilosc_wystapien"]


    trafienia = dane["trafienia"]



    ilosc_globalna += ilosc


    trafienia_globalne += trafienia



    ocena_wynikow[wynik] = {


        "ilosc_predykcji":

        ilosc,


        "trafienia":

        trafienia,


        "skutecznosc":

        (

            trafienia / ilosc

            if ilosc > 0

            else 0

        ),


        "bledy":

        dane["bledy"]

    }





ocena = {


    "model":

    NAZWA_MODELU,


    "data":

    czas,


    "ocena_ogolna":{


        "ilosc_meczow":

        ilosc_globalna,


        "trafienia":

        trafienia_globalne,


        "skutecznosc":

        (

            trafienia_globalne /

            ilosc_globalna

            if ilosc_globalna > 0

            else 0

        )

    },


    "ocena_wynikow":

    ocena_wynikow

}







# =====================================================
# ZAPIS PAMIĘCI
# =====================================================


with open(

    PLIK_PAMIEC,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        pamiec_obserwacji,

        f,

        indent=4,

        ensure_ascii=False

    )





# =====================================================
# ZAPIS OCENY
# =====================================================


with open(

    PLIK_OCENA,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        ocena,

        f,

        indent=4,

        ensure_ascii=False

    )







# =====================================================
# ZAPIS AKTUALNEJ PREDYKCJI
# =====================================================


pd.DataFrame(

    nowe_predykcje

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







# =====================================================
# ZAPIS HISTORII Z WYNIKAMI
# =====================================================


historia_csv = []



for mecz,lista in pamiec_obserwacji.items():


    ostatnia = lista[-1]


    historia_csv.append(


        {


            "id_meczu":

            mecz,


            "id_grupy":

            ostatnia["id_grupy"],


            "wynik_predykcji":

            ostatnia["predykcja"],


            "pewnosc":

            ostatnia["pewnosc"],


            "wynik_rzeczywisty":

            ostatnia["wynik_rzeczywisty"]

        }

    )







pd.DataFrame(

    historia_csv

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







print()

print("================================")

print("ZAKOŃCZONO")

print("================================")



print(

    "Pamięć:",

    PLIK_PAMIEC

)



print(

    "Ocena:",

    PLIK_OCENA

)



print(

    "Predykcje:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    )

)



print(

    "Historia:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    )

)
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = (
    r"modele_kursy_przygotowane"
    r"\siec_01_start_kursow"
)


NAZWA_BAZY = "kursy_przygotowane"


NAZWA_MODELU = os.path.basename(
    KATALOG_MODELU
)



# =====================================================
# LABORATORIUM
# =====================================================


KATALOG_LABORATORIUM = os.path.join(
    "laboratorium",
    NAZWA_BAZY,
    NAZWA_MODELU
)



os.makedirs(
    KATALOG_LABORATORIUM,
    exist_ok=True
)



# =====================================================
# PLIKI WEJŚCIOWE
# =====================================================


PLIK_KLASY = os.path.join(
    KATALOG_MODELU,
    "klasy.json"
)



PLIK_PRED_WYNIK = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_z_wynikiem.csv"
)



PLIK_PRED_GRUPY = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_grupy.csv"
)



PLIK_OCENA = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "ocena.json"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "pamiec_obserwacji.json"
)




# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(
    PLIK_KLASY,
    encoding="utf-8"
) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v):k

    for k,v in klasy.items()

}



print(
    "Załadowano klas:",
    len(ID_NA_WYNIK)
)



# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


df_historia = pd.read_csv(

    PLIK_PRED_WYNIK,

    sep=";",

    encoding="utf-8"

)



print(
    "Historia:",
    len(df_historia)
)



# =====================================================
# WCZYTANIE AKTUALNYCH PREDYKCJI
# =====================================================


df_predykcja = pd.read_csv(

    PLIK_PRED_GRUPY,

    sep=";",

    encoding="utf-8"

)



print(
    "Aktualne predykcje:",
    len(df_predykcja)
)



# =====================================================
# WCZYTANIE OCENY MODELU
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:

        ocena_modelu = json.load(f)


else:


    ocena_modelu = {}




# =====================================================
# WCZYTANIE PAMIĘCI OBSERWACJI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:

        pamiec_obserwacji = json.load(f)


else:


    pamiec_obserwacji = {}




print(
    "Pamięć obserwacji:",
    len(pamiec_obserwacji)
)




# =====================================================
# ANALIZA KLAS
# =====================================================


analiza_klas = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    ilosc = len(dane)



    if ilosc == 0:


        analiza_klas[str(id_grupy)] = {


            "wynik":

            wynik,


            "ilosc_predykcji":

            0,


            "trafienia":

            0,


            "skutecznosc":

            0,


            "rzeczywisty_rozkład":

            {}

        }


        continue




    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()




    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )




    analiza_klas[str(id_grupy)] = {


        "wynik":

        wynik,


        "ilosc_predykcji":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        ),



        "rzeczywisty_rozkład":

        rozklad

    }




# =====================================================
# ANALIZA PEWNOŚCI DYNAMICZNA
# =====================================================


analiza_pewnosci = {}




df_historia = df_historia.sort_values(
    "pewnosc"
)




# 10 równych grup według ilości danych

df_historia["koszyk_pewnosci"] = pd.qcut(

    df_historia["pewnosc"],

    q=10,

    duplicates="drop"

)




for koszyk, dane in df_historia.groupby(

    "koszyk_pewnosci",

    observed=True

):


    ilosc = len(dane)



    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()



    analiza_pewnosci[str(koszyk)] = {


        "ilosc":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        )

    }




# =====================================================
# ANALIZA PEWNOŚCI DLA KAŻDEJ KLASY
# =====================================================


analiza_pewnosci_klasy = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane_klasy = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    if len(dane_klasy) == 0:

        continue




    dane_klasy = dane_klasy.copy()



    dane_klasy["koszyk"] = pd.qcut(

        dane_klasy["pewnosc"],

        q=10,

        duplicates="drop"

    )



    koszyki = {}



    for koszyk,dane in dane_klasy.groupby(

        "koszyk",

        observed=True

    ):



        ilosc = len(dane)



        trafienia = (

            dane["wynik_predykcji"]

            ==

            dane["wynik_rzeczywisty"]

        ).sum()



        koszyki[str(koszyk)] = {


            "ilosc":

            int(ilosc),


            "trafienia":

            int(trafienia),


            "skutecznosc":

            float(

                trafienia / ilosc

            )

        }




    analiza_pewnosci_klasy[str(id_grupy)] = {


        "wynik":

        wynik,


        "progi_pewnosci":

        koszyki

    }




# KONIEC FRAGMENTU 1/2
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 2/2
# =====================================================


# =====================================================
# ANALIZA ODCHYLEŃ
# (CO SIEĆ TYPOWAŁA VS CO FAKTYCZNIE WYPADŁO)
# =====================================================


analiza_odchylen = {}



for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]


    if len(dane) == 0:

        continue



    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )



    uporzadkowane = sorted(

        rozklad.items(),

        key=lambda x:x[1],

        reverse=True

    )



    analiza_odchylen[str(id_grupy)] = {


        "wynik_typowany":

        wynik,


        "ilosc":

        int(len(dane)),


        "najczestsze_wyniki_rzeczywiste":

        dict(uporzadkowane[:10]),


        "czy_odwrócony_wzorzec":

        (
            uporzadkowane[0][0] != wynik
            if len(uporzadkowane)>0
            else False
        )

    }




# =====================================================
# ANALIZA PAMIĘCI OBSERWACJI
# =====================================================


analiza_pamieci = {


    "ilosc_meczow":

    len(pamiec_obserwacji),


    "zmiany_predykcji":0,


    "pierwsze_obserwacje":0

}



for mecz, obserwacje in pamiec_obserwacji.items():


    for obs in obserwacje:


        if obs.get(
            "pierwsza_obserwacja"
        ):

            analiza_pamieci[
                "pierwsze_obserwacje"
            ] += 1



        if obs.get(
            "zmiana_predykcji"
        ):

            analiza_pamieci[
                "zmiany_predykcji"
            ] += 1




# =====================================================
# ANALIZA AKTUALNYCH PREDYKCJI
# =====================================================


analiza_przyszlych = []



for _,mecz in df_predykcja.iterrows():


    id_grupy = int(
        mecz["id_grupy"]
    )


    wynik = str(
        mecz["wynik_predykcji"]
    )


    pewnosc = float(
        mecz["pewnosc"]
    )



    wiedza = analiza_klas.get(

        str(id_grupy),

        {}

    )



    pewnosc_klasy = analiza_pewnosci_klasy.get(

        str(id_grupy),

        {}

    )



    odchylenie = analiza_odchylen.get(

        str(id_grupy),

        {}

    )


    analiza_przyszlych.append(


        {


            "id_meczu":

            mecz["id_meczu"],



            "id_grupy":

            id_grupy,



            "wynik_predykcji":

            wynik,



            "pewnosc":

            pewnosc,



            "historyczna_skutecznosc_klasy":

            wiedza.get(

                "skutecznosc",

                0

            ),



            "najczestszy_realny_wynik":

            (
                max(

                    wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ),

                    key=wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ).get

                )

                if wiedza.get(

                    "rzeczywisty_rozkład"

                )

                else None
            ),



            "czy_odwrócony_wzorzec":

            odchylenie.get(

                "czy_odwrócony_wzorzec",

                False

            )

        }

    )




df_analiza_predykcji = pd.DataFrame(

    analiza_przyszlych

)



df_analiza_predykcji.to_csv(


    os.path.join(

        KATALOG_LABORATORIUM,

        "analiza_przyszlych_predykcji.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)




# =====================================================
# KOLEKTOR WIEDZY
# =====================================================


kolektor_wiedzy = {


    "model":

    NAZWA_MODELU,



    "data":

    datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    ),



    "ocena_modelu":

    ocena_modelu,



    "analiza_klas":

    analiza_klas,



    "analiza_pewnosci":

    analiza_pewnosci,



    "analiza_pewnosci_klasy":

    analiza_pewnosci_klasy,



    "analiza_odchylen":

    analiza_odchylen,



    "analiza_pamieci":

    analiza_pamieci

}




# =====================================================
# ZAPIS JSON
# =====================================================


pliki_json = {


    "analiza_klas.json":

    analiza_klas,


    "analiza_pewnosci.json":

    analiza_pewnosci,


    "analiza_pewnosci_klasy.json":

    analiza_pewnosci_klasy,


    "analiza_odchylen.json":

    analiza_odchylen,


    "analiza_pamieci.json":

    analiza_pamieci,


    "kolektor_wiedzy.json":

    kolektor_wiedzy

}




for nazwa,dane in pliki_json.items():


    with open(

        os.path.join(

            KATALOG_LABORATORIUM,

            nazwa

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            dane,

            f,

            indent=4,

            ensure_ascii=False

        )




# =====================================================
# RAPORT KOŃCOWY
# =====================================================


print()
print("======================================")
print("LABORATORIUM V2 ZAKOŃCZONE")
print("======================================")


print(
    "Model:",
    NAZWA_MODELU
)


print(
    "Katalog:",
    KATALOG_LABORATORIUM
)


print(
    "Analizowane mecze:",
    len(df_historia)
)


print(
    "Przyszłe predykcje:",
    len(df_predykcja)
)


print(
    "Pamięć:",
    len(pamiec_obserwacji)
)


print()
print("Utworzono:")

for plik in pliki_json:

    print(
        "-",
        plik
    )


print(
    "- analiza_przyszlych_predykcji.csv"
)

print()
print("======================================")








# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime

from tensorflow.keras.models import load_model



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = r"modele_kursy_przygotowane\siec_02_koniec_kursow"


PLIK_PREDYKCJI = r"dane\kursy_przygotowane.csv"


PLIK_HISTORIA = r"dane\mozg_kursy_przygotowane.csv"



KATALOG_OBSERWACJI = os.path.join(
    KATALOG_MODELU,
    "obserwacja"
)


KATALOG_PREDYKCJI = os.path.join(
    KATALOG_MODELU,
    "predykcje"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_OBSERWACJI,
    "pamiec_obserwacji.json"
)



PLIK_OCENA = os.path.join(
    KATALOG_OBSERWACJI,
    "ocena.json"
)



os.makedirs(
    KATALOG_OBSERWACJI,
    exist_ok=True
)



os.makedirs(
    KATALOG_PREDYKCJI,
    exist_ok=True
)





# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "metadata.json"
    ),

    encoding="utf-8"

) as f:

    metadata = json.load(f)



CECHY = metadata["cechy"]


NAZWA_MODELU = metadata["nazwa"]





# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "klasy.json"
    ),

    encoding="utf-8"

) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v): k

    for k,v in klasy.items()

}





# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================


df_pred = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



INDEX_MAP = {


    kolumna:index

    for index,kolumna

    in enumerate(df_pred.columns)

}



print("MAPA CECH")

print(INDEX_MAP)





# =====================================================
# CECHY MODELU
# =====================================================


INDEX_CECH = []



for cecha in CECHY:


    if cecha not in INDEX_MAP:


        raise Exception(

            f"Brak cechy modelu: {cecha}"

        )


    INDEX_CECH.append(

        INDEX_MAP[cecha]

    )



print(

    "Cechy modelu:",

    INDEX_CECH

)





# =====================================================
# AKTUALNE MECZE DO PREDYKCJI
# =====================================================


NAZWY_PREDYKCJI = (

    df_pred["mecz"]

    .astype(str)

    .tolist()

)



X_PREDYKCJA = df_pred.iloc[

    :,

    INDEX_CECH

]



X_PREDYKCJA = np.nan_to_num(

    X_PREDYKCJA.values

)





# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


hist = pd.read_csv(

    PLIK_HISTORIA,

    sep=";",

    header=None,

    encoding="utf-8"

)



NAZWY_HISTORIA = hist.iloc[:,0].astype(str)



X_HISTORIA = hist.iloc[

    :,

    INDEX_CECH

]



Y_HISTORIA = hist.iloc[:,-1]



X_HISTORIA = np.nan_to_num(

    X_HISTORIA.values

)





# =====================================================
# WCZYTANIE MODELU
# =====================================================


model = load_model(

    os.path.join(

        KATALOG_MODELU,

        "model.h5"

    )

)





# =====================================================
# PREDYKCJA HISTORII
# =====================================================


print(
    "Analiza historii..."
)



pred_hist = model.predict(

    X_HISTORIA

)



klasy_pred_hist = np.argmax(

    pred_hist,

    axis=1

)





# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================


print(

    "Analiza aktualnych meczów..."

)



pred = model.predict(

    X_PREDYKCJA

)



klasy_pred = np.argmax(

    pred,

    axis=1

)





# =====================================================
# WCZYTANIE PAMIĘCI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:


        pamiec_obserwacji = json.load(f)



else:


    pamiec_obserwacji = {}





# =====================================================
# WCZYTANIE OCENY
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:


        ocena = json.load(f)



else:


    ocena = {


        "model":

        NAZWA_MODELU,


        "ocena_ogolna":

        {

            "ilosc":

            0,


            "trafienia":

            0

        },


        "ocena_wynikow":

        {}

    }





# =====================================================
# STRUKTURY SESJI
# =====================================================


czas = datetime.now().strftime(

    "%Y-%m-%d %H:%M:%S"

)



nowe_obserwacje = []


nowe_predykcje = []


nowa_historia = []




analiza = {}



for wynik in klasy.keys():


    analiza[wynik] = {


        "ilosc_wystapien":0,


        "trafienia":0,


        "bledy":{}

    }




print(

    "Przygotowano dane."

)
# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 2/2
# =====================================================



# =====================================================
# ANALIZA HISTORII Z WYNIKAMI
# =====================================================


for i,p in enumerate(klasy_pred_hist):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    real_wynik = str(
        Y_HISTORIA.iloc[i]
    )


    nazwa_meczu = str(
        NAZWY_HISTORIA.iloc[i]
    )


    pewnosc = float(
        np.max(pred_hist[i])
    )


    trafienie = (
        pred_wynik == real_wynik
    )



    obserwacja = {


        "data":

        czas,


        "model":

        NAZWA_MODELU,


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "predykcja":

        pred_wynik,


        "wynik_rzeczywisty":

        real_wynik,


        "pewnosc":

        pewnosc,


        "trafienie":

        trafienie

    }





    # =========================================
    # AKTUALIZACJA PAMIĘCI MECZU
    # =========================================


    if nazwa_meczu not in pamiec_obserwacji:


        pamiec_obserwacji[nazwa_meczu] = []



        obserwacja["pierwsza_obserwacja"] = True



    else:


        ostatnia = pamiec_obserwacji[nazwa_meczu][-1]



        if ostatnia["predykcja"] != pred_wynik:


            obserwacja["zmiana_predykcji"] = {


                "stara":

                ostatnia["predykcja"],


                "nowa":

                pred_wynik

            }



        if ostatnia["pewnosc"] != pewnosc:


            obserwacja["zmiana_pewnosci"] = {


                "stara":

                ostatnia["pewnosc"],


                "nowa":

                pewnosc

            }





    pamiec_obserwacji[nazwa_meczu].append(

        obserwacja

    )



    nowe_obserwacje.append(

        obserwacja

    )





    # statystyka klasy


    analiza[pred_wynik]["ilosc_wystapien"] += 1



    if trafienie:


        analiza[pred_wynik]["trafienia"] += 1


    else:


        if real_wynik not in analiza[pred_wynik]["bledy"]:


            analiza[pred_wynik]["bledy"][real_wynik] = 0



        analiza[pred_wynik]["bledy"][real_wynik] += 1







# =====================================================
# AKTUALNE MECZE BEZ WYNIKU
# =====================================================


for i,p in enumerate(klasy_pred):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    nazwa_meczu = str(

        NAZWY_PREDYKCJI[i]

    )


    pewnosc = float(

        np.max(pred[i])

    )



    predykcja = {


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "wynik_predykcji":

        pred_wynik,


        "pewnosc":

        pewnosc

    }



    nowe_predykcje.append(

        predykcja

    )







# =====================================================
# AKTUALIZACJA OCENY MODELU
# =====================================================


ilosc_globalna = 0

trafienia_globalne = 0



ocena_wynikow = {}



for wynik,dane in analiza.items():


    ilosc = dane["ilosc_wystapien"]


    trafienia = dane["trafienia"]



    ilosc_globalna += ilosc


    trafienia_globalne += trafienia



    ocena_wynikow[wynik] = {


        "ilosc_predykcji":

        ilosc,


        "trafienia":

        trafienia,


        "skutecznosc":

        (

            trafienia / ilosc

            if ilosc > 0

            else 0

        ),


        "bledy":

        dane["bledy"]

    }





ocena = {


    "model":

    NAZWA_MODELU,


    "data":

    czas,


    "ocena_ogolna":{


        "ilosc_meczow":

        ilosc_globalna,


        "trafienia":

        trafienia_globalne,


        "skutecznosc":

        (

            trafienia_globalne /

            ilosc_globalna

            if ilosc_globalna > 0

            else 0

        )

    },


    "ocena_wynikow":

    ocena_wynikow

}







# =====================================================
# ZAPIS PAMIĘCI
# =====================================================


with open(

    PLIK_PAMIEC,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        pamiec_obserwacji,

        f,

        indent=4,

        ensure_ascii=False

    )





# =====================================================
# ZAPIS OCENY
# =====================================================


with open(

    PLIK_OCENA,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        ocena,

        f,

        indent=4,

        ensure_ascii=False

    )







# =====================================================
# ZAPIS AKTUALNEJ PREDYKCJI
# =====================================================


pd.DataFrame(

    nowe_predykcje

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







# =====================================================
# ZAPIS HISTORII Z WYNIKAMI
# =====================================================


historia_csv = []



for mecz,lista in pamiec_obserwacji.items():


    ostatnia = lista[-1]


    historia_csv.append(


        {


            "id_meczu":

            mecz,


            "id_grupy":

            ostatnia["id_grupy"],


            "wynik_predykcji":

            ostatnia["predykcja"],


            "pewnosc":

            ostatnia["pewnosc"],


            "wynik_rzeczywisty":

            ostatnia["wynik_rzeczywisty"]

        }

    )







pd.DataFrame(

    historia_csv

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







print()

print("================================")

print("ZAKOŃCZONO")

print("================================")



print(

    "Pamięć:",

    PLIK_PAMIEC

)



print(

    "Ocena:",

    PLIK_OCENA

)



print(

    "Predykcje:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    )

)



print(

    "Historia:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    )

)
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = (
    r"modele_kursy_przygotowane"
    r"\siec_02_koniec_kursow"
)


NAZWA_BAZY = "kursy_przygotowane"


NAZWA_MODELU = os.path.basename(
    KATALOG_MODELU
)



# =====================================================
# LABORATORIUM
# =====================================================


KATALOG_LABORATORIUM = os.path.join(
    "laboratorium",
    NAZWA_BAZY,
    NAZWA_MODELU
)



os.makedirs(
    KATALOG_LABORATORIUM,
    exist_ok=True
)



# =====================================================
# PLIKI WEJŚCIOWE
# =====================================================


PLIK_KLASY = os.path.join(
    KATALOG_MODELU,
    "klasy.json"
)



PLIK_PRED_WYNIK = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_z_wynikiem.csv"
)



PLIK_PRED_GRUPY = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_grupy.csv"
)



PLIK_OCENA = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "ocena.json"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "pamiec_obserwacji.json"
)




# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(
    PLIK_KLASY,
    encoding="utf-8"
) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v):k

    for k,v in klasy.items()

}



print(
    "Załadowano klas:",
    len(ID_NA_WYNIK)
)



# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


df_historia = pd.read_csv(

    PLIK_PRED_WYNIK,

    sep=";",

    encoding="utf-8"

)



print(
    "Historia:",
    len(df_historia)
)



# =====================================================
# WCZYTANIE AKTUALNYCH PREDYKCJI
# =====================================================


df_predykcja = pd.read_csv(

    PLIK_PRED_GRUPY,

    sep=";",

    encoding="utf-8"

)



print(
    "Aktualne predykcje:",
    len(df_predykcja)
)



# =====================================================
# WCZYTANIE OCENY MODELU
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:

        ocena_modelu = json.load(f)


else:


    ocena_modelu = {}




# =====================================================
# WCZYTANIE PAMIĘCI OBSERWACJI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:

        pamiec_obserwacji = json.load(f)


else:


    pamiec_obserwacji = {}




print(
    "Pamięć obserwacji:",
    len(pamiec_obserwacji)
)




# =====================================================
# ANALIZA KLAS
# =====================================================


analiza_klas = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    ilosc = len(dane)



    if ilosc == 0:


        analiza_klas[str(id_grupy)] = {


            "wynik":

            wynik,


            "ilosc_predykcji":

            0,


            "trafienia":

            0,


            "skutecznosc":

            0,


            "rzeczywisty_rozkład":

            {}

        }


        continue




    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()




    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )




    analiza_klas[str(id_grupy)] = {


        "wynik":

        wynik,


        "ilosc_predykcji":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        ),



        "rzeczywisty_rozkład":

        rozklad

    }




# =====================================================
# ANALIZA PEWNOŚCI DYNAMICZNA
# =====================================================


analiza_pewnosci = {}




df_historia = df_historia.sort_values(
    "pewnosc"
)




# 10 równych grup według ilości danych

df_historia["koszyk_pewnosci"] = pd.qcut(

    df_historia["pewnosc"],

    q=10,

    duplicates="drop"

)




for koszyk, dane in df_historia.groupby(

    "koszyk_pewnosci",

    observed=True

):


    ilosc = len(dane)



    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()



    analiza_pewnosci[str(koszyk)] = {


        "ilosc":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        )

    }




# =====================================================
# ANALIZA PEWNOŚCI DLA KAŻDEJ KLASY
# =====================================================


analiza_pewnosci_klasy = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane_klasy = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    if len(dane_klasy) == 0:

        continue




    dane_klasy = dane_klasy.copy()



    dane_klasy["koszyk"] = pd.qcut(

        dane_klasy["pewnosc"],

        q=10,

        duplicates="drop"

    )



    koszyki = {}



    for koszyk,dane in dane_klasy.groupby(

        "koszyk",

        observed=True

    ):



        ilosc = len(dane)



        trafienia = (

            dane["wynik_predykcji"]

            ==

            dane["wynik_rzeczywisty"]

        ).sum()



        koszyki[str(koszyk)] = {


            "ilosc":

            int(ilosc),


            "trafienia":

            int(trafienia),


            "skutecznosc":

            float(

                trafienia / ilosc

            )

        }




    analiza_pewnosci_klasy[str(id_grupy)] = {


        "wynik":

        wynik,


        "progi_pewnosci":

        koszyki

    }




# KONIEC FRAGMENTU 1/2
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 2/2
# =====================================================


# =====================================================
# ANALIZA ODCHYLEŃ
# (CO SIEĆ TYPOWAŁA VS CO FAKTYCZNIE WYPADŁO)
# =====================================================


analiza_odchylen = {}



for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]


    if len(dane) == 0:

        continue



    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )



    uporzadkowane = sorted(

        rozklad.items(),

        key=lambda x:x[1],

        reverse=True

    )



    analiza_odchylen[str(id_grupy)] = {


        "wynik_typowany":

        wynik,


        "ilosc":

        int(len(dane)),


        "najczestsze_wyniki_rzeczywiste":

        dict(uporzadkowane[:10]),


        "czy_odwrócony_wzorzec":

        (
            uporzadkowane[0][0] != wynik
            if len(uporzadkowane)>0
            else False
        )

    }




# =====================================================
# ANALIZA PAMIĘCI OBSERWACJI
# =====================================================


analiza_pamieci = {


    "ilosc_meczow":

    len(pamiec_obserwacji),


    "zmiany_predykcji":0,


    "pierwsze_obserwacje":0

}



for mecz, obserwacje in pamiec_obserwacji.items():


    for obs in obserwacje:


        if obs.get(
            "pierwsza_obserwacja"
        ):

            analiza_pamieci[
                "pierwsze_obserwacje"
            ] += 1



        if obs.get(
            "zmiana_predykcji"
        ):

            analiza_pamieci[
                "zmiany_predykcji"
            ] += 1




# =====================================================
# ANALIZA AKTUALNYCH PREDYKCJI
# =====================================================


analiza_przyszlych = []



for _,mecz in df_predykcja.iterrows():


    id_grupy = int(
        mecz["id_grupy"]
    )


    wynik = str(
        mecz["wynik_predykcji"]
    )


    pewnosc = float(
        mecz["pewnosc"]
    )



    wiedza = analiza_klas.get(

        str(id_grupy),

        {}

    )



    pewnosc_klasy = analiza_pewnosci_klasy.get(

        str(id_grupy),

        {}

    )



    odchylenie = analiza_odchylen.get(

        str(id_grupy),

        {}

    )


    analiza_przyszlych.append(


        {


            "id_meczu":

            mecz["id_meczu"],



            "id_grupy":

            id_grupy,



            "wynik_predykcji":

            wynik,



            "pewnosc":

            pewnosc,



            "historyczna_skutecznosc_klasy":

            wiedza.get(

                "skutecznosc",

                0

            ),



            "najczestszy_realny_wynik":

            (
                max(

                    wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ),

                    key=wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ).get

                )

                if wiedza.get(

                    "rzeczywisty_rozkład"

                )

                else None
            ),



            "czy_odwrócony_wzorzec":

            odchylenie.get(

                "czy_odwrócony_wzorzec",

                False

            )

        }

    )




df_analiza_predykcji = pd.DataFrame(

    analiza_przyszlych

)



df_analiza_predykcji.to_csv(


    os.path.join(

        KATALOG_LABORATORIUM,

        "analiza_przyszlych_predykcji.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)




# =====================================================
# KOLEKTOR WIEDZY
# =====================================================


kolektor_wiedzy = {


    "model":

    NAZWA_MODELU,



    "data":

    datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    ),



    "ocena_modelu":

    ocena_modelu,



    "analiza_klas":

    analiza_klas,



    "analiza_pewnosci":

    analiza_pewnosci,



    "analiza_pewnosci_klasy":

    analiza_pewnosci_klasy,



    "analiza_odchylen":

    analiza_odchylen,



    "analiza_pamieci":

    analiza_pamieci

}




# =====================================================
# ZAPIS JSON
# =====================================================


pliki_json = {


    "analiza_klas.json":

    analiza_klas,


    "analiza_pewnosci.json":

    analiza_pewnosci,


    "analiza_pewnosci_klasy.json":

    analiza_pewnosci_klasy,


    "analiza_odchylen.json":

    analiza_odchylen,


    "analiza_pamieci.json":

    analiza_pamieci,


    "kolektor_wiedzy.json":

    kolektor_wiedzy

}




for nazwa,dane in pliki_json.items():


    with open(

        os.path.join(

            KATALOG_LABORATORIUM,

            nazwa

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            dane,

            f,

            indent=4,

            ensure_ascii=False

        )




# =====================================================
# RAPORT KOŃCOWY
# =====================================================


print()
print("======================================")
print("LABORATORIUM V2 ZAKOŃCZONE")
print("======================================")


print(
    "Model:",
    NAZWA_MODELU
)


print(
    "Katalog:",
    KATALOG_LABORATORIUM
)


print(
    "Analizowane mecze:",
    len(df_historia)
)


print(
    "Przyszłe predykcje:",
    len(df_predykcja)
)


print(
    "Pamięć:",
    len(pamiec_obserwacji)
)


print()
print("Utworzono:")

for plik in pliki_json:

    print(
        "-",
        plik
    )


print(
    "- analiza_przyszlych_predykcji.csv"
)

print()
print("======================================")








# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime

from tensorflow.keras.models import load_model



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = r"modele_kursy_przygotowane\siec_03_zmiana_kursow"


PLIK_PREDYKCJI = r"dane\kursy_przygotowane.csv"


PLIK_HISTORIA = r"dane\mozg_kursy_przygotowane.csv"



KATALOG_OBSERWACJI = os.path.join(
    KATALOG_MODELU,
    "obserwacja"
)


KATALOG_PREDYKCJI = os.path.join(
    KATALOG_MODELU,
    "predykcje"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_OBSERWACJI,
    "pamiec_obserwacji.json"
)



PLIK_OCENA = os.path.join(
    KATALOG_OBSERWACJI,
    "ocena.json"
)



os.makedirs(
    KATALOG_OBSERWACJI,
    exist_ok=True
)



os.makedirs(
    KATALOG_PREDYKCJI,
    exist_ok=True
)





# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "metadata.json"
    ),

    encoding="utf-8"

) as f:

    metadata = json.load(f)



CECHY = metadata["cechy"]


NAZWA_MODELU = metadata["nazwa"]





# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "klasy.json"
    ),

    encoding="utf-8"

) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v): k

    for k,v in klasy.items()

}





# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================


df_pred = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



INDEX_MAP = {


    kolumna:index

    for index,kolumna

    in enumerate(df_pred.columns)

}



print("MAPA CECH")

print(INDEX_MAP)





# =====================================================
# CECHY MODELU
# =====================================================


INDEX_CECH = []



for cecha in CECHY:


    if cecha not in INDEX_MAP:


        raise Exception(

            f"Brak cechy modelu: {cecha}"

        )


    INDEX_CECH.append(

        INDEX_MAP[cecha]

    )



print(

    "Cechy modelu:",

    INDEX_CECH

)





# =====================================================
# AKTUALNE MECZE DO PREDYKCJI
# =====================================================


NAZWY_PREDYKCJI = (

    df_pred["mecz"]

    .astype(str)

    .tolist()

)



X_PREDYKCJA = df_pred.iloc[

    :,

    INDEX_CECH

]



X_PREDYKCJA = np.nan_to_num(

    X_PREDYKCJA.values

)





# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


hist = pd.read_csv(

    PLIK_HISTORIA,

    sep=";",

    header=None,

    encoding="utf-8"

)



NAZWY_HISTORIA = hist.iloc[:,0].astype(str)



X_HISTORIA = hist.iloc[

    :,

    INDEX_CECH

]



Y_HISTORIA = hist.iloc[:,-1]



X_HISTORIA = np.nan_to_num(

    X_HISTORIA.values

)





# =====================================================
# WCZYTANIE MODELU
# =====================================================


model = load_model(

    os.path.join(

        KATALOG_MODELU,

        "model.h5"

    )

)





# =====================================================
# PREDYKCJA HISTORII
# =====================================================


print(
    "Analiza historii..."
)



pred_hist = model.predict(

    X_HISTORIA

)



klasy_pred_hist = np.argmax(

    pred_hist,

    axis=1

)





# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================


print(

    "Analiza aktualnych meczów..."

)



pred = model.predict(

    X_PREDYKCJA

)



klasy_pred = np.argmax(

    pred,

    axis=1

)





# =====================================================
# WCZYTANIE PAMIĘCI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:


        pamiec_obserwacji = json.load(f)



else:


    pamiec_obserwacji = {}





# =====================================================
# WCZYTANIE OCENY
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:


        ocena = json.load(f)



else:


    ocena = {


        "model":

        NAZWA_MODELU,


        "ocena_ogolna":

        {

            "ilosc":

            0,


            "trafienia":

            0

        },


        "ocena_wynikow":

        {}

    }





# =====================================================
# STRUKTURY SESJI
# =====================================================


czas = datetime.now().strftime(

    "%Y-%m-%d %H:%M:%S"

)



nowe_obserwacje = []


nowe_predykcje = []


nowa_historia = []




analiza = {}



for wynik in klasy.keys():


    analiza[wynik] = {


        "ilosc_wystapien":0,


        "trafienia":0,


        "bledy":{}

    }




print(

    "Przygotowano dane."

)
# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 2/2
# =====================================================



# =====================================================
# ANALIZA HISTORII Z WYNIKAMI
# =====================================================


for i,p in enumerate(klasy_pred_hist):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    real_wynik = str(
        Y_HISTORIA.iloc[i]
    )


    nazwa_meczu = str(
        NAZWY_HISTORIA.iloc[i]
    )


    pewnosc = float(
        np.max(pred_hist[i])
    )


    trafienie = (
        pred_wynik == real_wynik
    )



    obserwacja = {


        "data":

        czas,


        "model":

        NAZWA_MODELU,


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "predykcja":

        pred_wynik,


        "wynik_rzeczywisty":

        real_wynik,


        "pewnosc":

        pewnosc,


        "trafienie":

        trafienie

    }





    # =========================================
    # AKTUALIZACJA PAMIĘCI MECZU
    # =========================================


    if nazwa_meczu not in pamiec_obserwacji:


        pamiec_obserwacji[nazwa_meczu] = []



        obserwacja["pierwsza_obserwacja"] = True



    else:


        ostatnia = pamiec_obserwacji[nazwa_meczu][-1]



        if ostatnia["predykcja"] != pred_wynik:


            obserwacja["zmiana_predykcji"] = {


                "stara":

                ostatnia["predykcja"],


                "nowa":

                pred_wynik

            }



        if ostatnia["pewnosc"] != pewnosc:


            obserwacja["zmiana_pewnosci"] = {


                "stara":

                ostatnia["pewnosc"],


                "nowa":

                pewnosc

            }





    pamiec_obserwacji[nazwa_meczu].append(

        obserwacja

    )



    nowe_obserwacje.append(

        obserwacja

    )





    # statystyka klasy


    analiza[pred_wynik]["ilosc_wystapien"] += 1



    if trafienie:


        analiza[pred_wynik]["trafienia"] += 1


    else:


        if real_wynik not in analiza[pred_wynik]["bledy"]:


            analiza[pred_wynik]["bledy"][real_wynik] = 0



        analiza[pred_wynik]["bledy"][real_wynik] += 1







# =====================================================
# AKTUALNE MECZE BEZ WYNIKU
# =====================================================


for i,p in enumerate(klasy_pred):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    nazwa_meczu = str(

        NAZWY_PREDYKCJI[i]

    )


    pewnosc = float(

        np.max(pred[i])

    )



    predykcja = {


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "wynik_predykcji":

        pred_wynik,


        "pewnosc":

        pewnosc

    }



    nowe_predykcje.append(

        predykcja

    )







# =====================================================
# AKTUALIZACJA OCENY MODELU
# =====================================================


ilosc_globalna = 0

trafienia_globalne = 0



ocena_wynikow = {}



for wynik,dane in analiza.items():


    ilosc = dane["ilosc_wystapien"]


    trafienia = dane["trafienia"]



    ilosc_globalna += ilosc


    trafienia_globalne += trafienia



    ocena_wynikow[wynik] = {


        "ilosc_predykcji":

        ilosc,


        "trafienia":

        trafienia,


        "skutecznosc":

        (

            trafienia / ilosc

            if ilosc > 0

            else 0

        ),


        "bledy":

        dane["bledy"]

    }





ocena = {


    "model":

    NAZWA_MODELU,


    "data":

    czas,


    "ocena_ogolna":{


        "ilosc_meczow":

        ilosc_globalna,


        "trafienia":

        trafienia_globalne,


        "skutecznosc":

        (

            trafienia_globalne /

            ilosc_globalna

            if ilosc_globalna > 0

            else 0

        )

    },


    "ocena_wynikow":

    ocena_wynikow

}







# =====================================================
# ZAPIS PAMIĘCI
# =====================================================


with open(

    PLIK_PAMIEC,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        pamiec_obserwacji,

        f,

        indent=4,

        ensure_ascii=False

    )





# =====================================================
# ZAPIS OCENY
# =====================================================


with open(

    PLIK_OCENA,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        ocena,

        f,

        indent=4,

        ensure_ascii=False

    )







# =====================================================
# ZAPIS AKTUALNEJ PREDYKCJI
# =====================================================


pd.DataFrame(

    nowe_predykcje

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







# =====================================================
# ZAPIS HISTORII Z WYNIKAMI
# =====================================================


historia_csv = []



for mecz,lista in pamiec_obserwacji.items():


    ostatnia = lista[-1]


    historia_csv.append(


        {


            "id_meczu":

            mecz,


            "id_grupy":

            ostatnia["id_grupy"],


            "wynik_predykcji":

            ostatnia["predykcja"],


            "pewnosc":

            ostatnia["pewnosc"],


            "wynik_rzeczywisty":

            ostatnia["wynik_rzeczywisty"]

        }

    )







pd.DataFrame(

    historia_csv

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







print()

print("================================")

print("ZAKOŃCZONO")

print("================================")



print(

    "Pamięć:",

    PLIK_PAMIEC

)



print(

    "Ocena:",

    PLIK_OCENA

)



print(

    "Predykcje:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    )

)



print(

    "Historia:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    )

)
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = (
    r"modele_kursy_przygotowane"
    r"\siec_03_zmiana_kursow"
)


NAZWA_BAZY = "kursy_przygotowane"


NAZWA_MODELU = os.path.basename(
    KATALOG_MODELU
)



# =====================================================
# LABORATORIUM
# =====================================================


KATALOG_LABORATORIUM = os.path.join(
    "laboratorium",
    NAZWA_BAZY,
    NAZWA_MODELU
)



os.makedirs(
    KATALOG_LABORATORIUM,
    exist_ok=True
)



# =====================================================
# PLIKI WEJŚCIOWE
# =====================================================


PLIK_KLASY = os.path.join(
    KATALOG_MODELU,
    "klasy.json"
)



PLIK_PRED_WYNIK = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_z_wynikiem.csv"
)



PLIK_PRED_GRUPY = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_grupy.csv"
)



PLIK_OCENA = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "ocena.json"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "pamiec_obserwacji.json"
)




# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(
    PLIK_KLASY,
    encoding="utf-8"
) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v):k

    for k,v in klasy.items()

}



print(
    "Załadowano klas:",
    len(ID_NA_WYNIK)
)



# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


df_historia = pd.read_csv(

    PLIK_PRED_WYNIK,

    sep=";",

    encoding="utf-8"

)



print(
    "Historia:",
    len(df_historia)
)



# =====================================================
# WCZYTANIE AKTUALNYCH PREDYKCJI
# =====================================================


df_predykcja = pd.read_csv(

    PLIK_PRED_GRUPY,

    sep=";",

    encoding="utf-8"

)



print(
    "Aktualne predykcje:",
    len(df_predykcja)
)



# =====================================================
# WCZYTANIE OCENY MODELU
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:

        ocena_modelu = json.load(f)


else:


    ocena_modelu = {}




# =====================================================
# WCZYTANIE PAMIĘCI OBSERWACJI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:

        pamiec_obserwacji = json.load(f)


else:


    pamiec_obserwacji = {}




print(
    "Pamięć obserwacji:",
    len(pamiec_obserwacji)
)




# =====================================================
# ANALIZA KLAS
# =====================================================


analiza_klas = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    ilosc = len(dane)



    if ilosc == 0:


        analiza_klas[str(id_grupy)] = {


            "wynik":

            wynik,


            "ilosc_predykcji":

            0,


            "trafienia":

            0,


            "skutecznosc":

            0,


            "rzeczywisty_rozkład":

            {}

        }


        continue




    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()




    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )




    analiza_klas[str(id_grupy)] = {


        "wynik":

        wynik,


        "ilosc_predykcji":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        ),



        "rzeczywisty_rozkład":

        rozklad

    }




# =====================================================
# ANALIZA PEWNOŚCI DYNAMICZNA
# =====================================================


analiza_pewnosci = {}




df_historia = df_historia.sort_values(
    "pewnosc"
)




# 10 równych grup według ilości danych

df_historia["koszyk_pewnosci"] = pd.qcut(

    df_historia["pewnosc"],

    q=10,

    duplicates="drop"

)




for koszyk, dane in df_historia.groupby(

    "koszyk_pewnosci",

    observed=True

):


    ilosc = len(dane)



    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()



    analiza_pewnosci[str(koszyk)] = {


        "ilosc":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        )

    }




# =====================================================
# ANALIZA PEWNOŚCI DLA KAŻDEJ KLASY
# =====================================================


analiza_pewnosci_klasy = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane_klasy = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    if len(dane_klasy) == 0:

        continue




    dane_klasy = dane_klasy.copy()



    dane_klasy["koszyk"] = pd.qcut(

        dane_klasy["pewnosc"],

        q=10,

        duplicates="drop"

    )



    koszyki = {}



    for koszyk,dane in dane_klasy.groupby(

        "koszyk",

        observed=True

    ):



        ilosc = len(dane)



        trafienia = (

            dane["wynik_predykcji"]

            ==

            dane["wynik_rzeczywisty"]

        ).sum()



        koszyki[str(koszyk)] = {


            "ilosc":

            int(ilosc),


            "trafienia":

            int(trafienia),


            "skutecznosc":

            float(

                trafienia / ilosc

            )

        }




    analiza_pewnosci_klasy[str(id_grupy)] = {


        "wynik":

        wynik,


        "progi_pewnosci":

        koszyki

    }




# KONIEC FRAGMENTU 1/2
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 2/2
# =====================================================


# =====================================================
# ANALIZA ODCHYLEŃ
# (CO SIEĆ TYPOWAŁA VS CO FAKTYCZNIE WYPADŁO)
# =====================================================


analiza_odchylen = {}



for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]


    if len(dane) == 0:

        continue



    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )



    uporzadkowane = sorted(

        rozklad.items(),

        key=lambda x:x[1],

        reverse=True

    )



    analiza_odchylen[str(id_grupy)] = {


        "wynik_typowany":

        wynik,


        "ilosc":

        int(len(dane)),


        "najczestsze_wyniki_rzeczywiste":

        dict(uporzadkowane[:10]),


        "czy_odwrócony_wzorzec":

        (
            uporzadkowane[0][0] != wynik
            if len(uporzadkowane)>0
            else False
        )

    }




# =====================================================
# ANALIZA PAMIĘCI OBSERWACJI
# =====================================================


analiza_pamieci = {


    "ilosc_meczow":

    len(pamiec_obserwacji),


    "zmiany_predykcji":0,


    "pierwsze_obserwacje":0

}



for mecz, obserwacje in pamiec_obserwacji.items():


    for obs in obserwacje:


        if obs.get(
            "pierwsza_obserwacja"
        ):

            analiza_pamieci[
                "pierwsze_obserwacje"
            ] += 1



        if obs.get(
            "zmiana_predykcji"
        ):

            analiza_pamieci[
                "zmiany_predykcji"
            ] += 1




# =====================================================
# ANALIZA AKTUALNYCH PREDYKCJI
# =====================================================


analiza_przyszlych = []



for _,mecz in df_predykcja.iterrows():


    id_grupy = int(
        mecz["id_grupy"]
    )


    wynik = str(
        mecz["wynik_predykcji"]
    )


    pewnosc = float(
        mecz["pewnosc"]
    )



    wiedza = analiza_klas.get(

        str(id_grupy),

        {}

    )



    pewnosc_klasy = analiza_pewnosci_klasy.get(

        str(id_grupy),

        {}

    )



    odchylenie = analiza_odchylen.get(

        str(id_grupy),

        {}

    )


    analiza_przyszlych.append(


        {


            "id_meczu":

            mecz["id_meczu"],



            "id_grupy":

            id_grupy,



            "wynik_predykcji":

            wynik,



            "pewnosc":

            pewnosc,



            "historyczna_skutecznosc_klasy":

            wiedza.get(

                "skutecznosc",

                0

            ),



            "najczestszy_realny_wynik":

            (
                max(

                    wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ),

                    key=wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ).get

                )

                if wiedza.get(

                    "rzeczywisty_rozkład"

                )

                else None
            ),



            "czy_odwrócony_wzorzec":

            odchylenie.get(

                "czy_odwrócony_wzorzec",

                False

            )

        }

    )




df_analiza_predykcji = pd.DataFrame(

    analiza_przyszlych

)



df_analiza_predykcji.to_csv(


    os.path.join(

        KATALOG_LABORATORIUM,

        "analiza_przyszlych_predykcji.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)




# =====================================================
# KOLEKTOR WIEDZY
# =====================================================


kolektor_wiedzy = {


    "model":

    NAZWA_MODELU,



    "data":

    datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    ),



    "ocena_modelu":

    ocena_modelu,



    "analiza_klas":

    analiza_klas,



    "analiza_pewnosci":

    analiza_pewnosci,



    "analiza_pewnosci_klasy":

    analiza_pewnosci_klasy,



    "analiza_odchylen":

    analiza_odchylen,



    "analiza_pamieci":

    analiza_pamieci

}




# =====================================================
# ZAPIS JSON
# =====================================================


pliki_json = {


    "analiza_klas.json":

    analiza_klas,


    "analiza_pewnosci.json":

    analiza_pewnosci,


    "analiza_pewnosci_klasy.json":

    analiza_pewnosci_klasy,


    "analiza_odchylen.json":

    analiza_odchylen,


    "analiza_pamieci.json":

    analiza_pamieci,


    "kolektor_wiedzy.json":

    kolektor_wiedzy

}




for nazwa,dane in pliki_json.items():


    with open(

        os.path.join(

            KATALOG_LABORATORIUM,

            nazwa

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            dane,

            f,

            indent=4,

            ensure_ascii=False

        )




# =====================================================
# RAPORT KOŃCOWY
# =====================================================


print()
print("======================================")
print("LABORATORIUM V2 ZAKOŃCZONE")
print("======================================")


print(
    "Model:",
    NAZWA_MODELU
)


print(
    "Katalog:",
    KATALOG_LABORATORIUM
)


print(
    "Analizowane mecze:",
    len(df_historia)
)


print(
    "Przyszłe predykcje:",
    len(df_predykcja)
)


print(
    "Pamięć:",
    len(pamiec_obserwacji)
)


print()
print("Utworzono:")

for plik in pliki_json:

    print(
        "-",
        plik
    )


print(
    "- analiza_przyszlych_predykcji.csv"
)

print()
print("======================================")








# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime

from tensorflow.keras.models import load_model



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = r"modele_kursy_przygotowane\siec_04_procent_kursow"


PLIK_PREDYKCJI = r"dane\kursy_przygotowane.csv"


PLIK_HISTORIA = r"dane\mozg_kursy_przygotowane.csv"



KATALOG_OBSERWACJI = os.path.join(
    KATALOG_MODELU,
    "obserwacja"
)


KATALOG_PREDYKCJI = os.path.join(
    KATALOG_MODELU,
    "predykcje"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_OBSERWACJI,
    "pamiec_obserwacji.json"
)



PLIK_OCENA = os.path.join(
    KATALOG_OBSERWACJI,
    "ocena.json"
)



os.makedirs(
    KATALOG_OBSERWACJI,
    exist_ok=True
)



os.makedirs(
    KATALOG_PREDYKCJI,
    exist_ok=True
)





# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "metadata.json"
    ),

    encoding="utf-8"

) as f:

    metadata = json.load(f)



CECHY = metadata["cechy"]


NAZWA_MODELU = metadata["nazwa"]





# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "klasy.json"
    ),

    encoding="utf-8"

) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v): k

    for k,v in klasy.items()

}





# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================


df_pred = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



INDEX_MAP = {


    kolumna:index

    for index,kolumna

    in enumerate(df_pred.columns)

}



print("MAPA CECH")

print(INDEX_MAP)





# =====================================================
# CECHY MODELU
# =====================================================


INDEX_CECH = []



for cecha in CECHY:


    if cecha not in INDEX_MAP:


        raise Exception(

            f"Brak cechy modelu: {cecha}"

        )


    INDEX_CECH.append(

        INDEX_MAP[cecha]

    )



print(

    "Cechy modelu:",

    INDEX_CECH

)





# =====================================================
# AKTUALNE MECZE DO PREDYKCJI
# =====================================================


NAZWY_PREDYKCJI = (

    df_pred["mecz"]

    .astype(str)

    .tolist()

)



X_PREDYKCJA = df_pred.iloc[

    :,

    INDEX_CECH

]



X_PREDYKCJA = np.nan_to_num(

    X_PREDYKCJA.values

)





# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


hist = pd.read_csv(

    PLIK_HISTORIA,

    sep=";",

    header=None,

    encoding="utf-8"

)



NAZWY_HISTORIA = hist.iloc[:,0].astype(str)



X_HISTORIA = hist.iloc[

    :,

    INDEX_CECH

]



Y_HISTORIA = hist.iloc[:,-1]



X_HISTORIA = np.nan_to_num(

    X_HISTORIA.values

)





# =====================================================
# WCZYTANIE MODELU
# =====================================================


model = load_model(

    os.path.join(

        KATALOG_MODELU,

        "model.h5"

    )

)





# =====================================================
# PREDYKCJA HISTORII
# =====================================================


print(
    "Analiza historii..."
)



pred_hist = model.predict(

    X_HISTORIA

)



klasy_pred_hist = np.argmax(

    pred_hist,

    axis=1

)





# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================


print(

    "Analiza aktualnych meczów..."

)



pred = model.predict(

    X_PREDYKCJA

)



klasy_pred = np.argmax(

    pred,

    axis=1

)





# =====================================================
# WCZYTANIE PAMIĘCI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:


        pamiec_obserwacji = json.load(f)



else:


    pamiec_obserwacji = {}





# =====================================================
# WCZYTANIE OCENY
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:


        ocena = json.load(f)



else:


    ocena = {


        "model":

        NAZWA_MODELU,


        "ocena_ogolna":

        {

            "ilosc":

            0,


            "trafienia":

            0

        },


        "ocena_wynikow":

        {}

    }





# =====================================================
# STRUKTURY SESJI
# =====================================================


czas = datetime.now().strftime(

    "%Y-%m-%d %H:%M:%S"

)



nowe_obserwacje = []


nowe_predykcje = []


nowa_historia = []




analiza = {}



for wynik in klasy.keys():


    analiza[wynik] = {


        "ilosc_wystapien":0,


        "trafienia":0,


        "bledy":{}

    }




print(

    "Przygotowano dane."

)
# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 2/2
# =====================================================



# =====================================================
# ANALIZA HISTORII Z WYNIKAMI
# =====================================================


for i,p in enumerate(klasy_pred_hist):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    real_wynik = str(
        Y_HISTORIA.iloc[i]
    )


    nazwa_meczu = str(
        NAZWY_HISTORIA.iloc[i]
    )


    pewnosc = float(
        np.max(pred_hist[i])
    )


    trafienie = (
        pred_wynik == real_wynik
    )



    obserwacja = {


        "data":

        czas,


        "model":

        NAZWA_MODELU,


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "predykcja":

        pred_wynik,


        "wynik_rzeczywisty":

        real_wynik,


        "pewnosc":

        pewnosc,


        "trafienie":

        trafienie

    }





    # =========================================
    # AKTUALIZACJA PAMIĘCI MECZU
    # =========================================


    if nazwa_meczu not in pamiec_obserwacji:


        pamiec_obserwacji[nazwa_meczu] = []



        obserwacja["pierwsza_obserwacja"] = True



    else:


        ostatnia = pamiec_obserwacji[nazwa_meczu][-1]



        if ostatnia["predykcja"] != pred_wynik:


            obserwacja["zmiana_predykcji"] = {


                "stara":

                ostatnia["predykcja"],


                "nowa":

                pred_wynik

            }



        if ostatnia["pewnosc"] != pewnosc:


            obserwacja["zmiana_pewnosci"] = {


                "stara":

                ostatnia["pewnosc"],


                "nowa":

                pewnosc

            }





    pamiec_obserwacji[nazwa_meczu].append(

        obserwacja

    )



    nowe_obserwacje.append(

        obserwacja

    )





    # statystyka klasy


    analiza[pred_wynik]["ilosc_wystapien"] += 1



    if trafienie:


        analiza[pred_wynik]["trafienia"] += 1


    else:


        if real_wynik not in analiza[pred_wynik]["bledy"]:


            analiza[pred_wynik]["bledy"][real_wynik] = 0



        analiza[pred_wynik]["bledy"][real_wynik] += 1







# =====================================================
# AKTUALNE MECZE BEZ WYNIKU
# =====================================================


for i,p in enumerate(klasy_pred):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    nazwa_meczu = str(

        NAZWY_PREDYKCJI[i]

    )


    pewnosc = float(

        np.max(pred[i])

    )



    predykcja = {


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "wynik_predykcji":

        pred_wynik,


        "pewnosc":

        pewnosc

    }



    nowe_predykcje.append(

        predykcja

    )







# =====================================================
# AKTUALIZACJA OCENY MODELU
# =====================================================


ilosc_globalna = 0

trafienia_globalne = 0



ocena_wynikow = {}



for wynik,dane in analiza.items():


    ilosc = dane["ilosc_wystapien"]


    trafienia = dane["trafienia"]



    ilosc_globalna += ilosc


    trafienia_globalne += trafienia



    ocena_wynikow[wynik] = {


        "ilosc_predykcji":

        ilosc,


        "trafienia":

        trafienia,


        "skutecznosc":

        (

            trafienia / ilosc

            if ilosc > 0

            else 0

        ),


        "bledy":

        dane["bledy"]

    }





ocena = {


    "model":

    NAZWA_MODELU,


    "data":

    czas,


    "ocena_ogolna":{


        "ilosc_meczow":

        ilosc_globalna,


        "trafienia":

        trafienia_globalne,


        "skutecznosc":

        (

            trafienia_globalne /

            ilosc_globalna

            if ilosc_globalna > 0

            else 0

        )

    },


    "ocena_wynikow":

    ocena_wynikow

}







# =====================================================
# ZAPIS PAMIĘCI
# =====================================================


with open(

    PLIK_PAMIEC,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        pamiec_obserwacji,

        f,

        indent=4,

        ensure_ascii=False

    )





# =====================================================
# ZAPIS OCENY
# =====================================================


with open(

    PLIK_OCENA,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        ocena,

        f,

        indent=4,

        ensure_ascii=False

    )







# =====================================================
# ZAPIS AKTUALNEJ PREDYKCJI
# =====================================================


pd.DataFrame(

    nowe_predykcje

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







# =====================================================
# ZAPIS HISTORII Z WYNIKAMI
# =====================================================


historia_csv = []



for mecz,lista in pamiec_obserwacji.items():


    ostatnia = lista[-1]


    historia_csv.append(


        {


            "id_meczu":

            mecz,


            "id_grupy":

            ostatnia["id_grupy"],


            "wynik_predykcji":

            ostatnia["predykcja"],


            "pewnosc":

            ostatnia["pewnosc"],


            "wynik_rzeczywisty":

            ostatnia["wynik_rzeczywisty"]

        }

    )







pd.DataFrame(

    historia_csv

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







print()

print("================================")

print("ZAKOŃCZONO")

print("================================")



print(

    "Pamięć:",

    PLIK_PAMIEC

)



print(

    "Ocena:",

    PLIK_OCENA

)



print(

    "Predykcje:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    )

)



print(

    "Historia:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    )

)
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = (
    r"modele_kursy_przygotowane"
    r"\siec_04_procent_kursow"
)


NAZWA_BAZY = "kursy_przygotowane"


NAZWA_MODELU = os.path.basename(
    KATALOG_MODELU
)



# =====================================================
# LABORATORIUM
# =====================================================


KATALOG_LABORATORIUM = os.path.join(
    "laboratorium",
    NAZWA_BAZY,
    NAZWA_MODELU
)



os.makedirs(
    KATALOG_LABORATORIUM,
    exist_ok=True
)



# =====================================================
# PLIKI WEJŚCIOWE
# =====================================================


PLIK_KLASY = os.path.join(
    KATALOG_MODELU,
    "klasy.json"
)



PLIK_PRED_WYNIK = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_z_wynikiem.csv"
)



PLIK_PRED_GRUPY = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_grupy.csv"
)



PLIK_OCENA = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "ocena.json"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "pamiec_obserwacji.json"
)




# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(
    PLIK_KLASY,
    encoding="utf-8"
) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v):k

    for k,v in klasy.items()

}



print(
    "Załadowano klas:",
    len(ID_NA_WYNIK)
)



# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


df_historia = pd.read_csv(

    PLIK_PRED_WYNIK,

    sep=";",

    encoding="utf-8"

)



print(
    "Historia:",
    len(df_historia)
)



# =====================================================
# WCZYTANIE AKTUALNYCH PREDYKCJI
# =====================================================


df_predykcja = pd.read_csv(

    PLIK_PRED_GRUPY,

    sep=";",

    encoding="utf-8"

)



print(
    "Aktualne predykcje:",
    len(df_predykcja)
)



# =====================================================
# WCZYTANIE OCENY MODELU
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:

        ocena_modelu = json.load(f)


else:


    ocena_modelu = {}




# =====================================================
# WCZYTANIE PAMIĘCI OBSERWACJI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:

        pamiec_obserwacji = json.load(f)


else:


    pamiec_obserwacji = {}




print(
    "Pamięć obserwacji:",
    len(pamiec_obserwacji)
)




# =====================================================
# ANALIZA KLAS
# =====================================================


analiza_klas = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    ilosc = len(dane)



    if ilosc == 0:


        analiza_klas[str(id_grupy)] = {


            "wynik":

            wynik,


            "ilosc_predykcji":

            0,


            "trafienia":

            0,


            "skutecznosc":

            0,


            "rzeczywisty_rozkład":

            {}

        }


        continue




    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()




    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )




    analiza_klas[str(id_grupy)] = {


        "wynik":

        wynik,


        "ilosc_predykcji":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        ),



        "rzeczywisty_rozkład":

        rozklad

    }




# =====================================================
# ANALIZA PEWNOŚCI DYNAMICZNA
# =====================================================


analiza_pewnosci = {}




df_historia = df_historia.sort_values(
    "pewnosc"
)




# 10 równych grup według ilości danych

df_historia["koszyk_pewnosci"] = pd.qcut(

    df_historia["pewnosc"],

    q=10,

    duplicates="drop"

)




for koszyk, dane in df_historia.groupby(

    "koszyk_pewnosci",

    observed=True

):


    ilosc = len(dane)



    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()



    analiza_pewnosci[str(koszyk)] = {


        "ilosc":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        )

    }




# =====================================================
# ANALIZA PEWNOŚCI DLA KAŻDEJ KLASY
# =====================================================


analiza_pewnosci_klasy = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane_klasy = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    if len(dane_klasy) == 0:

        continue




    dane_klasy = dane_klasy.copy()



    dane_klasy["koszyk"] = pd.qcut(

        dane_klasy["pewnosc"],

        q=10,

        duplicates="drop"

    )



    koszyki = {}



    for koszyk,dane in dane_klasy.groupby(

        "koszyk",

        observed=True

    ):



        ilosc = len(dane)



        trafienia = (

            dane["wynik_predykcji"]

            ==

            dane["wynik_rzeczywisty"]

        ).sum()



        koszyki[str(koszyk)] = {


            "ilosc":

            int(ilosc),


            "trafienia":

            int(trafienia),


            "skutecznosc":

            float(

                trafienia / ilosc

            )

        }




    analiza_pewnosci_klasy[str(id_grupy)] = {


        "wynik":

        wynik,


        "progi_pewnosci":

        koszyki

    }




# KONIEC FRAGMENTU 1/2
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 2/2
# =====================================================


# =====================================================
# ANALIZA ODCHYLEŃ
# (CO SIEĆ TYPOWAŁA VS CO FAKTYCZNIE WYPADŁO)
# =====================================================


analiza_odchylen = {}



for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]


    if len(dane) == 0:

        continue



    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )



    uporzadkowane = sorted(

        rozklad.items(),

        key=lambda x:x[1],

        reverse=True

    )



    analiza_odchylen[str(id_grupy)] = {


        "wynik_typowany":

        wynik,


        "ilosc":

        int(len(dane)),


        "najczestsze_wyniki_rzeczywiste":

        dict(uporzadkowane[:10]),


        "czy_odwrócony_wzorzec":

        (
            uporzadkowane[0][0] != wynik
            if len(uporzadkowane)>0
            else False
        )

    }




# =====================================================
# ANALIZA PAMIĘCI OBSERWACJI
# =====================================================


analiza_pamieci = {


    "ilosc_meczow":

    len(pamiec_obserwacji),


    "zmiany_predykcji":0,


    "pierwsze_obserwacje":0

}



for mecz, obserwacje in pamiec_obserwacji.items():


    for obs in obserwacje:


        if obs.get(
            "pierwsza_obserwacja"
        ):

            analiza_pamieci[
                "pierwsze_obserwacje"
            ] += 1



        if obs.get(
            "zmiana_predykcji"
        ):

            analiza_pamieci[
                "zmiany_predykcji"
            ] += 1




# =====================================================
# ANALIZA AKTUALNYCH PREDYKCJI
# =====================================================


analiza_przyszlych = []



for _,mecz in df_predykcja.iterrows():


    id_grupy = int(
        mecz["id_grupy"]
    )


    wynik = str(
        mecz["wynik_predykcji"]
    )


    pewnosc = float(
        mecz["pewnosc"]
    )



    wiedza = analiza_klas.get(

        str(id_grupy),

        {}

    )



    pewnosc_klasy = analiza_pewnosci_klasy.get(

        str(id_grupy),

        {}

    )



    odchylenie = analiza_odchylen.get(

        str(id_grupy),

        {}

    )


    analiza_przyszlych.append(


        {


            "id_meczu":

            mecz["id_meczu"],



            "id_grupy":

            id_grupy,



            "wynik_predykcji":

            wynik,



            "pewnosc":

            pewnosc,



            "historyczna_skutecznosc_klasy":

            wiedza.get(

                "skutecznosc",

                0

            ),



            "najczestszy_realny_wynik":

            (
                max(

                    wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ),

                    key=wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ).get

                )

                if wiedza.get(

                    "rzeczywisty_rozkład"

                )

                else None
            ),



            "czy_odwrócony_wzorzec":

            odchylenie.get(

                "czy_odwrócony_wzorzec",

                False

            )

        }

    )




df_analiza_predykcji = pd.DataFrame(

    analiza_przyszlych

)



df_analiza_predykcji.to_csv(


    os.path.join(

        KATALOG_LABORATORIUM,

        "analiza_przyszlych_predykcji.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)




# =====================================================
# KOLEKTOR WIEDZY
# =====================================================


kolektor_wiedzy = {


    "model":

    NAZWA_MODELU,



    "data":

    datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    ),



    "ocena_modelu":

    ocena_modelu,



    "analiza_klas":

    analiza_klas,



    "analiza_pewnosci":

    analiza_pewnosci,



    "analiza_pewnosci_klasy":

    analiza_pewnosci_klasy,



    "analiza_odchylen":

    analiza_odchylen,



    "analiza_pamieci":

    analiza_pamieci

}




# =====================================================
# ZAPIS JSON
# =====================================================


pliki_json = {


    "analiza_klas.json":

    analiza_klas,


    "analiza_pewnosci.json":

    analiza_pewnosci,


    "analiza_pewnosci_klasy.json":

    analiza_pewnosci_klasy,


    "analiza_odchylen.json":

    analiza_odchylen,


    "analiza_pamieci.json":

    analiza_pamieci,


    "kolektor_wiedzy.json":

    kolektor_wiedzy

}




for nazwa,dane in pliki_json.items():


    with open(

        os.path.join(

            KATALOG_LABORATORIUM,

            nazwa

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            dane,

            f,

            indent=4,

            ensure_ascii=False

        )




# =====================================================
# RAPORT KOŃCOWY
# =====================================================


print()
print("======================================")
print("LABORATORIUM V2 ZAKOŃCZONE")
print("======================================")


print(
    "Model:",
    NAZWA_MODELU
)


print(
    "Katalog:",
    KATALOG_LABORATORIUM
)


print(
    "Analizowane mecze:",
    len(df_historia)
)


print(
    "Przyszłe predykcje:",
    len(df_predykcja)
)


print(
    "Pamięć:",
    len(pamiec_obserwacji)
)


print()
print("Utworzono:")

for plik in pliki_json:

    print(
        "-",
        plik
    )


print(
    "- analiza_przyszlych_predykcji.csv"
)

print()
print("======================================")




# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime

from tensorflow.keras.models import load_model



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = r"modele_dataBase_futbol_trend\dataBase_futbol_trend"


PLIK_PREDYKCJI = r"dane\dataBase_futbol_trend.csv"


PLIK_HISTORIA = r"dane\kod_dataBase_futbol_trend.csv"



KATALOG_OBSERWACJI = os.path.join(
    KATALOG_MODELU,
    "obserwacja"
)


KATALOG_PREDYKCJI = os.path.join(
    KATALOG_MODELU,
    "predykcje"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_OBSERWACJI,
    "pamiec_obserwacji.json"
)



PLIK_OCENA = os.path.join(
    KATALOG_OBSERWACJI,
    "ocena.json"
)



os.makedirs(
    KATALOG_OBSERWACJI,
    exist_ok=True
)



os.makedirs(
    KATALOG_PREDYKCJI,
    exist_ok=True
)





# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "metadata.json"
    ),

    encoding="utf-8"

) as f:

    metadata = json.load(f)



CECHY = metadata["cechy"]


NAZWA_MODELU = metadata["nazwa"]





# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "klasy.json"
    ),

    encoding="utf-8"

) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v): k

    for k,v in klasy.items()

}





# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================


df_pred = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



INDEX_MAP = {


    kolumna:index

    for index,kolumna

    in enumerate(df_pred.columns)

}



print("MAPA CECH")

print(INDEX_MAP)





# =====================================================
# CECHY MODELU
# =====================================================


INDEX_CECH = []



for cecha in CECHY:


    if cecha not in INDEX_MAP:


        raise Exception(

            f"Brak cechy modelu: {cecha}"

        )


    INDEX_CECH.append(

        INDEX_MAP[cecha]

    )



print(

    "Cechy modelu:",

    INDEX_CECH

)





# =====================================================
# AKTUALNE MECZE DO PREDYKCJI
# =====================================================


NAZWY_PREDYKCJI = (

    df_pred["id_meczu"]

    .astype(str)

    .tolist()

)



X_PREDYKCJA = df_pred.iloc[

    :,

    INDEX_CECH

]



X_PREDYKCJA = np.nan_to_num(

    X_PREDYKCJA.values

)





# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


hist = pd.read_csv(

    PLIK_HISTORIA,

    sep=";",

    header=None,

    encoding="utf-8"

)



NAZWY_HISTORIA = hist.iloc[:,0].astype(str)



X_HISTORIA = hist.iloc[

    :,

    INDEX_CECH

]



Y_HISTORIA = hist.iloc[:,-1]



X_HISTORIA = np.nan_to_num(

    X_HISTORIA.values

)





# =====================================================
# WCZYTANIE MODELU
# =====================================================


model = load_model(

    os.path.join(

        KATALOG_MODELU,

        "model.h5"

    )

)





# =====================================================
# PREDYKCJA HISTORII
# =====================================================


print(
    "Analiza historii..."
)



pred_hist = model.predict(

    X_HISTORIA

)



klasy_pred_hist = np.argmax(

    pred_hist,

    axis=1

)





# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================


print(

    "Analiza aktualnych meczów..."

)



pred = model.predict(

    X_PREDYKCJA

)



klasy_pred = np.argmax(

    pred,

    axis=1

)





# =====================================================
# WCZYTANIE PAMIĘCI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:


        pamiec_obserwacji = json.load(f)



else:


    pamiec_obserwacji = {}





# =====================================================
# WCZYTANIE OCENY
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:


        ocena = json.load(f)



else:


    ocena = {


        "model":

        NAZWA_MODELU,


        "ocena_ogolna":

        {

            "ilosc":

            0,


            "trafienia":

            0

        },


        "ocena_wynikow":

        {}

    }





# =====================================================
# STRUKTURY SESJI
# =====================================================


czas = datetime.now().strftime(

    "%Y-%m-%d %H:%M:%S"

)



nowe_obserwacje = []


nowe_predykcje = []


nowa_historia = []




analiza = {}



for wynik in klasy.keys():


    analiza[wynik] = {


        "ilosc_wystapien":0,


        "trafienia":0,


        "bledy":{}

    }




print(

    "Przygotowano dane."

)
# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 2/2
# =====================================================



# =====================================================
# ANALIZA HISTORII Z WYNIKAMI
# =====================================================


for i,p in enumerate(klasy_pred_hist):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    real_wynik = str(
        Y_HISTORIA.iloc[i]
    )


    nazwa_meczu = str(
        NAZWY_HISTORIA.iloc[i]
    )


    pewnosc = float(
        np.max(pred_hist[i])
    )


    trafienie = (
        pred_wynik == real_wynik
    )



    obserwacja = {


        "data":

        czas,


        "model":

        NAZWA_MODELU,


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "predykcja":

        pred_wynik,


        "wynik_rzeczywisty":

        real_wynik,


        "pewnosc":

        pewnosc,


        "trafienie":

        trafienie

    }





    # =========================================
    # AKTUALIZACJA PAMIĘCI MECZU
    # =========================================


    if nazwa_meczu not in pamiec_obserwacji:


        pamiec_obserwacji[nazwa_meczu] = []



        obserwacja["pierwsza_obserwacja"] = True



    else:


        ostatnia = pamiec_obserwacji[nazwa_meczu][-1]



        if ostatnia["predykcja"] != pred_wynik:


            obserwacja["zmiana_predykcji"] = {


                "stara":

                ostatnia["predykcja"],


                "nowa":

                pred_wynik

            }



        if ostatnia["pewnosc"] != pewnosc:


            obserwacja["zmiana_pewnosci"] = {


                "stara":

                ostatnia["pewnosc"],


                "nowa":

                pewnosc

            }





    pamiec_obserwacji[nazwa_meczu].append(

        obserwacja

    )



    nowe_obserwacje.append(

        obserwacja

    )





    # statystyka klasy


    analiza[pred_wynik]["ilosc_wystapien"] += 1



    if trafienie:


        analiza[pred_wynik]["trafienia"] += 1


    else:


        if real_wynik not in analiza[pred_wynik]["bledy"]:


            analiza[pred_wynik]["bledy"][real_wynik] = 0



        analiza[pred_wynik]["bledy"][real_wynik] += 1







# =====================================================
# AKTUALNE MECZE BEZ WYNIKU
# =====================================================


for i,p in enumerate(klasy_pred):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    nazwa_meczu = str(

        NAZWY_PREDYKCJI[i]

    )


    pewnosc = float(

        np.max(pred[i])

    )



    predykcja = {


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "wynik_predykcji":

        pred_wynik,


        "pewnosc":

        pewnosc

    }



    nowe_predykcje.append(

        predykcja

    )







# =====================================================
# AKTUALIZACJA OCENY MODELU
# =====================================================


ilosc_globalna = 0

trafienia_globalne = 0



ocena_wynikow = {}



for wynik,dane in analiza.items():


    ilosc = dane["ilosc_wystapien"]


    trafienia = dane["trafienia"]



    ilosc_globalna += ilosc


    trafienia_globalne += trafienia



    ocena_wynikow[wynik] = {


        "ilosc_predykcji":

        ilosc,


        "trafienia":

        trafienia,


        "skutecznosc":

        (

            trafienia / ilosc

            if ilosc > 0

            else 0

        ),


        "bledy":

        dane["bledy"]

    }





ocena = {


    "model":

    NAZWA_MODELU,


    "data":

    czas,


    "ocena_ogolna":{


        "ilosc_meczow":

        ilosc_globalna,


        "trafienia":

        trafienia_globalne,


        "skutecznosc":

        (

            trafienia_globalne /

            ilosc_globalna

            if ilosc_globalna > 0

            else 0

        )

    },


    "ocena_wynikow":

    ocena_wynikow

}







# =====================================================
# ZAPIS PAMIĘCI
# =====================================================


with open(

    PLIK_PAMIEC,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        pamiec_obserwacji,

        f,

        indent=4,

        ensure_ascii=False

    )





# =====================================================
# ZAPIS OCENY
# =====================================================


with open(

    PLIK_OCENA,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        ocena,

        f,

        indent=4,

        ensure_ascii=False

    )







# =====================================================
# ZAPIS AKTUALNEJ PREDYKCJI
# =====================================================


pd.DataFrame(

    nowe_predykcje

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







# =====================================================
# ZAPIS HISTORII Z WYNIKAMI
# =====================================================


historia_csv = []



for mecz,lista in pamiec_obserwacji.items():


    ostatnia = lista[-1]


    historia_csv.append(


        {


            "id_meczu":

            mecz,


            "id_grupy":

            ostatnia["id_grupy"],


            "wynik_predykcji":

            ostatnia["predykcja"],


            "pewnosc":

            ostatnia["pewnosc"],


            "wynik_rzeczywisty":

            ostatnia["wynik_rzeczywisty"]

        }

    )







pd.DataFrame(

    historia_csv

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







print()

print("================================")

print("ZAKOŃCZONO")

print("================================")



print(

    "Pamięć:",

    PLIK_PAMIEC

)



print(

    "Ocena:",

    PLIK_OCENA

)



print(

    "Predykcje:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    )

)



print(

    "Historia:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    )

)
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = (
    r"modele_dataBase_futbol_trend"
    r"\dataBase_futbol_trend"
)


NAZWA_BAZY = "dataBase_futbol_trend"


NAZWA_MODELU = os.path.basename(
    KATALOG_MODELU
)



# =====================================================
# LABORATORIUM
# =====================================================


KATALOG_LABORATORIUM = os.path.join(
    "laboratorium",
    NAZWA_BAZY,
    NAZWA_MODELU
)



os.makedirs(
    KATALOG_LABORATORIUM,
    exist_ok=True
)



# =====================================================
# PLIKI WEJŚCIOWE
# =====================================================


PLIK_KLASY = os.path.join(
    KATALOG_MODELU,
    "klasy.json"
)



PLIK_PRED_WYNIK = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_z_wynikiem.csv"
)



PLIK_PRED_GRUPY = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_grupy.csv"
)



PLIK_OCENA = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "ocena.json"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "pamiec_obserwacji.json"
)




# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(
    PLIK_KLASY,
    encoding="utf-8"
) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v):k

    for k,v in klasy.items()

}



print(
    "Załadowano klas:",
    len(ID_NA_WYNIK)
)



# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


df_historia = pd.read_csv(

    PLIK_PRED_WYNIK,

    sep=";",

    encoding="utf-8"

)



print(
    "Historia:",
    len(df_historia)
)



# =====================================================
# WCZYTANIE AKTUALNYCH PREDYKCJI
# =====================================================


df_predykcja = pd.read_csv(

    PLIK_PRED_GRUPY,

    sep=";",

    encoding="utf-8"

)



print(
    "Aktualne predykcje:",
    len(df_predykcja)
)



# =====================================================
# WCZYTANIE OCENY MODELU
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:

        ocena_modelu = json.load(f)


else:


    ocena_modelu = {}




# =====================================================
# WCZYTANIE PAMIĘCI OBSERWACJI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:

        pamiec_obserwacji = json.load(f)


else:


    pamiec_obserwacji = {}




print(
    "Pamięć obserwacji:",
    len(pamiec_obserwacji)
)




# =====================================================
# ANALIZA KLAS
# =====================================================


analiza_klas = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    ilosc = len(dane)



    if ilosc == 0:


        analiza_klas[str(id_grupy)] = {


            "wynik":

            wynik,


            "ilosc_predykcji":

            0,


            "trafienia":

            0,


            "skutecznosc":

            0,


            "rzeczywisty_rozkład":

            {}

        }


        continue




    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()




    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )




    analiza_klas[str(id_grupy)] = {


        "wynik":

        wynik,


        "ilosc_predykcji":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        ),



        "rzeczywisty_rozkład":

        rozklad

    }




# =====================================================
# ANALIZA PEWNOŚCI DYNAMICZNA
# =====================================================


analiza_pewnosci = {}




df_historia = df_historia.sort_values(
    "pewnosc"
)




# 10 równych grup według ilości danych

df_historia["koszyk_pewnosci"] = pd.qcut(

    df_historia["pewnosc"],

    q=10,

    duplicates="drop"

)




for koszyk, dane in df_historia.groupby(

    "koszyk_pewnosci",

    observed=True

):


    ilosc = len(dane)



    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()



    analiza_pewnosci[str(koszyk)] = {


        "ilosc":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        )

    }




# =====================================================
# ANALIZA PEWNOŚCI DLA KAŻDEJ KLASY
# =====================================================


analiza_pewnosci_klasy = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane_klasy = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    if len(dane_klasy) == 0:

        continue




    dane_klasy = dane_klasy.copy()



    dane_klasy["koszyk"] = pd.qcut(

        dane_klasy["pewnosc"],

        q=10,

        duplicates="drop"

    )



    koszyki = {}



    for koszyk,dane in dane_klasy.groupby(

        "koszyk",

        observed=True

    ):



        ilosc = len(dane)



        trafienia = (

            dane["wynik_predykcji"]

            ==

            dane["wynik_rzeczywisty"]

        ).sum()



        koszyki[str(koszyk)] = {


            "ilosc":

            int(ilosc),


            "trafienia":

            int(trafienia),


            "skutecznosc":

            float(

                trafienia / ilosc

            )

        }




    analiza_pewnosci_klasy[str(id_grupy)] = {


        "wynik":

        wynik,


        "progi_pewnosci":

        koszyki

    }




# KONIEC FRAGMENTU 1/2
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 2/2
# =====================================================


# =====================================================
# ANALIZA ODCHYLEŃ
# (CO SIEĆ TYPOWAŁA VS CO FAKTYCZNIE WYPADŁO)
# =====================================================


analiza_odchylen = {}



for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]


    if len(dane) == 0:

        continue



    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )



    uporzadkowane = sorted(

        rozklad.items(),

        key=lambda x:x[1],

        reverse=True

    )



    analiza_odchylen[str(id_grupy)] = {


        "wynik_typowany":

        wynik,


        "ilosc":

        int(len(dane)),


        "najczestsze_wyniki_rzeczywiste":

        dict(uporzadkowane[:10]),


        "czy_odwrócony_wzorzec":

        (
            uporzadkowane[0][0] != wynik
            if len(uporzadkowane)>0
            else False
        )

    }




# =====================================================
# ANALIZA PAMIĘCI OBSERWACJI
# =====================================================


analiza_pamieci = {


    "ilosc_meczow":

    len(pamiec_obserwacji),


    "zmiany_predykcji":0,


    "pierwsze_obserwacje":0

}



for mecz, obserwacje in pamiec_obserwacji.items():


    for obs in obserwacje:


        if obs.get(
            "pierwsza_obserwacja"
        ):

            analiza_pamieci[
                "pierwsze_obserwacje"
            ] += 1



        if obs.get(
            "zmiana_predykcji"
        ):

            analiza_pamieci[
                "zmiany_predykcji"
            ] += 1




# =====================================================
# ANALIZA AKTUALNYCH PREDYKCJI
# =====================================================


analiza_przyszlych = []



for _,mecz in df_predykcja.iterrows():


    id_grupy = int(
        mecz["id_grupy"]
    )


    wynik = str(
        mecz["wynik_predykcji"]
    )


    pewnosc = float(
        mecz["pewnosc"]
    )



    wiedza = analiza_klas.get(

        str(id_grupy),

        {}

    )



    pewnosc_klasy = analiza_pewnosci_klasy.get(

        str(id_grupy),

        {}

    )



    odchylenie = analiza_odchylen.get(

        str(id_grupy),

        {}

    )


    analiza_przyszlych.append(


        {


            "id_meczu":

            mecz["id_meczu"],



            "id_grupy":

            id_grupy,



            "wynik_predykcji":

            wynik,



            "pewnosc":

            pewnosc,



            "historyczna_skutecznosc_klasy":

            wiedza.get(

                "skutecznosc",

                0

            ),



            "najczestszy_realny_wynik":

            (
                max(

                    wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ),

                    key=wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ).get

                )

                if wiedza.get(

                    "rzeczywisty_rozkład"

                )

                else None
            ),



            "czy_odwrócony_wzorzec":

            odchylenie.get(

                "czy_odwrócony_wzorzec",

                False

            )

        }

    )




df_analiza_predykcji = pd.DataFrame(

    analiza_przyszlych

)



df_analiza_predykcji.to_csv(


    os.path.join(

        KATALOG_LABORATORIUM,

        "analiza_przyszlych_predykcji.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)




# =====================================================
# KOLEKTOR WIEDZY
# =====================================================


kolektor_wiedzy = {


    "model":

    NAZWA_MODELU,



    "data":

    datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    ),



    "ocena_modelu":

    ocena_modelu,



    "analiza_klas":

    analiza_klas,



    "analiza_pewnosci":

    analiza_pewnosci,



    "analiza_pewnosci_klasy":

    analiza_pewnosci_klasy,



    "analiza_odchylen":

    analiza_odchylen,



    "analiza_pamieci":

    analiza_pamieci

}




# =====================================================
# ZAPIS JSON
# =====================================================


pliki_json = {


    "analiza_klas.json":

    analiza_klas,


    "analiza_pewnosci.json":

    analiza_pewnosci,


    "analiza_pewnosci_klasy.json":

    analiza_pewnosci_klasy,


    "analiza_odchylen.json":

    analiza_odchylen,


    "analiza_pamieci.json":

    analiza_pamieci,


    "kolektor_wiedzy.json":

    kolektor_wiedzy

}




for nazwa,dane in pliki_json.items():


    with open(

        os.path.join(

            KATALOG_LABORATORIUM,

            nazwa

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            dane,

            f,

            indent=4,

            ensure_ascii=False

        )




# =====================================================
# RAPORT KOŃCOWY
# =====================================================


print()
print("======================================")
print("LABORATORIUM V2 ZAKOŃCZONE")
print("======================================")


print(
    "Model:",
    NAZWA_MODELU
)


print(
    "Katalog:",
    KATALOG_LABORATORIUM
)


print(
    "Analizowane mecze:",
    len(df_historia)
)


print(
    "Przyszłe predykcje:",
    len(df_predykcja)
)


print(
    "Pamięć:",
    len(pamiec_obserwacji)
)


print()
print("Utworzono:")

for plik in pliki_json:

    print(
        "-",
        plik
    )


print(
    "- analiza_przyszlych_predykcji.csv"
)

print()
print("======================================")






# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime

from tensorflow.keras.models import load_model



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = r"modele_kursy_przygotowane\kursy_przygotowane"


PLIK_PREDYKCJI = r"dane\kursy_przygotowane.csv"


PLIK_HISTORIA = r"dane\mozg_kursy_przygotowane.csv"



KATALOG_OBSERWACJI = os.path.join(
    KATALOG_MODELU,
    "obserwacja"
)


KATALOG_PREDYKCJI = os.path.join(
    KATALOG_MODELU,
    "predykcje"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_OBSERWACJI,
    "pamiec_obserwacji.json"
)



PLIK_OCENA = os.path.join(
    KATALOG_OBSERWACJI,
    "ocena.json"
)



os.makedirs(
    KATALOG_OBSERWACJI,
    exist_ok=True
)



os.makedirs(
    KATALOG_PREDYKCJI,
    exist_ok=True
)





# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "metadata.json"
    ),

    encoding="utf-8"

) as f:

    metadata = json.load(f)



CECHY = metadata["cechy"]


NAZWA_MODELU = metadata["nazwa"]





# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(

    os.path.join(
        KATALOG_MODELU,
        "klasy.json"
    ),

    encoding="utf-8"

) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v): k

    for k,v in klasy.items()

}





# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================


df_pred = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



INDEX_MAP = {


    kolumna:index

    for index,kolumna

    in enumerate(df_pred.columns)

}



print("MAPA CECH")

print(INDEX_MAP)





# =====================================================
# CECHY MODELU
# =====================================================


INDEX_CECH = []



for cecha in CECHY:


    if cecha not in INDEX_MAP:


        raise Exception(

            f"Brak cechy modelu: {cecha}"

        )


    INDEX_CECH.append(

        INDEX_MAP[cecha]

    )



print(

    "Cechy modelu:",

    INDEX_CECH

)





# =====================================================
# AKTUALNE MECZE DO PREDYKCJI
# =====================================================


NAZWY_PREDYKCJI = (

    df_pred["mecz"]

    .astype(str)

    .tolist()

)



X_PREDYKCJA = df_pred.iloc[

    :,

    INDEX_CECH

]



X_PREDYKCJA = np.nan_to_num(

    X_PREDYKCJA.values

)





# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


hist = pd.read_csv(

    PLIK_HISTORIA,

    sep=";",

    header=None,

    encoding="utf-8"

)



NAZWY_HISTORIA = hist.iloc[:,0].astype(str)



X_HISTORIA = hist.iloc[

    :,

    INDEX_CECH

]



Y_HISTORIA = hist.iloc[:,-1]



X_HISTORIA = np.nan_to_num(

    X_HISTORIA.values

)





# =====================================================
# WCZYTANIE MODELU
# =====================================================


model = load_model(

    os.path.join(

        KATALOG_MODELU,

        "model.h5"

    )

)





# =====================================================
# PREDYKCJA HISTORII
# =====================================================


print(
    "Analiza historii..."
)



pred_hist = model.predict(

    X_HISTORIA

)



klasy_pred_hist = np.argmax(

    pred_hist,

    axis=1

)





# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================


print(

    "Analiza aktualnych meczów..."

)



pred = model.predict(

    X_PREDYKCJA

)



klasy_pred = np.argmax(

    pred,

    axis=1

)





# =====================================================
# WCZYTANIE PAMIĘCI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:


        pamiec_obserwacji = json.load(f)



else:


    pamiec_obserwacji = {}





# =====================================================
# WCZYTANIE OCENY
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:


        ocena = json.load(f)



else:


    ocena = {


        "model":

        NAZWA_MODELU,


        "ocena_ogolna":

        {

            "ilosc":

            0,


            "trafienia":

            0

        },


        "ocena_wynikow":

        {}

    }





# =====================================================
# STRUKTURY SESJI
# =====================================================


czas = datetime.now().strftime(

    "%Y-%m-%d %H:%M:%S"

)



nowe_obserwacje = []


nowe_predykcje = []


nowa_historia = []




analiza = {}



for wynik in klasy.keys():


    analiza[wynik] = {


        "ilosc_wystapien":0,


        "trafienia":0,


        "bledy":{}

    }




print(

    "Przygotowano dane."

)
# =====================================================
# GENERATOR ANALIZY TRENDÓW + PAMIĘĆ OBSERWACJI
# CZĘŚĆ 2/2
# =====================================================



# =====================================================
# ANALIZA HISTORII Z WYNIKAMI
# =====================================================


for i,p in enumerate(klasy_pred_hist):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    real_wynik = str(
        Y_HISTORIA.iloc[i]
    )


    nazwa_meczu = str(
        NAZWY_HISTORIA.iloc[i]
    )


    pewnosc = float(
        np.max(pred_hist[i])
    )


    trafienie = (
        pred_wynik == real_wynik
    )



    obserwacja = {


        "data":

        czas,


        "model":

        NAZWA_MODELU,


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "predykcja":

        pred_wynik,


        "wynik_rzeczywisty":

        real_wynik,


        "pewnosc":

        pewnosc,


        "trafienie":

        trafienie

    }





    # =========================================
    # AKTUALIZACJA PAMIĘCI MECZU
    # =========================================


    if nazwa_meczu not in pamiec_obserwacji:


        pamiec_obserwacji[nazwa_meczu] = []



        obserwacja["pierwsza_obserwacja"] = True



    else:


        ostatnia = pamiec_obserwacji[nazwa_meczu][-1]



        if ostatnia["predykcja"] != pred_wynik:


            obserwacja["zmiana_predykcji"] = {


                "stara":

                ostatnia["predykcja"],


                "nowa":

                pred_wynik

            }



        if ostatnia["pewnosc"] != pewnosc:


            obserwacja["zmiana_pewnosci"] = {


                "stara":

                ostatnia["pewnosc"],


                "nowa":

                pewnosc

            }





    pamiec_obserwacji[nazwa_meczu].append(

        obserwacja

    )



    nowe_obserwacje.append(

        obserwacja

    )





    # statystyka klasy


    analiza[pred_wynik]["ilosc_wystapien"] += 1



    if trafienie:


        analiza[pred_wynik]["trafienia"] += 1


    else:


        if real_wynik not in analiza[pred_wynik]["bledy"]:


            analiza[pred_wynik]["bledy"][real_wynik] = 0



        analiza[pred_wynik]["bledy"][real_wynik] += 1







# =====================================================
# AKTUALNE MECZE BEZ WYNIKU
# =====================================================


for i,p in enumerate(klasy_pred):


    grupa = int(p)


    pred_wynik = ID_NA_WYNIK[grupa]


    nazwa_meczu = str(

        NAZWY_PREDYKCJI[i]

    )


    pewnosc = float(

        np.max(pred[i])

    )



    predykcja = {


        "id_meczu":

        nazwa_meczu,


        "id_grupy":

        grupa,


        "wynik_predykcji":

        pred_wynik,


        "pewnosc":

        pewnosc

    }



    nowe_predykcje.append(

        predykcja

    )







# =====================================================
# AKTUALIZACJA OCENY MODELU
# =====================================================


ilosc_globalna = 0

trafienia_globalne = 0



ocena_wynikow = {}



for wynik,dane in analiza.items():


    ilosc = dane["ilosc_wystapien"]


    trafienia = dane["trafienia"]



    ilosc_globalna += ilosc


    trafienia_globalne += trafienia



    ocena_wynikow[wynik] = {


        "ilosc_predykcji":

        ilosc,


        "trafienia":

        trafienia,


        "skutecznosc":

        (

            trafienia / ilosc

            if ilosc > 0

            else 0

        ),


        "bledy":

        dane["bledy"]

    }





ocena = {


    "model":

    NAZWA_MODELU,


    "data":

    czas,


    "ocena_ogolna":{


        "ilosc_meczow":

        ilosc_globalna,


        "trafienia":

        trafienia_globalne,


        "skutecznosc":

        (

            trafienia_globalne /

            ilosc_globalna

            if ilosc_globalna > 0

            else 0

        )

    },


    "ocena_wynikow":

    ocena_wynikow

}







# =====================================================
# ZAPIS PAMIĘCI
# =====================================================


with open(

    PLIK_PAMIEC,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        pamiec_obserwacji,

        f,

        indent=4,

        ensure_ascii=False

    )





# =====================================================
# ZAPIS OCENY
# =====================================================


with open(

    PLIK_OCENA,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        ocena,

        f,

        indent=4,

        ensure_ascii=False

    )







# =====================================================
# ZAPIS AKTUALNEJ PREDYKCJI
# =====================================================


pd.DataFrame(

    nowe_predykcje

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







# =====================================================
# ZAPIS HISTORII Z WYNIKAMI
# =====================================================


historia_csv = []



for mecz,lista in pamiec_obserwacji.items():


    ostatnia = lista[-1]


    historia_csv.append(


        {


            "id_meczu":

            mecz,


            "id_grupy":

            ostatnia["id_grupy"],


            "wynik_predykcji":

            ostatnia["predykcja"],


            "pewnosc":

            ostatnia["pewnosc"],


            "wynik_rzeczywisty":

            ostatnia["wynik_rzeczywisty"]

        }

    )







pd.DataFrame(

    historia_csv

).to_csv(


    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)







print()

print("================================")

print("ZAKOŃCZONO")

print("================================")



print(

    "Pamięć:",

    PLIK_PAMIEC

)



print(

    "Ocena:",

    PLIK_OCENA

)



print(

    "Predykcje:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_grupy.csv"

    )

)



print(

    "Historia:",

    os.path.join(

        KATALOG_PREDYKCJI,

        "predykcja_z_wynikiem.csv"

    )

)
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 1/2
# =====================================================


import os
import json
import pandas as pd
import numpy as np

from datetime import datetime



# =====================================================
# KONFIGURACJA
# =====================================================


KATALOG_MODELU = (
    r"modele_kursy_przygotowane"
    r"\kursy_przygotowane"
)


NAZWA_BAZY = "kursy_przygotowane"


NAZWA_MODELU = os.path.basename(
    KATALOG_MODELU
)



# =====================================================
# LABORATORIUM
# =====================================================


KATALOG_LABORATORIUM = os.path.join(
    "laboratorium",
    NAZWA_BAZY,
    NAZWA_MODELU
)



os.makedirs(
    KATALOG_LABORATORIUM,
    exist_ok=True
)



# =====================================================
# PLIKI WEJŚCIOWE
# =====================================================


PLIK_KLASY = os.path.join(
    KATALOG_MODELU,
    "klasy.json"
)



PLIK_PRED_WYNIK = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_z_wynikiem.csv"
)



PLIK_PRED_GRUPY = os.path.join(
    KATALOG_MODELU,
    "predykcje",
    "predykcja_grupy.csv"
)



PLIK_OCENA = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "ocena.json"
)



PLIK_PAMIEC = os.path.join(
    KATALOG_MODELU,
    "obserwacja",
    "pamiec_obserwacji.json"
)




# =====================================================
# WCZYTANIE KLAS
# =====================================================


with open(
    PLIK_KLASY,
    encoding="utf-8"
) as f:

    klasy = json.load(f)



ID_NA_WYNIK = {

    int(v):k

    for k,v in klasy.items()

}



print(
    "Załadowano klas:",
    len(ID_NA_WYNIK)
)



# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================


df_historia = pd.read_csv(

    PLIK_PRED_WYNIK,

    sep=";",

    encoding="utf-8"

)



print(
    "Historia:",
    len(df_historia)
)



# =====================================================
# WCZYTANIE AKTUALNYCH PREDYKCJI
# =====================================================


df_predykcja = pd.read_csv(

    PLIK_PRED_GRUPY,

    sep=";",

    encoding="utf-8"

)



print(
    "Aktualne predykcje:",
    len(df_predykcja)
)



# =====================================================
# WCZYTANIE OCENY MODELU
# =====================================================


if os.path.exists(PLIK_OCENA):


    with open(

        PLIK_OCENA,

        encoding="utf-8"

    ) as f:

        ocena_modelu = json.load(f)


else:


    ocena_modelu = {}




# =====================================================
# WCZYTANIE PAMIĘCI OBSERWACJI
# =====================================================


if os.path.exists(PLIK_PAMIEC):


    with open(

        PLIK_PAMIEC,

        encoding="utf-8"

    ) as f:

        pamiec_obserwacji = json.load(f)


else:


    pamiec_obserwacji = {}




print(
    "Pamięć obserwacji:",
    len(pamiec_obserwacji)
)




# =====================================================
# ANALIZA KLAS
# =====================================================


analiza_klas = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    ilosc = len(dane)



    if ilosc == 0:


        analiza_klas[str(id_grupy)] = {


            "wynik":

            wynik,


            "ilosc_predykcji":

            0,


            "trafienia":

            0,


            "skutecznosc":

            0,


            "rzeczywisty_rozkład":

            {}

        }


        continue




    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()




    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )




    analiza_klas[str(id_grupy)] = {


        "wynik":

        wynik,


        "ilosc_predykcji":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        ),



        "rzeczywisty_rozkład":

        rozklad

    }




# =====================================================
# ANALIZA PEWNOŚCI DYNAMICZNA
# =====================================================


analiza_pewnosci = {}




df_historia = df_historia.sort_values(
    "pewnosc"
)




# 10 równych grup według ilości danych

df_historia["koszyk_pewnosci"] = pd.qcut(

    df_historia["pewnosc"],

    q=10,

    duplicates="drop"

)




for koszyk, dane in df_historia.groupby(

    "koszyk_pewnosci",

    observed=True

):


    ilosc = len(dane)



    trafienia = (

        dane["wynik_predykcji"]

        ==

        dane["wynik_rzeczywisty"]

    ).sum()



    analiza_pewnosci[str(koszyk)] = {


        "ilosc":

        int(ilosc),


        "trafienia":

        int(trafienia),


        "skutecznosc":

        float(

            trafienia / ilosc

        )

    }




# =====================================================
# ANALIZA PEWNOŚCI DLA KAŻDEJ KLASY
# =====================================================


analiza_pewnosci_klasy = {}




for id_grupy, wynik in ID_NA_WYNIK.items():


    dane_klasy = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]



    if len(dane_klasy) == 0:

        continue




    dane_klasy = dane_klasy.copy()



    dane_klasy["koszyk"] = pd.qcut(

        dane_klasy["pewnosc"],

        q=10,

        duplicates="drop"

    )



    koszyki = {}



    for koszyk,dane in dane_klasy.groupby(

        "koszyk",

        observed=True

    ):



        ilosc = len(dane)



        trafienia = (

            dane["wynik_predykcji"]

            ==

            dane["wynik_rzeczywisty"]

        ).sum()



        koszyki[str(koszyk)] = {


            "ilosc":

            int(ilosc),


            "trafienia":

            int(trafienia),


            "skutecznosc":

            float(

                trafienia / ilosc

            )

        }




    analiza_pewnosci_klasy[str(id_grupy)] = {


        "wynik":

        wynik,


        "progi_pewnosci":

        koszyki

    }




# KONIEC FRAGMENTU 1/2
# =====================================================
# LABORATORIUM V2
# ANALIZA PAMIĘCI + PEWNOŚCI + KLAS + PREDYKCJI
# FRAGMENT 2/2
# =====================================================


# =====================================================
# ANALIZA ODCHYLEŃ
# (CO SIEĆ TYPOWAŁA VS CO FAKTYCZNIE WYPADŁO)
# =====================================================


analiza_odchylen = {}



for id_grupy, wynik in ID_NA_WYNIK.items():


    dane = df_historia[

        df_historia["id_grupy"]

        ==

        id_grupy

    ]


    if len(dane) == 0:

        continue



    rozklad = (

        dane["wynik_rzeczywisty"]

        .value_counts(normalize=True)

        .to_dict()

    )



    uporzadkowane = sorted(

        rozklad.items(),

        key=lambda x:x[1],

        reverse=True

    )



    analiza_odchylen[str(id_grupy)] = {


        "wynik_typowany":

        wynik,


        "ilosc":

        int(len(dane)),


        "najczestsze_wyniki_rzeczywiste":

        dict(uporzadkowane[:10]),


        "czy_odwrócony_wzorzec":

        (
            uporzadkowane[0][0] != wynik
            if len(uporzadkowane)>0
            else False
        )

    }




# =====================================================
# ANALIZA PAMIĘCI OBSERWACJI
# =====================================================


analiza_pamieci = {


    "ilosc_meczow":

    len(pamiec_obserwacji),


    "zmiany_predykcji":0,


    "pierwsze_obserwacje":0

}



for mecz, obserwacje in pamiec_obserwacji.items():


    for obs in obserwacje:


        if obs.get(
            "pierwsza_obserwacja"
        ):

            analiza_pamieci[
                "pierwsze_obserwacje"
            ] += 1



        if obs.get(
            "zmiana_predykcji"
        ):

            analiza_pamieci[
                "zmiany_predykcji"
            ] += 1




# =====================================================
# ANALIZA AKTUALNYCH PREDYKCJI
# =====================================================


analiza_przyszlych = []



for _,mecz in df_predykcja.iterrows():


    id_grupy = int(
        mecz["id_grupy"]
    )


    wynik = str(
        mecz["wynik_predykcji"]
    )


    pewnosc = float(
        mecz["pewnosc"]
    )



    wiedza = analiza_klas.get(

        str(id_grupy),

        {}

    )



    pewnosc_klasy = analiza_pewnosci_klasy.get(

        str(id_grupy),

        {}

    )



    odchylenie = analiza_odchylen.get(

        str(id_grupy),

        {}

    )


    analiza_przyszlych.append(


        {


            "id_meczu":

            mecz["id_meczu"],



            "id_grupy":

            id_grupy,



            "wynik_predykcji":

            wynik,



            "pewnosc":

            pewnosc,



            "historyczna_skutecznosc_klasy":

            wiedza.get(

                "skutecznosc",

                0

            ),



            "najczestszy_realny_wynik":

            (
                max(

                    wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ),

                    key=wiedza.get(

                        "rzeczywisty_rozkład",

                        {}

                    ).get

                )

                if wiedza.get(

                    "rzeczywisty_rozkład"

                )

                else None
            ),



            "czy_odwrócony_wzorzec":

            odchylenie.get(

                "czy_odwrócony_wzorzec",

                False

            )

        }

    )




df_analiza_predykcji = pd.DataFrame(

    analiza_przyszlych

)



df_analiza_predykcji.to_csv(


    os.path.join(

        KATALOG_LABORATORIUM,

        "analiza_przyszlych_predykcji.csv"

    ),


    sep=";",


    index=False,


    encoding="utf-8"

)




# =====================================================
# KOLEKTOR WIEDZY
# =====================================================


kolektor_wiedzy = {


    "model":

    NAZWA_MODELU,



    "data":

    datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    ),



    "ocena_modelu":

    ocena_modelu,



    "analiza_klas":

    analiza_klas,



    "analiza_pewnosci":

    analiza_pewnosci,



    "analiza_pewnosci_klasy":

    analiza_pewnosci_klasy,



    "analiza_odchylen":

    analiza_odchylen,



    "analiza_pamieci":

    analiza_pamieci

}




# =====================================================
# ZAPIS JSON
# =====================================================


pliki_json = {


    "analiza_klas.json":

    analiza_klas,


    "analiza_pewnosci.json":

    analiza_pewnosci,


    "analiza_pewnosci_klasy.json":

    analiza_pewnosci_klasy,


    "analiza_odchylen.json":

    analiza_odchylen,


    "analiza_pamieci.json":

    analiza_pamieci,


    "kolektor_wiedzy.json":

    kolektor_wiedzy

}




for nazwa,dane in pliki_json.items():


    with open(

        os.path.join(

            KATALOG_LABORATORIUM,

            nazwa

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            dane,

            f,

            indent=4,

            ensure_ascii=False

        )




# =====================================================
# RAPORT KOŃCOWY
# =====================================================


print()
print("======================================")
print("LABORATORIUM V2 ZAKOŃCZONE")
print("======================================")


print(
    "Model:",
    NAZWA_MODELU
)


print(
    "Katalog:",
    KATALOG_LABORATORIUM
)


print(
    "Analizowane mecze:",
    len(df_historia)
)


print(
    "Przyszłe predykcje:",
    len(df_predykcja)
)


print(
    "Pamięć:",
    len(pamiec_obserwacji)
)


print()
print("Utworzono:")

for plik in pliki_json:

    print(
        "-",
        plik
    )


print(
    "- analiza_przyszlych_predykcji.csv"
)

print()
print("======================================")




# -*- coding: utf-8 -*-

import os
import json
import shutil
from datetime import datetime
from statistics import mean


ROOTS = [

    r"D:\sts\aplikacjaTyperBetAi\modele_dataBase_futbol_trend",

    r"D:\sts\aplikacjaTyperBetAi\modele_kursy_przygotowane"

]


BACKUP_DIR = r"D:\sts\aplikacjaTyperBetAi\memory_backup"



class MemoryEngine:


    def __init__(self):

        self.start_time = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )



    def load_json(self, path):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)



    def save_json(self, path, data):

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )



    def backup(self, file):

        folder = os.path.join(
            BACKUP_DIR,
            self.start_time
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        shutil.copy2(
            file,
            folder
        )



    def parse_date(self, value):

        try:

            return datetime.strptime(
                value,
                "%Y-%m-%d %H:%M:%S"
            )

        except:

            return datetime.min



    # =====================================================
    # KONSOLIDACJA PAMIECI
    # =====================================================


    def compress_records(self, records):


        records = sorted(
            records,
            key=lambda x:
                self.parse_date(
                    x.get("data","")
                )
        )


        result = []


        current = None

        confidence_values = []



        for record in records:


            group = record.get(
                "id_grupy"
            )


            prediction = record.get(
                "predykcja"
            )


            confidence = record.get(
                "pewnosc",
                0
            )



            if current is None:


                current = record.copy()

                confidence_values = [
                    confidence
                ]

                continue



            same = (

                current.get("id_grupy")
                ==
                group

                and

                current.get("predykcja")
                ==
                prediction

            )



            if same:


                confidence_values.append(
                    confidence
                )


                current["pewnosc"] = round(
                    mean(confidence_values),
                    12
                )


                continue



            old_conf = round(
                mean(confidence_values),
                12
            )


            result.append(
                current
            )


            new_record = record.copy()



            if current.get("predykcja") != prediction:


                new_record["zmiana_predykcji"] = {

                    "stara":
                        current.get("predykcja"),

                    "nowa":
                        prediction

                }



            new_record["zmiana_pewnosci"] = {

                "stara":
                    old_conf,

                "nowa":
                    confidence

            }



            current = new_record


            confidence_values = [
                confidence
            ]



        if current:

            current["pewnosc"] = round(
                mean(confidence_values),
                12
            )

            result.append(
                current
            )


        return result



    # =====================================================
    # PROFIL MODELU
    # =====================================================


    def create_profile(self, name):

        return {

            "model": name,

            "ostatnia_obserwacja": None,

            "liczniki": {

                "mecze":0,

                "rekordy":0,

                "zmian":0

            },


            "grupy": {},


            "przejscia": {}

        }



    def normalize_profile(self, profile, name):


        profile.setdefault(
            "model",
            name
        )


        profile.setdefault(
            "ostatnia_obserwacja",
            None
        )


        profile.setdefault(
            "liczniki",
            {}
        )


        profile["liczniki"].setdefault(
            "mecze",
            0
        )

        profile["liczniki"].setdefault(
            "rekordy",
            0
        )

        profile["liczniki"].setdefault(
            "zmian",
            0
        )


        profile.setdefault(
            "grupy",
            {}
        )


        profile.setdefault(
            "przejscia",
            {}
        )


        return profile



    def update_profile(
            self,
            model_name,
            memory,
            profile_file
    ):


        if os.path.exists(profile_file):

            profile = self.load_json(
                profile_file
            )

            profile = self.normalize_profile(
                profile,
                model_name
            )

        else:

            profile = self.create_profile(
                model_name
            )



        newest_date = None



        for match, records in memory.items():


            previous = None



            for r in records:


                date = r.get(
                    "data"
                )


                if newest_date is None or date > newest_date:

                    newest_date = date



                group = str(
                    r.get("id_grupy")
                )



                if group not in profile["grupy"]:


                    profile["grupy"][group] = {

                        "ilosc":0,

                        "srednia_pewnosc":0,

                        "trafienia":0

                    }



                g = profile["grupy"][group]


                old = g["ilosc"]

                new = old + 1



                g["srednia_pewnosc"] = (

                    (
                        g["srednia_pewnosc"]
                        *
                        old
                    )

                    +

                    r.get(
                        "pewnosc",
                        0
                    )

                ) / new



                g["ilosc"] = new



                if r.get("trafienie"):

                    g["trafienia"] += 1



                if previous is not None:


                    transition = (

                        previous
                        +
                        "->"
                        +
                        group

                    )


                    if transition not in profile["przejscia"]:


                        profile["przejscia"][transition] = {

                            "ilosc":0

                        }



                    profile["przejscia"][transition]["ilosc"] += 1


                    profile["liczniki"]["zmian"] += 1



                previous = group



        profile["liczniki"]["mecze"] = len(
            memory
        )


        profile["ostatnia_obserwacja"] = newest_date



        self.save_json(
            profile_file,
            profile
        )



    # =====================================================
    # MODEL
    # =====================================================


    def process_model(self, path):


        memory_file = os.path.join(

            path,

            "obserwacja",

            "pamiec_obserwacji.json"

        )



        if not os.path.exists(memory_file):

            return



        print(
            "\nAnaliza:",
            path
        )



        self.backup(
            memory_file
        )



        memory = self.load_json(
            memory_file
        )


        compressed = {}



        for match, records in memory.items():


            compressed[match] = self.compress_records(
                records
            )



        self.save_json(
            memory_file,
            compressed
        )



        profile_file = os.path.join(

            os.path.dirname(memory_file),

            "charakterystyka_modelu.json"

        )


        self.update_profile(

            os.path.basename(path),

            compressed,

            profile_file

        )


        print(
            "OK"
        )



    def run(self):


        print(
            "START KONSOLIDACJI PAMIĘCI"
        )


        for root in ROOTS:


            if not os.path.exists(root):

                continue



            for folder in os.listdir(root):


                path = os.path.join(
                    root,
                    folder
                )


                if os.path.isdir(path):

                    self.process_model(
                        path
                    )



        print(
            "\nGOTOWE"
        )



if __name__ == "__main__":


    engine = MemoryEngine()

    engine.run()