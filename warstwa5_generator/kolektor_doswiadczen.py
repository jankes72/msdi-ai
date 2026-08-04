"""
Kolektor Doświadczeń - Zbiera dane z V2 (Laboratorium Modeli)

Moduł odpowiedzialny za:
1. Przeszukiwanie struktur katalogów V2
2. Zbieranie plików: pamiec_obserwacji.json, ocena.json, historia.json, klasy.json, metadata.json
3. Łączenie danych w spójną strukturę
4. Wstępne przetwarzanie i walidację

Dane źródłowe:
- modele_dataBase_futbol_trend/siec_*/obserwacja/*
- modele_kursy_przygotowane/siec_*/obserwacja/*
- pamiec_modeli_v2/ (opcjonalnie)

Wynik:
- Zunifikowana struktura danych gotowa do analizy w Warstwie 5
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

from .konfiguracja import get_config


# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_config().sciezki.LOG_KOLEKTOR),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Obserwacja:
    """Pojedyncza obserwacja z pamiec_obserwacji.json.
    
    Nowy format V5 zawiera dodatkowe pola dla Decision Layer:
    - gole_dom_pred: Przewidywana liczba goli drużyny domowej
    - gole_wyj_pred: Przewidywana liczba goli drużyny wyjazdowej  
    - zmiana_predykcji: Zmiana predykcji (stara/nowa)
    - zmiana_pewnosci: Zmiana pewności (stara/nowa)
    
    Kompatybilny wstecz ze starym formatem.
    """
    data: str
    model: str
    id_meczu: str
    id_grupy: int
    predykcja: str
    wynik_rzeczywisty: str
    pewnosc: float
    trafienie: bool
    pierwsza_obserwacja: bool = False
    zmiana_pewnosci: Optional[Dict[str, float]] = None
    gole_dom_pred: int = 0
    gole_wyj_pred: int = 0
    zmiana_predykcji: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OcenaModelu:
    """Ocena modelu z ocena.json."""
    model: str
    data: str
    ocena_ogolna: Dict[str, Any]
    ocena_wynikow: Dict[str, Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetadaneSieci:
    """Metadane sieci z metadata.json."""
    nazwa: str
    opis: str
    cechy: List[str]
    data_utworzenia: str
    wersja: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HistoriaModelu:
    """Historia uczenia modelu z historia.json."""
    model: str
    epoki: List[Dict[str, Any]]
    metryki: Dict[str, List[float]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KlasyWynikow:
    """Mapa klas wyników z klasy.json."""
    model: str
    mapa_klas: Dict[str, int]
    opis_klas: Dict[int, str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DoswiadczenieSieci:
    """Zbiorcze doświadczenie pojedynczej sieci."""
    nazwa_sieci: str
    typ_sieci: str  # "trend" lub "kursy"
    obserwacje: Dict[str, List[Obserwacja]] = field(default_factory=dict)
    ocena: Optional[OcenaModelu] = None
    metadane: Optional[MetadaneSieci] = None
    historia: Optional[HistoriaModelu] = None
    klasy: Optional[KlasyWynikow] = None
    
    # Statystyki podsumowujące
    statystyki: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nazwa_sieci": self.nazwa_sieci,
            "typ_sieci": self.typ_sieci,
            "obserwacje": {mecz: [obs.to_dict() for obs in obserwacje] 
                          for mecz, obserwacje in self.obserwacje.items()},
            "ocena": self.ocena.to_dict() if self.ocena else None,
            "metadane": self.metadane.to_dict() if self.metadane else None,
            "historia": self.historia.to_dict() if self.historia else None,
            "klasy": self.klasy.to_dict() if self.klasy else None,
            "statystyki": self.statystyki
        }


class KolektorDoswiadczen:
    """
    Główna klasa kolektora doświadczeń.
    
    Zbiera dane z wszystkich sieci V2 i przygotowuje je do analizy.
    """
    
    def __init__(self):
        self.config = get_config()
        self.sieci_trend: Dict[str, DoswiadczenieSieci] = {}
        self.sieci_kursy: Dict[str, DoswiadczenieSieci] = {}
        self.wszystkie_mecze: set = set()
        self.statystyki_globalne: Dict[str, Any] = {}
        
    def zebranie_danych_z_v2(self) -> None:
        """
        Główna metoda - zbiera wszystkie dane z V2.
        """
        logger.info("=" * 80)
        logger.info("ROZPOCZYNAM ZBIERANIE DOSWIADCZEN Z V2")
        logger.info("=" * 80)
        
        # Zbieranie z sieci trend
        logger.info(f"Przetwarzam sieci trend ({len(self.config.SIECI_TREND)} sieci)...")
        self._zebranie_z_modulu(
            self.config.V2_MODELE_TREND,
            self.config.SIECI_TREND,
            "trend"
        )
        
        # Zbieranie z sieci kursy
        logger.info(f"Przetwarzam sieci kursy ({len(self.config.SIECI_KURSY)} sieci)...")
        self._zebranie_z_modulu(
            self.config.V2_MODELE_KURSY,
            self.config.SIECI_KURSY,
            "kursy"
        )
        
        # Podsumowanie
        self._wylicz_statystyki_globalne()
        logger.info(f"Zebrano dane z {len(self.sieci_trend)} sieci trend i {len(self.sieci_kursy)} sieci kursy")
        logger.info(f"Liczba unikalnych meczów: {len(self.wszystkie_mecze)}")
        logger.info("ZBIERANIE DOSWIADCZEN ZAKONCZONE")
        logger.info("=" * 80)
        
    def _zebranie_z_modulu(self, catalog_główny: str, lista_sieci: List[str], typ_sieci: str) -> None:
        """
        Zbiera dane z pojedynczego modułu (trend lub kursy).
        """
        sieci_target = self.sieci_trend if typ_sieci == "trend" else self.sieci_kursy
        
        for siec_nazwa in lista_sieci:
            siec_path = os.path.join(catalog_główny, siec_nazwa)
            obserwacja_path = os.path.join(siec_path, "obserwacja")
            
            if not os.path.exists(siec_path):
                logger.warning(f"Sieć {siec_nazwa} nie istnieje w {catalog_główny}")
                continue
            
            # Utwórz strukturę doświadczenia sieci
            doswiadczenie = DoswiadczenieSieci(
                nazwa_sieci=siec_nazwa,
                typ_sieci=typ_sieci
            )
            
            # Zbieraj pliki z katalogu obserwacja
            if os.path.exists(obserwacja_path):
                self._zebranie_plikow_obserwacji(doswiadczenie, obserwacja_path)
            else:
                logger.warning(f"Katalog obserwacja nie istnieje dla sieci {siec_nazwa}")
            
            # Zbieraj pliki z głównego katalogu sieci
            self._zebranie_plikow_glownych(doswiadczenie, siec_path)
            
            # Zapisz doświadczenie
            sieci_target[siec_nazwa] = doswiadczenie
            
            # Aktualizuj listę wszystkich meczów
            for mecz in doswiadczenie.obserwacje.keys():
                self.wszystkie_mecze.add(mecz)
        
    def _zebranie_plikow_obserwacji(self, doswiadczenie: DoswiadczenieSieci, obserwacja_path: str) -> None:
        """
        Zbiera pliki z katalogu obserwacja.
        """
        pliki_do_zebrania = [
            ("pamiec_obserwacji.json", self._zaladuj_pamiec_obserwacji),
            ("ocena.json", self._zaladuj_ocene),
            ("historia.json", self._zaladuj_historie),
            ("klasy.json", self._zaladuj_klasy),
            ("metadata.json", self._zaladuj_metadane)
        ]
        
        for plik_nazwa, loader in pliki_do_zebrania:
            plik_path = os.path.join(obserwacja_path, plik_nazwa)
            if os.path.exists(plik_path):
                try:
                    loader(doswiadczenie, plik_path)
                    logger.info(f"  Załadowano {plik_nazwa} z {obserwacja_path}")
                except Exception as e:
                    logger.error(f"  Błąd przy ładowaniu {plik_nazwa}: {e}")
            else:
                logger.warning(f"  Plik {plik_nazwa} nie istnieje w {obserwacja_path}")
        
    def _zebranie_plikow_glownych(self, doswiadczenie: DoswiadczenieSieci, siec_path: str) -> None:
        """
        Zbiera pliki z głównego katalogu sieci (poza obserwacja).
        """
        # Sprawdź czy są pliki bezpośrednio w katalogu sieci
        for plik_nazwa in ["metadata.json", "klasy.json"]:
            plik_path = os.path.join(siec_path, plik_nazwa)
            if os.path.exists(plik_path):
                try:
                    if plik_nazwa == "metadata.json":
                        self._zaladuj_metadane(doswiadczenie, plik_path)
                    elif plik_nazwa == "klasy.json":
                        self._zaladuj_klasy(doswiadczenie, plik_path)
                    logger.info(f"  Załadowano {plik_nazwa} z {siec_path}")
                except Exception as e:
                    logger.error(f"  Błąd przy ładowaniu {plik_nazwa} z katalogu głównego: {e}")
        
    def _zaladuj_pamiec_obserwacji(self, doswiadczenie: DoswiadczenieSieci, plik_path: str) -> None:
        """Ładowanie pamiec_obserwacji.json."""
        with open(plik_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for mecz_id, obserwacje_list in data.items():
            obserwacje_objects = []
            for obs_dict in obserwacje_list:
                obserwacja = Obserwacja(
                    data=obs_dict.get('data', ''),
                    model=obs_dict.get('model', doswiadczenie.nazwa_sieci),
                    id_meczu=obs_dict.get('id_meczu', mecz_id),
                    id_grupy=obs_dict.get('id_grupy', 0),
                    predykcja=obs_dict.get('predykcja', ''),
                    wynik_rzeczywisty=obs_dict.get('wynik_rzeczywisty', ''),
                    pewnosc=obs_dict.get('pewnosc', 0.0),
                    trafienie=obs_dict.get('trafienie', False),
                    pierwsza_obserwacja=obs_dict.get('pierwsza_obserwacja', False),
                    zmiana_pewnosci=obs_dict.get('zmiana_pewnosci')
                )
                obserwacje_objects.append(obserwacja)
            
            doswiadczenie.obserwacje[mecz_id] = obserwacje_objects
        
    def _zaladuj_ocene(self, doswiadczenie: DoswiadczenieSieci, plik_path: str) -> None:
        """Ładowanie ocena.json."""
        with open(plik_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        doswiadczenie.ocena = OcenaModelu(
            model=data.get('model', doswiadczenie.nazwa_sieci),
            data=data.get('data', ''),
            ocena_ogolna=data.get('ocena_ogolna', {}),
            ocena_wynikow=data.get('ocena_wynikow', {})
        )
        
    def _zaladuj_historie(self, doswiadczenie: DoswiadczenieSieci, plik_path: str) -> None:
        """Ładowanie historia.json."""
        with open(plik_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        doswiadczenie.historia = HistoriaModelu(
            model=data.get('model', doswiadczenie.nazwa_sieci),
            epoki=data.get('epoki', []),
            metryki=data.get('metryki', {})
        )
        
    def _zaladuj_klasy(self, doswiadczenie: DoswiadczenieSieci, plik_path: str) -> None:
        """Ładowanie klasy.json."""
        with open(plik_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        doswiadczenie.klasy = KlasyWynikow(
            model=data.get('model', doswiadczenie.nazwa_sieci),
            mapa_klas=data.get('mapa_klas', {}),
            opis_klas=data.get('opis_klas', {})
        )
        
    def _zaladuj_metadane(self, doswiadczenie: DoswiadczenieSieci, plik_path: str) -> None:
        """Ładowanie metadata.json."""
        with open(plik_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        doswiadczenie.metadane = MetadaneSieci(
            nazwa=data.get('nazwa', doswiadczenie.nazwa_sieci),
            opis=data.get('opis', ''),
            cechy=data.get('cechy', []),
            data_utworzenia=data.get('data_utworzenia', ''),
            wersja=data.get('wersja', '1.0')
        )
        
    def _wylicz_statystyki_globalne(self) -> None:
        """
        Wylicza statystyki globalne dla wszystkich zebranych danych.
        """
        total_obserwacji = 0
        total_trafien = 0
        sieci_z_danymi = 0
        
        # Statystyki dla sieci trend
        for siec_nazwa, doswiadczenie in self.sieci_trend.items():
            obs_count = sum(len(obs_list) for obs_list in doswiadczenie.obserwacje.values())
            total_obserwacji += obs_count
            
            trafien_count = sum(
                1 for obs_list in doswiadczenie.obserwacje.values()
                for obs in obs_list if obs.trafienie
            )
            total_trafien += trafien_count
            
            if obs_count > 0:
                sieci_z_danymi += 1
        
        # Statystyki dla sieci kursy
        for siec_nazwa, doswiadczenie in self.sieci_kursy.items():
            obs_count = sum(len(obs_list) for obs_list in doswiadczenie.obserwacje.values())
            total_obserwacji += obs_count
            
            trafien_count = sum(
                1 for obs_list in doswiadczenie.obserwacje.values()
                for obs in obs_list if obs.trafienie
            )
            total_trafien += trafien_count
            
            if obs_count > 0:
                sieci_z_danymi += 1
        
        self.statystyki_globalne = {
            "calkowita_liczba_obserwacji": total_obserwacji,
            "calkowita_liczba_trafien": total_trafien,
            "skutecznosc_globalna": total_trafien / total_obserwacji if total_obserwacji > 0 else 0,
            "liczba_sieci_z_danymi": sieci_z_danymi,
            "liczba_unikalnych_meczy": len(self.wszystkie_mecze),
            "liczba_sieci_trend": len(self.sieci_trend),
            "liczba_sieci_kursy": len(self.sieci_kursy),
            "data_zebrania": datetime.now().strftime(get_config().eksport.FORMAT_DATY)
        }
        
    def pobierz_doswiadczenia(self) -> Dict[str, DoswiadczenieSieci]:
        """
        Zwraca wszystkie zebrane doświadczenia.
        """
        wszystkie = {}
        wszystkie.update(self.sieci_trend)
        wszystkie.update(self.sieci_kursy)
        return wszystkie
        
    def pobierz_dane_dla_meczu(self, mecz_id: str) -> Dict[str, List[Obserwacja]]:
        """
        Zwraca wszystkie obserwacje dla danego meczu.
        """
        wszystkie_obserwacje = {}
        
        for siec_nazwa, doswiadczenie in self.sieci_trend.items():
            if mecz_id in doswiadczenie.obserwacje:
                wszystkie_obserwacje[f"trend_{siec_nazwa}"] = doswiadczenie.obserwacje[mecz_id]
        
        for siec_nazwa, doswiadczenie in self.sieci_kursy.items():
            if mecz_id in doswiadczenie.obserwacje:
                wszystkie_obserwacje[f"kursy_{siec_nazwa}"] = doswiadczenie.obserwacje[mecz_id]
        
        return wszystkie_obserwacje
    
    def eksportuj_dane(self, plik_wyjsciowy: Optional[str] = None) -> None:
        """
        Eksportuje zebrane dane do pliku JSON.
        """
        if plik_wyjsciowy is None:
            plik_wyjsciowy = self.config.sciezki.ROZSZERZONY_SWIAT_FILE
        
        data = {
            "metadane": {
                "typ": "zebrane_doswiadczenia_v2",
                "wersja": "1.0",
                "data": datetime.now().strftime(get_config().eksport.FORMAT_DATY),
                "statystyki": self.statystyki_globalne
            },
            "sieci_trend": {siec: dosw.to_dict() for siec, dosw in self.sieci_trend.items()},
            "sieci_kursy": {siec: dosw.to_dict() for siec, dosw in self.sieci_kursy.items()},
            "wszystkie_mecze": list(self.wszystkie_mecze)
        }
        
        with open(plik_wyjsciowy, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dane zeksportowane do: {plik_wyjsciowy}")


def zebranie_wszystkich_doswiadczen() -> KolektorDoswiadczen:
    """
    Funkcja wygodna - tworzy kolektor i zbiera wszystkie doświadczenia.
    
    Returns:
        KolektorDoswiadczen: Zainicjalizowany kolektor z zebranymi danymi
    """
    kolektor = KolektorDoswiadczen()
    kolektor.zebranie_danych_z_v2()
    return kolektor


if __name__ == "__main__":
    # Testowe zebranie danych
    logger.info("Testowe zebranie danych...")
    kolektor = zebranie_wszystkich_doswiadczen()
    
    # Eksport
    kolektor.eksportuj_dane()
    
    # Podsumowanie
    logger.info(f"Statystyki: {kolektor.statystyki_globalne}")
