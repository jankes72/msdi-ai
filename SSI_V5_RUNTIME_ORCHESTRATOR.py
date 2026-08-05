import subprocess
import time
from datetime import datetime, timedelta
import os

# Skrypty i harmonogram uruchomień (godziny w 24h, format HH:MM)
harmonogram = {
    'SSI_V5_MATCH_RESULTS_COLLECTOR.py': ['01:58'],
    'SSI_V5_MATCH_RESULTS_UPDATER.py': ['02:04'],

    'start_ssi_test.py': [
        '02:07',
        '15:07',
        '21:07'
    ],

    'SSI_V5_FOOTBALL_BETTING_MARKET_OBSERVER.py': [
        '01:01','01:47','02:01','02:31',
        '03:01','03:31','04:01','04:31',
        '05:00','05:30','06:01','06:31',
        '07:01','07:31','08:01','08:31',
        '09:01','09:31','10:01','10:31',
        '11:01','11:31','12:01','12:31',
        '13:00','13:30','14:01','14:31',
        '15:01','15:31','16:01','16:31',
        '17:01','17:31','18:01','18:31',
        '19:01','19:31','20:01','20:31',
        '21:01','21:31','22:01','22:31',
        '23:01','23:31','23:57'
    ],

    'SSI_V5_SPORTS_WORLD_MODEL_BUILDER.py': ['08:03'],

    'SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py': ['08:05']
}


def run_script(script_name):
    teraz = datetime.now()

    print(
        f"⏳ [{teraz.strftime('%Y-%m-%d %H:%M:%S')}] "
        f"Uruchamiam w nowym CMD: {script_name}"
    )

    if script_name.startswith("pandora_sts/"):
        folder = "pandora_sts"
        plik = script_name.split('/')[-1]

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                f"CMD - {plik}",
                "cmd",
                "/c",
                f"python {plik} && timeout /t 5 && exit"
            ],
            cwd=folder
        )

    else:

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                f"CMD - {script_name}",
                "cmd",
                "/c",
                f"python {script_name} && timeout /t 5 && exit"
            ]
        )

    print(f"✅ Otwarto nowe okno CMD: {script_name}")


def wait_seconds(seconds):
    print(f"🕒 Czekam {int(seconds)} sekund...\n")
    time.sleep(seconds)


def main_loop():

    ostatnie_wykonanie = {
        skrypt: None for skrypt in harmonogram
    }


    while True:

        teraz = datetime.now()
        current_time_str = teraz.strftime('%H:%M')


        # Harmonogram minutowy
        for skrypt, godziny in harmonogram.items():

            if godziny:

                if current_time_str in godziny:

                    ostatnia_wyk = ostatnie_wykonanie[skrypt]

                    if ostatnia_wyk != (
                        teraz.date(),
                        current_time_str
                    ):

                        run_script(skrypt)

                        ostatnie_wykonanie[skrypt] = (
                            teraz.date(),
                            current_time_str
                        )


        # Skrypty bez godzin - pełna godzina
        pelna_godzina = teraz.replace(
            minute=0,
            second=0,
            microsecond=0
        )


        for skrypt, godziny in harmonogram.items():

            if not godziny:

                ostatnia_wyk = ostatnie_wykonanie[skrypt]

                if ostatnia_wyk != pelna_godzina:

                    run_script(skrypt)

                    ostatnie_wykonanie[skrypt] = pelna_godzina



        # Czekanie do kolejnej minuty

        nastepna_minuta = (
            teraz + timedelta(minutes=1)
        ).replace(
            second=0,
            microsecond=0
        )


        sekundy_do_czekania = (
            nastepna_minuta - datetime.now()
        ).total_seconds()


        if sekundy_do_czekania > 0:
            wait_seconds(sekundy_do_czekania)



if __name__ == "__main__":
    main_loop()