"""
Eksport Świata - Moduł eksportowy Warstwy 5

Moduł odpowiedzialny za:
1. Łączenie wyników wszystkich analiz (Kolektor + Generator + Analizator)
2. Eksport do różnych formatów
3. Tworzenie podsumowań i raportów
4. Integrację z SSI V3

Dane wejściowe:
- Zebrane doświadczenia
- Rozszerzony świat z metadanymi
- Raport ewolucji

Dane wyjściowe:
- Kompleksowy eksport Świata Danych 2
- Podsumowania i raporty
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict

from .konfiguracja import get_config
from .kolektor_doswiadczen import KolektorDoswiadczen
from .generator_metadanych import RozszerzonySwiatDanych, GeneratorMetadanych
from .analizator_ewolucji import RaportEwolucji, AnalizatorEwolucji


# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_config().sciezki.LOG_GENERATOR),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class SwiatDanychV2:
    """
    Kompleksowy świat danych V2 (Świat danych 2).
    
    Łączy wszystkie dane z Warstwy 5:
    - Zebrane doświadczenia z V2
    - Rozszerzone metadane
    - Raport ewolucji
    """
    
    # Metadane globalne
    nazwa: str = "Swiat_Danych_V2"
    wersja: str = "1.0"
    data_utworzenia: str = ""
    
    # Składowe
    doswiadczenia: Optional[Dict[str, Any]] = None
    rozszerzony_swiat: Optional[Dict[str, Any]] = None
    raport_ewolucji: Optional[Dict[str, Any]] = None
    
    # Agregowane dane
    metadane_sieci: Dict[str, Any] = field(default_factory=dict)
    metadane_meczy: Dict[str, Any] = field(default_factory=dict)
    
    # Statystyki
    statystyki: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EksportSwiata:
    """
    Główna klasa eksportowa Warstwy 5.
    
    Łączy i eksportuje wszystkie dane generowane przez Warstwę 5.
    """
    
    def __init__(
        self,
        kolektor: Optional[KolektorDoswiadczen] = None,
        generator: Optional[GeneratorMetadanych] = None,
        analizator: Optional[AnalizatorEwolucji] = None
    ):
        self.config = get_config()
        self.kolektor = kolektor
        self.generator = generator
        self.analizator = analizator
        self.swiat_v2: Optional[SwiatDanychV2] = None
        
        if kolektor:
            self._buduj_swiat_v2()
        
    def _buduj_swiat_v2(self) -> SwiatDanychV2:
        """
        Buduje kompleksowy świat danych V2.
        """
        logger.info("=" * 80)
        logger.info("BUDOWANIE SWIATA DANYCH V2")
        logger.info("=" * 80)
        
        self.swiat_v2 = SwiatDanychV2(
            data_utworzenia=datetime.now().strftime(self.config.eksport.FORMAT_DATY)
        )
        
        # Dodaj doświadczenia
        if self.kolektor:
            self.swiat_v2.doswiadczenia = self._przetworz_doswiadczenia()
        
        # Dodaj rozszerzony świat
        if self.generator and self.generator.rozszerzony_swiat:
            self.swiat_v2.rozszerzony_swiat = self.generator.rozszerzony_swiat.to_dict()
            self.swiat_v2.metadane_sieci = {
                siec: meta.to_dict() 
                for siec, meta in self.generator.rozszerzony_swiat.metadane_sieci.items()
            }
            self.swiat_v2.metadane_meczy = {
                mecz: meta.to_dict() 
                for mecz, meta in self.generator.rozszerzony_swiat.metadane_meczy.items()
            }
        
        # Dodaj raport ewolucji
        if self.analizator and self.analizator.raport:
            self.swiat_v2.raport_ewolucji = self.analizator.raport.to_dict()
        
        # Wylicz statystyki
        self._wylicz_statystyki_swiata()
        
        logger.info("SWIAT DANYCH V2 ZOSTAŁ ZBUDOWANY")
        logger.info("=" * 80)
        
        return self.swiat_v2
    
    def _przetworz_doswiadczenia(self) -> Dict[str, Any]:
        """
        Przetwarza doświadczenia do postaci nadającej się do eksportu.
        """
        if not self.kolektor:
            return {}
        
        wszystkie = self.kolektor.pobierz_doswiadczenia()
        return {
            siec: dosw.to_dict() 
            for siec, dosw in wszystkie.items()
        }
    
    def _wylicz_statystyki_swiata(self) -> None:
        """
        Wylicza statystyki dla świata V2.
        """
        if not self.swiat_v2:
            return
        
        statystyki = {
            "data_utworzenia": self.swiat_v2.data_utworzenia,
            "wersja": self.swiat_v2.wersja,
            "liczba_sieci": len(self.swiat_v2.metadane_sieci) if self.swiat_v2.metadane_sieci else 0,
            "liczba_meczy": len(self.swiat_v2.metadane_meczy) if self.swiat_v2.metadane_meczy else 0,
        }
        
        # Statystyki z rozszerzonego świata
        if self.swiat_v2.rozszerzony_swiat:
            rs_stat = self.swiat_v2.rozszerzony_swiat.get("statystyki", {})
            statystyki.update(rs_stat)
        
        # Statystyki z raportu ewolucji
        if self.swiat_v2.raport_ewolucji:
            re_stat = self.swiat_v2.raport_ewolucji.get("statystyki", {})
            statystyki["ewolucja"] = re_stat
        
        # Statystyki z doświadczeń
        if self.kolektor:
            statystyki["zoswiadczenia"] = self.kolektor.statystyki_globalne
        
        self.swiat_v2.statystyki = statystyki
    
    def eksportuj_wszystko(self, katalog_wyjsciowy: Optional[str] = None) -> None:
        """
        Eksportuje wszystkie dane Warstwy 5.
        
        Args:
            katalog_wyjsciowy: Katalog docelowy (domyślnie z konfiguracji)
        """
        if katalog_wyjsciowy is None:
            katalog_wyjsciowy = self.config.sciezki.WARSTWA5_EXPORTS
        
        os.makedirs(katalog_wyjsciowy, exist_ok=True)
        
        logger.info(f"Eksportuję wszystkie dane do: {katalog_wyjsciowy}")
        
        # 1. Eksportuj zbiór doświadczeń
        if self.kolektor:
            plik_doswiadczen = os.path.join(katalog_wyjsciowy, "zbior_doswiadczen.json")
            with open(plik_doswiadczen, 'w', encoding='utf-8') as f:
                json.dump(
                    self.kolektor.pobierz_doswiadczenia(),
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                )
            logger.info(f"  Zbiór doświadczeń: {plik_doswiadczen}")
        
        # 2. Eksportuj rozszerzony świat
        if self.generator and self.generator.rozszerzony_swiat:
            plik_rozszerzony = os.path.join(katalog_wyjsciowy, "rozszerzony_swiat.json")
            with open(plik_rozszerzony, 'w', encoding='utf-8') as f:
                json.dump(
                    self.generator.rozszerzony_swiat.to_dict(),
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                )
            logger.info(f"  Rozszerzony świat: {plik_rozszerzony}")
        
        # 3. Eksportuj metadane sieci
        if self.generator and self.generator.rozszerzony_swiat:
            plik_metadane_sieci = os.path.join(katalog_wyjsciowy, "metadane_sieci.json")
            self.generator.eksportuj_metadane_sieci(plik_metadane_sieci)
            logger.info(f"  Metadane sieci: {plik_metadane_sieci}")
        
        # 4. Eksportuj raport ewolucji
        if self.analizator and self.analizator.raport:
            plik_ewolucja = os.path.join(katalog_wyjsciowy, "raport_ewolucji.json")
            self.analizator.eksportuj_raport(plik_ewolucja)
            logger.info(f"  Raport ewolucji: {plik_ewolucja}")
        
        # 5. Eksportuj podsumowanie
        plik_podsumowanie = os.path.join(katalog_wyjsciowy, "podsumowanie.json")
        self._eksportuj_podsumowanie(plik_podsumowanie)
        logger.info(f"  Podsumowanie: {plik_podsumowanie}")
        
        # 6. Eksportuj świat V2 (kompleksowy)
        if self.swiat_v2:
            plik_swiat_v2 = os.path.join(katalog_wyjsciowy, "swiat_danych_v2.json")
            with open(plik_swiat_v2, 'w', encoding='utf-8') as f:
                json.dump(
                    self.swiat_v2.to_dict(),
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                )
            logger.info(f"  Świat danych V2: {plik_swiat_v2}")
        
        logger.info("Eksport wszystkich danych zakończony")
    
    def _eksportuj_podsumowanie(self, plik_wyjsciowy: str) -> None:
        """
        Tworzy i eksportuje podsumowanie analizy.
        """
        podsumowanie = {
            "data": datetime.now().strftime(self.config.eksport.FORMAT_DATY),
            "wersja": "1.0",
            "typ": "podsumowanie_warstwy_5"
        }
        
        # Dodaj statystyki globalne
        if self.kolektor:
            podsumowanie["statystyki_doswiadczen"] = self.kolektor.statystyki_globalne
        
        if self.generator and self.generator.rozszerzony_swiat:
            podsumowanie["statystyki_metadanych"] = self.generator.rozszerzony_swiat.statystyki
        
        if self.analizator and self.analizator.raport:
            podsumowanie["statystyki_ewolucji"] = self.analizator.raport.statystyki
        
        # Dodaj statystyki świata V2
        if self.swiat_v2:
            podsumowanie["statystyki_swiata_v2"] = self.swiat_v2.statystyki
        
        with open(plik_wyjsciowy, 'w', encoding='utf-8') as f:
            json.dump(podsumowanie, f, ensure_ascii=False, indent=2)
    
    def pobierz_swiat_v2(self) -> Optional[SwiatDanychV2]:
        """
        Zwraca świat danych V2.
        """
        return self.swiat_v2
    
    def pobierz_dane_dla_v3(self) -> Dict[str, Any]:
        """
        Zwraca dane w formacie odpowiednim dla SSI V3.
        
        V3 potrzebuje:
        - Metadane sieci (role, specjalizacje, wagi)
        - Metadane meczów (konsensus, stabilność)
        - Raport ewolucji (trendy, klasyfikacje)
        
        Returns:
            Dict: Dane gotowe do użycia przez V3
        """
        if not self.swiat_v2:
            return {}
        
        dane_v3 = {
            "metadane_sieci": self.swiat_v2.metadane_sieci,
            "metadane_meczy": self.swiat_v2.metadane_meczy,
            "statystyki": self.swiat_v2.statystyki,
            "ewolucja": self.swiat_v2.raport_ewolucji if self.swiat_v2.raport_ewolucji else {},
            "data_generacji": self.swiat_v2.data_utworzenia
        }
        
        return dane_v3
    
    def zapisz_dane_dla_v3(self, plik_wyjsciowy: Optional[str] = None) -> None:
        """
        Zapisz dane dla V3 do pliku.
        """
        if plik_wyjsciowy is None:
            plik_wyjsciowy = os.path.join(
                self.config.sciezki.WARSTWA5_EXPORTS,
                "dane_dla_v3.json"
            )
        
        dane_v3 = self.pobierz_dane_dla_v3()
        
        with open(plik_wyjsciowy, 'w', encoding='utf-8') as f:
            json.dump(dane_v3, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dane dla V3 zeksportowane do: {plik_wyjsciowy}")


class Warstwa5:
    """
    Główna klasa Warstwy 5 - łączy wszystkie moduły.
    
    Umożliwia:
    1. Zbieranie doświadczeń z V2
    2. Generowanie metadanych
    3. Analizę ewolucji
    4. Eksport wszystkich danych
    
    Użycie:
        warstwa5 = Warstwa5()
        warstwa5.uruchom_kompletna_analize()
        warstwa5.eksportuj_wszystko()
    """
    
    def __init__(self):
        self.config = get_config()
        self.kolektor: Optional[KolektorDoswiadczen] = None
        self.generator: Optional[GeneratorMetadanych] = None
        self.analizator: Optional[AnalizatorEwolucji] = None
        self.eksport: Optional[EksportSwiata] = None
        
    def uruchom_kompletna_analize(self) -> None:
        """
        Uruchamia kompletny cykl analizy Warstwy 5.
        """
        logger.info("=" * 80)
        logger.info("ROZPOCZYNAM KOMPLETNA ANALIZE WARSTWY 5")
        logger.info("=" * 80)
        
        # Krok 1: Zbieranie doświadczeń
        logger.info("Krok 1/4: Zbieranie doświadczeń z V2")
        self.kolektor = KolektorDoswiadczen()
        self.kolektor.zebranie_danych_z_v2()
        
        # Krok 2: Generowanie metadanych
        logger.info("Krok 2/4: Generowanie metadanych")
        self.generator = GeneratorMetadanych(self.kolektor)
        
        # Krok 3: Analiza ewolucji
        logger.info("Krok 3/4: Analiza ewolucji pamięci")
        self.analizator = AnalizatorEwolucji(self.kolektor, self.generator.rozszerzony_swiat)
        
        # Krok 4: Łączenie i eksport
        logger.info("Krok 4/4: Łączenie danych i przygotowanie eksportu")
        self.eksport = EksportSwiata(self.kolektor, self.generator, self.analizator)
        
        logger.info("KOMPLETNA ANALIZA WARSTWY 5 ZAKOŃCZONA")
        logger.info("=" * 80)
    
    def eksportuj_wszystko(self, katalog_wyjsciowy: Optional[str] = None) -> None:
        """
        Eksportuje wszystkie dane Warstwy 5.
        """
        if not self.eksport:
            logger.warning("Najpierw uruchom kompletna_analize()")
            return
        
        self.eksport.eksportuj_wszystko(katalog_wyjsciowy)
    
    def pobierz_dane_dla_v3(self) -> Dict[str, Any]:
        """
        Zwraca dane gotowe do użycia przez V3.
        """
        if not self.eksport:
            return {}
        
        return self.eksport.pobierz_dane_dla_v3()
    
    def zapisz_dane_dla_v3(self, plik_wyjsciowy: Optional[str] = None) -> None:
        """
        Zapisz dane dla V3 do pliku.
        """
        if not self.eksport:
            logger.warning("Najpierw uruchom kompletna_analize()")
            return
        
        self.eksport.zapisz_dane_dla_v3(plik_wyjsciowy)


def uruchom_warstwe_5() -> Warstwa5:
    """
    Funkcja wygodna - uruchamia Warstwę 5 i zwraca gotową instancję.
    
    Returns:
        Warstwa5: Gotowa instancja Warstwy 5
    """
    warstwa5 = Warstwa5()
    warstwa5.uruchom_kompletna_analize()
    return warstwa5


if __name__ == "__main__":
    # Testowy uruchom Warstwy 5
    logger.info("Testowy uruchom Warstwy 5...")
    
    warstwa5 = uruchom_warstwe_5()
    warstwa5.eksportuj_wszystko()
    warstwa5.zapisz_dane_dla_v3()
    
    logger.info("Testowy uruchom Warstwy 5 zakończony")
