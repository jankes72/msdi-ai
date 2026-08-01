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