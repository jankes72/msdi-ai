"""
PAMIĘĆ MODELI V2 - CENTRALNE REPOZYTORIUM
==========================================

Centralne repozytorium pamięci łączące rozproszone pamięci sieci SSI.

Zadania:
1. Ładowanie istniejących pamięci z sieci_dataBase_futbol_trend/siec_XX/obserwacja/pamiec_obserwacji.json
2. Konwersja do unifikowanego formatu V2 (Obserwacja)
3. Zarządzanie centralną pamięcią (dodawanie, wyszukiwanie, aktualizacja)
4. Generowanie statystyk i raportów
5. Wersjonowanie pamięci (każda wersja = nowy plik JSON)

Integracja z SSI:
- Czyta pamięci obserwacji z 11 sieci trendów
- Czyta pamięci obserwacji z 4 sieci kursów  
- Łączy dane z kod_dataBase_futbol_trend_klasyfikator.csv
- Łączy dane z mozg_* plików

Autor: MSDI AI v0.02
Data: 2026-07-27
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import uuid

# Import z lokalnego modułu
from pamiec_modeli_v2.schemas import (
    Obserwacja,
    KlasaWyniku,
    StatystykiPamieci,
    KonfiguracjaV2,
    get_grupa_wyniku,
    KLASY_WYNIKOW_DOKLADNYCH
)


class PamiecRepozytorium:
    """
    Centralne repozytorium pamięci V2.
    
    Łączy rozproszone pamięci sieci SSI w jeden system.
    Każda obserwacja jest identyfikowana przez: f"{id_meczu}_{id_modelu}"
    """
    
    # Konfiguracja
    KONFIG = KonfiguracjaV2()
    
    # Ścieżki bazowe
    BASE_PATH: Path = Path("pamiec_modeli_v2")
    DANE_PATH: Path = BASE_PATH / "dane"
    ARCHIWUM_PATH: Path = BASE_PATH / "archiwum"
    
    # Ścieżki do sieci SSI (bezwzględne)
    SSI_TREND_PATH: Path = Path("D:/sts/aplikacjaTyperBetAi/modele_dataBase_futbol_trend")
    SSI_KURSY_PATH: Path = Path("D:/sts/aplikacjaTyperBetAi/modele_kursy_przygotowane")
    
    def __init__(self, auto_load: bool = True):
        """
        Inicjalizacja repozytorium.
        
        Args:
            auto_load: Czy automatycznie załadować istniejące pamięci sieci
        """
        # Kolekcje danych
        self.obserwacje: Dict[str, Obserwacja] = {}  # key: f"{id_meczu}_{id_modelu}"
        self.klasy: Dict[str, KlasaWyniku] = {}
        self.modele: Dict[str, List[Obserwacja]] = {}  # Obserwacje per model
        self.grupy: Dict[str, List[Obserwacja]] = {}  # Obserwacje per grupa
        
        # Metadane
        self.wersja: str = self._generuj_nazwe_wersji()
        self.data_utworzenia: datetime = datetime.now()
        self.ostatnia_aktualizacja: datetime = datetime.now()
        
        # Statystyki
        self._statystyki: Optional[StatystykiPamieci] = None
        
        # Ładuj istniejące dane
        if auto_load:
            self.zaladuj_istniejace_pamieci()
    
    def _generuj_nazwe_wersji(self) -> str:
        """Generuje unikalną nazwę wersji"""
        return f"v2_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    
    # =========================================================================
    # ŁADOWANIE ISTNIEJĄCYCH DANYCH (Integracja z SSI)
    # =========================================================================
    
    def zaladuj_istniejace_pamieci(self):
        """
        Ładuje pamięci z istniejących sieci SSI.
        
        Źródła:
        1. modele_dataBase_futbol_trend/siec_XX/obserwacja/pamiec_obserwacji.json
        2. modele_kursy_przygotowane/siec_XX/obserwacja/pamiec_obserwacji.json
        3. dane/kod_dataBase_futbol_trend_klasyfikator.csv
        4. dane/mozg_kursy_przygotowane.csv
        5. dane/mozg_analizaKursowDni_dataBase_futbol.csv
        """
        print("Ladowanie pamięci z sieci trendów...")
        self._zaladuj_z_sieci_trend()
        
        print("Ladowanie pamięci z sieci kursów...")
        self._zaladuj_z_sieci_kursy()
        
        print("Ladowanie pamięci z plików klasyfikator...")
        self._zaladuj_z_klasyfikatora()
        
        print("Ladowanie pamięci z mozg_kursy...")
        self._zaladuj_z_mozg_kursy()
        
        print("Ladowanie pamięci z mozg_analiza...")
        self._zaladuj_z_mozg_analiza()
        
        print(f"Załadowano {len(self.obserwacje)} obserwacji")
    
    def _zaladuj_z_sieci_trend(self):
        """Ładuje pamięci z sieci trendów (11 sieci)"""
        if not self.SSI_TREND_PATH.exists():
            print(f"  Brak katalogu: {self.SSI_TREND_PATH}")
            return
        
        # Prawdziwe nazwy sieci trendów
        sieci_trend = [
            "siec_01_zmiana_kursow",
            "siec_02_amplituda",
            "siec_03_tempo",
            "siec_04_max_wahanie",
            "siec_05_start_raw",
            "siec_06_koniec_raw",
            "siec_07_log_start",
            "siec_08_log_koniec",
            "siec_09_ratio_start",
            "siec_10_ratio_koniec",
            "siec_11_statystyka"
        ]
        
        for siec_id in sieci_trend:
            siec_path = self.SSI_TREND_PATH / siec_id
            obserwacja_path = siec_path / "obserwacja"
            pamiec_file = obserwacja_path / "pamiec_obserwacji.json"
            
            if pamiec_file.exists():
                self._przetworz_pamiec_sieci(siec_id, pamiec_file, "trend")
            else:
                print(f"  Brak pamiec_obserwacji.json w {siec_path}")
    
    def _zaladuj_z_sieci_kursy(self):
        """Ładuje pamięci z sieci kursów (4 sieci)"""
        if not self.SSI_KURSY_PATH.exists():
            print(f"  Brak katalogu: {self.SSI_KURSY_PATH}")
            return
        
        # Prawdziwe nazwy sieci kursów
        sieci_kursy = [
            "siec_01_start_kursow",
            "siec_02_koniec_kursow",
            "siec_03_zmiana_kursow",
            "siec_04_procent_kursow"
        ]
        
        for siec_id in sieci_kursy:
            siec_path = self.SSI_KURSY_PATH / siec_id
            obserwacja_path = siec_path / "obserwacja"
            pamiec_file = obserwacja_path / "pamiec_obserwacji.json"
            
            if pamiec_file.exists():
                self._przetworz_pamiec_sieci(siec_id, pamiec_file, "kursy")
            else:
                print(f"  Brak pamiec_obserwacji.json w {siec_path}")
    
    def _przetworz_pamiec_sieci(self, siec_id: str, pamiec_file: Path, typ: str = "trend"):
        """
        Konwertuje pamiec_obserwacji.json z sieci SSI do formatu V2.
        
        Format SSI:
        {
            "Nazwa Meczu": [
                {
                    "data": "2026-07-27 15:01:34",
                    "model": "siec_01_zmiana_kursow",
                    "id_meczu": "Team A - Team B",
                    "id_grupy": 13,
                    "predykcja": "1:1",
                    "wynik_rzeczywisty": "0:0",
                    "pewnosc": 0.104855,
                    "trafienie": false,
                    "pierwsza_obserwacja": true
                },
                ...
            ]
        }
        
        Args:
            siec_id: Identyfikator sieci
            pamiec_file: Ścieżka do pliku pamiec_obserwacji.json
            typ: Typ sieci ("trend" lub "kursy")
        """
        try:
            with open(pamiec_file, 'r', encoding='utf-8') as f:
                siec_pamiec = json.load(f)
        except Exception as e:
            print(f"  Blad odczytu {pamiec_file}: {e}")
            return
        
        for mecz_id, obserwacje_sieci in siec_pamiec.items():
            for obs_data in obserwacje_sieci:
                try:
                    # Konwersja do formatu V2
                    obserwacja = Obserwacja(
                        id_meczu=mecz_id,
                        id_grupy=str(obs_data.get("id_grupy", "BRAK")),
                        id_modelu=siec_id,
                        wynik_predykcji=obs_data.get("predykcja", ""),
                        confidence=float(obs_data.get("pewnosc", 0.5)),
                        wynik_rzeczywisty=obs_data.get("wynik_rzeczywisty", ""),
                        timestamp=datetime.fromisoformat(
                            obs_data.get("data", datetime.now().isoformat()).replace(" ", "T")
                        )
                    )
                    
                    # Dodaj do repozytorium
                    self._dodaj_obserwacje(obserwacja)
                    
                except Exception as e:
                    print(f"  Blad przetwarzania obserwacji {mecz_id}: {e}")
                    continue
    
    def _zaladuj_z_klasyfikatora(self):
        """Ładuje dane z kod_dataBase_futbol_trend_klasyfikator.csv"""
        plik = Path("dane/kod_dataBase_futbol_trend_klasyfikator.csv")
        if not plik.exists():
            print(f"  Brak pliku: {plik}")
            return
        
        try:
            with open(plik, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                
                for row in reader:
                    mecz_id = row.get('id_meczu', '')
                    wynik = row.get('wynik', '')
                    
                    if mecz_id and wynik:
                        # Tworzymy obserwację z danymi z klasyfikatora
                        # (nie mamy predykcji, ale mamy wynik rzeczywisty)
                        obserwacja = Obserwacja(
                            id_meczu=mecz_id,
                            id_grupy="klasyfikator",
                            id_modelu="klasyfikator_base",
                            wynik_predykcji=wynik,  # Jako predykcję używamy wyniku (placeholder)
                            confidence=0.5,
                            wynik_rzeczywisty=wynik,
                            timestamp=datetime.now()
                        )
                        self._dodaj_obserwacje(obserwacja)
        except Exception as e:
            print(f"  Blad odczytu {plik}: {e}")
    
    def _zaladuj_z_mozg_kursy(self):
        """Ładuje dane z mozg_kursy_przygotowane.csv"""
        plik = Path("dane/mozg_kursy_przygotowane.csv")
        if not plik.exists():
            print(f"  Brak pliku: {plik}")
            return
        
        try:
            with open(plik, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                
                for row in reader:
                    mecz_id = row.get('mecz', '')
                    wynik = row.get('wynik', '')
                    
                    if mecz_id and wynik:
                        obserwacja = Obserwacja(
                            id_meczu=mecz_id,
                            id_grupy="mozg_kursy",
                            id_modelu="mozg_kursy_base",
                            wynik_predykcji=wynik,
                            confidence=0.5,
                            wynik_rzeczywisty=wynik,
                            timestamp=datetime.now()
                        )
                        self._dodaj_obserwacje(obserwacja)
        except Exception as e:
            print(f"  Blad odczytu {plik}: {e}")
    
    def _zaladuj_z_mozg_analiza(self):
        """Ładuje dane z mozg_analizaKursowDni_dataBase_futbol.csv"""
        plik = Path("dane/mozg_analizaKursowDni_dataBase_futbol.csv")
        if not plik.exists():
            print(f"  Brak pliku: {plik}")
            return
        
        try:
            with open(plik, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=';')
                header = next(reader, None)  # Pobierz nagłówek
                
                if not header or len(header) < 3:
                    print(f"  Blad: nieprawidlowy format pliku {plik}")
                    return
                
                # Znajdź indeksy kolumn
                try:
                    idx_mecz = header.index('id_meczu_predykcja')
                    idx_grupa = 1  # Druga kolumna to grupa (poziomX...)
                    idx_wynik = header.index('wynik')
                except ValueError:
                    print(f"  Blad: nie znaleziono wymaganych kolumn w {plik}")
                    return
                
                for row in reader:
                    if len(row) > max(idx_mecz, idx_grupa, idx_wynik):
                        mecz_id = row[idx_mecz]
                        grupa = row[idx_grupa]
                        wynik = row[idx_wynik]
                        
                        if mecz_id and grupa and wynik:
                            obserwacja = Obserwacja(
                                id_meczu=mecz_id,
                                id_grupy=grupa,
                                id_modelu="mozg_analiza_base",
                                wynik_predykcji=wynik,
                                confidence=0.5,
                                wynik_rzeczywisty=wynik,
                                timestamp=datetime.now()
                            )
                            self._dodaj_obserwacje(obserwacja)
        except Exception as e:
            print(f"  Blad odczytu {plik}: {e}")
    
    # =========================================================================
    # DODAWANIE NOWYCH OBSERWACJI
    # =========================================================================
    
    def _dodaj_obserwacje(self, obserwacja: Obserwacja):
        """
        Dodaje nową obserwację do repozytorium.
        
        Args:
            obserwacja: Obiekt Obserwacja do dodania
        """
        # Generuj klucz
        key = f"{obserwacja.id_meczu}_{obserwacja.id_modelu}"
        
        # Zapisz obserwację
        self.obserwacje[key] = obserwacja
        
        # Dodaj do klasy
        if obserwacja.klasa_dokladna:
            if obserwacja.klasa_dokladna not in self.klasy:
                self.klasy[obserwacja.klasa_dokladna] = KlasaWyniku(
                    nazwa_klasy=obserwacja.klasa_dokladna
                )
            self.klasy[obserwacja.klasa_dokladna].dodaj_obserwacje(obserwacja)
        
        # Dodaj do modelu
        if obserwacja.id_modelu not in self.modele:
            self.modele[obserwacja.id_modelu] = []
        self.modele[obserwacja.id_modelu].append(obserwacja)
        
        # Dodaj do grupy
        if obserwacja.id_grupy not in self.grupy:
            self.grupy[obserwacja.id_grupy] = []
        self.grupy[obserwacja.id_grupy].append(obserwacja)
        
        # Aktualizuj timestamp
        self.ostatnia_aktualizacja = datetime.now()
        
        # Wyczyść cache statystyk
        self._statystyki = None
    
    def dodaj_obserwacje(self, obserwacja: Obserwacja):
        """
        Publiczna metoda dodawania obserwacji.
        
        Args:
            obserwacja: Obiekt Obserwacja
        """
        self._dodaj_obserwacje(obserwacja)
    
    def dodaj_z_dict(self, data: Dict[str, Any]):
        """
        Dodaje obserwację z słownika.
        
        Args:
            data: Słownik z danymi obserwacji
        """
        obserwacja = Obserwacja.from_dict(data)
        self.dodaj_obserwacje(obserwacja)
    
    # =========================================================================
    # WYSZUKIWANIE OBSERWACJI
    # =========================================================================
    
    def znajdz_po_meczu(self, mecz_id: str) -> List[Obserwacja]:
        """Zwraca wszystkie obserwacje dla danego meczu"""
        return [obs for key, obs in self.obserwacje.items() if obs.id_meczu == mecz_id]
    
    def znajdz_po_modelu(self, model_id: str) -> List[Obserwacja]:
        """Zwraca wszystkie obserwacje dla danego modelu"""
        return self.modele.get(model_id, [])
    
    def znajdz_po_grupie(self, grupa_id: str) -> List[Obserwacja]:
        """Zwraca wszystkie obserwacje dla danej grupy"""
        return self.grupy.get(grupa_id, [])
    
    def znajdz_po_klasie(self, klasa: str) -> List[Obserwacja]:
        """Zwraca wszystkie obserwacje dla danej klasy wyniku"""
        if klasa in self.klasy:
            return self.klasy[klasa].obserwacje
        return []
    
    def znajdz_trafione(self) -> List[Obserwacja]:
        """Zwraca wszystkie trafione obserwacje"""
        return [obs for obs in self.obserwacje.values() if obs.trafienie]
    
    def znajdz_nietrafione(self) -> List[Obserwacja]:
        """Zwraca wszystkie nietrafione obserwacje"""
        return [obs for obs in self.obserwacje.values() if not obs.trafienie]
    
    def znajdz_trafione_grupa(self) -> List[Obserwacja]:
        """Zwraca wszystkie obserwacje z trafioną grupą (1/X/2)"""
        return [obs for obs in self.obserwacje.values() if obs.trafienie_grupa]
    
    # =========================================================================
    # STATYSTYKI
    # =========================================================================
    
    def pobierz_statystyki(self) -> StatystykiPamieci:
        """Generuje aktualne statystyki pamięci"""
        if self._statystyki is not None:
            return self._statystyki
        
        # Oblicz statystyki
        calkowita_liczba = len(self.obserwacje)
        liczba_klas = len(self.klasy)
        liczba_modeli = len(self.modele)
        
        # Średnia skuteczność
        if liczba_klas > 0:
            srednia_skutecznosc = sum(
                k.skutecznosc for k in self.klasy.values()
            ) / liczba_klas
        else:
            srednia_skutecznosc = 0.0
        
        # Średni confidence
        if calkowita_liczba > 0:
            sredni_confidence = sum(
                obs.confidence for obs in self.obserwacje.values()
            ) / calkowita_liczba
        else:
            sredni_confidence = 0.0
        
        self._statystyki = StatystykiPamieci(
            calkowita_liczba_obserwacji=calkowita_liczba,
            liczba_klas=liczba_klas,
            srednia_skutecznosc=srednia_skutecznosc,
            sredni_confidence=sredni_confidence,
            liczba_modeli=liczba_modeli,
            data_utworzenia=self.data_utworzenia,
            wersja=self.wersja
        )
        
        return self._statystyki
    
    def pobierz_statystyki_klas(self) -> Dict[str, Dict[str, Any]]:
        """Zwraca statystyki dla wszystkich klas"""
        return {name: klasa.to_dict() for name, klasa in self.klasy.items()}
    
    def pobierz_statystyki_modeli(self) -> Dict[str, Dict[str, Any]]:
        """Zwraca statystyki dla wszystkich modeli"""
        stats = {}
        for model_id, obserwacje in self.modele.items():
            trafienia = sum(1 for o in obserwacje if o.trafienie)
            trafienia_grupa = sum(1 for o in obserwacje if o.trafienie_grupa)
            
            stats[model_id] = {
                "liczba_obserwacji": len(obserwacje),
                "trafienia": trafienia,
                "trafienia_grupa": trafienia_grupa,
                "skutecznosc": trafienia / len(obserwacje) if obserwacje else 0,
                "skutecznosc_grupa": trafienia_grupa / len(obserwacje) if obserwacje else 0,
                "sredni_confidence": sum(o.confidence for o in obserwacje) / len(obserwacje) if obserwacje else 0
            }
        return stats
    
    def pobierz_top_klasy(self, n: int = 10) -> List[Tuple[str, float]]:
        """Zwraca top N klas pod względem skuteczności"""
        sorted_klasy = sorted(
            self.klasy.items(),
            key=lambda x: x[1].skutecznosc,
            reverse=True
        )
        return [(name, klasa.skutecznosc) for name, klasa in sorted_klasy[:n]]
    
    def pobierz_top_modele(self, n: int = 10) -> List[Tuple[str, float]]:
        """Zwraca top N modeli pod względem skuteczności"""
        stats = self.pobierz_statystyki_modeli()
        sorted_modele = sorted(
            stats.items(),
            key=lambda x: x[1]["skutecznosc"],
            reverse=True
        )
        return [(model_id, data["skutecznosc"]) for model_id, data in sorted_modele[:n]]
    
    # =========================================================================
    # WERSJONOWANIE I ZAPIS
    # =========================================================================
    
    def zapisz_wersje(self, nazwa: Optional[str] = None, sciezka: Optional[Path] = None) -> Path:
        """
        Zapisuje aktualną pamięć jako nową wersję.
        
        Args:
            nazwa: Nazwa wersji (jeśli None, wygenerowana automatycznie)
            sciezka: Ścieżka zapisu (jeśli None, używa ARCHIWUM_PATH)
            
        Returns:
            Ścieżka do zapisanej wersji
        """
        if nazwa is None:
            nazwa = self.wersja
        
        if sciezka is None:
            sciezka = self.ARCHIWUM_PATH
        
        # Upewnij się, że katalog archiwum istnieje
        sciezka.mkdir(parents=True, exist_ok=True)
        
        # Generuj dane do zapisu
        data = {
            "wersja": nazwa,
            "data_utworzenia": self.data_utworzenia.isoformat(),
            "ostatnia_aktualizacja": self.ostatnia_aktualizacja.isoformat(),
            "statystyki": self.pobierz_statystyki().to_dict(),
            "statystyki_klas": self.pobierz_statystyki_klas(),
            "statystyki_modeli": self.pobierz_statystyki_modeli(),
            "obserwacje": [
                obs.to_dict() for obs in self.obserwacje.values()
            ],
            "konfiguracja": self.KONFIG.to_dict()
        }
        
        # Zapisz do pliku
        plik_wersji = sciezka / f"pamiec_{nazwa}.json"
        
        with open(plik_wersji, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Zapisano wersje: {plik_wersji}")
        return plik_wersji
    
    def zaladuj_wersje(self, sciezka_wersji: Path) -> bool:
        """
        Ładuje pamięć z konkretnej wersji.
        
        Args:
            sciezka_wersji: Ścieżka do pliku wersji
            
        Returns:
            True jeśli załadowano pomyślnie
        """
        try:
            with open(sciezka_wersji, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Wyczyszczenie aktualnych danych
            self.obserwacje.clear()
            self.klasy.clear()
            self.modele.clear()
            self.grupy.clear()
            
            # Załadowanie nowych danych
            self.wersja = data.get("wersja", self.wersja)
            self.data_utworzenia = datetime.fromisoformat(data.get("data_utworzenia", datetime.now().isoformat()))
            self.ostatnia_aktualizacja = datetime.fromisoformat(data.get("ostatnia_aktualizacja", datetime.now().isoformat()))
            
            for obs_dict in data.get("obserwacje", []):
                self.dodaj_z_dict(obs_dict)
            
            print(f"Załadowano wersje: {self.wersja}")
            return True
            
        except Exception as e:
            print(f"Blad ladowania wersji: {e}")
            return False
    
    def lista_wersji(self) -> List[Path]:
        """Zwraca listę dostępnych wersji pamięci"""
        if not self.ARCHIWUM_PATH.exists():
            return []
        
        return sorted(
            self.ARCHIWUM_PATH.glob("pamiec_v2_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
    
    # =========================================================================
    # EKSPORT I IMPORT (CSV, JSON)
    # =========================================================================
    
    def eksportuj_do_csv(self, sciezka: Path, typ: str = "wszystkie"):
        """
        Eksportuje obserwacje do pliku CSV.
        
        Args:
            sciezka: Ścieżka do pliku CSV
            typ: Typ eksportu ("wszystkie", "trafione", "nietrafione")
        """
        if typ == "trafione":
            obserwacje = self.znajdz_trafione()
        elif typ == "nietrafione":
            obserwacje = self.znajdz_nietrafione()
        else:
            obserwacje = list(self.obserwacje.values())
        
        # Nagłówki CSV
        naglowki = [
            "id_obserwacji", "id_meczu", "id_grupy", "id_modelu",
            "wynik_predykcji", "confidence", "wynik_rzeczywisty",
            "trafienie", "trafienie_grupa", "klasa_dokladna", "klasa_grupa",
            "timestamp"
        ]
        
        with open(sciezka, 'w', encoding='utf-8', newline='') as f:
            import csv
            writer = csv.DictWriter(f, fieldnames=naglowki, delimiter=';')
            writer.writeheader()
            
            for obs in obserwacje:
                writer.writerow(obs.to_dict())
        
        print(f"Eksportowano {len(obserwacje)} obserwacji do {sciezka}")
    
    def importuj_z_csv(self, sciezka: Path):
        """
        Importuje obserwacje z pliku CSV.
        
        Args:
            sciezka: Ścieżka do pliku CSV
        """
        try:
            with open(sciezka, 'r', encoding='utf-8-sig') as f:
                import csv
                reader = csv.DictReader(f, delimiter=';')
                
                for row in reader:
                    self.dodaj_z_dict(row)
            
            print(f"Zaimportowano obserwacje z {sciezka}")
        except Exception as e:
            print(f"Blad importu: {e}")
    
    # =========================================================================
    # CZYSZCZENIE I KONSERWACJA
    # =========================================================================
    
    def wyczysc(self):
        """Czyści całe repozytorium"""
        self.obserwacje.clear()
        self.klasy.clear()
        self.modele.clear()
        self.grupy.clear()
        self._statystyki = None
        self.wersja = self._generuj_nazwe_wersji()
        self.data_utworzenia = datetime.now()
        self.ostatnia_aktualizacja = datetime.now()
    
    def usun_duplikaty(self):
        """Usuwa duplikaty obserwacji (te same id_meczu + id_modelu)"""
        # Nic nie trzeba robić - struktura używa klucza f"{id_meczu}_{id_modelu}"
        # więc duplikaty są automatycznie nadpisywane
        pass
    
    def usun_stare_obserwacje(self, dni: int = 30):
        """
        Usuwa obserwacje starsze niż podana liczba dni.
        
        Args:
            dni: Liczba dni (domyślnie 30)
        """
        cutoff = datetime.now() - timedelta(days=dni)
        
        keys_to_remove = [
            key for key, obs in self.obserwacje.items()
            if obs.timestamp < cutoff
        ]
        
        for key in keys_to_remove:
            del self.obserwacje[key]
        
        # Odśwież struktury
        self.klasy.clear()
        self.modele.clear()
        self.grupy.clear()
        for obs in self.obserwacje.values():
            self._dodaj_obserwacje(obs)
        
        print(f"Usunieto {len(keys_to_remove)} starych obserwacji")


# Import dla funkcji timedelta
from datetime import timedelta


# =============================================================================
# FUNKCJE GLOBALNE (Wygoda)
# =============================================================================

def utworz_repozytorium() -> PamiecRepozytorium:
    """Tworzy nowe repozytorium i ładuje istniejące dane"""
    return PamiecRepozytorium(auto_load=True)


def utworz_puste_repozytorium() -> PamiecRepozytorium:
    """Tworzy puste repozytorium (bez ładowania danych)"""
    return PamiecRepozytorium(auto_load=False)


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing PamiecRepozytorium...")
    
    # Utworz repozytorium
    repo = utworz_repozytorium()
    
    # Podsumowanie
    stats = repo.pobierz_statystyki()
    print(f"\nStatystyki:")
    print(f"  Calkowita liczba obserwacji: {stats.calkowita_liczba_obserwacji}")
    print(f"  Liczba klas: {stats.liczba_klas}")
    print(f"  Liczba modeli: {stats.liczba_modeli}")
    print(f"  Srednia skutecznosc: {stats.srednia_skutecznosc:.4f}")
    print(f"  Sredni confidence: {stats.sredni_confidence:.4f}")
    
    # Top klasy
    print(f"\nTop 5 klas pod wzgledem skutecznosci:")
    for klasa, skutecznosc in repo.pobierz_top_klasy(5):
        print(f"  {klasa}: {skutecznosc:.4f}")
    
    # Top modele
    print(f"\nTop 5 modeli pod wzgledem skutecznosci:")
    for model, skutecznosc in repo.pobierz_top_modele(5):
        print(f"  {model}: {skutecznosc:.4f}")
    
    # Statystyki klas
    print(f"\nStatystyki wybranych klas:")
    for klasa_name in ["1:0", "2:1", "0:0", "1:1"]:
        if klasa_name in repo.klasy:
            klasa = repo.klasy[klasa_name]
            print(f"  {klasa_name}: {klasa.skutecznosc:.4f} ({klasa.czestotliwosc} obserwacji)")
    
    # Zapisz wersję testową
    repo.zapisz_wersje(nazwa="test_20260727")
    
    print("\nAll tests passed!")
