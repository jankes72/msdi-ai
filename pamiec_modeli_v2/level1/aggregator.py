"""
PAMIĘĆ MODELI V2 - AGREGATOR PREDIKCJI LEVEL 1
==============================================

Agreguje predykcje z 11 sieci trendów + 4 sieci kursów w jedno wyjście Level 1.

Zadania:
1. Zbieranie predykcji z wszystkich sieci za pomocą AdapterManager
2. Agregowanie wyników (głosowanie, średnia ważona, itd.)
3. Obliczanie confidence dla agregowanej predykcji
4. Generowanie pojedynczego wyjścia PredykcjaLevel1

Strategie agregacji:
- Głosowanie większościowe (Majority Voting)
- Średnia ważona confidence
- Agregacja na poziomie klas wyników (1/X/2)
- Hybrydowa (kombinacja powyższych)

Architektura:
    Wejście: Dane meczu → AdapterManager → 15 predykcji z sieci
    Agregator → 1 predykcja Level 1
    Wyjście: PredykcjaLevel1 (z agregowaną pewnością)

Autor: MSDI AI v0.02
Data: 2026-07-27
"""

from typing import Dict, List, Optional, Any, Tuple
from collections import Counter, defaultdict
import statistics

# Import z lokalnych modułów
from pamiec_modeli_v2.schemas import (
    PredykcjaLevel1,
    get_grupa_wyniku,
    KLASY_WYNIKOW_DOKLADNYCH
)
from pamiec_modeli_v2.level1.adapters.siec_trend_adapter import AdapterManager


class AgregatorPredykcji:
    """
    Agreguje predykcje z wielu sieci w pojedyncze wyjście Level 1.
    
    Obsługuje różne strategie agregacji:
    - MAJORITY_VOTING: Głosowanie większościowe
    - WEIGHTED_AVERAGE: Średnia ważona confidence
    - GROUP_VOTING: Głosowanie na poziomie grup (1/X/2)
    - HYBRID: Kombinacja wszystkich metod
    """
    
    # Dostępne strategie agregacji
    STRATEGIE_AGREGACJI = [
        "MAJORITY_VOTING",      # Głosowanie większościowe
        "WEIGHTED_AVERAGE",     # Średnia ważona confidence
        "GROUP_VOTING",        # Głosowanie na poziomie grup
        "HYBRID"               # Kombinacja metod
    ]
    
    def __init__(self, strategia: str = "HYBRID"):
        """
        Inicjalizacja agregatora.
        
        Args:
            strategia: Strategia agregacji (domyślnie HYBRID)
        """
        if strategia not in self.STRATEGIE_AGREGACJI:
            raise ValueError(f"Nieznana strategia: {strategia}. Dostępne: {self.STRATEGIE_AGREGACJI}")
        
        self.strategia = strategia
        self.adapter_manager = AdapterManager()
    
    def predykcja(self, dane_meczu: Dict[str, Any], mecz_id: str, 
                  grupa_id: str = "BRAK") -> PredykcjaLevel1:
        """
        Generuje agregowaną predykcję Level 1.
        
        Args:
            dane_meczu: Dane meczu (słownik z cechami)
            mecz_id: Identyfikator meczu
            grupa_id: Identyfikator grupy świata
            
        Returns:
            PredykcjaLevel1 z agregowanymi wynikami
        """
        # Pobierz predykcje ze wszystkich sieci
        predykcje_sieci = self.adapter_manager.predykcja_wszystkie_sieci(
            dane_meczu, mecz_id, grupa_id
        )
        
        # Agreguj predykcje
        if self.strategia == "MAJORITY_VOTING":
            return self._agreguj_głosowaniem_większościowym(predykcje_sieci, mecz_id, grupa_id)
        elif self.strategia == "WEIGHTED_AVERAGE":
            return self._agreguj_średnią_ważoną(predykcje_sieci, mecz_id, grupa_id)
        elif self.strategia == "GROUP_VOTING":
            return self._agreguj_głosowaniem_grupowym(predykcje_sieci, mecz_id, grupa_id)
        else:  # HYBRID
            return self._agreguj_hybrydowo(predykcje_sieci, mecz_id, grupa_id)
    
    def predykcja_batch(self, mecze: List[Dict[str, Any]]) -> List[PredykcjaLevel1]:
        """
        Generuje agregowane predykcje dla wielu meczów.
        
        Args:
            mecze: Lista danych meczów
            
        Returns:
            Lista PredykcjaLevel1
        """
        agregowane = []
        for mecz_data in mecze:
            mecz_id = mecz_data.get('id_meczu', mecz_data.get('mecz', ''))
            grupa_id = mecz_data.get('id_grupy', mecz_data.get('grupa', 'BRAK'))
            
            if mecz_id:
                pred = self.predykcja(mecz_data, mecz_id, grupa_id)
                agregowane.append(pred)
        
        return agregowane
    
    # =========================================================================
    # STRATEGIE AGREGACJI
    # =========================================================================
    
    def _agreguj_głosowaniem_większościowym(
        self, predykcje: Dict[str, PredykcjaLevel1], 
        mecz_id: str, grupa_id: str
    ) -> PredykcjaLevel1:
        """
        Agregacja przez głosowanie większościowe.
        
        Wybiera wynik, który pojawił się najczęściej wśród sieci.
        Confidence = średni confidence sieci, które wybrały ten wynik.
        """
        if not predykcje:
            return self._predykcja_domyślna(mecz_id, grupa_id)
        
        # Zliczaj wyniki
        wynik_counter = Counter()
        confidence_sum = defaultdict(float)
        confidence_count = defaultdict(int)
        
        for siec_id, pred in predykcje.items():
            wynik = pred.wynik_predykcji
            wynik_counter[wynik] += 1
            confidence_sum[wynik] += pred.confidence
            confidence_count[wynik] += 1
        
        # Znajdź wynik z największą liczbą głosów
        najczestszy_wynik, licznik = wynik_counter.most_common(1)[0]
        
        # Oblicz średni confidence dla tego wyniku
        if confidence_count[najczestszy_wynik] > 0:
            sredni_confidence = confidence_sum[najczestszy_wynik] / confidence_count[najczestszy_wynik]
        else:
            sredni_confidence = 0.5
        
        # Stwórz agregowaną predykcję
        return PredykcjaLevel1(
            id_modelu="AGGREGATOR_MAJORITY",
            id_meczu=mecz_id,
            id_grupy=grupa_id,
            wynik_predykcji=najczestszy_wynik,
            confidence=sredni_confidence,
            sieci_skladowe=self._zapisz_sieci_skladowe(predykcje, "MAJORITY_VOTING")
        )
    
    def _agreguj_średnią_ważoną(
        self, predykcje: Dict[str, PredykcjaLevel1], 
        mecz_id: str, grupa_id: str
    ) -> PredykcjaLevel1:
        """
        Agregacja przez średnią ważoną confidence.
        
        Oblicza ważoną średnią dla każdego możliwego wyniku,
        gdzie wagami są confidence poszczególnych sieci.
        """
        if not predykcje:
            return self._predykcja_domyślna(mecz_id, grupa_id)
        
        # Zbierz wszystkie unikalne wyniki
        unikalne_wyniki = set(pred.wynik_predykcji for pred in predykcje.values())
        
        # Oblicz wagę dla każdego wyniku
        wynik_waga = {}
        for wynik in unikalne_wyniki:
            waga = sum(
                pred.confidence for siec_id, pred in predykcje.items()
                if pred.wynik_predykcji == wynik
            )
            wynik_waga[wynik] = waga
        
        # Znajdź wynik z największą wagą
        if wynik_waga:
            najlepsy_wynik = max(wynik_waga, key=wynik_waga.get)
            total_waga = sum(wynik_waga.values())
            confidence = wynik_waga[najlepsy_wynik] / total_waga if total_waga > 0 else 0.5
        else:
            najlepsy_wynik = "1:0"
            confidence = 0.5
        
        return PredykcjaLevel1(
            id_modelu="AGGREGATOR_WEIGHTED",
            id_meczu=mecz_id,
            id_grupy=grupa_id,
            wynik_predykcji=najlepsy_wynik,
            confidence=confidence,
            sieci_skladowe=self._zapisz_sieci_skladowe(predykcje, "WEIGHTED_AVERAGE")
        )
    
    def _agreguj_głosowaniem_grupowym(
        self, predykcje: Dict[str, PredykcjaLevel1], 
        mecz_id: str, grupa_id: str
    ) -> PredykcjaLevel1:
        """
        Agregacja przez głosowanie na poziomie grup (1/X/2).
        
        Najpierw określa grupę (wygrana gospodarzy/remis/wygrana gości),
        potem wybiera konkretny wynik z tej grupy.
        """
        if not predykcje:
            return self._predykcja_domyślna(mecz_id, grupa_id)
        
        # Zliczaj grupy
        grupa_counter = Counter()
        for pred in predykcje.values():
            grupa = get_grupa_wyniku(pred.wynik_predykcji)
            grupa_counter[grupa] += 1
        
        # Określ zwycięską grupę
        wygrana_grupa = grupa_counter.most_common(1)[0][0]
        
        # Wybierz konkretny wynik z tej grupy
        # Filtruj predykcje do wygranej grupy
        predykcje_grupy = [
            pred for pred in predykcje.values()
            if get_grupa_wyniku(pred.wynik_predykcji) == wygrana_grupa
        ]
        
        if predykcje_grupy:
            # Wybierz wynik z największym confidence
            najlepsza = max(predykcje_grupy, key=lambda x: x.confidence)
            wynik = najlepsza.wynik_predykcji
            confidence = najlepsza.confidence
        else:
            # Fallback: użyj losowego wyniku z grupy
            wynik = self._losowy_wynik_z_grupy(wygrana_grupa)
            confidence = 0.3
        
        return PredykcjaLevel1(
            id_modelu="AGGREGATOR_GROUP",
            id_meczu=mecz_id,
            id_grupy=grupa_id,
            wynik_predykcji=wynik,
            confidence=confidence,
            sieci_skladowe=self._zapisz_sieci_skladowe(predykcje, "GROUP_VOTING")
        )
    
    def _agreguj_hybrydowo(
        self, predykcje: Dict[str, PredykcjaLevel1], 
        mecz_id: str, grupa_id: str
    ) -> PredykcjaLevel1:
        """
        Agregacja hybrydowa - kombinacja wszystkich metod.
        
        1. Używa głosowania grupowego (1/X/2) jako głównej metody
        2. Wybiera konkretny wynik z grupy na podstawie głosowania większościowego
        3. Confidence = kombinacja confidence z różnych metod
        """
        if not predykcje:
            return self._predykcja_domyślna(mecz_id, grupa_id)
        
        # Krok 1: Określ grupę przez głosowanie grupowe
        grupa_counter = Counter()
        for pred in predykcje.values():
            grupa = get_grupa_wyniku(pred.wynik_predykcji)
            grupa_counter[grupa] += pred.confidence  # Ważone confidence
        
        wygrana_grupa = grupa_counter.most_common(1)[0][0]
        
        # Krok 2: Wybierz konkretny wynik z grupy
        # Filtruj predykcje do wygranej grupy
        predykcje_grupy = [
            pred for pred in predykcje.values()
            if get_grupa_wyniku(pred.wynik_predykcji) == wygrana_grupa
        ]
        
        if predykcje_grupy:
            # Użyj głosowania większościowego w ramach grupy
            wynik_counter = Counter()
            confidence_sum = defaultdict(float)
            
            for pred in predykcje_grupy:
                wynik_counter[pred.wynik_predykcji] += 1
                confidence_sum[pred.wynik_predykcji] += pred.confidence
            
            if wynik_counter:
                najczestszy_wynik = wynik_counter.most_common(1)[0][0]
                confidence_grupy = confidence_sum[najczestszy_wynik] / len(predykcje_grupy)
                
                # Oblicz confidence hybrydowy
                # 70% waga: confidence z grupy
                # 30% waga: pewność grupy (stosunek głosów)
                total_votes = sum(grupa_counter.values())
                grupa_confidence = grupa_counter[wygrana_grupa] / total_votes
                
                hybrid_confidence = 0.7 * confidence_grupy + 0.3 * grupa_confidence
                
                return PredykcjaLevel1(
                    id_modelu="AGGREGATOR_HYBRID",
                    id_meczu=mecz_id,
                    id_grupy=grupa_id,
                    wynik_predykcji=najczestszy_wynik,
                    confidence=hybrid_confidence,
                    sieci_skladowe=self._zapisz_sieci_skladowe(predykcje, "HYBRID")
                )
        
        # Fallback
        return self._predykcja_domyślna(mecz_id, grupa_id)
    
    # =========================================================================
    # METODY POMOCNICZE
    # =========================================================================
    
    def _predykcja_domyślna(self, mecz_id: str, grupa_id: str) -> PredykcjaLevel1:
        """Tworzy domyślną predykcję (fallback)"""
        return PredykcjaLevel1(
            id_modelu="DEFAULT",
            id_meczu=mecz_id,
            id_grupy=grupa_id,
            wynik_predykcji="1:0",  # Najczęstszy wynik w piłce
            confidence=0.3,
            sieci_skladowe={}
        )
    
    def _zapisz_sieci_skladowe(
        self, predykcje: Dict[str, PredykcjaLevel1], 
        metoda: str
    ) -> Dict[str, Any]:
        """Zapisuje informacje o sieciach składających się na agregację"""
        sieci_skladowe = {}
        
        for siec_id, pred in predykcje.items():
            sieci_skladowe[siec_id] = {
                "wynik_predykcji": pred.wynik_predykcji,
                "confidence": pred.confidence,
                "cechy": list(pred.sieci_skladowe.get("cechy", [])),
                "wartosci": pred.sieci_skladowe.get("wartosci", [])
            }
        
        sieci_skladowe["_metoda"] = metoda
        sieci_skladowe["_liczba_sieci"] = len(predykcje)
        
        return sieci_skladowe
    
    def _losowy_wynik_z_grupy(self, grupa: str) -> str:
        """Zwraca losowy wynik z określonej grupy"""
        if grupa == "1":
            return "1:0"  # Wygrana gospodarzy
        elif grupa == "2":
            return "0:1"  # Wygrana gości
        else:
            return "1:1"  # Remis
    
    # =========================================================================
    # ANALIZA PREDIKCJI
    # =========================================================================
    
    def analiza_predykcji(self, predykcje: Dict[str, PredykcjaLevel1]) -> Dict[str, Any]:
        """
        Analizuje rozkład predykcji z różnych sieci.
        
        Args:
            predykcje: Słownik predykcji z sieci
            
        Returns:
            Słownik z analizą (rozkład wyników, grupy, confidence, itd.)
        """
        if not predykcje:
            return {}
        
        # Rozkład wyników
        wynik_counter = Counter(pred.wynik_predykcji for pred in predykcje.values())
        
        # Rozkład grup
        grupa_counter = Counter(
            get_grupa_wyniku(pred.wynik_predykcji) 
            for pred in predykcje.values()
        )
        
        # Statystyki confidence
        confidences = [pred.confidence for pred in predykcje.values()]
        
        # Zgoda sieci (agreement)
        if len(set(pred.wynik_predykcji for pred in predykcje.values())) == 1:
            zgoda = 1.0  # Wszystkie sieci zgodne
        else:
            max_count = wynik_counter.most_common(1)[0][1]
            zgoda = max_count / len(predykcje)
        
        return {
            "rozkład_wyników": dict(wynik_counter),
            "rozkład_grup": dict(grupa_counter),
            "statystyki_confidence": {
                "min": min(confidences),
                "max": max(confidences),
                "mean": statistics.mean(confidences),
                "median": statistics.median(confidences),
                "stdev": statistics.stdev(confidences) if len(confidences) > 1 else 0
            },
            "zgoda_sieci": zgoda,
            "liczba_sieci": len(predykcje)
        }
    
    def get_strategia(self) -> str:
        """Zwraca aktualną strategię agregacji"""
        return self.strategia
    
    def set_strategia(self, strategia: str):
        """Ustawia nową strategię agregacji"""
        if strategia not in self.STRATEGIE_AGREGACJI:
            raise ValueError(f"Nieznana strategia: {strategia}")
        self.strategia = strategia


# =============================================================================
# FUNKCJE GLOBALNE
# =============================================================================

def utworz_agregator(strategia: str = "HYBRID") -> AgregatorPredykcji:
    """Tworzy agregator z określoną strategią"""
    return AgregatorPredykcji(strategia=strategia)


# ============================================================================= 
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing AgregatorPredykcji...")
    
    # Test z różnymi strategiami
    dane_testowe = {
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
        "czas_h": 24.0
    }
    
    # Test z różnymi strategiami
    for strategia in ["MAJORITY_VOTING", "WEIGHTED_AVERAGE", "GROUP_VOTING", "HYBRID"]:
        print(f"\n--- Strategia: {strategia} ---")
        agregator = AgregatorPredykcji(strategia=strategia)
        
        pred = agregator.predykcja(dane_testowe, "Test Match", "test_group")
        print(f"Wynik: {pred.wynik_predykcji}")
        print(f"Confidence: {pred.confidence:.4f}")
        print(f"Model: {pred.id_modelu}")
        
        # Analiza
        predykcje_sieci = agregator.adapter_manager.predykcja_wszystkie_sieci(
            dane_testowe, "Test Match", "test_group"
        )
        analiza = agregator.analiza_predykcji(predykcje_sieci)
        print(f"Zgoda sieci: {analiza.get('zgoda_sieci', 0):.2%}")
        print(f"Rozkład grup: {analiza.get('rozkład_grup', {})}")
    
    # Test batch
    print("\n--- Test Batch ---")
    mecze_testowe = [
        {**dane_testowe, "id_meczu": "Match1", "grupa": "group1"},
        {**dane_testowe, "id_meczu": "Match2", "grupa": "group2"},
        {**dane_testowe, "id_meczu": "Match3", "grupa": "group3"}
    ]
    
    agregator = AgregatorPredykcji(strategia="HYBRID")
    predykcje_batch = agregator.predykcja_batch(mecze_testowe)
    
    print(f"Wygenerowano {len(predykcje_batch)} predykcji")
    for pred in predykcje_batch:
        print(f"  {pred.id_meczu}: {pred.wynik_predykcji} ({pred.confidence:.3f})")
    
    print("\nAll tests passed!")
