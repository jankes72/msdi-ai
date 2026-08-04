



import os
import json
import pandas as pd
import numpy as np


from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical



# ==========================================================
# KONFIGURACJA
# ==========================================================


PLIK_PREDYKCJI = (
    "dane/dataBase_futbol_trend.csv"
)


PLIK_TRENING = (
    "dane/kod_dataBase_futbol_trend.csv"
)


KATALOG_MODELE = (
    "modele_dataBase_futbol_trend"
)



os.makedirs(
    KATALOG_MODELE,
    exist_ok=True
)



# ==========================================================
# KLASY WYNIKÓW
# ==========================================================


WYNIKI = [

    "1:0",
    "2:0",
    "3:0",

    "2:1",
    "3:1",
    "3:2",

    "0:1",
    "0:2",
    "0:3",

    "1:2",
    "1:3",
    "2:3",

    "0:0",
    "1:1",
    "2:2"

]



MAPA_KLAS = {

    wynik:index

    for index,wynik

    in enumerate(WYNIKI)

}



# ==========================================================
# SPOJRZENIA ŚWIATA
# ==========================================================


SPOJRZENIA = {


"siec_01_zmiana_kursow":[

    "zmiana_1",
    "zmiana_X",
    "zmiana_2"

],


"siec_02_amplituda":[

    "amplituda_1",
    "amplituda_X",
    "amplituda_2"

],


"siec_03_tempo":[

    "tempo_1",
    "tempo_X",
    "tempo_2"

],


"siec_04_max_wahanie":[

    "max_wahanie_1",
    "max_wahanie_X",
    "max_wahanie_2"

],


"siec_05_start_raw":[

    "start_1_raw",
    "start_X_raw",
    "start_2_raw"

],


"siec_06_koniec_raw":[

    "koniec_1_raw",
    "koniec_X_raw",
    "koniec_2_raw"

],


"siec_07_log_start":[

    "log_start_1",
    "log_start_X",
    "log_start_2"

],


"siec_08_log_koniec":[

    "log_koniec_1",
    "log_koniec_X",
    "log_koniec_2"

],


"siec_09_ratio_start":[

    "ratio_1X_start",
    "ratio_1_2_start",
    "ratio_X2_start"

],


"siec_10_ratio_koniec":[

    "ratio_1X_koniec",
    "ratio_1_2_koniec",
    "ratio_X2_koniec"

],


"siec_11_statystyka":[

    "mean_1",
    "mean_X",
    "mean_2"

]

}



# ==========================================================
# WCZYTANIE SCHEMATU KOLUMN
# ==========================================================


print(
    "Wczytywanie nagłówków..."
)



predykcja = pd.read_csv(

    PLIK_PREDYKCJI,

    sep=";",

    encoding="utf-8"

)



NAGLOWKI = list(

    predykcja.columns

)



print(
    "Kolumny:",
    len(NAGLOWKI)
)



# ==========================================================
# WCZYTANIE HISTORII BEZ NAGŁÓWKA
# ==========================================================


print(
    "Wczytywanie treningu..."
)



df = pd.read_csv(

    PLIK_TRENING,

    sep=";",

    encoding="utf-8",

    header=None

)



df.columns = NAGLOWKI + [

    "wynik"

]



print(
    "Rekordów:",
    len(df)
)



# ==========================================================
# FILTR POPRAWNYCH WYNIKÓW
# ==========================================================


df = df[

    df["wynik"].isin(WYNIKI)

].copy()



print(
    "Po filtrze:",
    len(df)
)



# ==========================================================
# IDENTYFIKACJA KLASY
# ==========================================================


df["klasa"] = (

    df["wynik"]

    .map(MAPA_KLAS)

)



# ==========================================================
# FUNKCJA PODZIAŁU DANYCH
# ==========================================================


# ==========================================================
# FUNKCJA PODZIAŁU DANYCH 50 / 10 / 40
# ==========================================================


def podziel_dane(

    X,

    y

):


    X_temp, X_obserwacja, y_temp, y_obserwacja = train_test_split(

        X,

        y,

        test_size=0.40,

        random_state=42,

        stratify=y

    )



    X_train, X_val, y_train, y_val = train_test_split(

        X_temp,

        y_temp,

        test_size=0.166666,

        random_state=42,

        stratify=y_temp

    )


    # wynik:
    #
    # 50% - trening
    # 10% - walidacja
    # 40% - obserwacja dodatkowa
    #


    return (

        X_train,

        X_val,

        X_obserwacja,

        y_train,

        y_val,

        y_obserwacja

    )

# ==========================================================
# BUDOWA SIECI
# ==========================================================


def buduj_siec(

    nazwa,

    cechy

):


    print("\n================================")
    print(
        "START:",
        nazwa
    )
    print(
        "CECHY:",
        cechy
    )



    katalog = os.path.join(

        KATALOG_MODELE,

        nazwa

    )


    os.makedirs(

        katalog,

        exist_ok=True

    )



    # ----------------------------------
    # DANE DLA KONKRETNEJ SIECI
    # ----------------------------------


    X = df[cechy].values


    y = df["klasa"].values



    # zapamiętanie indeksów

    dane_info = df[

        ["id_meczu"]

    ].copy() if "id_meczu" in df.columns else pd.DataFrame()



    # ----------------------------------
    # PODZIAŁ 50 / 10 / 40
    # ----------------------------------


    (

        X_train,

        X_val,

        X_obserwacja,

        y_train,

        y_val,

        y_obserwacja

    ) = podziel_dane(

        X,

        y,


    )



    # ----------------------------------
    # NORMALIZACJA
    # ----------------------------------


    scaler = StandardScaler()



    X_train = scaler.fit_transform(

        X_train

    )


    X_val = scaler.transform(

        X_val

    )


    X_obserwacja = scaler.transform(

        X_obserwacja

    )



    # ----------------------------------
    # KATEGORIE
    # ----------------------------------


    y_train_cat = to_categorical(

        y_train,

        len(WYNIKI)

    )


    y_val_cat = to_categorical(

        y_val,

        len(WYNIKI)

    )



    # ----------------------------------
    # MODEL
    # ----------------------------------


    model = Sequential()



    model.add(

        Input(

            shape=(len(cechy),)

        )

    )


    model.add(

        Dense(

            32,

            activation="relu"

        )

    )


    model.add(

        Dense(

            64,

            activation="relu"

        )

    )


    model.add(

        Dropout(

            0.2

        )

    )


    model.add(

        Dense(

            len(WYNIKI),

            activation="softmax"

        )

    )



    model.compile(

        optimizer="adam",

        loss="categorical_crossentropy",

        metrics=["accuracy"]

    )



    stop = EarlyStopping(

        patience=20,

        restore_best_weights=True

    )



    # ----------------------------------
    # SZKOLENIE
    # ----------------------------------


    historia = model.fit(

        X_train,

        y_train_cat,

        validation_data=(

            X_val,

            y_val_cat

        ),

        epochs=200,

        batch_size=32,

        callbacks=[stop],

        verbose=1

    )



    # ----------------------------------
    # TEST WALIDACYJNY
    # ----------------------------------


    pred_val = model.predict(

        X_val

    )


    klasy_val = np.argmax(

        pred_val,

        axis=1

    )


    acc = accuracy_score(

        y_val,

        klasy_val

    )



    print(

        "Dokładność",

        nazwa,

        acc

    )



    # ======================================================
    # DODATKOWE 40% - NIE UCZONE
    # ======================================================


    pred_40 = model.predict(

        X_obserwacja

    )


    klasy_40 = np.argmax(

        pred_40,

        axis=1

    )



    prawdopodobienstwo = np.max(

        pred_40,

        axis=1

    )



    wynik_pred = [

        WYNIKI[x]

        for x in klasy_40

    ]



    wynik_realny = [

        WYNIKI[x]

        for x in y_obserwacja

    ]



    # ----------------------------------
    # ZAPIS WARSTWY OBSERWACJI
    # ----------------------------------


    tabela_40 = df.loc[

        df.index.isin(

            df.sample(

                len(y_obserwacja),

                random_state=42

            ).index

        )

    ].copy()



    tabela_40 = tabela_40.reset_index(

        drop=True

    )



    # zabezpieczenie zgodności długości


    tabela_40 = tabela_40.iloc[

        :len(klasy_40)

    ]



    tabela_40["model"] = nazwa


    tabela_40["klasa_predykcji"] = klasy_40


    tabela_40["wynik_predykcji"] = wynik_pred


    tabela_40["prawdopodobienstwo"] = prawdopodobienstwo



    # wynik zawsze ostatni


    if "wynik" in tabela_40.columns:

        wynik_koniec = tabela_40["wynik"]

        tabela_40 = tabela_40.drop(

            columns=["wynik"]

        )

        tabela_40["wynik"] = wynik_koniec



    tabela_40.to_csv(

        os.path.join(

            katalog,

            "walidacja_40_procent.csv"

        ),

        sep=";",

        index=False,

        encoding="utf-8"

    )



    # ----------------------------------
    # ZAPIS MODELU
    # ----------------------------------


    model.save(

        os.path.join(

            katalog,

            "model.h5"

        )

    )



    with open(

        os.path.join(

            katalog,

            "klasy.json"

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            MAPA_KLAS,

            f,

            indent=4,

            ensure_ascii=False

        )



    with open(

        os.path.join(

            katalog,

            "metadata.json"

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            {

            "nazwa":nazwa,

            "cechy":cechy,

            "dokladnosc":float(acc),

            "podzial":

                {

                "trening":"50%",

                "walidacja":"10%",

                "obserwacja":"40%"

                }

            },

            f,

            indent=4,

            ensure_ascii=False

        )



    with open(

        os.path.join(

            katalog,

            "historia.json"

        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            historia.history,

            f,

            indent=4

        )



# ==========================================================
# START WSZYSTKICH SIECI
# ==========================================================


for nazwa, cechy in SPOJRZENIA.items():


    brak = [

        x for x in cechy

        if x not in df.columns

    ]



    if brak:

        print(

            "POMINIĘTO:",

            nazwa,

            brak

        )

        continue



    buduj_siec(

        nazwa,

        cechy

    )



print()
print(
    "================================"
)

print(
    "SYSTEM SZKOLENIA + WARSTWA 40% GOTOWA"
)

print(
    "================================"
)
