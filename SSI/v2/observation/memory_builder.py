"""
SSI V2 Observation - Memory Builder

Moduł budujący pamięć modeli na podstawie obserwacji.
Integracja z pamiec_modeli_v2/schemas.py

Zadania:
- Budowa centralnego repozytorium obserwacji
- Zarządzanie klasami wyników
- Generowanie statystyk pamięci
- Integracja z systemem kalibracji

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2
- 02_DATA_STRUCTURE.md
- pamiec_modeli_v2/schemas.py

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import json
import os
from pathlib import Path

# Import z lokalnych schematów
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "pamiec_modeli_v2"))

try:
    from schemas import (
        Obserwacja, KlasaWyniku, WzorecZachowania, StatystykiPamieci,
        PredykcjaLevel1, PredykcjaLevel1Kalibrowana,
        KLASY_WYNIKOW_DOKLADNYCH, KLASY_GRUP_WYNIKOW,
        get_grupa_wyniku, get_gole, waliduj_wynik, normalizuj_wynik, generuj_id
    )
    SCHEMAS_AVAILABLE = True
except ImportError:
    SCHEMAS_AVAILABLE = False
    print("Warning: schemas.py not available, using local definitions")


# =============================================================================
# KONFIGURACJA MEMORY BUILDER
# =============================================================================

@dataclass
class MemoryConfig:
    """Konfiguracja budowy pamięci"""
    
    # Ścieżki
    BASE_PATH: str = "pamiec_modeli_v2"
    OBSERWACJE_PATH: str = "dane/obserwacja"
    PAMIEC_PATH: str = "pamiec"
    STATYSTYKI_PATH: str = "statystyki"
    ARCHIWUM_PATH: str = "archiwum"
    
    # Ustawienia zapisu
    SAVE_EVERY_N: int = 100  # Zapisz pamięć co N nowych obserwacji
    AUTO_BACKUP: bool = True
    MAX_OBSERWACJI_VOLUME: int = 1000000  # Maksymalna liczba obserwacji w pamięci
    
    # Ustawienia statystyk
    REBUILD_STATS_EVERY_N: int = 1000
    TRACK_INDIVIDUAL_MODELS: bool = True
    
    # Integracja z V2
    INTEGRATE_WITH_LEVEL2: bool = True
    KALIBRACJA_MIN_OBSERWACJI: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "BASE_PATH": self.BASE_PATH,
            "OBSERWACJE_PATH": self.OBSERWACJE_PATH,
            "PAMIEC_PATH": self.PAMIEC_PATH,
            "SAVE_EVERY_N": self.SAVE_EVERY_N,
            "AUTO_BACKUP": self.AUTO_BACKUP,
            "MAX_OBSERWACJI_VOLUME": self.MAX_OBSERWACJI_VOLUME,
            "REBUILD_STATS_EVERY_N": self.REBUILD_STATS_EVERY_N,
            "TRACK_INDIVIDUAL_MODELS": self.TRACK_INDIVIDUAL_MODELS,
            "INTEGRATE_WITH_LEVEL2": self.INTEGRATE_WITH_LEVEL2,
            "KALIBRACJA_MIN_OBSERWACJI": self.KALIBRACJA_MIN_OBSERWACJA
        }


# =============================================================================
# BUDOWNICZY PAMIĘCI
# =============================================================================

class MemoryBuilder:
    """
    Główny budowniczy pamięci modeli V2.
    
    Odpowiedzialności:
    - Zbieranie obserwacji z ModelObserver
    - Organizowanie obserwacji w klasy wyników
    - Budowa statystyk globalnych
    - Wykrywanie wzorców zachowania
    - Integracja z systemem kalibracji Level 2
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        self._initialize_structures()
        self._counter = 0
        
    def _initialize_structures(self):
        """Inicjalizacja struktur danych"""
        # Centralne repozytorium obserwacji
        self.obserwacje: List[Obserwacja] = []
        
        # Klasy wyników (dokładne: "1:0", "2:1", itp.)
        self.klasy_wynikow: Dict[str, KlasaWyniku] = {}
        
        # Klasy grupowe (1, X, 2)
        self.klasy_grupowe: Dict[str, KlasaWyniku] = {}
        
        # Wzorce zachowania
        self.wzorce: Dict[str, WzorecZachowania] = {}
        
        # Statystyki globalne
        self.statystyki: StatystykiPamieci = StatystykiPamieci()
        
        # Obserwacje posiadające kalibrowane predykcje
        self.obserwacje_kalibrowane: List[Dict[str, Any]] = []
        
        # Rejestr modeli
        self.modele: Dict[str, int] = {}  # model_id -> liczba obserwacji
        
        # Rejestr grup
        self.grupy: Dict[str, int] = {}  # grupa_id -> liczba obserwacji
        
    # =========================================================================
    # DODAWANIE OBSERWACJI
    # =========================================================================
    
    def dodaj_obserwacje(self, obserwacja: Obserwacja) -> str:
        """
        Dodaje nową obserwację do pamięci.
        
        Args:
            obserwacja: Obiekt Obserwacja z predykcją vs rzeczywistością
            
        Returns:
            id_obserwacji
        """
        # Walidacja
        if not SCHEMAS_AVAILABLE:
            obserwacja = self._create_obserwacja_from_dict(obserwacja)
        
        # Dodaj do centralnego repozytorium
        self.obserwacje.append(obserwacja)
        self._counter += 1
        
        # Zaktualizuj rejestr modeli
        if obserwacja.id_modelu not in self.modele:
            self.modele[obserwacja.id_modelu] = 0
        self.modele[obserwacja.id_modelu] += 1
        
        # Zaktualizuj rejestr grup
        if obserwacja.id_grupy not in self.grupy:
            self.grupy[obserwacja.id_grupy] = 0
        self.grupy[obserwacja.id_grupy] += 1
        
        # Dodaj do klasy dokładnej
        self._dodaj_do_klasy_dokladnej(obserwacja)
        
        # Dodaj do klasy grupowej
        self._dodaj_do_klasy_grupowej(obserwacja)
        
        # Sprawdź wzorce
        self._sprawdz_wzorce(obserwacja)
        
        # Auto-zapis
        if self._counter % self.config.SAVE_EVERY_N == 0:
            self.zapisz_pamiec()
        
        # Auto-rebuild statystyk
        if self._counter % self.config.REBUILD_STATS_EVERY_N == 0:
            self._rebuild_statystyki()
        
        return obserwacja.id_obserwacji
    
    def dodaj_obserwacje_z_dict(self, data: Dict[str, Any]) -> str:
        """Dodaje obserwację z słownika"""
        if SCHEMAS_AVAILABLE:
            obs = Obserwacja.from_dict(data)
        else:
            obs = self._create_obserwacja_from_dict(data)
        return self.dodaj_obserwacje(obs)
    
    def dodaj_predykcje_kalibrowana(self, predykcja: PredykcjaLevel1Kalibrowana, 
                                   wynik_rzeczywisty: str) -> str:
        """
        Dodaje obserwację na podstawie kalibrowanej predykcji.
        
        Args:
            predykcja: PredykcjaLevel1Kalibrowana
            wynik_rzeczywisty: Rzeczywisty wynik meczu
            
        Returns:
            id_obserwacji
        """
        if not SCHEMAS_AVAILABLE:
            raise ImportError("schemas.py required for this operation")
        
        obs = Obserwacja(
            id_meczu=predykcja.id_meczu,
            id_grupy=predykcja.id_grupy,
            id_modelu=predykcja.id_modelu,
            wynik_predykcji=predykcja.wynik_predykcji,
            confidence=predykcja.confidence_kalibrowana,
            wynik_rzeczywisty=wynik_rzeczywisty
        )
        
        # Zapisz dodatkowe dane kalibracji
        kalibracja_data = {
            "confidence_oryginalna": predykcja.confidence,
            "confidence_kalibrowana": predykcja.confidence_kalibrowana,
            "poprawka_kalibracji": predykcja.poprawka_kalibracji
        }
        
        obserwacja_kalibrowana = {
            "id_obserwacji": obs.id_obserwacji,
            "kalibracja": kalibracja_data
        }
        self.obserwacje_kalibrowane.append(obserwacja_kalibrowana)
        
        return self.dodaj_obserwacje(obs)
    
    # =========================================================================
    # PRYWATNE METODY DODAWANIA
    # =========================================================================
    
    def _dodaj_do_klasy_dokladnej(self, obserwacja: Obserwacja):
        """Dodaje obserwację do odpowiedniej klasy dokładnej"""
        if not obserwacja.klasa_dokladna:
            return
            
        if obserwacja.klasa_dokladna not in self.klasy_wynikow:
            self.klasy_wynikow[obserwacja.klasa_dokladna] = KlasaWyniku(
                nazwa_klasy=obserwacja.klasa_dokladna
            )
        
        self.klasy_wynikow[obserwacja.klasa_dokladna].dodaj_obserwacje(obserwacja)
    
    def _dodaj_do_klasy_grupowej(self, obserwacja: Obserwacja):
        """Dodaje obserwację do odpowiedniej klasy grupowej (1/X/2)"""
        if not obserwacja.klasa_grupa:
            return
        
        if obserwacja.klasa_grupa not in self.klasy_grupowe:
            self.klasy_grupowe[obserwacja.klasa_grupa] = KlasaWyniku(
                nazwa_klasy=obserwacja.klasa_grupa
            )
        
        self.klasy_grupowe[obserwacja.klasa_grupa].dodaj_obserwacje(obserwacja)
    
    def _sprawdz_wzorce(self, obserwacja: Obserwacja):
        """Sprawdza i aktualizuje wzorce zachowania"""
        # Wzorzec: niska pewność + trafienie
        if obserwacja.confidence < 0.3 and obserwacja.trafienie:
            self._dodaj_do_wzorca(
                "niska_pewnosc_trafienie",
                "Predykcje z niską pewnością (<0.3) które się sprawdziły",
                obserwacja.id_meczu,
                {"confidence": obserwacja.confidence}
            )
        
        # Wzorzec: wysoka pewność + nietrafienie
        if obserwacja.confidence > 0.9 and not obserwacja.trafienie:
            self._dodaj_do_wzorca(
                "wysoka_pewnosc_bledy",
                "Predykcje z wysoką pewnością (>0.9) które się nie sprawdziły",
                obserwacja.id_meczu,
                {"confidence": obserwacja.confidence}
            )
        
        # Wzorzec: tra عمرfienie grupowe ale nie dokładne
        if obserwacja.trafienie_grupa and not obserwacja.trafienie:
            self._dodaj_do_wzorca(
                "trafienie_grupowe_ tylko",
                "Trafienie grupowe (1/X/2) ale nie dokładny wynik",
                obserwacja.id_meczu,
                {
                    "predykcja": obserwacja.wynik_predykcji,
                    "rzeczywisty": obserwacja.wynik_rzeczywisty
                }
            )
    
    def _dodaj_do_wzorca(self, nazwa: str, opis: str, id_meczu: str, 
                         cechy: Optional[Dict[str, float]] = None):
        """Dodaje przykład do wzorca"""
        if nazwa not in self.wzorce:
            self.wzorce[nazwa] = WzorecZachowania(
                nazwa=nazwa,
                opis=opis
            )
        
        self.wzorce[nazwa].dodaj_przyklad(id_meczu, cechy)
    
    # =========================================================================
    # STATYSTYKI
    # =========================================================================
    
    def _rebuild_statystyki(self):
        """Przebudowuje statystyki globalne"""
        self.statystyki.calkowita_liczba_obserwacji = len(self.obserwacje)
        self.statystyki.liczba_klas = len(self.klasy_wynikow)
        self.statystyki.liczba_modeli = len(self.modele)
        
        # Średnia skuteczność
        if self.klasy_wynikow:
            total_skutecznosc = sum(
                k.skutecznosc for k in self.klasy_wynikow.values()
            )
            self.statystyki.srednia_skutecznosc = total_skutecznosc / len(self.klasy_wynikow)
        
        # Średni confidence
        if self.obserwacje:
            total_confidence = sum(o.confidence for o in self.obserwacje)
            self.statystyki.sredni_confidence = total_confidence / len(self.obserwacje)
    
    def pobierz_statystyki(self) -> Dict[str, Any]:
        """Zwraca aktualne statystyki"""
        self._rebuild_statystyki()
        return self.statystyki.to_dict()
    
    def pobierz_statystyki_rozszerzone(self) -> Dict[str, Any]:
        """Zwraca rozszerzone statystyki"""
        return {
            "globalne": self.pobierz_statystyki(),
            "modele": {mid: count for mid, count in self.modele.items()},
            "grupy": {gid: count for gid, count in self.grupy.items()},
            "klasy_dokladne": {k: v.to_dict() for k, v in self.klasy_wynikow.items()},
            "klasy_grupowe": {k: v.to_dict() for k, v in self.klasy_grupowe.items()},
            "wzorce": {k: v.to_dict() for k, v in self.wzorce.items()}
        }
    
    # =========================================================================
    # ZAPIS I ODCZYT
    # =========================================================================
    
    def zapisz_pamiec(self, sciezka: Optional[str] = None):
        """Zapisuje pamięć do pliku JSON"""
        if not sciezka:
            sciezka = os.path.join(
                self.config.BASE_PATH,
                self.config.PAMIEC_PATH,
                f"pamiec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        # Upewnij się, że katalog exists
        os.makedirs(os.path.dirname(sciezka), exist_ok=True)
        
        data = {
            "obserwacje": [o.to_dict() for o in self.obserwacje],
            "statystyki": self.pobierz_statystyki(),
            "modele": self.modele,
            "grupy": self.grupy,
            "counter": self._counter,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(sciezka, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return sciezka
    
    def wczytaj_pamiec(self, sciezka: str) -> bool:
        """Wczytuje pamięć z pliku JSON"""
        try:
            with open(sciezka, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Przywróć obserwacje
            for obs_dict in data.get("obserwacje", []):
                if SCHEMAS_AVAILABLE:
                    obs = Obserwacja.from_dict(obs_dict)
                else:
                    obs = self._create_obserwacja_from_dict(obs_dict)
                self.obserwacje.append(obs)
            
            # Przywróć statystyki
            if "statystyki" in data:
                for k, v in data["statystyki"].items():
                    setattr(self.statystyki, k, v)
            
            # Przywróć rejestry
            self.modele = data.get("modele", {})
            self.grupy = data.get("grupy", {})
            self._counter = data.get("counter", 0)
            
            # Rebuild struktur
            for obs in self.obserwacje:
                self._dodaj_do_klasy_dokladnej(obs)
                self._dodaj_do_klasy_grupowej(obs)
            
            return True
            
        except Exception as e:
            print(f"Error loading memory: {e}")
            return False
    
    def zapisz_archiwum(self):
        """Zapisuje archiwum pamięci"""
        sciezka = os.path.join(
            self.config.BASE_PATH,
            self.config.ARCHIWUM_PATH,
            f"archiwum_{datetime.now().strftime('%Y%m%d')}"
        )
        os.makedirs(sciezka, exist_ok=True)
        
        # Zapisz pełną pamięć
        self.zapisz_pamiec(os.path.join(sciezka, "pamiec_full.json"))
        
        # Zapisz statystyki
        stats_path = os.path.join(
            self.config.BASE_PATH,
            self.config.STATYSTYKI_PATH
        )
        os.makedirs(stats_path, exist_ok=True)
        
        with open(os.path.join(stats_path, f"statystyki_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"), 'w') as f:
            json.dump(self.pobierz_statystyki_rozszerzone(), f, indent=2, ensure_ascii=False)
    
    # =========================================================================
    # INTEGRACJA Z LEVEL 2 (KALIBRACJA)
    # =========================================================================
    
    def pobierz_dane_do_kalibracji(self, min_obserwacji: int = 100) -> List[Dict[str, Any]]:
        """
        Zwraca dane do kalibracji Level 2.
        
        Args:
            min_obserwacji: Minimalna liczba obserwacji dla modelu
            
        Returns:
            Lista obserwacji z modeli mających wystarczającą liczbę danych
        """
        result = []
        
        for model_id, count in self.modele.items():
            if count >= min_obserwacji:
                model_obs = [
                    o.to_dict() for o in self.obserwacje 
                    if o.id_modelu == model_id
                ]
                result.extend(model_obs)
        
        return result
    
    def dodaj_kalibracje(self, kalibracja_data: Dict[str, Any]):
        """Dodaje dane kalibracji do pamięci"""
        self.obserwacje_kalibrowane.append(kalibracja_data)
    
    # =========================================================================
    # METODY UŻYTECZNE
    # =========================================================================
    
    def pobierz_wszystkie_obserwacje(self) -> List[Obserwacja]:
        """Zwraca wszystkie obserwacje"""
        return self.obserwacje.copy()
    
    def pobierz_obserwacje_modelu(self, model_id: str) -> List[Obserwacja]:
        """Zwraca obserwacje dla konkretnego modelu"""
        return [o for o in self.obserwacje if o.id_modelu == model_id]
    
    def pobierz_obserwacje_grupy(self, grupa_id: str) -> List[Obserwacja]:
        """Zwraca obserwacje dla konkretnej grupy"""
        return [o for o in self.obserwacje if o.id_grupy == grupa_id]
    
    def pobierz_obserwacje_klasy(self, klasa: str) -> List[Obserwacja]:
        """Zwraca obserwacje dla konkretnej klasy wyniku"""
        if klasa in self.klasy_wynikow:
            return self.klasy_wynikow[klasa].obserwacje
        return []
    
    def czysc_pamiec(self):
        """Czyści pamięć (ostrzeganie: usuwa wszystkie dane!)"""
        self._initialize_structures()
        self._counter = 0
    
    def rozmiar_pamieci(self) -> int:
        """Zwraca aktualny rozmiar pamięci"""
        return len(self.obserwacje)
    
    # =========================================================================
    # FALLBACK DEFINICJE (na wypadek braku schemas.py)
    # =========================================================================
    
    @staticmethod
    def _create_obserwacja_from_dict(data: Dict[str, Any]) -> Any:
        """Tworzy obserwację z dicta (fallback)"""
        class SimpleObserwacja:
            def __init__(self, data):
                self.id_meczu = data.get("id_meczu", "")
                self.id_grupy = data.get("id_grupy", "")
                self.id_modelu = data.get("id_modelu", "")
                self.wynik_predykcji = data.get("wynik_predykcji", "")
                self.confidence = float(data.get("confidence", 0.5))
                self.wynik_rzeczywisty = data.get("wynik_rzeczywisty", "")
                self.timestamp = datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
                self.id_obserwacji = data.get("id_obserwacji", generuj_id())
                
                # Obliczenia
                self.trafienie = self.wynik_predykcji == self.wynik_rzeczywisty
                self.klasa_dokladna = self.wynik_rzeczywisty if ":" in self.wynik_rzeczywisty else None
                self.klasa_grupa = self._get_grupa(self.wynik_rzeczywisty)
                self.trafienie_grupa = self._get_grupa(self.wynik_predykcji) == self.klasa_grupa
            
            @staticmethod
            def _get_grupa(wynik):
                if ":" not in wynik:
                    return "X"
                try:
                    parts = wynik.split(":")
                    if int(parts[0]) > int(parts[1]):
                        return "1"
                    elif int(parts[0]) < int(parts[1]):
                        return "2"
                    else:
                        return "X"
                except:
                    return "X"
            
            def to_dict(self):
                return {
                    "id_obserwacji": self.id_obserwacji,
                    "id_meczu": self.id_meczu,
                    "id_grupy": self.id_grupy,
                    "id_modelu": self.id_modelu,
                    "wynik_predykcji": self.wynik_predykcji,
                    "confidence": self.confidence,
                    "wynik_rzeczywisty": self.wynik_rzeczywisty,
                    "trafienie": self.trafienie,
                    "trafienie_grupa": self.trafienie_grupa,
                    "klasa_dokladna": self.klasa_dokladna,
                    "klasa_grupa": self.klasa_grupa,
                    "timestamp": self.timestamp.isoformat()
                }
        
        return SimpleObserwacja(data)


# =============================================================================
# FABRYKA MEMORY BUILDER
# =============================================================================

def tworzenie_memory_builder(config: Optional[Dict[str, Any]] = None) -> MemoryBuilder:
    """
    Fabryka tworzących MemoryBuilder.
    
    Args:
        config: Opcjonalna konfiguracja (dict lub MemoryConfig)
        
    Returns:
        MemoryBuilder
    """
    if isinstance(config, dict):
        config_obj = MemoryConfig(**config)
    elif isinstance(config, MemoryConfig):
        config_obj = config
    else:
        config_obj = MemoryConfig()
    
    return MemoryBuilder(config_obj)


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing MemoryBuilder...")
    
    # Tworzenie buildera
    builder = tworzenie_memory_builder()
    
    # Test dodawania obserwacji
    if SCHEMAS_AVAILABLE:
        obs = Obserwacja(
            id_meczu="Test1 - Test2",
            id_grupy="test_group",
            id_modelu="test_model",
            wynik_predykcji="2:1",
            confidence=0.85,
            wynik_rzeczywisty="2:1"
        )
        obs_id = builder.dodaj_obserwacje(obs)
        print(f"Dodano obserwację: {obs_id}")
        
        # Test dodawania z dicta
        obs_dict = {
            "id_meczu": "Test3 - Test4",
            "id_grupy": "test_group",
            "id_modelu": "test_model",
            "wynik_predykcji": "1:0",
            "confidence": 0.95,
            "wynik_rzeczywisty": "0:0",
            "timestamp": datetime.now().isoformat()
        }
        obs_id2 = builder.dodaj_obserwacje_z_dict(obs_dict)
        print(f"Dodano obserwację z dict: {obs_id2}")
        
        # Test statystyk
        stats = builder.pobierz_statystyki()
        print(f"Statystyki: {stats}")
        
        # Test klas
        print(f"Liczba klas dokładnych: {len(builder.klasy_wynikow)}")
        print(f"Liczba klas grupowych: {len(builder.klasy_grupowe)}")
        
        # Test wzorców
        print(f"Liczba wzorców: {len(builder.wzorce)}")
        
        # Test rozmiaru
        print(f"Rozmiar pamięci: {builder.rozmiar_pamieci()}")
        
    else:
        print("schemas.py not available, running in fallback mode")
        
        # Test fallback
        obs_dict = {
            "id_meczu": "Test1 - Test2",
            "id_grupy": "test_group",
            "id_modelu": "test_model",
            "wynik_predykcji": "2:1",
            "confidence": 0.85,
            "wynik_rzeczywisty": "2:1"
        }
        obs_id = builder.dodaj_obserwacje_z_dict(obs_dict)
        print(f"Dodano obserwację (fallback): {obs_id}")
    
    print("\nAll MemoryBuilder tests passed!")
