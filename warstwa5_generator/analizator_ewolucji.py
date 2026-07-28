"""
Analizator Ewolucji - Analizuje rozwój pamięci modeli w czasie

Moduł odpowiedzialny za:
1. Analizę zmian pewności w kolejnych obserwacjach
2. Wykrywanie trendów rozwoju pamięci
3. Klasyfikację zachowań pamięci
4. Generowanie raportów ewolucji

Dane wejściowe:
- Zebrane doświadczenia z Kolektora
- Rozszerzony świat z Generatora Metadanych

Dane wyjściowe:
- Raporty ewolucji pamięci
- Klasyfikacja zachowań
- Trendy rozwoju
"""

import os
import json
import logging
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from statistics import mean, stdev

from .konfiguracja import get_config
from .kolektor_doswiadczen import KolektorDoswiadczen, DoswiadczenieSieci, Obserwacja
from .generator_metadanych import RozszerzonySwiatDanych, MetadaneSieci


# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_config().sciezki.LOG_ANALIZATOR),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ZachowaniePamieci:
    """Klasyfikacja zachowania pamięci."""
    typ: str  # stabilna, rosnaca, malejaca, niestabilna, dojrzewajaca
    opis: str
    wartosc: float  # wartość numeryczna zachowania
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TrendPamieci:
    """Trend rozwoju pamięci."""
    nazwa_sieci: str
    typ_trendu: str  # rosnacy, malejacy, stabilny, cykliczny, chaotyczny
    nachylenie: float
    moc_trendu: float  # 0-1, im wyższa tym silniejszy trend
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EwolucjaMeczu:
    """Ewolucja pamięci dla pojedynczego meczu."""
    id_meczu: str
    liczba_obserwacji: int
    
    # Ewolucja pewności
    pewnosc_poczatkowa: float = 0.0
    pewnosc_koncowa: float = 0.0
    zmiana_pewnosci: float = 0.0
    trend_pewnosci: float = 0.0
    
    # Ewolucja predykcji
    predykcje: List[str] = field(default_factory=list)
    stabilnosc_predykcji: float = 0.0
    
    # Klasyfikacja
    zachowanie: Optional[ZachowaniePamieci] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EwolucjaSieci:
    """Ewolucja pamięci dla pojedynczej sieci."""
    nazwa_sieci: str
    typ_sieci: str
    
    # Statystyki ewolucji
    sredni_trend_pewnosci: float = 0.0
    srednia_stabilnosc: float = 0.0
    odchylenie_stabilnosci: float = 0.0
    
    # Klasyfikacja
    typ_ewolucji: str = "nieokreślony"  # dojrzewajaca, stabilna, degradujaca, chaotyczna
    
    # Trend ogólny
    trend_ogolny: Optional[TrendPamieci] = None
    
    # zachowania po meczach
    ewolucje_meczy: Dict[str, EwolucjaMeczu] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RaportEwolucji:
    """Kompleksowy raport ewolucji pamięci."""
    data_generacji: str
    wersja: str = "1.0"
    
    # Ewolucje sieci
    ewolucje_sieci: Dict[str, EwolucjaSieci] = field(default_factory=dict)
    
    # Ewolucje meczów
    ewolucje_meczy: Dict[str, EwolucjaMeczu] = field(default_factory=dict)
    
    # Statystyki globalne
    statystyki: Dict[str, Any] = field(default_factory=dict)
    
    # Klasyfikacje
    klasyfikacja_sieci: Dict[str, str] = field(default_factory=dict)
    klasyfikacja_meczy: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AnalizatorEwolucji:
    """
    Główna klasa analizatora ewolucji.
    
    Analizuje rozwój pamięci modeli w czasie.
    """
    
    def __init__(self, kolektor: Optional[KolektorDoswiadczen] = None, 
                 rozszerzony_swiat: Optional[RozszerzonySwiatDanych] = None):
        self.config = get_config()
        self.kolektor = kolektor
        self.rozszerzony_swiat = rozszerzony_swiat
        self.raport: Optional[RaportEwolucji] = None
        
        if kolektor or rozszerzony_swiat:
            self.analizuj_ewolucje()
        
    def analizuj_ewolucje(self) -> RaportEwolucji:
        """
        Analizuje ewolucję pamięci dla wszystkich sieci i meczów.
        
        Returns:
            RaportEwolucji: Kompleksowy raport ewolucji
        """
        logger.info("=" * 80)
        logger.info("ANALIZA EWOLUCJI PAMIĘCI")
        logger.info("=" * 80)
        
        self.raport = RaportEwolucji(
            data_generacji=datetime.now().strftime(self.config.eksport.FORMAT_DATY)
        )
        
        # Jeśli mamy rozszerzony świat, użyj go
        if self.rozszerzony_swiat:
            self._analizuj_z_rozszerzonego_swiata()
        elif self.kolektor:
            # W przeciwnym razie analizuj bezpośrednio z kolektora
            self._analizuj_z_kolektora()
        
        # Wylicz statystyki globalne
        self._wylicz_statystyki_globalne()
        
        # Klasyfikuj sieci i mecze
        self._klasyfikuj_sieci()
        self._klasyfikuj_mecze()
        
        logger.info("ANALIZA EWOLUCJI ZAKOŃCZONA")
        logger.info("=" * 80)
        
        return self.raport
    
    def _analizuj_z_rozszerzonego_swiata(self) -> None:
        """
        Analizuj ewolucję na podstawie rozszerzonego świata.
        """
        if not self.rozszerzony_swiat:
            return
        
        # Analiza ewolucji sieci
        for siec_nazwa, metadane_sieci in self.rozszerzony_swiat.metadane_sieci.items():
            if self.kolektor:
                doswiadczenie = self.kolektor.pobierz_doswiadczenia().get(siec_nazwa)
                if doswiadczenie:
                    ewolucja = self._analizuj_ewolucje_sieci(siec_nazwa, doswiadczenie, metadane_sieci)
                    self.raport.ewolucje_sieci[siec_nazwa] = ewolucja
            else:
                # Utwórz ewolucję na podstawie metadanych
                ewolucja = self._utworz_ewolucje_z_metadanych(siec_nazwa, metadane_sieci)
                self.raport.ewolucje_sieci[siec_nazwa] = ewolucja
        
        # Analiza ewolucji meczów
        for mecz_id, metadane_meczu in self.rozszerzony_swiat.metadane_meczy.items():
            ewolucja = self._analizuj_ewolucje_meczu(mecz_id, metadane_meczu)
            self.raport.ewolucje_meczy[mecz_id] = ewolucja
        
    def _analizuj_z_kolektora(self) -> None:
        """
        Analizuj ewolucję bezpośrednio z kolektora.
        """
        if not self.kolektor:
            return
        
        # Analiza ewolucji sieci
        for siec_nazwa, doswiadczenie in self.kolektor.pobierz_doswiadczenia().items():
            ewolucja = self._analizuj_ewolucje_sieci(siec_nazwa, doswiadczenie)
            self.raport.ewolucje_sieci[siec_nazwa] = ewolucja
        
    def _analizuj_ewolucje_sieci(
        self, 
        siec_nazwa: str, 
        doswiadczenie: DoswiadczenieSieci,
        metadane_sieci: Optional[MetadaneSieci] = None
    ) -> EwolucjaSieci:
        """
        Analizuje ewolucję pamięci dla pojedynczej sieci.
        """
        ewolucja = EwolucjaSieci(
            nazwa_sieci=siec_nazwa,
            typ_sieci=doswiadczenie.typ_sieci
        )
        
        # Analiza dla każdego meczu
        for mecz_id, obserwacje in doswiadczenie.obserwacje.items():
            if len(obserwacje) >= self.config.parametry.MIN_OBSERWACJI_DO_ANALIZY:
                ewolucja_meczu = self._analizuj_ewolucje_meczu_dla_sieci(mecz_id, obserwacje)
                ewolucja.ewolucje_meczy[mecz_id] = ewolucja_meczu
        
        # Agregacja statystyk
        if ewolucja.ewolucje_meczy:
            trendy = [e.trend_pewnosci for e in ewolucja.ewolucje_meczy.values()]
            stabilnosci = [e.stabilnosc_predykcji for e in ewolucja.ewolucje_meczy.values()]
            
            ewolucja.sredni_trend_pewnosci = mean(trendy) if trendy else 0.0
            ewolucja.srednia_stabilnosc = mean(stabilnosci) if stabilnosci else 0.0
            ewolucja.odchylenie_stabilnosci = stdev(stabilnosci) if len(stabilnosci) > 1 else 0.0
        
        # Określ typ ewolucji
        ewolucja.typ_ewolucji = self._okresl_typ_ewolucji_sieci(ewolucja)
        
        # Określ trend ogólny
        if metadane_sieci:
            ewolucja.trend_ogolny = TrendPamieci(
                nazwa_sieci=siec_nazwa,
                typ_trendu=self._okresl_typ_trendu(ewolucja.sredni_trend_pewnosci),
                nachylenie=ewolucja.sredni_trend_pewnosci,
                moc_trendu=abs(ewolucja.sredni_trend_pewnosci) / (
                    self.config.parametry.PROG_TREND_ROSNACY * 2
                ) if ewolucja.sredni_trend_pewnosci != 0 else 0.0
            )
        
        return ewolucja
    
    def _analizuj_ewolucje_meczu_dla_sieci(
        self, 
        mecz_id: str, 
        obserwacje: List[Obserwacja]
    ) -> EwolucjaMeczu:
        """
        Analizuje ewolucję pamięci dla meczu w kontekście pojedynczej sieci.
        """
        ewolucja = EwolucjaMeczu(
            id_meczu=mecz_id,
            liczba_obserwacji=len(obserwacje)
        )
        
        if not obserwacje:
            return ewolucja
        
        # Ewolucja pewności
        pewnosci = [obs.pewnosc for obs in obserwacje]
        ewolucja.pewnosc_poczatkowa = pewnosci[0]
        ewolucja.pewnosc_koncowa = pewnosci[-1]
        ewolucja.zmiana_pewnosci = ewolucja.pewnosc_koncowa - ewolucja.pewnosc_poczatkowa
        ewolucja.trend_pewnosci = self._wylicz_trend(pewnosci)
        
        # Ewolucja predykcji
        ewolucja.predykcje = [obs.predykcja for obs in obserwacje]
        ewolucja.stabilnosc_predykcji = self._wylicz_stabilnosc(obserwacje)
        
        # Klasyfikacja zachowania
        ewolucja.zachowanie = self._klasyfikuj_zachowanie(
            ewolucja.trend_pewnosci,
            ewolucja.stabilnosc_predykcji,
            ewolucja.zmiana_pewnosci
        )
        
        return ewolucja
    
    def _analizuj_ewolucje_meczu(
        self, 
        mecz_id: str, 
        metadane_meczu: Any
    ) -> EwolucjaMeczu:
        """
        Analizuje ewolucję pamięci dla meczu (agregacja wszystkich sieci).
        """
        ewolucja = EwolucjaMeczu(
            id_meczu=mecz_id,
            liczba_obserwacji=sum(
                len(preds) for preds in metadane_meczu.wszystkie_predykcje.values()
            )
        )
        
        # Uśrednione metryki
        wszystkie_pewnosci = []
        for pewnosci in metadane_meczu.wszystkie_pewnosci.values():
            wszystkie_pewnosci.extend(pewnosci)
        
        if wszystkie_pewnosci:
            ewolucja.pewnosc_poczatkowa = wszystkie_pewnosci[0]
            ewolucja.pewnosc_koncowa = wszystkie_pewnosci[-1]
            ewolucja.zmiana_pewnosci = ewolucja.pewnosc_koncowa - ewolucja.pewnosc_poczatkowa
            ewolucja.trend_pewnosci = self._wylicz_trend(wszystkie_pewnosci)
        
        # Stabilność konsensusu
        ewolucja.stabilnosc_predykcji = self._wylicz_stabilnosc_konsensusu(metadane_meczu)
        
        # Klasyfikacja zachowania
        ewolucja.zachowanie = self._klasyfikuj_zachowanie(
            ewolucja.trend_pewnosci,
            ewolucja.stabilnosc_predykcji,
            ewolucja.zmiana_pewnosci
        )
        
        return ewolucja
    
    def _utworz_ewolucje_z_metadanych(
        self, 
        siec_nazwa: str, 
        metadane_sieci: MetadaneSieci
    ) -> EwolucjaSieci:
        """
        Tworzy ewolucję sieci na podstawie metadanych (jeśli nie ma dostępu do surowych danych).
        """
        ewolucja = EwolucjaSieci(
            nazwa_sieci=siec_nazwa,
            typ_sieci=metadane_sieci.typ_sieci,
            sredni_trend_pewnosci=metadane_sieci.sredni_trend_pewnosci,
            srednia_stabilnosc=metadane_sieci.srednia_stabilnosc
        )
        
        # Określ typ ewolucji
        ewolucja.typ_ewolucji = self._okresl_typ_ewolucji_sieci(ewolucja)
        
        # Trend ogólny
        ewolucja.trend_ogolny = TrendPamieci(
            nazwa_sieci=siec_nazwa,
            typ_trendu=self._okresl_typ_trendu(metadane_sieci.sredni_trend_pewnosci),
            nachylenie=metadane_sieci.sredni_trend_pewnosci,
            moc_trendu=abs(metadane_sieci.sredni_trend_pewnosci) / (
                self.config.parametry.PROG_TREND_ROSNACY * 2
            ) if metadane_sieci.sredni_trend_pewnosci != 0 else 0.0
        )
        
        return ewolucja
    
    def _wylicz_trend(self, wartosci: List[float]) -> float:
        """
        Wylicza trend liniowy dla serii wartości.
        """
        if len(wartosci) < 2:
            return 0.0
        
        n = len(wartosci)
        x_values = list(range(n))
        x_mean = sum(x_values) / n
        y_mean = sum(wartosci) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, wartosci))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _wylicz_stabilnosc(self, obserwacje: List[Obserwacja]) -> float:
        """
        Wylicza stabilność predykcji.
        """
        if len(obserwacje) < 2:
            return 1.0
        
        zmiany = sum(
            1 for i in range(1, len(obserwacje)) 
            if obserwacje[i].predykcja != obserwacje[i-1].predykcja
        )
        
        max_zmian = len(obserwacje) - 1
        return 1.0 - (zmiany / max_zmian) if max_zmian > 0 else 1.0
    
    def _wylicz_stabilnosc_konsensusu(self, metadane_meczu: Any) -> float:
        """
        Wylicza stabilność konsensusu (jak często sieci zgadzają się ze sobą).
        """
        if not metadane_meczu.wszystkie_predykcje:
            return 0.0
        
        # Dla każdej obserwacji (indeksu), sprawdź czy sieci się zgadzają
        max_obs = max(len(preds) for preds in metadane_meczu.wszystkie_predykcje.values())
        if max_obs == 0:
            return 0.0
        
        zgody = 0
        wszystkie = 0
        
        for i in range(max_obs):
            predykcje_na_pozycji = []
            for siec_key, preds in metadane_meczu.wszystkie_predykcje.items():
                if i < len(preds):
                    predykcje_na_pozycji.append(preds[i])
            
            if len(predykcje_na_pozycji) > 1:
                wszystkie += 1
                # Sprawdź czy wszystkie są takie same
                if all(p == predykcje_na_pozycji[0] for p in predykcje_na_pozycji):
                    zgody += 1
        
        return zgody / wszystkie if wszystkie > 0 else 0.0
    
    def _okresl_typ_trendu(self, trend: float) -> str:
        """
        Określa typ trendu na podstawie jego wartości.
        """
        if trend > self.config.parametry.PROG_TREND_ROSNACY:
            return "rosnacy"
        elif trend < self.config.parametry.PROG_TREND_MALEJACY:
            return "malejacy"
        elif abs(trend) <= self.config.parametry.PROG_TREND_ROSNACY * 0.5:
            return "stabilny"
        else:
            return "lekko_rosnacy" if trend > 0 else "lekko_malejacy"
    
    def _klasyfikuj_zachowanie(
        self, 
        trend: float, 
        stabilnosc: float,
        zmiana_pewnosci: float
    ) -> ZachowaniePamieci:
        """
        Klasyfikuje zachowanie pamięci.
        """
        # Określ typ zachowania
        if stabilnosc >= self.config.parametry.PROG_STABILNOSCI_WYSOKA:
            if trend > self.config.parametry.PROG_TREND_ROSNACY:
                typ = "dojrzewajaca"
                opis = "Pamięć jest stabilna i zyskuje pewność"
            elif trend < self.config.parametry.PROG_TREND_MALEJACY:
                typ = "degradujaca"
                opis = "Pamięć jest stabilna ale traci pewność"
            else:
                typ = "stabilna"
                opis = "Pamięć utrzymuje stabilną pewność"
        elif stabilnosc >= self.config.parametry.PROG_STABILNOSCI_SREDNIA:
            if trend > 0:
                typ = "rosnaca"
                opis = "Pamięć umiarkowanie stabilna, pewność rośnie"
            else:
                typ = "malejaca"
                opis = "Pamięć umiarkowanie stabilna, pewność maleje"
        else:
            if trend > 0:
                typ = "niestabilna_rosnaca"
                opis = "Pamięć niestabilna, pewność rośnie"
            else:
                typ = "chaotyczna"
                opis = "Pamięć wysoce niestabilna"
        
        return ZachowaniePamieci(
            typ=typ,
            opis=opis,
            wartosc=stabilnosc * (1 + abs(trend))  # Combined metric
        )
    
    def _okresl_typ_ewolucji_sieci(self, ewolucja: EwolucjaSieci) -> str:
        """
        Określa typ ewolucji sieci na podstawie jej charakterystyk.
        """
        # Na podstawie średniej stabilności
        if ewolucja.srednia_stabilnosc >= self.config.parametry.PROG_STABILNOSCI_WYSOKA:
            if ewolucja.sredni_trend_pewnosci > 0:
                return "dojrzewajaca"
            elif ewolucja.sredni_trend_pewnosci < 0:
                return "degradujaca"
            else:
                return "stabilna_wysoka"
        elif ewolucja.srednia_stabilnosc >= self.config.parametry.PROG_STABILNOSCI_SREDNIA:
            if ewolucja.sredni_trend_pewnosci > 0:
                return "stabilna_rosnaca"
            elif ewolucja.sredni_trend_pewnosci < 0:
                return "stabilna_malejaca"
            else:
                return "stabilna"
        else:
            if ewolucja.odchylenie_stabilnosci > 0.3:
                return "chaotyczna"
            else:
                return "niestabilna"
    
    def _wylicz_statystyki_globalne(self) -> None:
        """
        Wylicza statystyki globalne dla raportu.
        """
        if not self.raport:
            return
        
        typy_ewolucji = defaultdict(int)
        typy_trendow = defaultdict(int)
        typy_zachowan = defaultdict(int)
        
        # Statystyki sieci
        for ewolucja in self.raport.ewolucje_sieci.values():
            typy_ewolucji[ewolucja.typ_ewolucji] += 1
            if ewolucja.trend_ogolny:
                typy_trendow[ewolucja.trend_ogolny.typ_trendu] += 1
        
        # Statystyki meczów
        for ewolucja in self.raport.ewolucje_meczy.values():
            if ewolucja.zachowanie:
                typy_zachowan[ewolucja.zachowanie.typ] += 1
        
        # Średnie metryki
        trendy_sieci = [
            e.sredni_trend_pewnosci for e in self.raport.ewolucje_sieci.values()
        ]
        stabilnosci_sieci = [
            e.srednia_stabilnosc for e in self.raport.ewolucje_sieci.values()
        ]
        
        self.raport.statystyki = {
            "liczba_sieci": len(self.raport.ewolucje_sieci),
            "liczba_meczy": len(self.raport.ewolucje_meczy),
            "sredni_trend_pewnosci_sieci": mean(trendy_sieci) if trendy_sieci else 0,
            "srednia_stabilnosc_sieci": mean(stabilnosci_sieci) if stabilnosci_sieci else 0,
            "rozkład_typow_ewolucji": dict(typy_ewolucji),
            "rozkład_typow_trendow": dict(typy_trendow),
            "rozkład_typow_zachowan": dict(typy_zachowan),
            "liczba_sieci_dojrzewajacych": typy_ewolucji.get("dojrzewajaca", 0),
            "liczba_sieci_stabilnych": typy_ewolucji.get("stabilna", 0) + 
                                   typy_ewolucji.get("stabilna_wysoka", 0) +
                                   typy_ewolucji.get("stabilna_rosnaca", 0),
            "liczba_sieci_chaotycznych": typy_ewolucji.get("chaotyczna", 0)
        }
    
    def _klasyfikuj_sieci(self) -> None:
        """
        Klasyfikuje sieci według ich ewolucji.
        """
        if not self.raport:
            return
        
        for siec_nazwa, ewolucja in self.raport.ewolucje_sieci.items():
            self.raport.klasyfikacja_sieci[siec_nazwa] = ewolucja.typ_ewolucji
        
    def _klasyfikuj_mecze(self) -> None:
        """
        Klasyfikuje mecze według zachowania pamięci.
        """
        if not self.raport:
            return
        
        for mecz_id, ewolucja in self.raport.ewolucje_meczy.items():
            if ewolucja.zachowanie:
                self.raport.klasyfikacja_meczy[mecz_id] = ewolucja.zachowanie.typ
            else:
                self.raport.klasyfikacja_meczy[mecz_id] = "nieokreślony"
    
    def eksportuj_raport(self, plik_wyjsciowy: Optional[str] = None) -> None:
        """
        Eksportuje raport ewolucji do pliku JSON.
        """
        if not self.raport:
            logger.error("Brak raportu do eksportu")
            return
        
        if plik_wyjsciowy is None:
            plik_wyjsciowy = self.config.sciezki.EWOLUCJA_PAMIECI_FILE
        
        data = self.raport.to_dict()
        
        with open(plik_wyjsciowy, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Raport ewolucji zeksportowany do: {plik_wyjsciowy}")


def analizuj_ewolucje_pamieci(
    kolektor: Optional[KolektorDoswiadczen] = None,
    rozszerzony_swiat: Optional[RozszerzonySwiatDanych] = None
) -> RaportEwolucji:
    """
    Funkcja wygodna - analizuje ewolucję pamięci.
    
    Args:
        kolektor: Kolektor z zebranymi doświadczeniami
        rozszerzony_swiat: Rozszerzony świat z metadanymi
        
    Returns:
        RaportEwolucji: Kompleksowy raport ewolucji
    """
    analizator = AnalizatorEwolucji(kolektor, rozszerzony_swiat)
    return analizator.raport


if __name__ == "__main__":
    # Testowa analiza
    logger.info("Testowa analiza ewolucji...")
    
    from .kolektor_doswiadczen import zebranie_wszystkich_doswiadczen
    from .generator_metadanych import GeneratorMetadanych
    
    kolektor = zebranie_wszystkich_doswiadczen()
    generator = GeneratorMetadanych(kolektor)
    
    analizator = AnalizatorEwolucji(kolektor, generator.rozszerzony_swiat)
    
    # Eksport
    analizator.eksportuj_raport()
    
    logger.info("Testowa analiza zakończona")
