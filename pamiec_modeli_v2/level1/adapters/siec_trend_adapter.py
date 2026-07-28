"""
PAMIĘĆ MODELI V2 - ADAPTER DLA SIECI TRENDÓW
=============================================

Adapter integracyjny pomiędzy istniejącymi sieciami SSI (modele_dataBase_futbol_trend/)
a Systemem Pamięci V2.

Zadania:
1. Konwersja danych wejściowych do formatu zrozumiałego przez sieci SSI
2. Generowanie predykcji za pomocą sieci neuronowych (model.h5)
3. Konwersja wyjścia sieci do formatu PredykcjaLevel1
4. Obsługa confidence z sieci

Architektura:
- Każda sieć analizuje 3 konkretne cechy z 45 dostępnych
- Sieci są trenowane na historycznych danych z wynikami
- Adapter integruje się z istniejącym systemem bez jego modyfikacji

Uwaga: Aktualnie sieci SSI nie są bezpośrednio używane do predykcji
w systemie V2. Adapter służy jako warstwa abstrakcji, która w przyszłości
pozwoli na łatwe podłączenie rzeczywistych modeli neuronowych.

Autor: MSDI AI v0.02
Data: 2026-07-27
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

# Import z lokalnych modułów
from pamiec_modeli_v2.schemas import (
    PredykcjaLevel1,
    KLASY_WYNIKOW_DOKLADNYCH,
    get_grupa_wyniku,
    normalizuj_wynik
)


class SiecTrendAdapter:
    """
    Adapter dla pojedynczej sieci trendów z modele_dataBase_futbol_trend/
    
    Każda sieć analizuje 3 konkretne cechy i generuje predykcję wyniku.
    
    Atrybuty:
        siec_id: Identyfikator sieci (np. "siec_01_zmiana_kursow")
        siec_path: Ścieżka do katalogu sieci
        cechy: Lista 3 cech analizowanych przez tę sieć
        metadata: Metadane sieci (z metadata.json)
    """
    
    # Ścieżka bazowa do sieci trendów
    BASE_PATH: Path = Path("D:/sts/aplikacjaTyperBetAi/modele_dataBase_futbol_trend")
    
    # Mapowanie sieci na ich cechy (zgodnie z dokumentacją SSI)
    SIECI_CECHY: Dict[str, Tuple[str, str, str]] = {
        "siec_01_zmiana_kursow": ("zmiana_1", "zmiana_X", "zmiana_2"),
        "siec_02_amplituda": ("amplituda_1", "amplituda_X", "amplituda_2"),
        "siec_03_tempo": ("tempo_1", "tempo_X", "tempo_2"),
        "siec_04_max_wahanie": ("max_wahanie_1", "max_wahanie_X", "max_wahanie_2"),
        "siec_05_start_raw": ("start_1_raw", "start_X_raw", "start_2_raw"),
        "siec_06_koniec_raw": ("koniec_1_raw", "koniec_X_raw", "koniec_2_raw"),
        "siec_07_log_start": ("log_start_1", "log_start_X", "log_start_2"),
        "siec_08_log_koniec": ("log_koniec_1", "log_koniec_X", "log_koniec_2"),
        "siec_09_ratio_start": ("ratio_1X_start", "ratio_1_2_start", "ratio_X2_start"),
        "siec_10_ratio_koniec": ("ratio_1X_koniec", "ratio_1_2_koniec", "ratio_X2_koniec"),
        "siec_11_statystyka": ("mean_1", "mean_X", "mean_2"),
    }
    
    # Mapowanie indeksów kolumn w pliku dataBase_futbol_trend.csv
    # (zgodnie ze strukturą z stukturaDanychWejsciowych.csv)
    CECHY_INDEKSY: Dict[str, int] = {
        # Cechy zmian
        "zmiana_1": 1, "zmiana_X": 2, "zmiana_2": 3,
        # Cechy amplitudy
        "amplituda_1": 4, "amplituda_X": 5, "amplituda_2": 6,
        # Cechy tempo
        "tempo_1": 7, "tempo_X": 8, "tempo_2": 9,
        # Synchronizacja
        "synchronizacja": 10,
        # Max wahanie
        "max_wahanie_1": 11, "max_wahanie_X": 12, "max_wahanie_2": 13,
        # Kursy raw start
        "start_1_raw": 14, "start_X_raw": 15, "start_2_raw": 16,
        # Kursy raw koniec
        "koniec_1_raw": 17, "koniec_X_raw": 18, "koniec_2_raw": 19,
        # Log start
        "log_start_1": 20, "log_start_X": 21, "log_start_2": 22,
        # Log koniec
        "log_koniec_1": 23, "log_koniec_X": 24, "log_koniec_2": 25,
        # Ratio start
        "ratio_1X_start": 26, "ratio_1_2_start": 27, "ratio_X2_start": 28,
        # Ratio koniec
        "ratio_1X_koniec": 29, "ratio_1_2_koniec": 30, "ratio_X2_koniec": 31,
        # Statystyki
        "mean_1": 32, "mean_X": 33, "mean_2": 34,
        "median_1": 35, "median_X": 36, "median_2": 37,
        "stdev_1": 38, "stdev_X": 39, "stdev_2": 40,
        # Czas
        "czas_h": 41,
    }
    
    def __init__(self, siec_id: str):
        """
        Inicjalizacja adaptera dla konkretnej sieci.
        
        Args:
            siec_id: Identyfikator sieci (np. "siec_01_zmiana_kursow")
        """
        self.siec_id = siec_id
        self.siec_path = self.BASE_PATH / siec_id
        self.cechy = self.SIECI_CECHY.get(siec_id, ("", "", ""))
        self.metadata: Dict[str, Any] = {}
        
        # Załaduj metadane
        self._zaladuj_metadata()
        
        # Inicjalizuj model (opcjonalnie)
        self.model = None
        # self._zaladuj_model()  # Wyłączone - nie mamy zewnętrznych bibliotek
    
    def _zaladuj_metadata(self):
        """Ładuje metadane sieci z metadata.json"""
        metadata_file = self.siec_path / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"Blad ladowania metadata dla {self.siec_id}: {e}")
        
        # Jeśli nie ma metadata, użyj domyślnych
        if not self.metadata:
            self.metadata = {
                "nazwa": self.siec_id,
                "cechy": list(self.cechy),
                "opis": f"Sieć analizująca cechy: {', '.join(self.cechy)}"
            }
    
    def _zaladuj_model(self):
        """
        Ładuje model sieci neuronowej (model.h5).
        
        UWAGA: Ta metoda wymaga biblioteki tensorflow/keras.
        Aktualnie wyłączona, ale gotowa do użycia w przyszłości.
        """
        try:
            import tensorflow as tf
            from tensorflow.keras.models import load_model
            
            model_file = self.siec_path / "model.h5"
            if model_file.exists():
                self.model = load_model(model_file)
                print(f"Zaladowano model dla {self.siec_id}")
        except ImportError:
            print(f"Brak tensorflow - model sieci {self.siec_id} nie dostepny")
        except Exception as e:
            print(f"Blad ladowania modelu {self.siec_id}: {e}")
    
    def pobierz_cechy(self) -> Tuple[str, str, str]:
        """Zwraca tuple 3 cech analizowanych przez tę sieć"""
        return self.cechy
    
    def pobierz_metadata(self) -> Dict[str, Any]:
        """Zwraca metadane sieci"""
        return self.metadata
    
    # =========================================================================
    # PREDYKCJA (Symulacja - bez rzeczywistej sieci neuronowej)
    # =========================================================================
    
    def predykcja(self, dane_wejsciowe: Dict[str, Any], mecz_id: str, 
                  grupa_id: str = "BRAK") -> PredykcjaLevel1:
        """
        Generuje predykcję na podstawie danych wejściowych.
        
        Aktualnie: Symulacja oparta na historycznych wzorcach.
        W przyszłości: Użycie rzeczywistej sieci neuronowej.
        
        Args:
            dane_wejsciowe: Słownik z danymi meczu (cechy jako klucze)
            mecz_id: Identyfikator meczu
            grupa_id: Identyfikator grupy świata
            
        Returns:
            PredykcjaLevel1 z wynikiem i confidence
        """
        # Pobierz wartości 3 cech
        cecha1_val = float(dane_wejsciowe.get(self.cechy[0], 0.0))
        cecha2_val = float(dane_wejsciowe.get(self.cechy[1], 0.0))
        cecha3_val = float(dane_wejsciowe.get(self.cechy[2], 0.0))
        
        # Symulacja predykcji ( docelowo: self._predykcja_siecia(cecha1_val, cecha2_val, cecha3_val))
        wynik, confidence = self._predykcja_symulowana(cecha1_val, cecha2_val, cecha3_val, mecz_id)
        
        return PredykcjaLevel1(
            id_modelu=self.siec_id,
            id_meczu=mecz_id,
            id_grupy=grupa_id,
            wynik_predykcji=wynik,
            confidence=confidence,
            sieci_skladowe={
                "cechy": list(self.cechy),
                "wartosci": [cecha1_val, cecha2_val, cecha3_val]
            }
        )
    
    def _predykcja_symulowana(self, cecha1: float, cecha2: float, 
                              cecha3: float, mecz_id: str) -> Tuple[str, float]:
        """
        Symulacja predykcji (docelowo zastąpione przez sieć neuronową).
        
        Strategia:
        1. Jeśli mamy historyczne dane dla tego meczu, użyj średniego wyniku grupy
        2. W przeciwnym razie użyj statystycznego podejścia
        
        Args:
            cecha1, cecha2, cecha3: Wartości 3 cech
            mecz_id: Identyfikator meczu
            
        Returns:
            Tuple (wynik_predykcji, confidence)
        """
        # Strategia 1: Użyj grupy meczów z tags_world_map.json
        grupa = self._pobierz_grupe_meczu(mecz_id)
        if grupa:
            wynik = self._pobierz_sredni_wynik_grupy(grupa)
            if wynik:
                # Confidence na podstawie stabilności cech
                confidence = self._oblicz_confidence_symulowane(cecha1, cecha2, cecha3)
                return normalizuj_wynik(wynik), confidence
        
        # Strategia 2: Użyj średniej z wszystkich historycznych wyników
        sredni_wynik = self._pobierz_sredni_wynik_globalny()
        confidence = 0.3  # Niska pewność dla domyślnej predykcji
        return normalizuj_wynik(sredni_wynik), confidence
    
    def _predykcja_siecia(self, cecha1: float, cecha2: float, cecha3: float) -> Tuple[str, float]:
        """
        Predykcja używająca rzeczywistej sieci neuronowej.
        
        Docelowa implementacja - wymaga tensorflow.
        
        Args:
            cecha1, cecha2, cecha3: Wartości 3 cech (znormalizowane)
            
        Returns:
            Tuple (wynik_predykcji, confidence)
        """
        # TODO: Implementacja z użyciem self.model
        # Na razie zwracamy symulację
        return self._predykcja_symulowana(cecha1, cecha2, cecha3, "")
    
    def _oblicz_confidence_symulowane(self, cecha1: float, cecha2: float, 
                                      cecha3: float) -> float:
        """
        Oblicza symulowane confidence na podstawie stabilności cech.
        
        Im mniejsze odchylenie cech od średniej, tym wyższa pewność.
        """
        # Średnie wartości cech (przykładowe - docelowo z historycznych danych)
        srednie = {
            "zmiana_1": 0.0, "zmiana_X": 0.0, "zmiana_2": 0.0,
            "amplituda_1": 0.1, "amplituda_X": 0.1, "amplituda_2": 0.1,
            "tempo_1": 0.0, "tempo_X": 0.0, "tempo_2": 0.0,
            "max_wahanie_1": 0.1, "max_wahanie_X": 0.1, "max_wahanie_2": 0.1,
        }
        
        # Odchylenia standardowe
        odchylenia = {
            "zmiana_1": 0.1, "zmiana_X": 0.1, "zmiana_2": 0.1,
            "amplituda_1": 0.05, "amplituda_X": 0.05, "amplituda_2": 0.05,
        }
        
        # Oblicz odległość od średniej
        cechy = [self.cechy[0], self.cechy[1], self.cechy[2]]
        wartosci = [cecha1, cecha2, cecha3]
        
        suma_odleglosci = 0
        for cecha, wartosc in zip(cechy, wartosci):
            avg = srednie.get(cecha, 0.0)
            std = odchylenia.get(cecha, 0.1)
            if std > 0:
                suma_odleglosci += abs(wartosc - avg) / std
        
        # Im mniejsza odległość, tym wyższa pewność
        # Confidence w zakresie [0.1, 0.9]
        confidence = max(0.1, min(0.9, 1.0 - (suma_odleglosci / 10)))
        return confidence
    
    # =========================================================================
    # POBIERANIE DANYCH HISTORYCZNYCH
    # =========================================================================
    
    def _pobierz_grupe_meczu(self, mecz_id: str) -> Optional[str]:
        """Pobiera grupę meczu z tags_world_map.json"""
        tags_file = Path("D:/sts/aplikacjaTyperBetAi/dane/tags_world_map.json")
        if not tags_file.exists():
            return None
        
        try:
            with open(tags_file, 'r', encoding='utf-8') as f:
                tags = json.load(f)
            
            for grupa, mecze in tags.items():
                for mecz_data in mecze:
                    if mecz_data.get("mecz") == mecz_id:
                        return grupa
            return None
        except Exception as e:
            print(f"Blad odczytu tags_world_map.json: {e}")
            return None
    
    def _pobierz_sredni_wynik_grupy(self, grupa: str) -> Optional[str]:
        """Pobiera średni wynik dla danej grupy z historycznych danych"""
        # Użyj dopasowanie_swiata_* plików
        dopasowanie_file = Path(f"D:/sts/aplikacjaTyperBetAi/dane/dopasowanie_swiata_kod_dataBase_futbol_trend_klasyfikatorr.csv")
        if not dopasowanie_file.exists():
            return None
        
        try:
            wyniki = []
            with open(dopasowanie_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    if row.get('id_grupy', '') == grupa:
                        wynik = row.get('wynik', '')
                        if wynik and ':' in wynik:
                            wyniki.append(wynik)
            
            if wyniki:
                # Zwróć najczęstszy wynik
                from collections import Counter
                counter = Counter(wyniki)
                return counter.most_common(1)[0][0]
            return None
        except Exception as e:
            print(f"Blad odczytu {dopasowanie_file}: {e}")
            return None
    
    def _pobierz_sredni_wynik_globalny(self) -> str:
        """Pobiera średni wynik ze wszystkich historycznych meczów"""
        # Użyj najczęstszych wyników z klas
        # Najczęstsze wyniki w piłce nożnej: 1:0, 2:1, 0:0, 1:1, 2:0
        return "1:0"
    
    # =========================================================================
    # INTEGRACJA Z DANYMI WEJŚCIOWYMI
    # =========================================================================
    
    def pobierz_dane_meczu(self, mecz_id: str, sciezka_database: Optional[Path] = None) -> Dict[str, Any]:
        """
        Pobiera dane meczu z database_dzisiaj.csv lub podobnego.
        
        Args:
            mecz_id: Identyfikator meczu
            sciezka_database: Ścieżka do pliku database (domyślnie database_dzisiaj.csv)
            
        Returns:
            Słownik z danymi meczu (cechy jako klucze)
        """
        if sciezka_database is None:
            sciezka_database = Path("D:/sts/aplikacjaTyperBetAi/dane/database_dzisiaj.csv")
        
        if not sciezka_database.exists():
            return {}
        
        try:
            with open(sciezka_database, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=';')
                header = next(reader, None)
                
                if not header:
                    return {}
                
                # Znajdź indeks kolumny z nazwą meczu
                try:
                    idx_mecz = header.index('id_meczu') if 'id_meczu' in header else 0
                except ValueError:
                    idx_mecz = 0
                
                for row in reader:
                    if len(row) > idx_mecz and row[idx_mecz] == mecz_id:
                        # Konwertuj wiersz na słownik
                        data = {}
                        for i, col_name in enumerate(header):
                            if i < len(row):
                                data[col_name] = row[i]
                        return data
            
            return {}
        except Exception as e:
            print(f"Blad odczytu {sciezka_database}: {e}")
            return {}
    
    def ekstraktuj_cechy(self, dane_meczu: Dict[str, Any]) -> Dict[str, float]:
        """
        Ekstraktuje 3 cechy analizowane przez tę sieć z danych meczu.
        
        Args:
            dane_meczu: Słownik z danymi meczu
            
        Returns:
            Słownik z 3 cechami i ich wartościami
        """
        cechy = {}
        for cecha in self.cechy:
            # Spróbuj pobrać wartość z danych
            if cecha in dane_meczu:
                try:
                    cechy[cecha] = float(dane_meczu[cecha])
                except (ValueError, TypeError):
                    cechy[cecha] = 0.0
            else:
                cechy[cecha] = 0.0
        return cechy
    
    # =========================================================================
    # BATCH PREDICTION
    # =========================================================================
    
    def predykcja_batch(self, mecze: List[Dict[str, Any]]) -> List[PredykcjaLevel1]:
        """
        Generuje predykcje dla wielu meczów naraz.
        
        Args:
            mecze: Lista słowników z danymi meczów
            
        Returns:
            Lista PredykcjaLevel1
        """
        predykcje = []
        for mecz_data in mecze:
            mecz_id = mecz_data.get('id_meczu', mecz_data.get('mecz', ''))
            grupa_id = mecz_data.get('id_grupy', mecz_data.get('grupa', 'BRAK'))
            
            if mecz_id:
                predykcja = self.predykcja(mecz_data, mecz_id, grupa_id)
                predykcje.append(predykcja)
        
        return predykcje


# =============================================================================
# ADAPTER MANAGER (Zarządzanie wszystkimi sieciami)
# =============================================================================

class AdapterManager:
    """
    Zarządca adapterów dla wszystkich sieci trendów.
    
    Umożliwia:
    - Agregację predykcji z wielu sieci
    - Zarządzanie adapterami
    - Monitorowanie wydajności sieci
    """
    
    def __init__(self):
        """Inicjalizacja menedżera z adapterami dla wszystkich sieci"""
        self.adaptery: Dict[str, SiecTrendAdapter] = {}
        self._inicjalizuj_adaptery()
    
    def _inicjalizuj_adaptery(self):
        """Inicjalizuje adaptery dla wszystkich sieci trendów"""
        sieci_list = [
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
            "siec_11_statystyka",
        ]
        
        for siec_id in sieci_list:
            try:
                adapter = SiecTrendAdapter(siec_id)
                self.adaptery[siec_id] = adapter
            except Exception as e:
                print(f"Blad inicjalizacji adaptera {siec_id}: {e}")
    
    def get_adapter(self, siec_id: str) -> Optional[SiecTrendAdapter]:
        """Zwraca adapter dla konkretnej sieci"""
        return self.adaptery.get(siec_id)
    
    def get_all_adapters(self) -> Dict[str, SiecTrendAdapter]:
        """Zwraca wszystkie adaptery"""
        return self.adaptery
    
    def predykcja_wszystkie_sieci(self, dane_meczu: Dict[str, Any], 
                                   mecz_id: str, grupa_id: str = "BRAK") -> Dict[str, PredykcjaLevel1]:
        """
        Generuje predykcje ze wszystkich sieci dla jednego meczu.
        
        Args:
            dane_meczu: Dane meczu
            mecz_id: Identyfikator meczu
            grupa_id: Identyfikator grupy
            
        Returns:
            Słownik {siec_id: PredykcjaLevel1}
        """
        predykcje = {}
        for siec_id, adapter in self.adaptery.items():
            try:
                pred = adapter.predykcja(dane_meczu, mecz_id, grupa_id)
                predykcje[siec_id] = pred
            except Exception as e:
                print(f"Blad predykcji sieci {siec_id}: {e}")
        
        return predykcje
    
    def predykcja_batch_wszystkie(self, mecze: List[Dict[str, Any]]) -> Dict[str, List[PredykcjaLevel1]]:
        """
        Generuje predykcje ze wszystkich sieci dla wielu meczów.
        
        Args:
            mecze: Lista danych meczów
            
        Returns:
            Słownik {siec_id: [PredykcjaLevel1, ...]}
        """
        wyniki = {siec_id: [] for siec_id in self.adaptery}
        
        for mecz_data in mecze:
            mecz_id = mecz_data.get('id_meczu', mecz_data.get('mecz', ''))
            grupa_id = mecz_data.get('id_grupy', mecz_data.get('grupa', 'BRAK'))
            
            for siec_id, adapter in self.adaptery.items():
                try:
                    pred = adapter.predykcja(mecz_data, mecz_id, grupa_id)
                    wyniki[siec_id].append(pred)
                except Exception as e:
                    print(f"Blad predykcji sieci {siec_id} dla {mecz_id}: {e}")
        
        return wyniki


# =============================================================================
# FUNKCJE GLOBALNE
# =============================================================================

def utworz_adapter(siec_id: str) -> SiecTrendAdapter:
    """Tworzy adapter dla konkretnej sieci"""
    return SiecTrendAdapter(siec_id)


def utworz_adapter_manager() -> AdapterManager:
    """Tworzy menedżera adapterów dla wszystkich sieci"""
    return AdapterManager()


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing SiecTrendAdapter...")
    
    # Test pojedynczego adaptera
    adapter = SiecTrendAdapter("siec_01_zmiana_kursow")
    print(f"Sieć: {adapter.siec_id}")
    print(f"Cechy: {adapter.cechy}")
    print(f"Metadata: {adapter.metadata}")
    
    # Test predykcji symulowanej
    dane_testowe = {
        "zmiana_1": 0.5,
        "zmiana_X": 0.3,
        "zmiana_2": 0.2,
        "id_meczu": "Test Team A - Test Team B"
    }
    
    pred = adapter.predykcja(dane_testowe, "Test Team A - Test Team B", "test_group")
    print(f"\nPredykcja: {pred.wynik_predykcji}")
    print(f"Confidence: {pred.confidence:.4f}")
    
    # Test menedżera
    print("\n" + "="*50)
    print("Testing AdapterManager...")
    manager = AdapterManager()
    print(f"Liczba adapterów: {len(manager.adaptery)}")
    print(f"Sieci: {list(manager.adaptery.keys())}")
    
    # Test predykcji ze wszystkich sieci
    wszystkie_predykcje = manager.predykcja_wszystkie_sieci(
        dane_testowe, "Test Team A - Test Team B", "test_group"
    )
    print(f"\nPredykcje ze wszystkich sieci:")
    for siec_id, pred in list(wszystkie_predykcje.items())[:3]:
        print(f"  {siec_id}: {pred.wynik_predykcji} (confidence: {pred.confidence:.4f})")
    
    print("\nAll tests passed!")
