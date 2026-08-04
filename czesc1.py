# -*- coding: utf-8 -*-

import csv
import math
import statistics
import os
import sys
import time
from datetime import datetime


csv.field_size_limit(sys.maxsize)


# ==========================================
# SSI V5 - GLOBALNE STRUKTURY DLA AGENTÓW
# ==========================================

# Rejestr statusu procesu
SSI_STAGE_STATUS = {
    "engine": "generatorDataBaseTrendAnalisAll",
    "part": "czesc1",
    "stage": "",
    "status": "",
    "timestamp": "",
    "processing_stats": {},
    "errors": []
}

# Punkty wejścia dla agentów
SSI_AGENT_INPUT = {
    "files_to_process": None,
    "custom_data": None,
    "analysis_params": None,
    "observations": None,
    "research_task": None
}

# Punkty wyjścia dla agentów
SSI_AGENT_OUTPUT = {
    "results": None,
    "analyses": None,
    "memory_updates": None,
    "diagnostics": None,
    "processing_time": None
}


def update_stage_status(stage, status, timestamp=None):
    """Aktualizuje globalny rejestr statusu procesu dla SSI V5"""
    SSI_STAGE_STATUS["stage"] = stage
    SSI_STAGE_STATUS["status"] = status
    SSI_STAGE_STATUS["timestamp"] = str(datetime.now()) if timestamp is None else timestamp


def register_agent_input(data_type, data):
    """Rejestruje dane wejściowe od agentów SSI V5"""
    SSI_AGENT_INPUT[data_type] = data


def export_agent_output(data_type, data):
    """Exports dane wyjściowe dla agentów SSI V5"""
    if SSI_AGENT_OUTPUT[data_type] is None:
        SSI_AGENT_OUTPUT[data_type] = []
    SSI_AGENT_OUTPUT[data_type].append(data)


# ==========================================================
# SSI V5 - EVENT LOGGER i HOOKI DLA CZESC1
# ==========================================================

SSI_EVENTS = []


def SSI_EVENT(event, network="", stage="", status="", data=None):
    """
    SSI V5 - Logowanie zdarzen dla agentow w czesc1
    
    Args:
        event: Typ zdarzenia (NETWORK_START, TRAINING_START, etc.)
        network: Nazwa sieci
        stage: Etap procesu
        status: Status
        data: Dodatkowe dane (dict)
    """
    global SSI_STAGE_STATUS, SSI_EVENTS
    
    # Aktualizacja globalnego statusu
    if network:
        SSI_STAGE_STATUS["network"] = network
    if stage:
        SSI_STAGE_STATUS["stage"] = stage  
    if status:
        SSI_STAGE_STATUS["status"] = status
    SSI_STAGE_STATUS["timestamp"] = str(datetime.now())
    
    # Utworzenie rekordu zdarzenia
    event_record = {
        "timestamp": str(datetime.now()),
        "event": event,
        "engine": SSI_STAGE_STATUS.get("engine", ""),
        "part": SSI_STAGE_STATUS.get("part", ""),
        "network": SSI_STAGE_STATUS.get("network", network),
        "stage": SSI_STAGE_STATUS.get("stage", stage),
        "status": SSI_STAGE_STATUS.get("status", status)
    }
    
    if data:
        event_record["data"] = data
    
    SSI_EVENTS.append(event_record)
    
    # Aktualizacja agent output
    export_agent_output("events", event_record)
    
    print(f"[SSI EVENT] {event} | Network: {network} | Stage: {stage} | Status: {status}")


def SSI_START_NETWORK_BUILD(network, features):
    """Hook: Rozpoczecie budowy sieci"""
    update_stage_status("network_building", "started")
    SSI_EVENT(
        event="NETWORK_START",
        network=network,
        stage="network_building",
        status="started",
        data={"features": features, "feature_count": len(features)}
    )


def SSI_START_TRAINING(network, X_train_shape, y_train_shape, X_val_shape, epochs, batch_size):
    """Hook: Rozpoczecie szkolenia"""
    update_stage_status("training", "started")
    SSI_STAGE_STATUS["training_start"] = time.time()
    SSI_EVENT(
        event="TRAINING_START",
        network=network,
        stage="training",
        status="started",
        data={
            "X_train_shape": list(X_train_shape),
            "y_train_shape": list(y_train_shape),
            "X_val_shape": list(X_val_shape),
            "epochs": epochs,
            "batch_size": batch_size
        }
    )


def SSI_END_TRAINING(network, accuracy, loss, val_accuracy, val_loss, duration):
    """Hook: Zakonczenie szkolenia"""
    update_stage_status("training", "completed")
    SSI_STAGE_STATUS["training_end"] = time.time()
    SSI_EVENT(
        event="TRAINING_END",
        network=network,
        stage="training",
        status="completed",
        data={
            "accuracy": float(accuracy),
            "loss": float(loss),
            "val_accuracy": float(val_accuracy),
            "val_loss": float(val_loss),
            "duration_seconds": duration
        }
    )


def SSI_OUTPUT_READY(network, catalog, file_list, model_accuracy):
    """Hook: Gotowosc wyjścia"""
    update_stage_status("output", "ready")
    SSI_EVENT(
        event="OUTPUT_READY",
        network=network,
        stage="output",
        status="ready",
        data={
            "catalog": catalog,
            "files": file_list,
            "model_accuracy": float(model_accuracy)
        }
    )


def SSI_NETWORK_FINISH(network):
    """Hook: Zakonczenie przetwarzania sieci"""
    update_stage_status("network_processing", "completed")
    SSI_EVENT(
        event="NETWORK_FINISH",
        network=network,
        stage="network_processing",
        status="completed"
    )


def SSI_MAIN_LOOP_START(total_networks):
    """Hook: Rozpoczecie petli glownej"""
    SSI_STAGE_STATUS["start_time"] = time.time()
    SSI_STAGE_STATUS["total_networks"] = total_networks
    SSI_STAGE_STATUS["completed_networks"] = 0
    SSI_STAGE_STATUS["skipped_networks"] = 0
    update_stage_status("main_loop", "started")
    SSI_EVENT(
        event="MAIN_LOOP_START",
        stage="main_loop",
        status="started",
        data={"total_networks": total_networks}
    )


def SSI_MAIN_LOOP_END(completed_networks, skipped_networks):
    """Hook: Zakonczenie petli glownej"""
    duration = time.time() - SSI_STAGE_STATUS.get("start_time", time.time())
    SSI_STAGE_STATUS["completed_networks"] = completed_networks
    SSI_STAGE_STATUS["skipped_networks"] = skipped_networks
    SSI_STAGE_STATUS["status"] = "completed"
    update_stage_status("main_loop", "completed")
    SSI_EVENT(
        event="MAIN_LOOP_END",
        stage="main_loop",
        status="completed",
        data={
            "completed_networks": completed_networks,
            "skipped_networks": skipped_networks,
            "total_duration_seconds": duration
        }
    )


# SSI_AGENT_HOOK_MODULE_START



def normalize(value, min_val, max_val):

    if max_val - min_val == 0:
        return 0.5

    return max(
        0,
        min(
            1,
            (value - min_val) / (max_val - min_val)
        )
    )



def bezpieczny_log(value):

    return math.log(
        max(value, 1.01)
    )



def oblicz_cechy_3kursy_rozszerzone(bloki):


    kurs_1 = [b[0] for b in bloki]
    kurs_X = [b[1] for b in bloki]
    kurs_2 = [b[2] for b in bloki]
    czasy = [b[3] for b in bloki]


    start_1 = kurs_1[0]
    start_X = kurs_X[0]
    start_2 = kurs_2[0]


    koniec_1 = kurs_1[-1]
    koniec_X = kurs_X[-1]
    koniec_2 = kurs_2[-1]



    zmiana_1 = ((start_1-koniec_1)/start_1)*100 if start_1 else 0
    zmiana_X = ((start_X-koniec_X)/start_X)*100 if start_X else 0
    zmiana_2 = ((start_2-koniec_2)/start_2)*100 if start_2 else 0



    amplituda_1 = ((max(kurs_1)-min(kurs_1))/start_1)*100 if start_1 else 0
    amplituda_X = ((max(kurs_X)-min(kurs_X))/start_X)*100 if start_X else 0
    amplituda_2 = ((max(kurs_2)-min(kurs_2))/start_2)*100 if start_2 else 0



    czas_trwania = max(czasy)-min(czasy)

    czas_h = czas_trwania / 3600 if czas_trwania else 0



    tempo_1 = zmiana_1/czas_h if czas_h else 0
    tempo_X = zmiana_X/czas_h if czas_h else 0
    tempo_2 = zmiana_2/czas_h if czas_h else 0



    synchronizacja = 1 if (

        (zmiana_1 > 0 and zmiana_X > 0 and zmiana_2 > 0)

        or

        (zmiana_1 < 0 and zmiana_X < 0 and zmiana_2 < 0)

    ) else 0



    max_wahanie_1 = max(
        abs(kurs_1[i+1]-kurs_1[i])
        for i in range(len(kurs_1)-1)
    )


    max_wahanie_X = max(
        abs(kurs_X[i+1]-kurs_X[i])
        for i in range(len(kurs_X)-1)
    )


    max_wahanie_2 = max(
        abs(kurs_2[i+1]-kurs_2[i])
        for i in range(len(kurs_2)-1)
    )



    log_min = math.log(1.01)
    log_max = math.log(10)



    log_start_1 = normalize(
        bezpieczny_log(start_1),
        log_min,
        log_max
    )

    log_start_X = normalize(
        bezpieczny_log(start_X),
        log_min,
        log_max
    )

    log_start_2 = normalize(
        bezpieczny_log(start_2),
        log_min,
        log_max
    )


    log_koniec_1 = normalize(
        bezpieczny_log(koniec_1),
        log_min,
        log_max
    )

    log_koniec_X = normalize(
        bezpieczny_log(koniec_X),
        log_min,
        log_max
    )

    log_koniec_2 = normalize(
        bezpieczny_log(koniec_2),
        log_min,
        log_max
    )



    ratio_1X_start = start_1/start_X if start_X else 1
    ratio_1_2_start = start_1/start_2 if start_2 else 1
    ratio_X2_start = start_X/start_2 if start_2 else 1


    ratio_1X_koniec = koniec_1/koniec_X if koniec_X else 1
    ratio_1_2_koniec = koniec_1/koniec_2 if koniec_2 else 1
    ratio_X2_koniec = koniec_X/koniec_2 if koniec_2 else 1



    stat_mean = [
        statistics.mean(kurs_1),
        statistics.mean(kurs_X),
        statistics.mean(kurs_2)
    ]


    stat_median = [
        statistics.median(kurs_1),
        statistics.median(kurs_X),
        statistics.median(kurs_2)
    ]


    stat_stdev = [

        statistics.stdev(kurs_1)
        if len(kurs_1)>1 else 0,

        statistics.stdev(kurs_X)
        if len(kurs_X)>1 else 0,

        statistics.stdev(kurs_2)
        if len(kurs_2)>1 else 0

    ]



    return [

        normalize(zmiana_1,-100,100),
        normalize(zmiana_X,-100,100),
        normalize(zmiana_2,-100,100),

        normalize(amplituda_1,0,100),
        normalize(amplituda_X,0,100),
        normalize(amplituda_2,0,100),

        normalize(tempo_1,-50,50),
        normalize(tempo_X,-50,50),
        normalize(tempo_2,-50,50),

        synchronizacja,

        max_wahanie_1,
        max_wahanie_X,
        max_wahanie_2,

        normalize(start_1,1.01,10),
        normalize(start_X,1.01,10),
        normalize(start_2,1.01,10),

        normalize(koniec_1,1.01,10),
        normalize(koniec_X,1.01,10),
        normalize(koniec_2,1.01,10),

        log_start_1,
        log_start_X,
        log_start_2,

        log_koniec_1,
        log_koniec_X,
        log_koniec_2,

        normalize(ratio_1X_start,0,10),
        normalize(ratio_1_2_start,0,10),
        normalize(ratio_X2_start,0,10),

        normalize(ratio_1X_koniec,0,10),
        normalize(ratio_1_2_koniec,0,10),
        normalize(ratio_X2_koniec,0,10),

        normalize(stat_mean[0],1,10),
        normalize(stat_mean[1],1,10),
        normalize(stat_mean[2],1,10),

        normalize(stat_median[0],1,10),
        normalize(stat_median[1],1,10),
        normalize(stat_median[2],1,10),

        normalize(stat_stdev[0],0,5),
        normalize(stat_stdev[1],0,5),
        normalize(stat_stdev[2],0,5),

        czas_h
    ]



def przetworz_plik_3kursy_rozszerzone(
        nazwa_pliku,
        nazwa_wyjsciowa
):
    # SSI_AGENT_HOOK_START
    update_stage_status("file_processing", "start")
    
    # Sprawdzenie czy agent dostarczył dane do przetwarzania zamiast pliku
    if SSI_AGENT_INPUT.get("custom_data"):
        # Agent dostarczył własne dane - pomiń sprawdzanie pliku
        pass
    elif not os.path.exists(nazwa_pliku):

        print(
            "Brak pliku:",
            nazwa_pliku
        )

        update_stage_status("file_processing", "error")
        SSI_STAGE_STATUS["errors"].append(f"Brak pliku: {nazwa_pliku}")
        return



    zapisano = 0
    pominieto = 0



    try:

        with open(
            nazwa_pliku,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as f, open(
            nazwa_wyjsciowa,
            "w",
            encoding="utf-8",
            newline=""
        ) as out:


            reader = csv.reader(
                f,
                delimiter=";"
            )


            writer = csv.writer(
                out,
                delimiter=";"
            )



            writer.writerow(
                [
                    "id_meczu",
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
            )



            for row in reader:


                if len(row)<7:

                    pominieto += 1
                    continue



                mecz = row[2]

                bloki = []



                for i in range(3,len(row),4):

                    try:

                        k1 = float(row[i])
                        kX = float(row[i+1])
                        k2 = float(row[i+2])

                        # poprawka dla starych i nowych danych
                        czas = float(row[i+3])


                        bloki.append(
                            (
                                k1,
                                kX,
                                k2,
                                czas
                            )
                        )


                    except (ValueError,IndexError):

                        continue



                if len(bloki)<2:

                    pominieto += 1
                    continue



                cechy = oblicz_cechy_3kursy_rozszerzone(
                    bloki
                )


                writer.writerow(
                    [
                        mecz
                    ]
                    +
                    [
                        round(x,5)
                        for x in cechy
                    ]
                )


                zapisano += 1



                if zapisano % 10000 == 0:

                    print(
                        "Zapisano:",
                        zapisano
                    )



        print("===================")
        print("Gotowe")
        print("Zapisano:", zapisano)
        print("Pominięto:", pominieto)
        print("Plik:", nazwa_wyjsciowa)



    except Exception as e:

        print(
            "Błąd:",
            e
        )
        
        update_stage_status("file_processing", "error")
        SSI_STAGE_STATUS["errors"].append(str(e))

    # SSI_AGENT_HOOK_END
    update_stage_status("file_processing", "end")
    export_agent_output("results", {
        "file": nazwa_pliku,
        "output": nazwa_wyjsciowa,
        "saved": zapisano,
        "skipped": pominieto
    })


# ================================
# START
# ================================

# SSI_AGENT_HOOK_PROCESS_START
update_stage_status("main_processing", "start")

pliki = [

    (
        "./dane/database_popularne_dzisiaj.csv",
        "./dane/dataBase_futbol_popularne_trend.csv"
    ),
    
    (
        "./dane/database_dzisiaj.csv",
        "./dane/dataBase_futbol_trend.csv"
    )

]

# Sprawdzenie czy agent dostarczył dodatkowe pliki do przetwarzania
if SSI_AGENT_INPUT.get("files_to_process"):
    additional_files = SSI_AGENT_INPUT["files_to_process"]
    if isinstance(additional_files, list):
        pliki.extend(additional_files)


for plik_in, plik_out in pliki:

    przetworz_plik_3kursy_rozszerzone(
        plik_in,
        plik_out
    )

# SSI_AGENT_HOOK_PROCESS_END
update_stage_status("main_processing", "end")


import csv
import sys
import pandas as pd


# ==========================================
# Zwiększenie limitu wielkości pola CSV
# (duże rekordy z historią kursów)
# ==========================================

csv.field_size_limit(sys.maxsize)



# ==========================================
# PLIKI
# ==========================================

plik_wej = "./dane/database_popularne_dzisiaj.csv"

plik_wyj = "./dane/kursy_popularne_przygotowane.csv"



# ==========================================
# ODCZYT PLIKU
# ==========================================

wyniki = []


with open(
    plik_wej,
    "r",
    encoding="utf-8",
    newline="",
    errors="ignore"
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
            # ostatnie wartości:
            #
            # row[-1]  = czas Unix
            # row[-2]  = kurs 2
            # row[-3]  = kurs X
            # row[-4]  = kurs 1


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



# ==========================================
# Zamiana kursów na liczby
# ==========================================


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
# ZMIANY KURSÓW
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



# ==========================================
# PROCENTOWA ZMIANA KURSÓW
# ==========================================


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



# ==========================================
# PODSUMOWANIE
# ==========================================


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


import csv
import sys
import pandas as pd


# ==========================================
# Zwiększenie limitu wielkości pola CSV
# (duże rekordy z historią kursów)
# ==========================================

csv.field_size_limit(sys.maxsize)



# ==========================================
# PLIKI
# ==========================================

plik_wej = "./dane/database_dzisiaj.csv"

plik_wyj = "./dane/kursy_przygotowane.csv"



# ==========================================
# ODCZYT PLIKU
# ==========================================

wyniki = []


with open(
    plik_wej,
    "r",
    encoding="utf-8",
    newline="",
    errors="ignore"
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
            # ostatnie wartości:
            #
            # row[-1]  = czas Unix
            # row[-2]  = kurs 2
            # row[-3]  = kurs X
            # row[-4]  = kurs 1


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



# ==========================================
# Zamiana kursów na liczby
# ==========================================


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
# ZMIANY KURSÓW
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



# ==========================================
# PROCENTOWA ZMIANA KURSÓW
# ==========================================


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



# ==========================================
# PODSUMOWANIE
# ==========================================


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



# -*- coding: utf-8 -*-

import csv
import sys


# zwiększenie limitu pojedynczego pola CSV
csv.field_size_limit(sys.maxsize)



# ==========================================
# KLASYFIKACJA KURSÓW
# ==========================================

def classify_odds(odds):

    levels = []


    for odd in odds:

        if odd < 1.2:
            level = 'poziom1'

        elif 1.2 <= odd < 1.4:
            level = 'poziom2'

        elif 1.4 <= odd < 1.6:
            level = 'poziom3'

        elif 1.6 <= odd < 1.8:
            level = 'poziom4'

        elif 1.8 <= odd < 2.0:
            level = 'poziom5'

        elif 2.0 <= odd < 2.2:
            level = 'poziom6'

        elif 2.2 <= odd < 2.4:
            level = 'poziom7'

        elif 2.4 <= odd < 2.6:
            level = 'poziom8'

        elif 2.6 <= odd < 2.8:
            level = 'poziom9'

        elif 2.8 <= odd < 3.0:
            level = 'poziom10'

        elif 3.0 <= odd < 3.2:
            level = 'poziom11'

        elif 3.2 <= odd < 3.4:
            level = 'poziom12'

        elif 3.4 <= odd < 3.6:
            level = 'poziom13'

        elif 3.6 <= odd < 3.8:
            level = 'poziom14'

        elif 3.8 <= odd < 4.0:
            level = 'poziom15'

        elif 4.0 <= odd < 4.2:
            level = 'poziom16'

        elif 4.2 <= odd < 4.4:
            level = 'poziom17'

        elif 4.4 <= odd < 4.6:
            level = 'poziom18'

        elif 4.6 <= odd < 4.8:
            level = 'poziom19'

        elif 4.8 <= odd < 5.0:
            level = 'poziom20'

        elif 5.0 <= odd < 5.2:
            level = 'poziom21'

        elif 5.2 <= odd < 5.4:
            level = 'poziom22'

        elif 5.4 <= odd < 5.6:
            level = 'poziom23'

        elif 5.6 <= odd < 5.8:
            level = 'poziom24'

        elif 5.8 <= odd < 6.0:
            level = 'poziom25'

        elif 6.0 <= odd < 6.2:
            level = 'poziom26'

        elif 6.2 <= odd < 6.4:
            level = 'poziom27'

        elif 6.4 <= odd < 6.6:
            level = 'poziom28'

        elif 6.6 <= odd < 6.8:
            level = 'poziom29'

        else:
            level = 'poziom30'


        levels.append(level)


    return levels



# ==========================================
# PRZETWARZANIE DUŻEGO CSV
# ==========================================

def process_and_save_data(
        input_file_path,
        output_file_path
):


    licznik = 0


    with open(
        input_file_path,
        'r',
        encoding='utf-8',
        newline=''
    ) as input_file, open(
        output_file_path,
        'w',
        encoding='utf-8',
        newline=''
    ) as output_file:


        reader = csv.reader(
            input_file,
            delimiter=';'
        )


        writer = csv.writer(
            output_file,
            delimiter=';'
        )


        writer.writerow(
            [
                'Mecz',
                'Poziomy'
            ]
        )


        for row in reader:


            if len(row) < 6:

                continue



            try:

                match_name = row[2]

                home_odds = float(
                    row[3]
                )

                draw_odds = float(
                    row[4]
                )

                away_odds = float(
                    row[5]
                )


            except:

                continue



            home_level = classify_odds(
                [home_odds]
            )


            draw_level = classify_odds(
                [draw_odds]
            )


            away_level = classify_odds(
                [away_odds]
            )


            combined_levels = (
                ''.join(home_level)
                +
                ''.join(draw_level)
                +
                ''.join(away_level)
            )



            writer.writerow(
                [
                    match_name,
                    combined_levels
                ]
            )


            licznik += 1



            if licznik % 10000 == 0:

                print(
                    "Przetworzono:",
                    licznik
                )



    print()
    print(
        "Zakończono."
    )

    print(
        "Liczba rekordów:",
        licznik
    )

    print(
        "Plik:",
        output_file_path
    )





# ==========================================
# START
# ==========================================


input_file_path = (
    './dane/'
    'database_Popularne_dzisiaj.csv'
)


output_file_path = (
    './dane/'
    'analizaKursowDni_dataBase_futbol_Popularne.csv'
)



process_and_save_data(
    input_file_path,
    output_file_path
)




import csv
import sys


# zwiększenie limitu pojedynczego pola CSV
csv.field_size_limit(sys.maxsize)



# ==========================================
# KLASYFIKACJA KURSÓW
# ==========================================

def classify_odds(odds):

    levels = []


    for odd in odds:

        if odd < 1.2:
            level = 'poziom1'

        elif 1.2 <= odd < 1.4:
            level = 'poziom2'

        elif 1.4 <= odd < 1.6:
            level = 'poziom3'

        elif 1.6 <= odd < 1.8:
            level = 'poziom4'

        elif 1.8 <= odd < 2.0:
            level = 'poziom5'

        elif 2.0 <= odd < 2.2:
            level = 'poziom6'

        elif 2.2 <= odd < 2.4:
            level = 'poziom7'

        elif 2.4 <= odd < 2.6:
            level = 'poziom8'

        elif 2.6 <= odd < 2.8:
            level = 'poziom9'

        elif 2.8 <= odd < 3.0:
            level = 'poziom10'

        elif 3.0 <= odd < 3.2:
            level = 'poziom11'

        elif 3.2 <= odd < 3.4:
            level = 'poziom12'

        elif 3.4 <= odd < 3.6:
            level = 'poziom13'

        elif 3.6 <= odd < 3.8:
            level = 'poziom14'

        elif 3.8 <= odd < 4.0:
            level = 'poziom15'

        elif 4.0 <= odd < 4.2:
            level = 'poziom16'

        elif 4.2 <= odd < 4.4:
            level = 'poziom17'

        elif 4.4 <= odd < 4.6:
            level = 'poziom18'

        elif 4.6 <= odd < 4.8:
            level = 'poziom19'

        elif 4.8 <= odd < 5.0:
            level = 'poziom20'

        elif 5.0 <= odd < 5.2:
            level = 'poziom21'

        elif 5.2 <= odd < 5.4:
            level = 'poziom22'

        elif 5.4 <= odd < 5.6:
            level = 'poziom23'

        elif 5.6 <= odd < 5.8:
            level = 'poziom24'

        elif 5.8 <= odd < 6.0:
            level = 'poziom25'

        elif 6.0 <= odd < 6.2:
            level = 'poziom26'

        elif 6.2 <= odd < 6.4:
            level = 'poziom27'

        elif 6.4 <= odd < 6.6:
            level = 'poziom28'

        elif 6.6 <= odd < 6.8:
            level = 'poziom29'

        else:
            level = 'poziom30'


        levels.append(level)


    return levels



# ==========================================
# PRZETWARZANIE DUŻEGO CSV
# ==========================================

def process_and_save_data(
        input_file_path,
        output_file_path
):


    licznik = 0


    with open(
        input_file_path,
        'r',
        encoding='utf-8',
        newline=''
    ) as input_file, open(
        output_file_path,
        'w',
        encoding='utf-8',
        newline=''
    ) as output_file:


        reader = csv.reader(
            input_file,
            delimiter=';'
        )


        writer = csv.writer(
            output_file,
            delimiter=';'
        )


        writer.writerow(
            [
                'Mecz',
                'Poziomy'
            ]
        )


        for row in reader:


            if len(row) < 6:

                continue



            try:

                match_name = row[2]

                home_odds = float(
                    row[3]
                )

                draw_odds = float(
                    row[4]
                )

                away_odds = float(
                    row[5]
                )


            except:

                continue



            home_level = classify_odds(
                [home_odds]
            )


            draw_level = classify_odds(
                [draw_odds]
            )


            away_level = classify_odds(
                [away_odds]
            )


            combined_levels = (
                ''.join(home_level)
                +
                ''.join(draw_level)
                +
                ''.join(away_level)
            )



            writer.writerow(
                [
                    match_name,
                    combined_levels
                ]
            )


            licznik += 1



            if licznik % 10000 == 0:

                print(
                    "Przetworzono:",
                    licznik
                )



    print()
    print(
        "Zakończono."
    )

    print(
        "Liczba rekordów:",
        licznik
    )

    print(
        "Plik:",
        output_file_path
    )





# ==========================================
# START
# ==========================================


input_file_path = (
    './dane/'
    'database_dzisiaj.csv'
)


output_file_path = (
    './dane/'
    'analizaKursowDni_dataBase_futbol.csv'
)



process_and_save_data(
    input_file_path,
    output_file_path
)















import csv

plik_wej = "./dane/dataBase_futbol_trend.csv"
plik_wyj = "./dane/dataBase_futbol_trend_klasyfikator.csv"


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

plik_wej = "./dane/kod_dataBase_futbol_trend.csv"
plik_wyj = "./dane/kod_dataBase_futbol_trend_klasyfikator.csv"


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

plik_predykcja_klasyfikator = "./dane/dataBase_futbol_trend_klasyfikator.csv"

plik_historia_klasyfikator = "./dane/kod_dataBase_futbol_trend_klasyfikator.csv"

plik_historia_pelna = "./dane/kod_dataBase_futbol_trend.csv"

plik_wyj = "./dane/dopasowane_trendy_historyczne.csv"

plik_wagi = "./dane/wagi_dopasowania.csv"



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

plik_dane = "./dane/dopasowane_trendy_historyczne.csv"

plik_wagi = "./dane/wagi_dopasowania.csv"


plik_korelacja = "./dane/analiza_korelacji_cech.csv"

plik_rf = "./dane/random_forest_waznosc_cech.csv"

plik_ranking = "./dane/ranking_cech.csv"

plik_syntetyczne = "./dane/syntetyczne_trendy_historyczne.csv"

plik_poisson = "./dane/analiza_poisson_dixon.csv"



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

plik_wejscie = "./dane/dopasowane_trendy_historyczne.csv"

plik_wynik = "./dane/predykcja_poisson_dc_v2.csv"


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
import os
import json
from collections import defaultdict



# ==========================================
# POPRAWA WYNIKU
# 3.0 -> 3:0
# 3:0 zostaje
# ==========================================

def popraw_wynik(wynik):

    wynik = wynik.strip()

    if "." in wynik:

        wynik = wynik.replace(
            ".",
            ":"
        )

    return wynik




# ==========================================
# WCZYTYWANIE CSV
# FORMAT:
#
# index 0 = mecz
# index 1 = grupa/tag
# index 2 = wynik
#
# ==========================================

def load_csv(
        file_path,
        delimiter=';',
        encoding='utf-8'
):

    data = []


    with open(
        file_path,
        'r',
        encoding=encoding,
        errors="ignore",
        newline=""
    ) as file:


        reader = csv.reader(
            file,
            delimiter=delimiter
        )


        for row in reader:


            if len(row) >= 3:


                row[2] = popraw_wynik(
                    row[2]
                )


                data.append(
                    row
                )


    return data




# ==========================================
# TWORZENIE MAPY TAGÓW
#
# GRUPA
#   |
#   +-- mecz
#   +-- wynik
#
# ==========================================

def create_tag_map(data):


    tag_map = defaultdict(list)



    for row in data:


        if len(row) < 3:

            continue



        mecz = row[0].strip()

        grupa = row[1].strip()

        wynik = row[2].strip()



        rekord = {

            "mecz": mecz,

            "wynik": wynik

        }



        tag_map[grupa].append(
            rekord
        )



    return tag_map




# ==========================================
# ZAPIS CSV GRUPOWANY
# (opcjonalny pomocniczy)
# ==========================================


import pandas as pd
import numpy as np


from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import StandardScaler



# ============================================================
# PLIKI
# ============================================================


PLIK_TRENING = r"dane\mozg_kursy_przygotowane.csv"

OUTPUT = r"dane\ranking_cech_kursy_przygotowane.csv"



# ============================================================
# NAZWY KOLUMN
# (plik treningowy NIE posiada nagłówka)
# ============================================================


KOLUMNY = [

    "mecz",

    "kurs_1_start",
    "kurs_X_start",
    "kurs_2_start",

    "kurs_1_koniec",
    "kurs_X_koniec",
    "kurs_2_koniec",

    "zmiana_kurs_1",
    "zmiana_kurs_X",
    "zmiana_kurs_2",

    "procent_kurs_1",
    "procent_kurs_X",
    "procent_kurs_2",

    "wynik"

]



# ============================================================
# WCZYTANIE PLIKU BEZ NAGŁÓWKA
# ============================================================


df = pd.read_csv(

    PLIK_TRENING,

    sep=";",

    header=None,

    names=KOLUMNY,

    encoding="utf-8"

)



print(
    "Wczytano rekordów:",
    len(df)
)



# ============================================================
# KONWERSJA WYNIKU NA KLASĘ
# ============================================================


def klasyfikuj_wynik(wynik):

    try:

        if pd.isna(wynik):
            return None


        wynik = str(wynik).strip()


        if ":" not in wynik:
            return None


        gospodarz, gosc = wynik.split(":")


        gospodarz = int(gospodarz)

        gosc = int(gosc)



        if gospodarz > gosc:

            return 1


        elif gospodarz == gosc:

            return 0


        else:

            return -1



    except:

        return None



df["klasa"] = df["wynik"].apply(
    klasyfikuj_wynik
)



# usunięcie braków

df = df.dropna(
    subset=["klasa"]
)



print(
    "Mecze po klasyfikacji:",
    len(df)
)



# ============================================================
# PRZYGOTOWANIE CECH
# ============================================================


CECHY = [

    c for c in KOLUMNY

    if c not in [

        "mecz",

        "wynik"

    ]

]



X = df[CECHY]


y = df["klasa"]



# wszystkie kursy jako liczby

X = X.apply(

    pd.to_numeric,

    errors="coerce"

)



X = X.fillna(0)



# ============================================================
# KORELACJA DC
# ============================================================


korelacja = {}


for cecha in CECHY:


    korelacja[cecha] = abs(

        np.corrcoef(

            X[cecha],

            y

        )[0,1]

    )



korelacja = pd.Series(
    korelacja
)



korelacja = korelacja.fillna(0)



# ============================================================
# RANDOM FOREST
# ============================================================


rf = RandomForestClassifier(

    n_estimators=500,

    random_state=42,

    class_weight="balanced"

)


rf.fit(

    X,

    y

)



rf_score = pd.Series(

    rf.feature_importances_,

    index=CECHY

)



# ============================================================
# DC - MUTUAL INFORMATION
# ============================================================


scaler = StandardScaler()


X_scaled = scaler.fit_transform(

    X

)



dc = mutual_info_classif(

    X_scaled,

    y,

    random_state=42

)



dc_score = pd.Series(

    dc,

    index=CECHY

)



# ============================================================
# NORMALIZACJA
# ============================================================


def normalizuj(x):

    if x.max() == x.min():

        return x * 0


    return (

        x - x.min()

    ) / (

        x.max() - x.min()

    )



korelacja_n = normalizuj(
    korelacja
)


rf_n = normalizuj(
    rf_score
)


dc_n = normalizuj(
    dc_score
)



# ============================================================
# BUDOWA RANKINGU
# ============================================================


ranking = pd.DataFrame()


ranking["cecha"] = CECHY


ranking["korelacja_dc"] = (

    korelacja_n.values

)


ranking["RF"] = (

    rf_n.values

)


ranking["DC"] = (

    dc_n.values

)



# końcowa siła

ranking["sila"] = (

    ranking["korelacja_dc"] * 0.4

    +

    ranking["RF"] * 0.3

    +

    ranking["DC"] * 0.3

)



ranking = ranking.sort_values(

    by="sila",

    ascending=False

)



# ============================================================
# ZAPIS
# ============================================================


ranking.to_csv(

    OUTPUT,

    sep=";",

    index=False,

    encoding="utf-8"

)



print()

print(
    "Gotowe:",
    OUTPUT
)


print(
    ranking.head(20)
)



import os
import pandas as pd
import numpy as np


from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import StandardScaler



# ============================================================
# ŚCIEŻKI
# ============================================================


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


PLIK_TRENING = os.path.join(
    BASE_DIR,
    "dane",
    "kod_dataBase_futbol_trend_klasyfikator.csv"
)


OUTPUT = os.path.join(
    BASE_DIR,
    "dane",
    "ranking_cech_dataBase_futbol_trend_klasyfikator.csv"
)



# ============================================================
# WCZYTANIE DANYCH
# (TUTAJ JEST NAGŁÓWEK)
# ============================================================


df = pd.read_csv(

    PLIK_TRENING,

    sep=";",

    encoding="utf-8"

)



print(
    "Wczytano rekordów:",
    len(df)
)



# ============================================================
# KLASYFIKACJA WYNIKU
#
# 1  - gospodarze
# 0  - remis
# -1 - goście
# ============================================================


def klasyfikuj_wynik(wynik):

    try:

        wynik = str(wynik).strip()


        if ":" not in wynik:

            return None


        dom, wyjazd = wynik.split(":")


        dom = int(dom)

        wyjazd = int(wyjazd)



        if dom > wyjazd:

            return 1


        elif dom == wyjazd:

            return 0


        else:

            return -1


    except:

        return None




df["klasa"] = df["wynik"].apply(
    klasyfikuj_wynik
)



df = df.dropna(
    subset=["klasa"]
)



print(
    "Mecze po klasyfikacji:",
    len(df)
)



# ============================================================
# WYBÓR CECH
# ============================================================


CECHY = [

    "log_start_1",

    "log_start_X",

    "log_start_2",

    "log_koniec_1",

    "log_koniec_X",

    "log_koniec_2"

]



X = df[CECHY]


y = df["klasa"]



X = X.apply(

    pd.to_numeric,

    errors="coerce"

)


X = X.fillna(0)



# ============================================================
# KORELACJA DC
# ============================================================


korelacja = {}


for cecha in CECHY:


    korelacja[cecha] = abs(

        np.corrcoef(

            X[cecha],

            y

        )[0,1]

    )



korelacja = pd.Series(
    korelacja
)



korelacja = korelacja.fillna(0)



# ============================================================
# RANDOM FOREST
# ============================================================


rf = RandomForestClassifier(

    n_estimators=500,

    random_state=42,

    class_weight="balanced"

)



rf.fit(

    X,

    y

)



rf_score = pd.Series(

    rf.feature_importances_,

    index=CECHY

)



# ============================================================
# DC - MUTUAL INFORMATION
# ============================================================


scaler = StandardScaler()


X_scaled = scaler.fit_transform(

    X

)



dc = mutual_info_classif(

    X_scaled,

    y,

    random_state=42

)



dc_score = pd.Series(

    dc,

    index=CECHY

)



# ============================================================
# NORMALIZACJA
# ============================================================


def normalizuj(x):


    if x.max() == x.min():

        return x * 0


    return (

        x - x.min()

    ) / (

        x.max() - x.min()

    )



korelacja_n = normalizuj(
    korelacja
)


rf_n = normalizuj(
    rf_score
)


dc_n = normalizuj(
    dc_score
)



# ============================================================
# RANKING
# ============================================================


ranking = pd.DataFrame()



ranking["cecha"] = CECHY


ranking["korelacja_dc"] = (

    korelacja_n.values

)


ranking["RF"] = (

    rf_n.values

)


ranking["DC"] = (

    dc_n.values

)



ranking["sila"] = (

    ranking["korelacja_dc"] * 0.4

    +

    ranking["RF"] * 0.3

    +

    ranking["DC"] * 0.3

)



ranking = ranking.sort_values(

    by="sila",

    ascending=False

)



# ============================================================
# ZAPIS
# ============================================================


ranking.to_csv(

    OUTPUT,

    sep=";",

    index=False,

    encoding="utf-8"

)



print()

print(
    "Utworzono:",
    OUTPUT
)


print()

print(
    ranking
)

import os
import json
import csv


# ==========================================================
# KONFIGURACJA
# ==========================================================

KATALOG = "dane"


PLIK_GRUPY = os.path.join(
    KATALOG,
    "analizaKursowDni_dataBase_futbol.csv"
)


PLIK_JSON = os.path.join(
    KATALOG,
    "tags_world_map.json"
)


PLIK_CECHY = os.path.join(
    KATALOG,
    "kod_dataBase_futbol_trend_klasyfikator.csv"
)


PLIK_WYNIK = os.path.join(
    KATALOG,
    "dopasowanie_swiata_kod_dataBase_futbol_trend_klasyfikatorr.csv"
)



# ==========================================================
# WCZYTANIE JSON - MAPA ŚWIATA
# ==========================================================

with open(
    PLIK_JSON,
    "r",
    encoding="utf-8"
) as plik:

    TAGS_WORLD_MAP = json.load(plik)



print(
    "Załadowano grup JSON:",
    len(TAGS_WORLD_MAP)
)



# ==========================================================
# WCZYTANIE BAZY CECH
# kod_dataBase_futbol_trend_klasyfikator.csv
#
# indeks:
# 0 id_meczu
# 1 log_start_1
# 2 log_start_X
# 3 log_start_2
# 4 log_koniec_1
# 5 log_koniec_X
# 6 log_koniec_2
# 7 wynik
# ==========================================================

BAZA_CECH = {}


with open(
    PLIK_CECHY,
    "r",
    encoding="utf-8"
) as plik:


    reader = csv.reader(
        plik,
        delimiter=";"
    )


    for row in reader:


        if len(row) >= 8:

            id_meczu = row[0].strip()


            BAZA_CECH[id_meczu] = row



print(
    "Załadowano meczów z cechami:",
    len(BAZA_CECH)
)



# ==========================================================
# ANALIZA AKTUALNYCH MECZÓW
# ==========================================================

WYNIKI = []


with open(
    PLIK_GRUPY,
    "r",
    encoding="utf-8"
) as plik:


    reader = csv.reader(
        plik,
        delimiter=";"
    )


    for row in reader:


        if len(row) < 2:
            continue



        id_meczu_predykcja = row[0].strip()

        grupa = row[1].strip()



        if grupa not in TAGS_WORLD_MAP:

            print(
                "Brak grupy:",
                grupa
            )

            continue



        historia = TAGS_WORLD_MAP[grupa]



        DOPASOWANE = []



        # ------------------------------------------
        # Szukanie faktycznych dopasowań
        # ------------------------------------------

        for rekord in historia:


            id_historyczny = rekord["mecz"].strip()



            if id_historyczny in BAZA_CECH:


                dane = BAZA_CECH[id_historyczny]


                DOPASOWANE.append(

                    [

                    id_meczu_predykcja,

                    id_historyczny,

                    dane[1],  # log_start_1
                    dane[2],  # log_start_X
                    dane[3],  # log_start_2
                    dane[4],  # log_koniec_1
                    dane[5],  # log_koniec_X
                    dane[6],  # log_koniec_2
                    dane[7]   # wynik

                    ]

                )



        # licznik tylko znalezionych rekordów

        ilosc_dopasowan = len(DOPASOWANE)



        # dodanie liczby dopasowań

        for rekord in DOPASOWANE:


            rekord.insert(
                1,
                ilosc_dopasowan
            )


            WYNIKI.append(
                rekord
            )



# ==========================================================
# ZAPIS
# ==========================================================

with open(
    PLIK_WYNIK,
    "w",
    encoding="utf-8",
    newline=""
) as plik:


    writer = csv.writer(
        plik,
        delimiter=";"
    )


    writer.writerow(

        [

        "id_meczu_predykcja",
        "ilosc_dopsowan",
        "id_meczu",
        "log_start_1",
        "log_start_X",
        "log_start_2",
        "log_koniec_1",
        "log_koniec_X",
        "log_koniec_2",
        "wynik"

        ]

    )


    writer.writerows(
        WYNIKI
    )



print()
print(
    "================================"
)

print(
    "ZAKOŃCZONO"
)

print(
    "Zapisano:",
    PLIK_WYNIK
)

print(
    "Liczba rekordów:",
    len(WYNIKI)
)

print(
    "================================"
)

import os
import json
import csv


# ==========================================================
# KONFIGURACJA
# ==========================================================

KATALOG = "dane"


PLIK_GRUPY = os.path.join(
    KATALOG,
    "analizaKursowDni_dataBase_futbol.csv"
)


PLIK_JSON = os.path.join(
    KATALOG,
    "tags_world_map.json"
)


PLIK_TREND = os.path.join(
    KATALOG,
    "kod_dataBase_futbol_trend.csv"
)


PLIK_WYNIK = os.path.join(
    KATALOG,
    "dopasowanie_swiata_kod_dataBase_futbol_trend.csv"
)



# ==========================================================
# WCZYTANIE TAGS WORLD MAP
# ==========================================================

with open(
    PLIK_JSON,
    "r",
    encoding="utf-8"
) as plik:

    TAGS_WORLD_MAP = json.load(
        plik
    )


print(
    "Załadowano grup JSON:",
    len(TAGS_WORLD_MAP)
)



# ==========================================================
# WCZYTANIE BAZY TRENDÓW
#
# kod_dataBase_futbol_trend.csv
#
# 0  id_meczu
# 1  zmiana_1
# 2  zmiana_X
# ...
# ostatni wynik
# ==========================================================

BAZA_TREND = {}


with open(
    PLIK_TREND,
    "r",
    encoding="utf-8"
) as plik:


    reader = csv.reader(
        plik,
        delimiter=";"
    )


    for row in reader:


        if len(row) < 2:
            continue


        id_meczu = row[0].strip()


        BAZA_TREND[id_meczu] = row



print(
    "Załadowano rekordów trend:",
    len(BAZA_TREND)
)



# ==========================================================
# NAGŁÓWEK ŹRÓDŁOWY
# ==========================================================

HEADER_TREND = [

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



# ==========================================================
# ANALIZA MECZÓW
# ==========================================================

WYNIKI = []


with open(
    PLIK_GRUPY,
    "r",
    encoding="utf-8"
) as plik:


    reader = csv.reader(
        plik,
        delimiter=";"
    )


    for row in reader:


        if len(row) < 2:
            continue



        id_meczu_predykcja = row[0].strip()

        grupa = row[1].strip()



        if grupa not in TAGS_WORLD_MAP:


            print(
                "Brak grupy:",
                grupa
            )

            continue



        historia = TAGS_WORLD_MAP[grupa]



        DOPASOWANE = []



        # --------------------------------------
        # Szukanie faktycznych dopasowań
        # --------------------------------------

        for rekord in historia:


            id_historyczny = rekord["mecz"].strip()



            if id_historyczny in BAZA_TREND:


                dane = BAZA_TREND[id_historyczny]


                DOPASOWANE.append(
                    [
                        id_meczu_predykcja,
                        id_historyczny,
                        *dane[1:]
                    ]
                )



        ilosc_dopasowan = len(
            DOPASOWANE
        )



        # dodanie licznika

        for rekord in DOPASOWANE:


            rekord.insert(
                1,
                ilosc_dopasowan
            )


            WYNIKI.append(
                rekord
            )



# ==========================================================
# ZAPIS CSV
# ==========================================================

with open(
    PLIK_WYNIK,
    "w",
    encoding="utf-8",
    newline=""
) as plik:


    writer = csv.writer(
        plik,
        delimiter=";"
    )


    writer.writerow(

        [

        "id_meczu_predykcja",
        "ilosc_dopsowan",

        *HEADER_TREND

        ]

    )


    writer.writerows(
        WYNIKI
    )



# ==========================================================
# PODSUMOWANIE
# ==========================================================

print()
print(
    "======================================"
)

print(
    "DOPASOWANIE ŚWIATA ZAKOŃCZONE"
)

print(
    "Plik:",
    PLIK_WYNIK
)

print(
    "Rekordów:",
    len(WYNIKI)
)

print(
    "======================================"
)

import os
import json
import csv


# ==========================================================
# KONFIGURACJA
# ==========================================================

KATALOG = "dane"


PLIK_GRUPY = os.path.join(
    KATALOG,
    "analizaKursowDni_dataBase_futbol.csv"
)


PLIK_JSON = os.path.join(
    KATALOG,
    "tags_world_map.json"
)


PLIK_CECHY = os.path.join(
    KATALOG,
    "mozg_kursy_przygotowane.csv"
)


PLIK_WYNIK = os.path.join(
    KATALOG,
    "dopasowanie_swiata_mozg_kursy_przygotowane.csv"
)



# ==========================================================
# WCZYTANIE JSON - MAPA ŚWIATA
# ==========================================================

with open(
    PLIK_JSON,
    "r",
    encoding="utf-8"
) as plik:

    TAGS_WORLD_MAP = json.load(
        plik
    )


print(
    "Załadowano grup JSON:",
    len(TAGS_WORLD_MAP)
)



# ==========================================================
# WCZYTANIE BAZY KURSÓW
#
# mozg_kursy_przygotowane.csv
#
# 0  mecz
# 1  kurs_1_start
# 2  kurs_X_start
# 3  kurs_2_start
# 4  kurs_1_koniec
# 5  kurs_X_koniec
# 6  kurs_2_koniec
# 7  zmiana_kurs_1
# 8  zmiana_kurs_X
# 9  zmiana_kurs_2
# 10 procent_kurs_1
# 11 procent_kurs_X
# 12 procent_kurs_2
# 13 wynik
# ==========================================================

BAZA_CECH = {}


with open(
    PLIK_CECHY,
    "r",
    encoding="utf-8"
) as plik:


    reader = csv.reader(
        plik,
        delimiter=";"
    )


    for row in reader:


        if len(row) >= 14:


            id_meczu = row[0].strip()


            BAZA_CECH[id_meczu] = row



print(
    "Załadowano meczów z kursami:",
    len(BAZA_CECH)
)



# ==========================================================
# ANALIZA AKTUALNYCH MECZÓW
# ==========================================================

WYNIKI = []


with open(
    PLIK_GRUPY,
    "r",
    encoding="utf-8"
) as plik:


    reader = csv.reader(
        plik,
        delimiter=";"
    )


    for row in reader:


        if len(row) < 2:
            continue



        id_meczu_predykcja = row[0].strip()

        grupa = row[1].strip()



        if grupa not in TAGS_WORLD_MAP:


            print(
                "Brak grupy:",
                grupa
            )

            continue



        historia = TAGS_WORLD_MAP[grupa]


        DOPASOWANE = []



        # --------------------------------------------------
        # SZUKANIE FAKTYCZNYCH DOPASOWAŃ
        # --------------------------------------------------

        for rekord in historia:


            id_historyczny = rekord["mecz"].strip()



            if id_historyczny in BAZA_CECH:


                dane = BAZA_CECH[id_historyczny]


                DOPASOWANE.append(

                    [

                    id_meczu_predykcja,

                    id_historyczny,

                    dane[1],   # kurs_1_start
                    dane[2],   # kurs_X_start
                    dane[3],   # kurs_2_start

                    dane[4],   # kurs_1_koniec
                    dane[5],   # kurs_X_koniec
                    dane[6],   # kurs_2_koniec

                    dane[7],   # zmiana_kurs_1
                    dane[8],   # zmiana_kurs_X
                    dane[9],   # zmiana_kurs_2

                    dane[10],  # procent_kurs_1
                    dane[11],  # procent_kurs_X
                    dane[12],  # procent_kurs_2

                    dane[13]   # wynik

                    ]

                )



        # tylko realne dopasowania

        ilosc_dopasowan = len(
            DOPASOWANE
        )



        # dodanie licznika

        for rekord in DOPASOWANE:


            rekord.insert(
                1,
                ilosc_dopasowan
            )


            WYNIKI.append(
                rekord
            )



# ==========================================================
# ZAPIS WYNIKU
# ==========================================================

with open(
    PLIK_WYNIK,
    "w",
    encoding="utf-8",
    newline=""
) as plik:


    writer = csv.writer(
        plik,
        delimiter=";"
    )


    writer.writerow(

        [

        "id_meczu_predykcja",
        "ilosc_dopsowan",
        "id_meczu",

        "kurs_1_start",
        "kurs_X_start",
        "kurs_2_start",

        "kurs_1_koniec",
        "kurs_X_koniec",
        "kurs_2_koniec",

        "zmiana_kurs_1",
        "zmiana_kurs_X",
        "zmiana_kurs_2",

        "procent_kurs_1",
        "procent_kurs_X",
        "procent_kurs_2",

        "wynik"

        ]

    )


    writer.writerows(
        WYNIKI
    )



# ==========================================================
# PODSUMOWANIE
# ==========================================================

print()

print(
    "================================"
)

print(
    "DOPASOWANIE ŚWIATA ZAKOŃCZONE"
)

print(
    "Zapisano:",
    PLIK_WYNIK
)

print(
    "Liczba rekordów:",
    len(WYNIKI)
)

print(
    "================================"
)

import os
import json
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import StandardScaler



# ============================================================
# KONFIGURACJA
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


DATA_DIR = os.path.join(
    BASE_DIR,
    "dane"
)



PLIKI = [

    "dopasowanie_swiata_kod_dataBase_futbol_trend.csv",

    "dopasowanie_swiata_kod_dataBase_futbol_trend_klasyfikatorr.csv",

    "dopasowanie_swiata_mozg_kursy_przygotowane.csv"

]



# ============================================================
# KLASYFIKACJA WYNIKU
# ============================================================


def klasyfikuj_wynik(wynik):

    try:

        wynik = str(wynik).strip()


        if ":" not in wynik:

            return None


        dom, wyjazd = wynik.split(":")


        dom = int(dom)

        wyjazd = int(wyjazd)



        if dom > wyjazd:

            return 1


        elif dom == wyjazd:

            return 0


        else:

            return -1


    except:

        return None



# ============================================================
# NORMALIZACJA
# ============================================================


def normalizuj(x):


    if x.max() == x.min():

        return x * 0


    return (

        x - x.min()

    ) / (

        x.max() - x.min()

    )



# ============================================================
# KORELACJA BEZ OSTRZEŻEŃ
# ============================================================


def policz_korelacje(cecha, y):


    try:

        if cecha.std() == 0:

            return 0


        wynik = np.corrcoef(

            cecha,

            y

        )[0,1]


        if np.isnan(wynik):

            return 0


        return abs(wynik)


    except:

        return 0



# ============================================================
# ANALIZA JEDNEGO PLIKU
# ============================================================


def analizuj_plik(nazwa_pliku):


    INPUT = os.path.join(

        DATA_DIR,

        nazwa_pliku

    )



    nazwa_json = nazwa_pliku.replace(

        ".csv",

        ".json"

    )



    OUTPUT = os.path.join(

        DATA_DIR,

        nazwa_json

    )



    print()
    print("="*70)
    print("ANALIZA ŚWIATA:")
    print(nazwa_pliku)
    print("="*70)



    df = pd.read_csv(

        INPUT,

        sep=";",

        encoding="utf-8"

    )



    print(
        "Rekordów:",
        len(df)
    )



    kolumny = list(
        df.columns
    )



    # --------------------------------------------------------
    # STAŁE STRUKTURY
    # --------------------------------------------------------


    ID_PRED = kolumny[0]

    ILOSC_DOPASOWAN = kolumny[1]

    ID_HISTORYCZNE = kolumny[2]

    WYNIK = kolumny[-1]



    # dynamiczne cechy

    CECHY = [

        ILOSC_DOPASOWAN

    ] + kolumny[3:-1]



    print(
        "Cechy:",
        CECHY
    )



    WORLD_MEMORY = {

        "plik_zrodlo": nazwa_pliku,

        "liczba_rekordow": len(df),

        "swiaty": {}

    }



    # ========================================================
    # KAŻDY MECZ PREDYKCYJNY OSOBNO
    # ========================================================


    for id_predykcji, grupa in df.groupby(
        ID_PRED
    ):


        print()

        print(
            "ŚWIAT:",
            id_predykcji
        )


        print(
            "Historia:",
            len(grupa)
        )



        dane = grupa.copy()



        dane["klasa"] = dane[WYNIK].apply(

            klasyfikuj_wynik

        )



        dane = dane.dropna(

            subset=[

                "klasa"

            ]

        )



        if len(dane) < 5:

            print(
                "Za mało danych"
            )

            continue



        X = dane[CECHY].copy()


        y = dane["klasa"]



        X = X.apply(

            pd.to_numeric,

            errors="coerce"

        )


        X = X.fillna(0)



        # ----------------------------------------------------
        # KORELACJA
        # ----------------------------------------------------


        korelacja = {}


        for cecha in CECHY:


            korelacja[cecha] = policz_korelacje(

                X[cecha],

                y

            )



        korelacja = pd.Series(

            korelacja

        )



        # ----------------------------------------------------
        # RANDOM FOREST
        # ----------------------------------------------------


        rf = RandomForestClassifier(

            n_estimators=300,

            random_state=42,

            class_weight="balanced"

        )



        rf.fit(

            X,

            y

        )



        rf_score = pd.Series(

            rf.feature_importances_,

            index=CECHY

        )



        # ----------------------------------------------------
        # MUTUAL INFORMATION
        # ----------------------------------------------------


        scaler = StandardScaler()



        X_scaled = scaler.fit_transform(

            X

        )



        dc = mutual_info_classif(

            X_scaled,

            y,

            random_state=42

        )



        dc_score = pd.Series(

            dc,

            index=CECHY

        )



        # ----------------------------------------------------
        # NORMALIZACJA
        # ----------------------------------------------------


        korelacja_n = normalizuj(

            korelacja

        )


        rf_n = normalizuj(

            rf_score

        )


        dc_n = normalizuj(

            dc_score

        )



        ranking = []



        for cecha in CECHY:


            ranking.append(

                {

                "cecha": cecha,

                "korelacja": float(

                    korelacja_n[cecha]

                ),

                "RF": float(

                    rf_n[cecha]

                ),

                "DC": float(

                    dc_n[cecha]

                ),

                "sila": float(

                    korelacja_n[cecha] * 0.4

                    +

                    rf_n[cecha] * 0.3

                    +

                    dc_n[cecha] * 0.3

                )

                }

            )



        ranking = sorted(

            ranking,

            key=lambda x:

            x["sila"],

            reverse=True

        )



        WORLD_MEMORY["swiaty"][id_predykcji] = {


            "ilosc_dopasowan": int(

                grupa[ILOSC_DOPASOWAN].iloc[0]

            ),


            "liczba_historycznych_meczow": len(grupa),


            "ranking_cech": ranking


        }



    # ========================================================
    # ZAPIS JSON
    # ========================================================


    with open(

        OUTPUT,

        "w",

        encoding="utf-8"

    ) as plik:


        json.dump(

            WORLD_MEMORY,

            plik,

            indent=4,

            ensure_ascii=False

        )



    print()

    print(
        "ZAPISANO:"
    )

    print(
        OUTPUT
    )



# ============================================================
# START
# ============================================================


for plik in PLIKI:


    analizuj_plik(

        plik

    )



print()
print("="*70)
print("WSZYSTKIE ŚWIATY ZBUDOWANE")
print("="*70)

import os
import json
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import StandardScaler



# ============================================================
# KONFIGURACJA
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


DATA_DIR = os.path.join(
    BASE_DIR,
    "dane"
)



PLIKI = [

    "dopasowane_trendy_historyczne.csv",


]



# ============================================================
# KLASYFIKACJA WYNIKU
# ============================================================


def klasyfikuj_wynik(wynik):

    try:

        wynik = str(wynik).strip()


        if ":" not in wynik:

            return None


        dom, wyjazd = wynik.split(":")


        dom = int(dom)

        wyjazd = int(wyjazd)



        if dom > wyjazd:

            return 1


        elif dom == wyjazd:

            return 0


        else:

            return -1


    except:

        return None



# ============================================================
# NORMALIZACJA
# ============================================================


def normalizuj(x):


    if x.max() == x.min():

        return x * 0


    return (

        x - x.min()

    ) / (

        x.max() - x.min()

    )



# ============================================================
# KORELACJA BEZ OSTRZEŻEŃ
# ============================================================


def policz_korelacje(cecha, y):


    try:

        if cecha.std() == 0:

            return 0


        wynik = np.corrcoef(

            cecha,

            y

        )[0,1]


        if np.isnan(wynik):

            return 0


        return abs(wynik)


    except:

        return 0



# ============================================================
# ANALIZA JEDNEGO PLIKU
# ============================================================


def analizuj_plik(nazwa_pliku):


    INPUT = os.path.join(

        DATA_DIR,

        nazwa_pliku

    )



    nazwa_json = nazwa_pliku.replace(

        ".csv",

        ".json"

    )



    OUTPUT = os.path.join(

        DATA_DIR,

        nazwa_json

    )



    print()
    print("="*70)
    print("ANALIZA ŚWIATA:")
    print(nazwa_pliku)
    print("="*70)



    df = pd.read_csv(

        INPUT,

        sep=";",

        encoding="utf-8"

    )



    print(
        "Rekordów:",
        len(df)
    )



    kolumny = list(
        df.columns
    )



    # --------------------------------------------------------
    # STAŁE STRUKTURY
    # --------------------------------------------------------


    ID_PRED = kolumny[0]

    ILOSC_DOPASOWAN = kolumny[1]

    ID_HISTORYCZNE = kolumny[2]

    WYNIK = kolumny[-1]



    # dynamiczne cechy

    CECHY = [

        ILOSC_DOPASOWAN

    ] + kolumny[3:-1]



    print(
        "Cechy:",
        CECHY
    )



    WORLD_MEMORY = {

        "plik_zrodlo": nazwa_pliku,

        "liczba_rekordow": len(df),

        "swiaty": {}

    }



    # ========================================================
    # KAŻDY MECZ PREDYKCYJNY OSOBNO
    # ========================================================


    for id_predykcji, grupa in df.groupby(
        ID_PRED
    ):


        print()

        print(
            "ŚWIAT:",
            id_predykcji
        )


        print(
            "Historia:",
            len(grupa)
        )



        dane = grupa.copy()



        dane["klasa"] = dane[WYNIK].apply(

            klasyfikuj_wynik

        )



        dane = dane.dropna(

            subset=[

                "klasa"

            ]

        )



        if len(dane) < 5:

            print(
                "Za mało danych"
            )

            continue



        X = dane[CECHY].copy()


        y = dane["klasa"]



        X = X.apply(

            pd.to_numeric,

            errors="coerce"

        )


        X = X.fillna(0)



        # ----------------------------------------------------
        # KORELACJA
        # ----------------------------------------------------


        korelacja = {}


        for cecha in CECHY:


            korelacja[cecha] = policz_korelacje(

                X[cecha],

                y

            )



        korelacja = pd.Series(

            korelacja

        )



        # ----------------------------------------------------
        # RANDOM FOREST
        # ----------------------------------------------------


        rf = RandomForestClassifier(

            n_estimators=300,

            random_state=42,

            class_weight="balanced"

        )



        rf.fit(

            X,

            y

        )



        rf_score = pd.Series(

            rf.feature_importances_,

            index=CECHY

        )



        # ----------------------------------------------------
        # MUTUAL INFORMATION
        # ----------------------------------------------------


        scaler = StandardScaler()



        X_scaled = scaler.fit_transform(

            X

        )



        dc = mutual_info_classif(

            X_scaled,

            y,

            random_state=42

        )



        dc_score = pd.Series(

            dc,

            index=CECHY

        )



        # ----------------------------------------------------
        # NORMALIZACJA
        # ----------------------------------------------------


        korelacja_n = normalizuj(

            korelacja

        )


        rf_n = normalizuj(

            rf_score

        )


        dc_n = normalizuj(

            dc_score

        )



        ranking = []



        for cecha in CECHY:


            ranking.append(

                {

                "cecha": cecha,

                "korelacja": float(

                    korelacja_n[cecha]

                ),

                "RF": float(

                    rf_n[cecha]

                ),

                "DC": float(

                    dc_n[cecha]

                ),

                "sila": float(

                    korelacja_n[cecha] * 0.4

                    +

                    rf_n[cecha] * 0.3

                    +

                    dc_n[cecha] * 0.3

                )

                }

            )



        ranking = sorted(

            ranking,

            key=lambda x:

            x["sila"],

            reverse=True

        )



        WORLD_MEMORY["swiaty"][id_predykcji] = {


            "ilosc_dopasowan": int(

                grupa[ILOSC_DOPASOWAN].iloc[0]

            ),


            "liczba_historycznych_meczow": len(grupa),


            "ranking_cech": ranking


        }



    # ========================================================
    # ZAPIS JSON
    # ========================================================


    with open(

        OUTPUT,

        "w",

        encoding="utf-8"

    ) as plik:


        json.dump(

            WORLD_MEMORY,

            plik,

            indent=4,

            ensure_ascii=False

        )



    print()

    print(
        "ZAPISANO:"
    )

    print(
        OUTPUT
    )



# ============================================================
# START
# ============================================================


for plik in PLIKI:


    analizuj_plik(

        plik

    )



print()
print("="*70)
print("WSZYSTKIE ŚWIATY ZBUDOWANE")
print("="*70)


# ============================================================
# WORLD FOOTBALL ANALYSIS GENERATOR

# FRAGMENT 1/2

# Budowa pierwszej warstwy wiedzy świata piłki nożnej
# na podstawie grup kursowych i historycznych wyników
# ============================================================


import os

import csv

import json


from collections import Counter







# ============================================================
# KONFIGURACJA SYSTEMU
# ============================================================


BASE_DIR = os.path.dirname(

    os.path.abspath(__file__)

)



DATA_DIR = os.path.join(

    BASE_DIR,

    "dane"

)



WORLD_DIR = os.path.join(

    BASE_DIR,

    "WORLD"

)



WORLD_CURRENT_DIR = os.path.join(

    WORLD_DIR,

    "aktualny"

)



os.makedirs(

    WORLD_CURRENT_DIR,

    exist_ok=True

)







# ============================================================
# PLIKI WEJŚCIOWE
# ============================================================


PLIK_GRUP = os.path.join(

    DATA_DIR,

    "matches_by_odds.csv"

)







# ============================================================
# DEFINICJA WYNIKÓW NAJBARDZIEJ ISTOTNYCH
# ============================================================


WYNIKI_DOM = [

    "1:0",

    "2:0",

    "3:0",

    "2:1",

    "3:1",

    "3:2"

]





WYNIKI_WYJAZD = [

    "0:1",

    "0:2",

    "0:3",

    "1:2",

    "1:3",

    "2:3"

]





WYNIKI_REMIS = [

    "0:0",

    "1:1",

    "2:2"

]





WYNIKI_ANALIZOWANE = (

    WYNIKI_DOM

    +

    WYNIKI_WYJAZD

    +

    WYNIKI_REMIS

)







# ============================================================
# WCZYTANIE MAPY GRUP
# ============================================================


GRUPY = {}





with open(

    PLIK_GRUP,

    "r",

    encoding="utf-8"

) as plik:


    reader = csv.reader(

        plik,

        delimiter=";"

    )



    for row in reader:


        if len(row) < 2:

            continue




        grupa = row[0].strip()



        wyniki = []



        for element in row[1:]:


            element = element.strip()



            if ";" in element:


                wyniki.extend(

                    element.split(";")

                )

            else:


                wyniki.append(

                    element

                )






        poprawne = []



        for wynik in wyniki:


            try:


                dom, wyjazd = wynik.split(":")


                int(dom)

                int(wyjazd)



                poprawne.append(

                    wynik

                )


            except:


                pass






        GRUPY[grupa] = poprawne







print(

    "Załadowano grup:",

    len(GRUPY)

)








# ============================================================
# OKREŚLENIE TYPU MECZU
# ============================================================


def typ_wyniku(wynik):


    try:


        dom, wyjazd = wynik.split(":")


        dom = int(dom)

        wyjazd = int(wyjazd)



        if dom > wyjazd:


            return "1"



        elif dom == wyjazd:


            return "X"



        else:


            return "2"



    except:


        return None








# ============================================================
# KLASYFIKACJA WYNIKU
# ============================================================


def kategoria_wyniku(wynik):


    if wynik in WYNIKI_DOM:


        return "trafiony_wynik_gospodarze"




    elif wynik in WYNIKI_WYJAZD:


        return "trafiony_wynik_goscie"




    elif wynik in WYNIKI_REMIS:


        return "trafiony_wynik_remis"




    typ = typ_wyniku(wynik)



    if typ == "1":


        return "inne_wygrane_gospodarzy"



    elif typ == "2":


        return "inne_wygrane_gosci"



    elif typ == "X":


        return "inne_remisy"



    return "nieznany"








# ============================================================
# GŁÓWNY ANALIZATOR GRUPY
# ============================================================


def analiza_grupy(wyniki):


    ilosc = len(wyniki)



    if ilosc == 0:


        return {}




    licznik = Counter(

        wyniki

    )




    kategorie = Counter()



    for wynik in wyniki:


        kategorie[

            kategoria_wyniku(wynik)

        ] += 1







    wyniki_docelowe = {}



    for wynik in WYNIKI_ANALIZOWANE:


        wystapienia = licznik.get(

            wynik,

            0

        )


        wyniki_docelowe[wynik] = {


            "ilosc":

                wystapienia,


            "procent":

                round(

                    wystapienia

                    /

                    ilosc

                    *

                    100,

                    2

                )

        }






    profil = {


        "gospodarze":0,


        "remis":0,


        "goscie":0

    }




    gole_dom = 0


    gole_wyj = 0





    for wynik in wyniki:


        typ = typ_wyniku(wynik)



        if typ == "1":


            profil["gospodarze"] += 1



        elif typ == "X":


            profil["remis"] += 1



        elif typ == "2":


            profil["goscie"] += 1




        try:


            dom, wyj = wynik.split(":")


            gole_dom += int(dom)


            gole_wyj += int(wyj)



        except:


            pass





    for element in profil:


        profil[element] = {


            "ilosc":

                profil[element],


            "procent":

                round(

                    profil[element]

                    /

                    ilosc

                    *

                    100,

                    2

                )

        }







    return {


        "ilosc_przypadkow":

            ilosc,



        "wyniki_docelowe":

            wyniki_docelowe,



        "profil_meczu_1X2":

            profil,



        "statystyka_goli":{


            "srednia_gole_dom":

                round(

                    gole_dom / ilosc,

                    3

                ),



            "srednia_gole_wyj":

                round(

                    gole_wyj / ilosc,

                    3

                ),



            "srednia_goli_mecz":

                round(

                    (gole_dom + gole_wyj)

                    /

                    ilosc,

                    3

                )

        }

    }
# ============================================================
# FRAGMENT 2/2
#
# BUDOWA TRZECH WARSTW ŚWIATA
# I ZAPIS AKTUALNEJ WIEDZY
# ============================================================




# ============================================================
# KATALOGI ŚWIATA
# ============================================================


WORLD_LEVEL_1 = {}

WORLD_LEVEL_2 = {}

WORLD_FULL = {}







# ============================================================
# ROZBIJANIE NA POZIOMY
#
# przykład:
#
# poziom3poziom17poziom20
#
# wynik:
#
# [
#   poziom3,
#   poziom17,
#   poziom20
# ]
#
# ============================================================


def pobierz_poziomy(grupa):


    elementy = grupa.split(
        "poziom"
    )


    poziomy = []



    for element in elementy:


        element = element.strip()



        if element:


            poziomy.append(

                "poziom" + element

            )



    return poziomy







# ============================================================
# BUDOWA MAPY ŚWIATA
# ============================================================


for grupa, wyniki in GRUPY.items():


    poziomy = pobierz_poziomy(

        grupa

    )



    if len(poziomy) == 0:


        continue







    # ========================================================
    # POZIOM 1
    #
    # przykład:
    #
    # poziom3
    #
    # zbiera wszystkie:
    #
    # poziom3poziom17
    # poziom3poziom17poziom20
    #
    # ========================================================


    poziom_1 = poziomy[0]



    if poziom_1 not in WORLD_LEVEL_1:


        WORLD_LEVEL_1[poziom_1] = []



    WORLD_LEVEL_1[poziom_1].extend(

        wyniki

    )









    # ========================================================
    # POZIOM 2
    #
    # przykład:
    #
    # poziom3poziom17
    #
    # ========================================================


    if len(poziomy) >= 2:



        poziom_2 = (

            poziomy[0]

            +

            poziomy[1]

        )




        if poziom_2 not in WORLD_LEVEL_2:


            WORLD_LEVEL_2[poziom_2] = []



        WORLD_LEVEL_2[poziom_2].extend(

            wyniki

        )









    # ========================================================
    # PEŁNA GRUPA
    #
    # dokładny przypadek
    #
    # poziom3poziom17poziom20
    #
    # ========================================================


    WORLD_FULL[grupa] = wyniki







# ============================================================
# ANALIZA WARSTWY ŚWIATA
# ============================================================


def analizuj_warstwę(dane):


    wynik = {}



    for nazwa, historia in dane.items():



        wynik[nazwa] = {


            "poziom":

                nazwa,


            "analiza":

                analiza_grupy(

                    historia

                )

        }



    return wynik







# ============================================================
# GENEROWANIE TRZECH ŚWIATÓW
# ============================================================


ANALIZA_LEVEL_1 = analizuj_warstwę(

    WORLD_LEVEL_1

)



ANALIZA_LEVEL_2 = analizuj_warstwę(

    WORLD_LEVEL_2

)



ANALIZA_FULL = analizuj_warstwę(

    WORLD_FULL

)







# ============================================================
# ZAPIS PLIKÓW ŚWIATA
# ============================================================


PLIKI_WORLD = {


    "WORLD_LEVEL_1_ANALYSIS.json":

        ANALIZA_LEVEL_1,



    "WORLD_LEVEL_2_ANALYSIS.json":

        ANALIZA_LEVEL_2,



    "WORLD_FULL_GROUP_ANALYSIS.json":

        ANALIZA_FULL

}







for nazwa_pliku, dane in PLIKI_WORLD.items():


    sciezka = os.path.join(

        WORLD_CURRENT_DIR,

        nazwa_pliku

    )



    with open(

        sciezka,

        "w",

        encoding="utf-8"

    ) as plik:



        json.dump(

            dane,

            plik,

            indent=4,

            ensure_ascii=False

        )



    print(

        "Zapisano:",

        sciezka

    )









# ============================================================
# PODSUMOWANIE GENERATORA
# ============================================================


print()

print(
    "=========================================="
)

print(
    " WORLD FOOTBALL ANALYSIS GOTOWY "
)

print(
    "=========================================="
)


print(

    "Poziom 1:",

    len(ANALIZA_LEVEL_1)

)



print(

    "Poziom 2:",

    len(ANALIZA_LEVEL_2)

)



print(

    "Pełne grupy:",

    len(ANALIZA_FULL)

)



print()

print(

    "Katalog świata:",

    WORLD_CURRENT_DIR

)


print()

print(
    "=========================================="
)


import os
import csv
import json
from datetime import datetime



# ============================================================
# KONFIGURACJA
# ============================================================


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


DATA_DIR = os.path.join(
    BASE_DIR,
    "dane"
)


WORLD_DIR = os.path.join(
    BASE_DIR,
    "WORLD",
    "aktualny"
)


os.makedirs(
    WORLD_DIR,
    exist_ok=True
)



PLIK_MECZE = os.path.join(
    DATA_DIR,
    "analizaKursowDni_dataBase_futbol.csv"
)


PLIK_POISSON = os.path.join(
    DATA_DIR,
    "analiza_poisson_dixon.csv"
)



WORLD_LEVEL_1_FILE = os.path.join(
    WORLD_DIR,
    "WORLD_LEVEL_1_ANALYSIS.json"
)


WORLD_LEVEL_2_FILE = os.path.join(
    WORLD_DIR,
    "WORLD_LEVEL_2_ANALYSIS.json"
)


WORLD_FULL_FILE = os.path.join(
    WORLD_DIR,
    "WORLD_FULL_GROUP_ANALYSIS.json"
)


OUTPUT = os.path.join(
    WORLD_DIR,
    "WORLD_MATCH_DATABASE.json"
)





# ============================================================
# WCZYTANIE ŚWIATA
# ============================================================


def load_json(path):


    if not os.path.exists(path):

        print(
            "Brak pliku:",
            path
        )

        return {}



    with open(

        path,

        "r",

        encoding="utf-8"

    ) as plik:


        return json.load(plik)





WORLD_LEVEL_1 = load_json(
    WORLD_LEVEL_1_FILE
)


WORLD_LEVEL_2 = load_json(
    WORLD_LEVEL_2_FILE
)


WORLD_FULL = load_json(
    WORLD_FULL_FILE
)





print(
    "Załadowano świat:"
)

print(
    "Level 1:",
    len(WORLD_LEVEL_1)
)

print(
    "Level 2:",
    len(WORLD_LEVEL_2)
)

print(
    "Full:",
    len(WORLD_FULL)
)







# ============================================================
# FUNKCJA POZIOMÓW
# ============================================================


def zbuduj_poziomy(grupa):


    elementy = grupa.split(
        "poziom"
    )


    poziomy = []



    for e in elementy:


        if e.strip():

            poziomy.append(

                "poziom" + e.strip()

            )



    wynik = {


        "level_1":
            None,


        "level_2":
            None,


        "full":
            grupa

    }



    if len(poziomy) >= 1:

        wynik["level_1"] = poziomy[0]



    if len(poziomy) >= 2:

        wynik["level_2"] = (

            poziomy[0]

            +

            poziomy[1]

        )



    return wynik







# ============================================================
# WCZYTANIE POISSON
# ============================================================


POISSON = {}



with open(

    PLIK_POISSON,

    "r",

    encoding="utf-8"

) as plik:


    reader = csv.DictReader(

        plik,

        delimiter=";"

    )


    for row in reader:


        mecz = row[
            "id_meczu_predykcja"
        ]



        if mecz not in POISSON:


            POISSON[mecz] = []



        POISSON[mecz].append(


            {


                "wynik":
                    row["wynik"],


                "gole_dom":
                    row["gole_dom"],


                "gole_wyj":
                    row["gole_wyj"],


                "gole":
                    row["gole"],


                "prawdopodobienstwo_dc":
                    float(
                        row["prawdopodobienstwo_dc"]
                    )


            }

        )





print(
    "Poisson meczów:",
    len(POISSON)
)







# ============================================================
# BUDOWA WORLD MATCH DATABASE
# ============================================================


WORLD_MATCH_DATABASE = {}



with open(

    PLIK_MECZE,

    "r",

    encoding="utf-8"

) as plik:


    reader = csv.reader(

        plik,

        delimiter=";"

    )


    next(reader)



    for row in reader:


        if len(row) < 2:

            continue



        mecz = row[0].strip()


        grupa = row[1].strip()



        poziomy = zbuduj_poziomy(

            grupa

        )



        rekord = {


            "metadata": {


                "mecz":

                    mecz,


                "grupa_kursowa":

                    grupa,


                "data_budowy":

                    str(
                        datetime.now()
                    )

            },



            "identyfikacja": poziomy,



            "world_analysis": {


                "level_1":

                    WORLD_LEVEL_1.get(

                        poziomy["level_1"],

                        {}

                    ),



                "level_2":

                    WORLD_LEVEL_2.get(

                        poziomy["level_2"],

                        {}

                    ),



                "full_group":

                    WORLD_FULL.get(

                        poziomy["full"],

                        {}

                    )

            },



            "poisson_dixon_coles":

                POISSON.get(

                    mecz,

                    []

                )

        }



        WORLD_MATCH_DATABASE[mecz] = rekord







# ============================================================
# ZAPIS
# ============================================================


with open(

    OUTPUT,

    "w",

    encoding="utf-8"

) as plik:


    json.dump(

        WORLD_MATCH_DATABASE,

        plik,

        indent=4,

        ensure_ascii=False

    )





print()

print(
    "======================================"
)

print(
    "WORLD MATCH DATABASE GOTOWY"
)

print(
    "Mecze:",
    len(WORLD_MATCH_DATABASE)
)

print(
    "Zapis:"
)

print(
    OUTPUT
)

print(
    "======================================"
)

# ==========================================================
# AI FOOTBALL AGENT SYSTEM
# SIEĆ 1 - ZMIANY KURSÓW
# ==========================================================












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
    "dane/kursy_przygotowane.csv"
)


PLIK_TRENING = (
    "dane/mozg_kursy_przygotowane.csv"
)


KATALOG_MODELE = (
    "modele_kursy_przygotowane"
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


"siec_01_start_kursow":[

    "kurs_1_start",
    "kurs_X_start",
    "kurs_2_start"

],


"siec_02_koniec_kursow":[

    "kurs_1_koniec",
    "kurs_X_koniec",
    "kurs_2_koniec"

],


"siec_03_zmiana_kursow":[

    "zmiana_kurs_1",
    "zmiana_kurs_X",
    "zmiana_kurs_2"

],


"siec_04_procent_kursow":[

    "procent_kurs_1",
    "procent_kurs_X",
    "procent_kurs_2"

],


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

        ["mecz"]

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


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_01_zmiana_kursow"


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
    r"\siec_01_zmiana_kursow"
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


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_02_amplituda"


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
    r"\siec_02_amplituda"
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


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_03_tempo"


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
    r"\siec_03_tempo"
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


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_04_max_wahanie"


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
    r"\siec_04_max_wahanie"
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


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_05_start_raw"


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
    r"\siec_05_start_raw"
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


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_06_koniec_raw"


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
    r"\siec_06_koniec_raw"
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


KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_07_log_start"


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
    r"\siec_07_log_start"
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


