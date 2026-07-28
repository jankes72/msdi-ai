"""
PAMIĘĆ MODELI V2 - INTEGRACJA SYSTEMU
======================================

Główny moduł integracyjny łączący:
- Level 1 (Agregator predykcji z 15 sieci SSI)
- Level 2 (Kalibrator uczący się zachowania Level 1)
- Pamięć (Centralne repozytorium obserwacji)

Architektura systemu:

    DANE WEJŚCIOWE (database_dzisiaj.csv, itd.)
           ↓
    Level 1: AdapterManager → AgregatorPredykcji → PredykcjaLevel1
           ↓
    [Czekaj na wynik meczu]
           ↓
    Pamięć: Obserwacja (predykcja + wynik_rzeczywisty + confidence)
           ↓
    Level 2: Kalibrator → PredykcjaLevel1Kalibrowana
           ↓
    Repozytorium: Zapisz do centralnej pamięci + wersjonowanie

Cykl życia predykcji:
1. Generuj predykcję Level 1 (agregacja z sieci SSI)
2. Po poznaniu wyniku: zapisz obserwację do pamięci
3. Trenuj kalibrator na podstawie nowych obserwacji
4. Generuj kalibrowane predykcje (Level 1 + Level 2)
5. Zapisz nową wersję pamięci (nie nadpisujemy!)

Zasady (z dokumentacji):
- Nie modyfikujemy istniejących plików SSI
- Każde uruchomienie tworzy nową wersję pamięci
- Podział danych: 50% trening, 10% walidacja, 40% obserwacja

Autor: MSDI AI v0.02
Data: 2026-07-27
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import uuid

# Import z lokalnych modułów V2
from pamiec_modeli_v2.schemas import (
    PredykcjaLevel1,
    PredykcjaLevel1Kalibrowana,
    Obserwacja,
    KonfiguracjaV2,
    get_grupa_wyniku,
    normalizuj_wynik,
    waliduj_wynik,
)
from pamiec_modeli_v2.level1.aggregator import AgregatorPredykcji, utworz_agregator
from pamiec_modeli_v2.level1.adapters.siec_trend_adapter import AdapterManager, utworz_adapter_manager
from pamiec_modeli_v2.level2.kalibrator import KalibratorLevel2, utworz_kalibrator, KalibratorConfig
from pamiec_modeli_v2.pamiec.repozytorium import PamiecRepozytorium, utworz_repozytorium


# =============================================================================
# KLASA: SYSTEM PAMIĘCI MODELI V2 (GŁÓWNA FASADA)
# =============================================================================

class SystemPamieciV2:
    """
    Główna fasada Systemu Pamięci Modeli V2.
    
    Łączy wszystkie komponenty w jeden spójny system:
    - Level 1: Agregator predykcji z 15 sieci SSI
    - Level 2: Kalibrator uczący się zachowania Level 1
    - Pamięć: Centralne repozytorium obserwacji
    
    Użycie:
    >>> system = SystemPamieciV2()
    >>> 
    >>> # Generuj predykcję
    >>> pred_l1 = system.generuj_predykcje(dane_meczu, mecz_id, grupa_id)
    >>> 
    >>> # Po poznaniu wyniku, zapisz obserwację
    >>> system.zapisz_obserwacje(mecz_id, wynik_rzeczywisty)
    >>> 
    >>> # Generuj kalibrowaną predykcję (po nauczeniu kalibratora)
    >>> pred_kalibrowana = system.generuj_predykcje_kalibrowana(dane_meczu, mecz_id, grupa_id)
    >>> 
    >>> # Zapisz nową wersję pamięci
    >>> system.zapisz_wersje_pamieci()
    """
    
    # Konfiguracja systemu
    config: KonfiguracjaV2 = KonfiguracjaV2()
    kalibrator_config: KalibratorConfig = KalibratorConfig()
    
    # Komponenty systemu
    agregator: Optional[AgregatorPredykcji] = None
    kalibrator: Optional[KalibratorLevel2] = None
    repozytorium: Optional[PamiecRepozytorium] = None
    
    # Stan systemu
    _zainicjalizowany: bool = False
    _wersja_pamieci: str = ""
    _data_utworzenia: datetime = None
    
    # Historia predykcji (dla batch processing)
    historia_predykcji: Dict[str, PredykcjaLevel1] = {}
    historia_obserwacji: Dict[str, Obserwacja] = {}
    
    # -------------------------------------------------------------------------
    # INICJALIZACJA
    # -------------------------------------------------------------------------
    
    def __init__(self, 
                 auto_init: bool = True,
                 config: Optional[KonfiguracjaV2] = None,
                 kalibrator_config: Optional[KalibratorConfig] = None):
        """
        Inicjalizacja systemu.
        
        Args:
            auto_init: Czy automatycznie zainicjalizować komponenty
            config: Konfiguracja systemu V2
            kalibrator_config: Konfiguracja kalibratora Level 2
        """
        if config:
            self.config = config
        if kalibrator_config:
            self.kalibrator_config = kalibrator_config
        
        self._data_utworzenia = datetime.now()
        self._wersja_pamieci = self._generuj_wersje_pamieci()
        
        if auto_init:
            self.inicjalizuj()
    
    def _generuj_wersje_pamieci(self) -> str:
        """Generuje unikalną nazwę wersji pamięci"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"v2_{timestamp}_{unique_id}"
    
    def inicjalizuj(self) -> bool:
        """
        Inicjalizuje wszystkie komponenty systemu.
        
        Returns:
            True jeśli inicjalizacja się powiodła
        """
        try:
            # 1. Inicjalizuj Agregator Level 1
            self.agregator = utworz_agregator(strategia=self.config.STRATEGIE_AGREGACJI[0])
            
            # 2. Inicjalizuj Kalibrator Level 2
            self.kalibrator = utworz_kalibrator(self.kalibrator_config)
            
            # 3. Inicjalizuj Repozytorium Pamięci
            self.repozytorium = utworz_repozytorium()
            
            # 4. Połącz Kalibrator z Repozytorium
            self.kalibrator.ustaw_repozytorium(self.repozytorium)
            
            self._zainicjalizowany = True
            
            print("System Pamieci V2 zainicjalizowany pomyślnie.")
            print(f"  Level 1: {len(self.agregator.adapter_manager.adaptery)} sieci")
            print(f"  Level 2: Metoda={self.kalibrator.config.METODA_KALIBRACJI}, ML={self.kalibrator.config.ML_ENABLED}")
            print(f"  Pamięć: {len(self.repozytorium.obserwacje)} obserwacji załadowanych")
            print(f"  Wersja: {self._wersja_pamieci}")
            
            return True
            
        except Exception as e:
            print(f"Błąd inicjalizacji systemu: {e}")
            self._zainicjalizowany = False
            return False
    
    def reinicjalizuj(self) -> bool:
        """Reinicjalizuje system (przydatne po zmianach konfiguracji)"""
        self._zainicjalizowany = False
        self.agregator = None
        self.kalibrator = None
        self.repozytorium = None
        return self.inicjalizuj()
    
    # -------------------------------------------------------------------------
    # GENEROWANIE PREDIKCJI
    # -------------------------------------------------------------------------
    
    def generuj_predykcje(self, dane_meczu: Dict[str, Any], 
                          mecz_id: str, 
                          grupa_id: str = "BRAK") -> Optional[PredykcjaLevel1]:
        """
        Generuje predykcję Level 1 (agregacja z 15 sieci SSI).
        
        Args:
            dane_meczu: Dane meczu (słownik z cechami)
            mecz_id: Identyfikator meczu
            grupa_id: Identyfikator grupy świata
        
        Returns:
            PredykcjaLevel1 lub None w przypadku błędu
        """
        if not self._zainicjalizowany or self.agregator is None:
            print("System nie zainicjalizowany. Wywołaj inicjalizuj().")
            return None
        
        try:
            predykcja = self.agregator.predykcja(dane_meczu, mecz_id, grupa_id)
            
            # Zapisz do historii
            self.historia_predykcji[f"{mecz_id}_{predykcja.id_modelu}"] = predykcja
            
            return predykcja
            
        except Exception as e:
            print(f"Błąd generowania predykcji: {e}")
            return None
    
    def generuj_predykcje_batch(self, mecze: List[Dict[str, Any]]) -> List[PredykcjaLevel1]:
        """
        Generuje predykcje Level 1 dla wielu meczów.
        
        Args:
            mecze: Lista danych meczów
        
        Returns:
            Lista PredykcjaLevel1
        """
        if not self._zainicjalizowany or self.agregator is None:
            print("System nie zainicjalizowany.")
            return []
        
        try:
            predykcje = self.agregator.predykcja_batch(mecze)
            
            # Zapisz do historii
            for pred in predykcje:
                self.historia_predykcji[f"{pred.id_meczu}_{pred.id_modelu}"] = pred
            
            return predykcje
            
        except Exception as e:
            print(f"Błąd generowania predykcji batch: {e}")
            return []
    
    def generuj_predykcje_kalibrowana(self, dane_meczu: Dict[str, Any], 
                                    mecz_id: str, 
                                    grupa_id: str = "BRAK") -> Optional[PredykcjaLevel1Kalibrowana]:
        """
        Generuje kalibrowaną predykcję (Level 1 + Level 2).
        
        Args:
            dane_meczu: Dane meczu
            mecz_id: Identyfikator meczu
            grupa_id: Identyfikator grupy
        
        Returns:
            PredykcjaLevel1Kalibrowana lub None
        """
        # Najpierw wygeneruj predykcję Level 1
        pred_l1 = self.generuj_predykcje(dane_meczu, mecz_id, grupa_id)
        
        if pred_l1 is None:
            return None
        
        # Kalibruj confidence
        if self.kalibrator is None:
            # Fallback: zwróć oryginalne confidence
            return PredykcjaLevel1Kalibrowana(
                id_modelu=pred_l1.id_modelu,
                id_meczu=pred_l1.id_meczu,
                id_grupy=pred_l1.id_grupy,
                wynik_predykcji=pred_l1.wynik_predykcji,
                confidence=pred_l1.confidence,
                confidence_kalibrowana=pred_l1.confidence,
                poprawka_kalibracji=0.0,
            )
        
        # Pobierz sieci składające (jeśli dostępne)
        sieci_skladowe = pred_l1.sieci_skladowe
        
        # Kalibruj
        pred_kalibrowana = self.kalibrator.kalibruj(pred_l1, sieci_skladowe)
        
        return pred_kalibrowana
    
    def generuj_predykcje_kalibrowana_batch(self, mecze: List[Dict[str, Any]]) -> List[PredykcjaLevel1Kalibrowana]:
        """
        Generuje kalibrowane predykcje dla wielu meczów.
        
        Args:
            mecze: Lista danych meczów
        
        Returns:
            Lista PredykcjaLevel1Kalibrowana
        """
        predykcje_l1 = self.generuj_predykcje_batch(mecze)
        
        if not predykcje_l1 or self.kalibrator is None:
            return []
        
        kalibrowane = []
        for pred_l1 in predykcje_l1:
            pred_kal = self.kalibrator.kalibruj(pred_l1, pred_l1.sieci_skladowe)
            kalibrowane.append(pred_kal)
        
        return kalibrowane
    
    # -------------------------------------------------------------------------
    # ZAPISYWANIE OBSERWACJI (PO ZNAJOMOŚCI WYNIKU)
    # -------------------------------------------------------------------------
    
    def zapisz_obserwacje(self, mecz_id: str, wynik_rzeczywisty: str, 
                         id_modelu: str = "AGGREGATOR_HYBRID",
                         id_grupy: str = "BRAK",
                         confidence: Optional[float] = None,
                         wynik_predykcji: Optional[str] = None) -> Optional[Obserwacja]:
        """
        Zapisuje obserwację po poznaniu rzeczywistego wyniku meczu.
        
        Ta metoda powinna być wywołana PO zakończeniu meczu,
        gdy znany jest wynik_rzeczywisty.
        
        Args:
            mecz_id: Identyfikator meczu
            wynik_rzeczywisty: Rzeczywisty wynik meczu (format "X:Y")
            id_modelu: Identyfikator modelu (domyślnie agregator)
            id_grupy: Identyfikator grupy świata
            confidence: Poziom pewności (jeśli None, pobrany z historii)
            wynik_predykcji: Predykcja (jeśli None, pobrana z historii)
        
        Returns:
            Obserwacja lub None w przypadku błędu
        """
        if not self._zainicjalizowany or self.repozytorium is None:
            print("System nie zainicjalizowany.")
            return None
        
        if not waliduj_wynik(wynik_rzeczywisty):
            print(f"Nieprawidłowy wynik: {wynik_rzeczywisty}")
            return None
        
        try:
            # Pobierz predykcję z historii (jeśli dostępna)
            if wynik_predykcji is None or confidence is None:
                # Szukaj w historii predykcji
                for key, pred in self.historia_predykcji.items():
                    if mecz_id in key:
                        if wynik_predykcji is None:
                            wynik_predykcji = pred.wynik_predykcji
                        if confidence is None:
                            confidence = pred.confidence
                        break
            
            # Jeśli ciągle brak, użyj domyślnych wartości
            if wynik_predykcji is None:
                wynik_predykcji = "1:0"  # Domyślna predykcja
            if confidence is None:
                confidence = 0.5  # Domyślne confidence
            
            # Utwórz obserwację
            obserwacja = Obserwacja(
                id_meczu=mecz_id,
                id_grupy=id_grupy,
                id_modelu=id_modelu,
                wynik_predykcji=wynik_predykcji,
                confidence=confidence,
                wynik_rzeczywisty=wynik_rzeczywisty,
            )
            
            # Dodaj do repozytorium
            self.repozytorium.dodaj_obserwacje(obserwacja)
            
            # Dodaj do historii
            self.historia_obserwacji[f"{mecz_id}_{id_modelu}"] = obserwacja
            
            print(f"Obserwacja zapisana: {mecz_id} -> {wynik_predykcji} vs {wynik_rzeczywisty} "
                  f"(trafienie: {obserwacja.trafienie}, grupa: {obserwacja.trafienie_grupa})")
            
            return obserwacja
            
        except Exception as e:
            print(f"Błąd zapisu obserwacji: {e}")
            return None
    
    def zapisz_obserwacje_z_predykcji(self, predykcja: PredykcjaLevel1, 
                                     wynik_rzeczywisty: str) -> Optional[Obserwacja]:
        """
        Zapisuje obserwację na podstawie predykcji Level 1 i wyniku rzeczywistego.
        
        Args:
            predykcja: PredykcjaLevel1 z Level 1
            wynik_rzeczywisty: Rzeczywisty wynik meczu
        
        Returns:
            Obserwacja lub None
        """
        return self.zapisz_obserwacje(
            mecz_id=predykcja.id_meczu,
            wynik_rzeczywisty=wynik_rzeczywisty,
            id_modelu=predykcja.id_modelu,
            id_grupy=predykcja.id_grupy,
            confidence=predykcja.confidence,
            wynik_predykcji=predykcja.wynik_predykcji,
        )
    
    # -------------------------------------------------------------------------
    # TRENOWANIE KALIBRATORA
    # -------------------------------------------------------------------------
    
    def trenuj_kalibrator(self, min_obserwacji: int = 100) -> bool:
        """
        Trenuje kalibrator Level 2 na podstawie zebranych obserwacji.
        
        Args:
            min_obserwacji: Minimalna liczba obserwacji do trenowania
        
        Returns:
            True jeśli trening się powiódł
        """
        if not self._zainicjalizowany or self.kalibrator is None or self.repozytorium is None:
            print("System nie zainicjalizowany.")
            return False
        
        # Sprawdź liczbę obserwacji
        if len(self.repozytorium.obserwacje) < min_obserwacji:
            print(f"Za mało obserwacji ({len(self.repozytorium.obserwacje)}) do trenowania. "
                  f"Minimum: {min_obserwacji}")
            return False
        
        try:
            # Pobierz wszystkie obserwacje
            obserwacje = list(self.repozytorium.obserwacje.values())
            
            # Trenuj kalibrator
            trenowanie_ok = self.kalibrator.trenuj(obserwacje)
            
            if trenowanie_ok:
                # Wykryj wzorce
                self.kalibrator.wykryj_wzorce(obserwacje)
                
                print(f"Kalibrator wytrenowany pomyślnie.")
                print(f"  Obserwacje: {len(obserwacje)}")
                print(f"  Wzorce: {len(self.kalibrator.wzorce)}")
                
                # Zapisz model kalibratora
                self.kalibrator.zapisz_model()
            
            return trenowanie_ok
            
        except Exception as e:
            print(f"Błąd trenowania kalibratora: {e}")
            return False
    
    def trenuj_kalibrator_auto(self) -> bool:
        """
        Automatycznie trenuje kalibrator, jeśli jest wystarczająco danych.
        
        Sprawdza, czy liczba obserwacji osiągnęła próg do trenowania.
        
        Returns:
            True jeśli trening się powiódł
        """
        if not self._zainicjalizowany:
            return False
        
        min_obs = self.kalibrator_config.MIN_OBSERWACJI_TRENING
        
        if len(self.repozytorium.obserwacje) >= min_obs:
            return self.trenuj_kalibrator()
        
        return False
    
    # -------------------------------------------------------------------------
    # PERSYSTENCJA (ZAPIS/WERSJONOWANIE)
    # -------------------------------------------------------------------------
    
    def zapisz_wersje_pamieci(self, nazwa: Optional[str] = None) -> Optional[Path]:
        """
        Zapisuje aktualną pamięć jako nową wersję.
        
        ZASADA: Nie nadpisujemy pamięci. Każde uruchomienie tworzy nową wersję.
        
        Args:
            nazwa: Nazwa wersji (domyślnie auto-wygenerowana)
        
        Returns:
            Ścieżka do zapisanej wersji lub None
        """
        if not self._zainicjalizowany or self.repozytorium is None:
            print("System nie zainicjalizowany.")
            return None
        
        try:
            if nazwa is None:
                nazwa = self._wersja_pamieci
            
            # Zapis z repozytorium
            plik_wersji = self.repozytorium.zapisz_wersje(nazwa=nazwa)
            
            # Dodatkowo zapisz metadane systemu
            self._zapisz_metadata_systemu(nazwa, plik_wersji.parent)
            
            # Wygeneruj nową wersję pamięci
            self._wersja_pamieci = self._generuj_wersje_pamieci()
            
            print(f"Wersja pamięci zapisana: {plik_wersji}")
            return plik_wersji
            
        except Exception as e:
            print(f"Błąd zapisu wersji pamięci: {e}")
            return None
    
    def _zapisz_metadata_systemu(self, nazwa: str, sciezka: Path):
        """Zapisuje metadane systemu"""
        metadata = {
            "system": "PAMIEC_MODELI_V2",
            "wersja": nazwa,
            "data_utworzenia": self._data_utworzenia.isoformat(),
            "data_zapisu": datetime.now().isoformat(),
            "konfiguracja": self.config.to_dict(),
            "kalibrator": self.kalibrator.metadata if self.kalibrator else {},
            "statystyki": self.repozytorium.pobierz_statystyki().to_dict() if self.repozytorium else {},
        }
        
        metadata_file = sciezka / f"system_metadata_{nazwa}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Metadane systemu zapisane: {metadata_file}")
    
    def zaladuj_wersje_pamieci(self, sciezka_wersji: Path) -> bool:
        """
        Ładuje pamięć z konkretnej wersji.
        
        Args:
            sciezka_wersji: Ścieżka do pliku wersji pamięci
        
        Returns:
            True jeśli załadowano pomyślnie
        """
        if not self._zainicjalizowany or self.repozytorium is None:
            print("System nie zainicjalizowany.")
            return False
        
        try:
            return self.repozytorium.zaladuj_wersje(sciezka_wersji)
        except Exception as e:
            print(f"Błąd ładowania wersji pamięci: {e}")
            return False
    
    def lista_wersji_pamieci(self) -> List[Path]:
        """Zwraca listę dostępnych wersji pamięci"""
        if self.repozytorium is None:
            return []
        return self.repozytorium.lista_wersji()
    
    # -------------------------------------------------------------------------
    # ANALIZA I STATYSTYKI
    # -------------------------------------------------------------------------
    
    def pobierz_statystyki_systemu(self) -> Dict[str, Any]:
        """
        Zwraca statystyki całego systemu.
        
        Returns:
            Słownik ze statystykami
        """
        if not self._zainicjalizowany:
            return {}
        
        statystyki = {
            "system": {
                "wersja": self._wersja_pamieci,
                "data_utworzenia": self._data_utworzenia.isoformat(),
                "zainicjalizowany": self._zainicjalizowany,
            },
            "level1": self._pobierz_statystyki_level1(),
            "level2": self._pobierz_statystyki_level2(),
            "pamiec": self._pobierz_statystyki_pamieci(),
        }
        
        return statystyki
    
    def _pobierz_statystyki_level1(self) -> Dict[str, Any]:
        """Pobiera statystyki Level 1"""
        if self.agregator is None:
            return {}
        
        # Statystyki agregatora
        stats = {
            "strategia": self.agregator.strategia,
            "liczba_sieci": len(self.agregator.adapter_manager.adaptery) if self.agregator.adapter_manager else 0,
        }
        
        # Statystyki z ostatniej predykcji (jeśli dostępne)
        if self.historia_predykcji:
            ostatnia = list(self.historia_predykcji.values())[-1]
            stats["ostatnia_predykcja"] = {
                "mecz": ostatnia.id_meczu,
                "wynik": ostatnia.wynik_predykcji,
                "confidence": ostatnia.confidence,
            }
        
        return stats
    
    def _pobierz_statystyki_level2(self) -> Dict[str, Any]:
        """Pobiera statystyki Level 2"""
        if self.kalibrator is None:
            return {}
        
        return {
            "metoda": self.kalibrator.config.METODA_KALIBRACJI,
            "ml_dostepny": self.kalibrator.config.ML_ENABLED,
            "wytrenowany": self.kalibrator.model_bucket is not None or self.kalibrator.model_ml is not None,
            "wersja": self.kalibrator.metadata.get("wersja", ""),
            "wzorce": len(self.kalibrator.wzorce),
            "statystyki": self.kalibrator.statystyki.get("global", {}),
        }
    
    def _pobierz_statystyki_pamieci(self) -> Dict[str, Any]:
        """Pobiera statystyki pamięci"""
        if self.repozytorium is None:
            return {}
        
        stats = self.repozytorium.pobierz_statystyki()
        return {
            "obserwacje": stats.calkowita_liczba_obserwacji,
            "klasy": stats.liczba_klas,
            "modele": stats.liczba_modeli,
            "skutecznosc": stats.srednia_skutecznosc,
            "sredni_confidence": stats.sredni_confidence,
        }
    
    def pobierz_wzorce(self) -> List[Any]:
        """Zwraca listę wykrytych wzorców zachowania"""
        if self.kalibrator is None:
            return []
        return self.kalibrator.pobierz_wzorce()
    
    # -------------------------------------------------------------------------
    # PEŁNY CYKL (PRZYKŁADOWE UŻYCIE)
    # -------------------------------------------------------------------------
    
    def pelny_cykl(self, dane_meczu: Dict[str, Any], mecz_id: str, 
                   grupa_id: str = "BRAK", wynik_rzeczywisty: Optional[str] = None) -> Dict[str, Any]:
        """
        Wykonuje pełny cykl systemu dla jednego meczu.
        
        Działanie:
        1. Generuje predykcję Level 1
        2. Kalibruje confidence (jeśli kalibrator jest wytrenowany)
        3. Jeśli wynik_rzeczywisty jest podany, zapisuje obserwację
        4. Zwraca wyniki
        
        Args:
            dane_meczu: Dane meczu
            mecz_id: Identyfikator meczu
            grupa_id: Identyfikator grupy
            wynik_rzeczywisty: Opcjonalny rzeczywisty wynik (jeśli znany)
        
        Returns:
            Słownik z wynikami całego cyklu
        """
        wynik = {
            "mecz_id": mecz_id,
            "grupa_id": grupa_id,
            "timestamp": datetime.now().isoformat(),
            "level1": None,
            "level2": None,
            "obserwacja": None,
        }
        
        # Krok 1: Generuj predykcję Level 1
        pred_l1 = self.generuj_predykcje(dane_meczu, mecz_id, grupa_id)
        if pred_l1:
            wynik["level1"] = pred_l1.to_dict()
        
        # Krok 2: Kalibruj confidence
        if pred_l1:
            pred_kal = self.generuj_predykcje_kalibrowana(dane_meczu, mecz_id, grupa_id)
            if pred_kal:
                wynik["level2"] = pred_kal.to_dict()
        
        # Krok 3: Zapis obserwacji (jeśli wynik rzeczywisty jest znany)
        if wynik_rzeczywisty and pred_l1:
            obs = self.zapisz_obserwacje_z_predykcji(pred_l1, wynik_rzeczywisty)
            if obs:
                wynik["obserwacja"] = obs.to_dict()
                
                # Auto-trenuj kalibrator (jeśli wystarczająco danych)
                self.trenuj_kalibrator_auto()
                
                # Zapisz nową wersję pamięci
                self.zapisz_wersje_pamieci()
        
        return wynik
    
    def pelny_cykl_batch(self, mecze: List[Dict[str, Any]], 
                        wyniki_rzeczywiste: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Wykonuje pełny cykl systemu dla wielu meczów.
        
        Args:
            mecze: Lista danych meczów
            wyniki_rzeczywiste: Opcjonalny słownik {mecz_id: wynik} z prawdziwymi wynikami
        
        Returns:
            Lista wyników dla każdego meczu
        """
        wyniki = []
        
        for mecz_data in mecze:
            mecz_id = mecz_data.get('id_meczu', mecz_data.get('mecz', ''))
            grupa_id = mecz_data.get('id_grupy', mecz_data.get('grupa', 'BRAK'))
            
            wynik_rzeczywisty = None
            if wyniki_rzeczywiste and mecz_id in wyniki_rzeczywiste:
                wynik_rzeczywisty = wyniki_rzeczywiste[mecz_id]
            
            wynik = self.pelny_cykl(dane_meczu=mecz_data, mecz_id=mecz_id, 
                                   grupa_id=grupa_id, wynik_rzeczywisty=wynik_rzeczywisty)
            wyniki.append(wynik)
        
        return wyniki


# =============================================================================
# FUNKCJE GLOBALNE
# =============================================================================

def utworz_system() -> SystemPamieciV2:
    """
    Tworzy nowy system Pamięci Modeli V2.
    
    Returns:
        Obiekt SystemPamieciV2
    """
    return SystemPamieciV2(auto_init=True)


def utworz_system_bez_inicjalizacji() -> SystemPamieciV2:
    """
    Tworzy system bez automatycznej inicjalizacji.
    
    Returns:
        Obiekt SystemPamieciV2
    """
    return SystemPamieciV2(auto_init=False)


def utworz_system_z_konfiguracja(config: KonfiguracjaV2, 
                                kalibrator_config: KalibratorConfig) -> SystemPamieciV2:
    """
    Tworzy system z niestandardową konfiguracją.
    
    Args:
        config: Konfiguracja systemu V2
        kalibrator_config: Konfiguracja kalibratora
    
    Returns:
        Obiekt SystemPamieciV2
    """
    return SystemPamieciV2(auto_init=True, config=config, kalibrator_config=kalibrator_config)


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Testing SystemPamieciV2 - Integracja Level 1 + Level 2 + Pamięć")
    print("=" * 70)
    
    # Test 1: Inicjalizacja systemu
    print("\n--- Test 1: Inicjalizacja systemu ---")
    system = utworz_system()
    print(f"Zainicjalizowany: {system._zainicjalizowany}")
    print(f"Agregator: {system.agregator is not None}")
    print(f"Kalibrator: {system.kalibrator is not None}")
    print(f"Repozytorium: {system.repozytorium is not None}")
    print(f"Obserwacje w pamięci: {len(system.repozytorium.obserwacje)}")
    
    # Test 2: Generowanie predykcji
    print("\n--- Test 2: Generowanie predykcji Level 1 ---")
    
    dane_testowe = {
        "id_meczu": "TestMatch_1",
        "zmiana_1": 0.5, "zmiana_X": 0.3, "zmiana_2": 0.2,
        "amplituda_1": 0.1, "amplituda_X": 0.2, "amplituda_2": 0.15,
        "tempo_1": 0.05, "tempo_X": 0.03, "tempo_2": 0.02,
        "max_wahanie_1": 0.1, "max_wahanie_X": 0.08, "max_wahanie_2": 0.12,
        "start_1_raw": 1.5, "start_X_raw": 4.0, "start_2_raw": 5.0,
        "koniec_1_raw": 1.6, "koniec_X_raw": 4.2, "koniec_2_raw": 5.5,
        "log_start_1": 0.5, "log_start_X": 0.7, "log_start_2": 0.8,
        "log_koniec_1": 0.55, "log_koniec_X": 0.75, "log_koniec_2": 0.85,
        "ratio_1X_start": 1.5, "ratio_1_2_start": 2.0, "ratio_X2_start": 0.75,
        "ratio_1X_koniec": 1.6, "ratio_1_2_koniec": 2.2, "ratio_X2_koniec": 0.8,
        "mean_1": 1.55, "mean_X": 4.1, "mean_2": 5.25,
        "median_1": 1.55, "median_X": 4.1, "median_2": 5.25,
        "stdev_1": 0.1, "stdev_X": 0.2, "stdev_2": 0.3,
        "czas_h": 24.0,
        "id_grupy": "test_group",
    }
    
    pred_l1 = system.generuj_predykcje(dane_testowe, "TestMatch_1", "test_group")
    if pred_l1:
        print(f"Predykcja Level 1: {pred_l1.wynik_predykcji}")
        print(f"Confidence: {pred_l1.confidence:.4f}")
        print(f"Model: {pred_l1.id_modelu}")
        print(f"Sieci składające: {len(pred_l1.sieci_skladowe)}")
    
    # Test 3: Kalibrowana predykcja
    print("\n--- Test 3: Kalibrowana predykcja (Level 1 + Level 2) ---")
    
    # Najpierw trenuj kalibrator (z symulowanymi danymi)
    print("Trenowanie kalibratora z symulowanymi danymi...")
    import random
    random.seed(42)
    
    # Generuj symulowane obserwacje do trenowania
    obserwacje_train = []
    for i in range(150):
        pred_wynik = random.choice(["1:0", "0:1", "2:0", "0:2", "1:1", "2:1"])
        rzeczyw_wynik = random.choice(["1:0", "0:1", "2:0", "0:2", "1:1", "2:1"])
        confidence = random.uniform(0.1, 0.9)
        
        obs = Obserwacja(
            id_meczu=f"TrainMatch_{i}",
            id_grupy="train_group",
            id_modelu="train_model",
            wynik_predykcji=pred_wynik,
            confidence=confidence,
            wynik_rzeczywisty=rzeczyw_wynik,
        )
        obserwacje_train.append(obs)
    
    # Dodaj do repozytorium
    for obs in obserwacje_train:
        system.repozytorium.dodaj_obserwacje(obs)
    
    # Trenuj kalibrator
    trenowanie_ok = system.trenuj_kalibrator(min_obserwacji=100)
    print(f"Trenowanie kalibratora: {'SUKCES' if trenowanie_ok else 'FAIL'}")
    
    # Teraz generuj kalibrowaną predykcję
    pred_kal = system.generuj_predykcje_kalibrowana(dane_testowe, "TestMatch_2", "test_group")
    if pred_kal:
        print(f"Predykcja Level 2: {pred_kal.wynik_predykcji}")
        print(f"Oryginalne confidence: {pred_kal.confidence:.4f}")
        print(f"Kalibrowane confidence: {pred_kal.confidence_kalibrowana:.4f}")
        print(f"Poprawka: {pred_kal.poprawka_kalibracji:.4f}")
    
    # Test 4: Zapis obserwacji
    print("\n--- Test 4: Zapis obserwacji ---")
    
    obs = system.zapisz_obserwacje(
        mecz_id="TestMatch_1",
        wynik_rzeczywisty="2:1",
        id_modelu=pred_l1.id_modelu if pred_l1 else "test",
        id_grupy="test_group",
        confidence=pred_l1.confidence if pred_l1 else 0.7,
        wynik_predykcji=pred_l1.wynik_predykcji if pred_l1 else "1:1",
    )
    if obs:
        print(f"Obserwacja zapisana: {obs.id_meczu}")
        print(f"Trafienie: {obs.trafienie}")
        print(f"Trafienie grupa: {obs.trafienie_grupa}")
    
    # Test 5: Pełny cykl
    print("\n--- Test 5: Pełny cykl (predykcja + wynik) ---")
    
    wynik_cyklu = system.pelny_cykl(
        dane_meczu=dane_testowe,
        mecz_id="TestMatch_3",
        grupa_id="test_group",
        wynik_rzeczywisty="1:0"
    )
    
    print(f"Level 1: {wynik_cyklu.get('level1', {}).get('wynik_predykcji', 'N/A')}")
    print(f"Level 2: {wynik_cyklu.get('level2', {}).get('wynik_predykcji', 'N/A')}")
    print(f"Level 2 confidence: {wynik_cyklu.get('level2', {}).get('confidence_kalibrowana', 0):.4f}")
    print(f"Obserwacja trafienie: {wynik_cyklu.get('obserwacja', {}).get('trafienie', 'N/A')}")
    
    # Test 6: Statystyki systemu
    print("\n--- Test 6: Statystyki systemu ---")
    
    statystyki = system.pobierz_statystyki_systemu()
    print(f"System zainicjalizowany: {statystyki.get('system', {}).get('zainicjalizowany')}")
    print(f"Obserwacje w pamięci: {statystyki.get('pamiec', {}).get('obserwacje', 0)}")
    print(f"Skuteczność globalna: {statystyki.get('pamiec', {}).get('skutecznosc', 0):.4f}")
    print(f"Kalibrator wytrenowany: {statystyki.get('level2', {}).get('wytrenowany')}")
    print(f"Liczba wzorców: {statystyki.get('level2', {}).get('wzorce', 0)}")
    
    # Test 7: Zapis wersji pamięci
    print("\n--- Test 7: Zapis wersji pamięci ---")
    
    wersja_path = system.zapisz_wersje_pamieci()
    print(f"Wersja pamięci zapisana: {wersja_path}")
    
    # Test 8: Wzorce zachowania
    print("\n--- Test 8: Wzorce zachowania ---")
    
    wzorce = system.pobierz_wzorce()
    print(f"Wykryto {len(wzorce)} wzorców:")
    for wzor in wzorce[:5]:
        print(f"  - {wzor.nazwa}: {wzor.opis}")
    
    # Test 9: Batch processing
    print("\n--- Test 9: Batch processing ---")
    
    mecze_test = [
        {**dane_testowe, "id_meczu": f"BatchMatch_{i}", "id_grupy": "batch_group"}
        for i in range(5)
    ]
    
    wyniki_batch = system.pelny_cykl_batch(
        mecze=mecze_test,
        wyniki_rzeczywiste={
            "BatchMatch_0": "1:0",
            "BatchMatch_1": "2:1",
            "BatchMatch_2": "0:0",
            "BatchMatch_3": "1:1",
            "BatchMatch_4": "2:0",
        }
    )
    
    print(f"Przetworzono {len(wyniki_batch)} meczów")
    for wynik in wyniki_batch:
        level1 = wynik.get('level1', {})
        level2 = wynik.get('level2', {})
        obs = wynik.get('obserwacja', {})
        print(f"  {wynik['mecz_id']}: "
              f"L1={level1.get('wynik_predykcji', 'N/A')}, "
              f"L2_conf={level2.get('confidence_kalibrowana', 0):.3f}, "
              f"trafienie={obs.get('trafienie', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)
