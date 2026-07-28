"""
Generator Metadanych - Tworzy rozszerzone cechy dla Świata Danych 2

Moduł odpowiedzialny za:
1. Analizę obserwacji i generowanie metadanych dla każdej sieci i meczu
2. Tworzenie rozszerzonych cech (Świat danych 2)
3. Kalkulację trendów, stabilności, pewności i innych metryk

Dane wejściowe:
- Zebrane doświadczenia z Kolektora (kolektor_doswiadczen.py)

Dane wyjściowe:
- Rozszerzone metadane dla każdej sieci i meczu
- Statystyki ewolucji pamięci
"""

import os
import json
import logging
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict

from .konfiguracja import get_config
from .kolektor_doswiadczen import KolektorDoswiadczen, DoswiadczenieSieci, Obserwacja


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
class MetadaneObserwacji:
    """Metadane dla pojedynczej obserwacji."""
    # Pierwotne dane
    data: str
    model: str
    id_meczu: str
    predykcja: str
    wynik_rzeczywisty: str
    pewnosc: float
    trafienie: bool
    
    # Rozszerzone metadane
    aktualna_pewnosc: float = 0.0
    trend_pewnosci: float = 0.0  # Dodatni = rosnąca, ujemny = malejąca
    ilosc_obserwacji: int = 0
    stabilnosc: float = 0.0  # 0-1, im wyższa tym bardziej stabilna
    wartość_klasy: str = ""
    typ_błędu: Optional[str] = None
    zachowanie_pamieci: str = "stabilna"  # stabilna, rosnaca, malejaca, niestabilna
    
    # Kontekst
    grupa_wyniku: str = ""  # 1, X, 2
    czy_pierwsza_obserwacja: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetadaneMeczu:
    """Metadane dla pojedynczego meczu (agregacja wszystkich sieci)."""
    id_meczu: str
    
    # Dane z obserwacji
    wszystkie_predykcje: Dict[str, List[str]] = field(default_factory=dict)  # siec -> [predykcje]
    wszystkie_pewnosci: Dict[str, List[float]] = field(default_factory=dict)  # siec -> [pewnosci]
    trafienia_po_sieciach: Dict[str, int] = field(default_factory=dict)  # siec -> liczba trafien
    
    # Agregowane metryki
    srednia_pewnosc: Dict[str, float] = field(default_factory=dict)  # siec -> średnia pewność
    stabilnosc_sieci: Dict[str, float] = field(default_factory=dict)  # siec -> stabilność
    trend_pewnosci_sieci: Dict[str, float] = field(default_factory=dict)  # siec -> trend
    
    # Konsensus
    najczestsza_predykcja: str = ""
    konsensus_pewnosc: float = 0.0
    licznosc_konsensusu: int = 0
    
    # Rzeczywisty wynik
    wynik_rzeczywisty: Optional[str] = None
    
    # Grupy wyników
    grupa_rzeczywista: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetadaneSieci:
    """Metadane dla pojedynczej sieci (agregacja wszystkich meczów)."""
    nazwa_sieci: str
    typ_sieci: str  # "trend" lub "kursy"
    
    # Statystyki ogólne
    liczba_meczy: int = 0
    liczba_obserwacji: int = 0
    skutecznosc: float = 0.0
    srednia_pewnosc: float = 0.0
    
    # Statystyki stabilności
    srednia_stabilnosc: float = 0.0
    odchylenie_stabilnosci: float = 0.0
    
    # Statystyki trendów
    sredni_trend_pewnosci: float = 0.0
    liczba_rosnacych: int = 0
    liczba_malejacych: int = 0
    liczba_stabilnych: int = 0
    
    # Klasyfikacja sieci
    rola: str = "nieokreślona"  # predyktor, klasyfikator, detektor_trendow, itd.
    specjalizacja: str = "ogólna"  # np. "wygrane_gospodarzy", "remisy", itd.
    
    # Wagi dla V3
    waga_wiedzy: float = 1.0
    waga_stabilnosci: float = 1.0
    waga_skutecznosci: float = 1.0
    
    # Cechy charakterystyczne
    cechy: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RozszerzonySwiatDanych:
    """Rozszerzony świat danych (Świat danych 2)."""
    
    # Metadane globalne
    data_generacji: str
    wersja: str = "1.0"
    
    # Metadane dla meczów
    metadane_meczy: Dict[str, MetadaneMeczu] = field(default_factory=dict)
    
    # Metadane dla sieci
    metadane_sieci: Dict[str, MetadaneSieci] = field(default_factory=dict)
    
    # Statystyki globalne
    statystyki: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GeneratorMetadanych:
    """
    Główna klasa generatora metadanych.
    
    Tworzy rozszerzone cechy i metadane na podstawie zebranych doświadczeń.
    """
    
    def __init__(self, kolektor: Optional[KolektorDoswiadczen] = None):
        self.config = get_config()
        self.kolektor = kolektor
        self.rozszerzony_swiat: Optional[RozszerzonySwiatDanych] = None
        
        if kolektor:
            self.generuj_rozszerzony_swiat()
        
    def generuj_rozszerzony_swiat(self) -> RozszerzonySwiatDanych:
        """
        Generuje rozszerzony świat danych na podstawie zebranych doświadczeń.
        
        Returns:
            RozszerzonySwiatDanych: Rozszerzony świat z metadanymi
        """
        logger.info("=" * 80)
        logger.info("GENEROWANIE ROZSZERZONEGO SWIATA DANYCH")
        logger.info("=" * 80)
        
        self.rozszerzony_swiat = RozszerzonySwiatDanych(
            data_generacji=datetime.now().strftime(self.config.eksport.FORMAT_DATY)
        )
        
        # Przetwarzaj każdą sieć
        wszystkie_doswiadczenia = self.kolektor.pobierz_doswiadczenia()
        
        for siec_nazwa, doswiadczenie in wszystkie_doswiadczenia.items():
            logger.info(f"Przetwarzam sieć: {siec_nazwa}")
            
            # Generuj metadane dla sieci
            metadane_sieci = self._generuj_metadane_sieci(siec_nazwa, doswiadczenie)
            self.rozszerzony_swiat.metadane_sieci[siec_nazwa] = metadane_sieci
            
            # Generuj metadane dla każdego meczu w sieci
            for mecz_id, obserwacje in doswiadczenie.obserwacje.items():
                if mecz_id not in self.rozszerzony_swiat.metadane_meczy:
                    self.rozszerzony_swiat.metadane_meczy[mecz_id] = MetadaneMeczu(id_meczu=mecz_id)
                
                # Dodaj obserwacje sieci do meczu
                self._dodaj_obserwacje_do_meczu(
                    self.rozszerzony_swiat.metadane_meczy[mecz_id],
                    siec_nazwa,
                    obserwacje,
                    doswiadczenie.typ_sieci
                )
        
        # Agreguj dane dla meczów (konsensus, statystyki)
        for mecz_id, metadane in self.rozszerzony_swiat.metadane_meczy.items():
            self._agreguj_dane_meczu(metadane)
        
        # Wylicz statystyki globalne
        self._wylicz_statystyki_globalne()
        
        logger.info("GENEROWANIE ROZSZERZONEGO SWIATA ZAKOŃCZONE")
        logger.info("=" * 80)
        
        return self.rozszerzony_swiat
    
    def _generuj_metadane_sieci(self, siec_nazwa: str, doswiadczenie: DoswiadczenieSieci) -> MetadaneSieci:
        """
        Generuje metadane dla pojedynczej sieci.
        """
        metadane = MetadaneSieci(
            nazwa_sieci=siec_nazwa,
            typ_sieci=doswiadczenie.typ_sieci
        )
        
        # Podstawowe statystyki
        metadane.liczba_meczy = len(doswiadczenie.obserwacje)
        metadane.liczba_obserwacji = sum(len(obs_list) for obs_list in doswiadczenie.obserwacje.values())
        
        # Skuteczność
        trafienia = sum(
            1 for obs_list in doswiadczenie.obserwacje.values()
            for obs in obs_list if obs.trafienie
        )
        metadane.skutecznosc = trafienia / metadane.liczba_obserwacji if metadane.liczba_obserwacji > 0 else 0
        
        # Średnia pewność
        pewnosci = [
            obs.pewnosc for obs_list in doswiadczenie.obserwacje.values()
            for obs in obs_list
        ]
        metadane.srednia_pewnosc = sum(pewnosci) / len(pewnosci) if pewnosci else 0
        
        # Analiza stabilności i trendów
        stabilnosci = []
        trendy = []
        
        for mecz_id, obs_list in doswiadczenie.obserwacje.items():
            if len(obs_list) >= self.config.parametry.MIN_OBSERWACJI_DO_ANALIZY:
                # Analiza stabilności predykcji
                stabilnosc = self._wylicz_stabilnosc_predykcji(obs_list)
                stabilnosci.append(stabilnosc)
                
                # Analiza trendu pewności
                trend = self._wylicz_trend_pewnosci(obs_list)
                trendy.append(trend)
        
        metadane.srednia_stabilnosc = sum(stabilnosci) / len(stabilnosci) if stabilnosci else 0
        metadane.sredni_trend_pewnosci = sum(trendy) / len(trendy) if trendy else 0
        
        # Klasyfikacja trendów
        metadane.liczba_rosnacych = sum(1 for t in trendy if t > self.config.parametry.PROG_TREND_ROSNACY)
        metadane.liczba_malejacych = sum(1 for t in trendy if t < self.config.parametry.PROG_TREND_MALEJACY)
        metadane.liczba_stabilnych = sum(1 for t in trendy if 
            self.config.parametry.PROG_TREND_MALEJACY <= t <= self.config.parametry.PROG_TREND_ROSNACY)
        
        # Cechy z metadanych sieci
        if doswiadczenie.metadane:
            metadane.cechy = doswiadczenie.metadane.cechy
        
        # Określ role sieci
        metadane.rola = self._okresl_role_sieci(metadane)
        
        # Określ specjalizację
        metadane.specjalizacja = self._okresl_specjalizacje_sieci(doswiadczenie)
        
        return metadane
    
    def _dodaj_obserwacje_do_meczu(
        self, 
        metadane_meczu: MetadaneMeczu, 
        siec_nazwa: str, 
        obserwacje: List[Obserwacja],
        typ_sieci: str
    ) -> None:
        """
        Dodaje obserwacje z sieci do metadanych meczu.
        """
        siec_key = f"{typ_sieci}_{siec_nazwa}"
        
        # Dodaj predykcje i pewności
        for obs in obserwacje:
            if siec_key not in metadane_meczu.wszystkie_predykcje:
                metadane_meczu.wszystkie_predykcje[siec_key] = []
                metadane_meczu.wszystkie_pewnosci[siec_key] = []
            
            metadane_meczu.wszystkie_predykcje[siec_key].append(obs.predykcja)
            metadane_meczu.wszystkie_pewnosci[siec_key].append(obs.pewnosc)
            
            # Zapisz wynik rzeczywisty (jeśli dostępny)
            if obs.wynik_rzeczywisty:
                metadane_meczu.wynik_rzeczywisty = obs.wynik_rzeczywisty
                metadane_meczu.grupa_rzeczywista = self.config.GRUPY_WYNIKOW.get(
                    obs.wynik_rzeczywisty, "nieznana"
                )
        
    def _agreguj_dane_meczu(self, metadane_meczu: MetadaneMeczu) -> None:
        """
        Agreguje dane dla meczu (liczy konsensus, średnie, itd.).
        """
        # Średnie pewności dla każdej sieci
        for siec_key, pewnosci in metadane_meczu.wszystkie_pewnosci.items():
            if pewnosci:
                metadane_meczu.srednia_pewnosc[siec_key] = sum(pewnosci) / len(pewnosci)
        
        # Znajdź najczęstszą predykcję (konsensus)
        wszystkie_predykcje = []
        for siec_key, predykcje in metadane_meczu.wszystkie_predykcje.items():
            wszystkie_predykcje.extend(predykcje)
        
        if wszystkie_predykcje:
            counter = defaultdict(int)
            for pred in wszystkie_predykcje:
                counter[pred] += 1
            
            najczestsza = max(counter.items(), key=lambda x: x[1])
            metadane_meczu.najczestsza_predykcja = najczestsza[0]
            metadane_meczu.licznosc_konsensusu = najczestsza[1]
            metadane_meczu.konsensus_pewnosc = metadane_meczu.srednia_pewnosc.get(
                next(iter(metadane_meczu.srednia_pewnosc.keys())), 0.0
            ) if metadane_meczu.srednia_pewnosc else 0.0
    
    def _wylicz_stabilnosc_predykcji(self, obserwacje: List[Obserwacja]) -> float:
        """
        Wylicza stabilność predykcji (0-1).
        Im wyższa, tym bardziej stabilne predykcje.
        """
        if len(obserwacje) < 2:
            return 0.0
        
        # Zlicz zmiany predykcji
        zmiany = 0
        for i in range(1, len(obserwacje)):
            if obserwacje[i].predykcja != obserwacje[i-1].predykcja:
                zmiany += 1
        
        # Stabilność = 1 - (zmiany / maksymalne_mozliwe_zmiany)
        max_zmian = len(obserwacje) - 1
        stabilnosc = 1.0 - (zmiany / max_zmian) if max_zmian > 0 else 1.0
        
        return stabilnosc
    
    def _wylicz_trend_pewnosci(self, obserwacje: List[Obserwacja]) -> float:
        """
        Wylicza trend pewności.
        Dodatni = pewność rośnie, ujemny = pewność maleje.
        """
        if len(obserwacje) < 2:
            return 0.0
        
        # Oblicz liniowy trend
        n = len(obserwacje)
        x_values = list(range(n))
        y_values = [obs.pewnosc for obs in obserwacje]
        
        # Średnie
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        # Nachylenie linii regresji (trend)
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0.0
        
        trend = numerator / denominator
        return trend
    
    def _okresl_role_sieci(self, metadane: MetadaneSieci) -> str:
        """
        Określa rolę sieci na podstawie jej charakterystyk.
        """
        # Na podstawie skuteczności
        if metadane.skutecznosc >= self.config.parametry.SKUTECZNOSC_WYSOKA:
            return "predyktor_dokladny"
        elif metadane.skutecznosc >= self.config.parametry.SKUTECZNOSC_SREDNIA:
            return "predyktor_sredni"
        elif metadane.skutecznosc >= self.config.parametry.SKUTECZNOSC_NISKA:
            return "klasyfikator_grup"
        else:
            return "analizator_trendow"
    
    def _okresl_specjalizacje_sieci(self, doswiadczenie: DoswiadczenieSieci) -> str:
        """
        Określa specjalizację sieci na podstawie rozkładu trafień.
        """
        if not doswiadczenie.ocena:
            return "ogólna"
        
        # Analizuj ocena_wynikow
        ocena_wynikow = doswiadczenie.ocena.ocena_wynikow
        
        # Grupuj wyniki
        grupy_count = defaultdict(int)
        for wynik, data in ocena_wynikow.items():
            grupa = self.config.GRUPY_WYNIKOW.get(wynik, "nieznana")
            grupy_count[grupa] += data.get("ilosc_predykcji", 0)
        
        # Znajdź dominującą grupę
        if grupy_count:
            dominujaca = max(grupy_count.items(), key=lambda x: x[1])
            if dominujaca[1] > sum(grupy_count.values()) * 0.5:
                return f"specjalista_{dominujaca[0]}"
        
        return "ogólna"
    
    def _wylicz_statystyki_globalne(self) -> None:
        """
        Wylicza statystyki globalne dla rozszerzonego świata.
        """
        if not self.rozszerzony_swiat:
            return
        
        # Statystyki sieci
        skutecznosci = [m.skutecznosc for m in self.rozszerzony_swiat.metadane_sieci.values()]
        stabilnosci = [m.srednia_stabilnosc for m in self.rozszerzony_swiat.metadane_sieci.values()]
        trendy = [m.sredni_trend_pewnosci for m in self.rozszerzony_swiat.metadane_sieci.values()]
        
        self.rozszerzony_swiat.statystyki = {
            "srednia_skutecznosc_sieci": sum(skutecznosci) / len(skutecznosci) if skutecznosci else 0,
            "srednia_stabilnosc_sieci": sum(stabilnosci) / len(stabilnosci) if stabilnosci else 0,
            "sredni_trend_pewnosci": sum(trendy) / len(trendy) if trendy else 0,
            "liczba_meczy": len(self.rozszerzony_swiat.metadane_meczy),
            "liczba_sieci": len(self.rozszerzony_swiat.metadane_sieci),
            "liczba_rosnacych_sieci": sum(
                1 for m in self.rozszerzony_swiat.metadane_sieci.values() 
                if m.sredni_trend_pewnosci > self.config.parametry.PROG_TREND_ROSNACY
            ),
            "liczba_stabilnych_sieci": sum(
                1 for m in self.rozszerzony_swiat.metadane_sieci.values()
                if (self.config.parametry.PROG_TREND_MALEJACY <= m.sredni_trend_pewnosci 
                    <= self.config.parametry.PROG_TREND_ROSNACY)
            )
        }
    
    def eksportuj_rozszerzony_swiat(self, plik_wyjsciowy: Optional[str] = None) -> None:
        """
        Eksportuje rozszerzony świat do pliku JSON.
        """
        if not self.rozszerzony_swiat:
            logger.error("Brak rozszerzonego świata do eksportu")
            return
        
        if plik_wyjsciowy is None:
            plik_wyjsciowy = self.config.sciezki.METADANE_CECH_FILE
        
        data = self.rozszerzony_swiat.to_dict()
        
        with open(plik_wyjsciowy, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Rozszerzony świat zeksportowany do: {plik_wyjsciowy}")
    
    def eksportuj_metadane_sieci(self, plik_wyjsciowy: Optional[str] = None) -> None:
        """
        Eksportuje metadane sieci do oddzielnego pliku.
        """
        if not self.rozszerzony_swiat:
            logger.error("Brak rozszerzonego świata do eksportu")
            return
        
        if plik_wyjsciowy is None:
            plik_wyjsciowy = os.path.join(
                self.config.sciezki.WARSTWA5_EXPORTS,
                "metadane_sieci.json"
            )
        
        data = {
            siec: metadane.to_dict() 
            for siec, metadane in self.rozszerzony_swiat.metadane_sieci.items()
        }
        
        with open(plik_wyjsciowy, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Metadane sieci zeksportowane do: {plik_wyjsciowy}")


def generuj_rozszerzony_swiat(kolektor: KolektorDoswiadczen) -> RozszerzonySwiatDanych:
    """
    Funkcja wygodna - generuje rozszerzony świat.
    
    Args:
        kolektor: Kolektor z zebranymi doświadczeniami
        
    Returns:
        RozszerzonySwiatDanych: Rozszerzony świat z metadanymi
    """
    generator = GeneratorMetadanych(kolektor)
    return generator.rozszerzony_swiat


if __name__ == "__main__":
    # Testowa generacja
    logger.info("Testowa generacja rozszerzonego świata...")
    
    from .kolektor_doswiadczen import zebranie_wszystkich_doswiadczen
    
    kolektor = zebranie_wszystkich_doswiadczen()
    generator = GeneratorMetadanych(kolektor)
    
    # Eksport
    generator.eksportuj_rozszerzony_swiat()
    generator.eksportuj_metadane_sieci()
    
    logger.info("Testowa generacja zakończona")
