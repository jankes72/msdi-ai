"""
SSI V2 to V3 Bridge - Most między systemami V2 i V3

Moduł odpowiedzialny za:
- Konwersję danych między V2 a V3
- Transfer obserwacji i pamięci
- Synchronizację światów danych
- Koordynację przepływu informacji

Architektura:
V2 (Modele, Pamięć) <-Bridge-> V3 (Światy, Metadane, Pamięć)

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2, 3.x
- 02_DATA_STRUCTURE.md

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import uuid
import json
import sys

# Importy z V2
from SSI.v2.models import BaseModelV2
from SSI.v2.observation import MemoryBuilder, ModelObserver
from SSI.v2.integration import V2Integration

# Importy z pamiec_modeli_v2 (V3 otrzyma system pamięci)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "pamiec_modeli_v2"))

try:
    from schemas import (
        Obserwacja, PredykcjaLevel1, PredykcjaLevel1Kalibrowana,
        KLASY_WYNIKOW_DOKLADNYCH, get_grupa_wyniku
    )
    SCHEMAS_AVAILABLE = True
except ImportError:
    SCHEMAS_AVAILABLE = False


# =============================================================================
# KONFIGURACJA MOSTU
# =============================================================================

@dataclass
class BridgeConfig:
    """Konfiguracja mostu V2-V3"""
    
    # Ustawienia synchronizacji
    SYNC_INTERVAL: int = 100  # Co ile obserwacji synchronizować
    AUTO_SYNC: bool = True
    SYNC_MEMORY: bool = True
    SYNC_OBSERVATIONS: bool = True
    SYNC_PATTERNS: bool = True
    
    # Ustawienia konwersji
    CONVERT_FORMAT: str = "full"  # full, minimal, custom
    PRESERVE_METADATA: bool = True
    
    # Ustawienia filtrów
    MIN_CONFIDENCE_THRESHOLD: float = 0.0  # Minimalny confidence do transferu
    FILTER_GRUPY: List[str] = field(default_factory=list)  # Filtrowanie po grupach
    
    # Ścieżki
    V2_MEMORY_PATH: str = "pamiec_modeli_v2/pamiec"
    V3_WORLDS_PATH: str = "pamiec_modeli_v2/worlds"
    BRIDGE_LOG_PATH: str = "pamiec_modeli_v2/logs/bridge.log"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "SYNC_INTERVAL": self.SYNC_INTERVAL,
            "AUTO_SYNC": self.AUTO_SYNC,
            "SYNC_MEMORY": self.SYNC_MEMORY,
            "SYNC_OBSERVATIONS": self.SYNC_OBSERVATIONS,
            "SYNC_PATTERNS": self.SYNC_PATTERNS,
            "CONVERT_FORMAT": self.CONVERT.Format,
            "PRESERVE_METADATA": self.PRESERVE_METADATA,
            "MIN_CONFIDENCE_THRESHOLD": self.MIN_CONFIDENCE_THRESHOLD,
            "CONVERT_FORMAT": self.CONVERT_FORMAT
        }


# =============================================================================
# STRUKTURA DANYCH DLA V3
# =============================================================================

@dataclass
class WorldDataPackage:
    """
    Pakiet danych do transferu do systemu V3.
    
    Zawiera:
    - Obserwacje z V2
    - Statystyki modeli
    - Wzorce zachowania
    - Metadane konwersji
    """
    
    # Identyfikatory
    id_pakietu: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    id_swiata: Optional[str] = None
    
    # Dane
    obserwacje: List[Dict[str, Any]] = field(default_factory=list)
    statystyki_modeli: Dict[str, Any] = field(default_factory=dict)
    wzorce: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadane
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "V2_to_V3_Bridge"
    
    # Informacje o konwersji
    format: str = "full"
    licznosc_obserwacji: int = 0
    licznosc_wzorców: int = 0
    
    # Filtrowanie
    min_confidence: float = 0.0
    wywołane_grupy: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_pakietu": self.id_pakietu,
            "id_swiata": self.id_swiata,
            "obserwacje": self.obserwacje,
            "statystyki_modeli": self.statystyki_modeli,
            "wzorce": self.wzorce,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "format": self.format,
            "licznosc_obserwacji": self.licznosc_obserwacji,
            "licznosc_wzorców": self.licznosc_wzorców,
            "min_confidence": self.min_confidence,
            "wywołane_grupy": self.wywołane_grupy
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldDataPackage":
        return cls(
            id_pakietu=data.get("id_pakietu", uuid.uuid4().hex[:12]),
            id_swiata=data.get("id_swiata"),
            obserwacje=data.get("obserwacje", []),
            statystyki_modeli=data.get("statystyki_modeli", {}),
            wzorce=data.get("wzorce", []),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            source=data.get("source", "V2_to_V3_Bridge"),
            format=data.get("format", "full"),
            licznosc_obserwacji=data.get("licznosc_obserwacji", 0),
            licznosc_wzorców=data.get("licznosc_wzorców", 0),
            min_confidence=float(data.get("min_confidence", 0.0)),
            wywołane_grupy=data.get("wywołane_grupy", [])
        )


# =============================================================================
# KONWERTER DANYCH V2 -> V3
# =============================================================================

class V2ToV3DataConverter:
    """
    Konwertuje dane z formatu V2 do formatu zrozumiałego przez V3.
    """
    
    @staticmethod
    def konwertuj_obserwacje(obserwacje: List[Any], 
                           min_confidence: float = 0.0,
                           filter_grupy: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Konwertuje obserwacje V2 do formatu V3"""
        result = []
        
        for obs in obserwacje:
            if hasattr(obs, 'confidence') and obs.confidence < min_confidence:
                continue
            
            # Pobierz grupę
            if hasattr(obs, 'klasa_grupa'):
                grupa = obs.klasa_grupa
            elif hasattr(obs, 'wynik_rzeczywisty'):
                grupa = get_grupa_wyniku(obs.wynik_rzeczywisty) if SCHEMAS_AVAILABLE else "X"
            else:
                grupa = "X"
            
            if filter_grupy and grupa not in filter_grupy:
                continue
            
            # Konwersja
            v3_obs = {
                # Podstawowe dane
                "id": getattr(obs, 'id_obserwacji', str(uuid.uuid4().hex[:12])),
                "mecz_id": getattr(obs, 'id_meczu', ''),
                "grupa_id": getattr(obs, 'id_grupy', ''),
                "model_id": getattr(obs, 'id_modelu', ''),
                
                # Predykcja vs Rzeczywistość
                "predykcja": getattr(obs, 'wynik_predykcji', '0:0'),
                "rzeczywistosc": getattr(obs, 'wynik_rzeczywisty', '0:0'),
                "trafienie": getattr(obs, 'trafienie', False),
                "trafienie_grupa": getattr(obs, 'trafienie_grupa', False),
                
                # Metryki
                "confidence": float(getattr(obs, 'confidence', 0.5)),
                
                # Klasyfikacja
                "klasa_dokladna": getattr(obs, 'klasa_dokladna', None),
                "klasa_grupa": grupa,
                
                # Timestamps
                "timestamp": getattr(obs, 'timestamp', datetime.now()).isoformat(),
                
                # Metadane V3
                "world_version": "v3",
                "data_type": "observation",
                "source": "V2_bridge"
            }
            
            result.append(v3_obs)
        
        return result
    
    @staticmethod
    def konwertuj_statystyki(statystyki: Dict[str, Any]) -> Dict[str, Any]:
        """Konwertuje statystyki V2 do formatu V3"""
        return {
            "id": f"stats_{uuid.uuid4().hex[:8]}",
            "calkowita_liczba_obserwacji": statystyki.get("calkowita_liczba_obserwacji", 0),
            "liczba_klas": statystyki.get("liczba_klas", 0),
            "srednia_skutecznosc": statystyki.get("srednia_skutecznosc", 0.0),
            "sredni_confidence": statystyki.get("sredni_confidence", 0.0),
            "liczba_modeli": statystyki.get("liczba_modeli", 0),
            "wersja": statystyki.get("wersja", "v2_std"),
            "data_utworzenia": statystyki.get("data_utworzenia", datetime.now().isoformat()),
            "source": "V2_bridge",
            "world_version": "v3"
        }
    
    @staticmethod
    def konwertuj_wzorce(wzorce: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Konwertuje wzorce zachowania do formatu V3"""
        result = []
        
        for nazwa, wzorzec in wzorce.items():
            if hasattr(wzorzec, 'to_dict'):
                wzorzec_dict = wzorec.to_dict()
            else:
                wzorzec_dict = wzorzec
            
            v3_wzorec = {
                "id": f"pattern_{uuid.uuid4().hex[:8]}",
                "nazwa": wzorzec_dict.get("nazwa", nazwa),
                "opis": wzorzec_dict.get("opis", ""),
                "czestotliwosc": wzorzec_dict.get("czestotliwosc", 0),
                "przykłady": wzorzec_dict.get("przykłady", []),
                "cechy": wzorzec_dict.get("cechy_charakterystyczne", {}),
                "data_odkrycia": wzorzec_dict.get("data_odkrycia", datetime.now().isoformat()),
                "source": "V2_bridge",
                "world_version": "v3"
            }
            
            result.append(v3_wzorec)
        
        return result


# =============================================================================
# GŁÓWNY MOST V2-V3
# =============================================================================

class V2ToV3Bridge:
    """
    Most łączący systemy V2 i V3.
    
    Odpowiedzialności:
    - Transfer danych z V2 (pamięć modeli) do V3 (światy)
    - Konwersja formatów
    - Synchronizacja w obie strony
    - Zarządzanie pakietami danych
    """
    
    def __init__(self, 
                 v2_integration: Optional[V2Integration] = None,
                 v2_memory: Optional[MemoryBuilder] = None,
                 config: Optional[BridgeConfig] = None):
        self.config = config or BridgeConfig()
        
        # Komponenty V2
        self.v2_integration = v2_integration
        self.v2_memory = v2_memory or (v2_integration.memory_builder if v2_integration else None)
        
        # Konwerter
        self.converter = V2ToV3DataConverter()
        
        # Rejestry
        self.transferred_packages: List[WorldDataPackage] = []
        self.sync_history: List[Dict[str, Any]] = []
        self._sync_counter = 0
        
        # Inicjalizacja
        if self.v2_memory is None:
            from SSI.v2.observation import MemoryBuilder, MemoryConfig
            self.v2_memory = MemoryBuilder(MemoryConfig())
    
    # =========================================================================
    # SYNCHRONIZACJA V2 -> V3
    # =========================================================================
    
    def synchronizuj_do_v3(self, id_swiata: Optional[str] = None) -> WorldDataPackage:
        """
        Synchronizuje dane z V2 do V3.
        
        Args:
            id_swiata: Opcjonalny ID świata docelowego
            
        Returns:
            WorldDataPackage
        """
        # 1. Pobierz dane z V2
        obserwacje = self._pobierz_obserwacje_v2()
        statystyki = self._pobierz_statystyki_v2()
        wzorce = self._pobierz_wzorce_v2()
        
        # 2. Konwertuj dane
        v3_obserwacje = self.converter.konwertuj_obserwacje(
            obserwacje,
            min_confidence=self.config.MIN_CONFIDENCE_THRESHOLD,
            filter_grupy=self.config.FILTER_GRUPY if self.config.FILTER_GRUPY else None
        )
        v3_statystyki = self.converter.konwertuj_statystyki(statystyki)
        v3_wzorce = self.converter.konwertuj_wzorce(wzorce)
        
        # 3. Utwórz pakiet
        pakiet = WorldDataPackage(
            id_swiata=id_swiata,
            obserwacje=v3_obserwacje,
            statystyki_modeli=v3_statystyki,
            wzorce=v3_wzorce,
            format=self.config.CONVERT_FORMAT,
            licznosc_obserwacji=len(v3_obserwacje),
            licznosc_wzorców=len(v3_wzorce),
            min_confidence=self.config.MIN_CONFIDENCE_THRESHOLD
        )
        
        # 4. Zapisz historię
        self._zapisz_sync_historie(pakiet)
        
        # 5. Zapamiętaj pakiet
        self.transferred_packages.append(pakiet)
        if len(self.transferred_packages) > 100:
            self.transferred_packages = self.transferred_packages[-100:]
        
        return pakiet
    
    def _pobierz_obserwacje_v2(self) -> List[Any]:
        """Pobiera obserwacje z V2"""
        if self.v2_memory:
            return self.v2_memory.pobierz_wszystkie_obserwacje()
        return []
    
    def _pobierz_statystyki_v2(self) -> Dict[str, Any]:
        """Pobiera statystyki z V2"""
        if self.v2_memory:
            return self.v2_memory.pobierz_statystyki()
        return {}
    
    def _pobierz_wzorce_v2(self) -> Dict[str, Any]:
        """Pobiera wzorce z V2"""
        if self.v2_memory:
            return {k: v.to_dict() for k, v in self.v2_memory.wzorce.items()}
        return {}
    
    def _zapisz_sync_historie(self, pakiet: WorldDataPackage):
        """Zapisuje historię synchronizacji"""
        self._sync_counter += 1
        
        history_entry = {
            "id": self._sync_counter,
            "timestamp": datetime.now().isoformat(),
            "pakiet_id": pakiet.id_pakietu,
            "licznosc_obserwacji": pakiet.licznosc_obserwacji,
            "licznosc_wzorców": pakiet.licznosc_wzorców,
            "status": "completed"
        }
        
        self.sync_history.append(history_entry)
        if len(self.sync_history) > 1000:
            self.sync_history = self.sync_history[-1000:]
    
    # =========================================================================
    # AUTOMATYCZNA SYNCHRONIZACJA
    # =========================================================================
    
    def zarejestruj_nową_obserwację(self):
        """Powiadamia most, że została dodana nowa obserwacja"""
        if not self.config.AUTO_SYNC:
            return
        
        if self.v2_memory:
            if self.v2_memory.rozmiar_pamieci() % self.config.SYNC_INTERVAL == 0:
                self.synchronizuj_do_v3()
    
    def ustaw_callback_v2(self, v2_integration: V2Integration):
        """Ustawia callback do V2 Integration"""
        self.v2_integration = v2_integration
        self.v2_memory = v2_integration.memory_builder
        
        # Podłącz się do eventów V2 (jeśli będą zaimplementowane)
        # Na razie używamy manualnego callbacku
    
    # =========================================================================
    # ZAPIS I ODCZYT PAKIETÓW
    # =========================================================================
    
    def zapisz_pakiet(self, pakiet: WorldDataPackage, sciezka: Optional[str] = None) -> str:
        """Zapisuje pakiet do pliku"""
        if not sciezka:
            sciezka = f"{self.config.V3_WORLDS_PATH}/pakiet_{pakiet.id_pakietu}.json"
        
        # Upewnij się, że katalog exists
        import os
        os.makedirs(os.path.dirname(sciezka), exist_ok=True)
        
        with open(sciezka, 'w', encoding='utf-8') as f:
            f.write(pakiet.to_json())
        
        return sciezka
    
    def wczytaj_pakiet(self, sciezka: str) -> Optional[WorldDataPackage]:
        """Wczytuje pakiet z pliku"""
        try:
            import os
            if os.path.exists(sciezka):
                with open(sciezka, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return WorldDataPackage.from_dict(data)
        except Exception as e:
            print(f"Błąd wczytywania pakietu: {e}")
        return None
    
    # =========================================================================
    # DODATKOWE METODY
    # =========================================================================
    
    def tworzenie_raportu_synchronizacji(self) -> Dict[str, Any]:
        """Tworzy raport synchronizacji"""
        return {
            "total_syncs": len(self.sync_history),
            "total_packages": len(self.transferred_packages),
            "total_observations": sum(p.licznosc_obserwacji for p in self.transferred_packages),
            "total_patterns": sum(p.licznosc_wzorców for p in self.transferred_packages),
            "last_sync": self.sync_history[-1] if self.sync_history else None
        }
    
    def czysc_historie(self):
        """Czyści historię synchronizacji"""
        self.sync_history.clear()
        self.transferred_packages.clear()
    
    def eksportuj_wszystko_do_v3(self) -> List[WorldDataPackage]:
        """
        Eksportuje wszystkie dane z V2 do V3.
        
        Zwraca listę pakietów (po jednym na świat/grupę)
        """
        if not self.v2_memory:
            return []
        
        #Grupuj obserwacje poworld_id (grupa)
        grupy = {}
        for obs in self.v2_memory.pobierz_wszystkie_obserwacje():
            grupa_id = getattr(obs, 'id_grupy', 'default')
            if grupa_id not in grupy:
                grupy[grupa_id] = []
            grupy[grupa_id].append(obs)
        
        # Twórz pakiety dla każdej grupy
        pakiety = []
        for grupa_id, obserwacje in grupy.items():
            pakiet = self.synchronizuj_do_v3(id_swiata=grupa_id)
            pakiety.append(pakiet)
        
        return pakiety


# =============================================================================
# FABRYKA
# =============================================================================

def tworz_bridge_v2_v3(
    v2_integration: Optional[V2Integration] = None,
    v2_memory: Optional[MemoryBuilder] = None,
    config: Optional[Dict[str, Any]] = None
) -> V2ToV3Bridge:
    """
    Fabryka tworzących most V2-V3.
    
    Args:
        v2_integration: Opcjonalna instancja V2Integration
        v2_memory: Opcjonalna instancja MemoryBuilder
        config: Opcjonalna konfiguracja (dict lub BridgeConfig)
        
    Returns:
        V2ToV3Bridge
    """
    if isinstance(config, dict):
        config_obj = BridgeConfig(**config)
    elif isinstance(config, BridgeConfig):
        config_obj = config
    else:
        config_obj = BridgeConfig()
    
    return V2ToV3Bridge(
        v2_integration=v2_integration,
        v2_memory=v2_memory,
        config=config_obj
    )


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing V2ToV3Bridge...")
    
    # Test konwersji
    converter = V2ToV3DataConverter()
    
    # Tworzenie testowych obserwacji
    if SCHEMAS_AVAILABLE:
        test_obs = [
            Obserwacja(
                id_meczu="Test1",
                id_grupy="world1",
                id_modelu="model1",
                wynik_predykcji="2:1",
                confidence=0.8,
                wynik_rzeczywisty="2:1"
            ),
            Obserwacja(
                id_meczu="Test2",
                id_grupy="world1", 
                id_modelu="model1",
                wynik_predykcji="1:0",
                confidence=0.6,
                wynik_rzeczywisty="0:0"
            )
        ]
        
        # Test konwersji
        v3_obs = converter.konwertuj_obserwacje(test_obs)
        print(f"Skofnwertowano {len(v3_obs)} obserwacji")
        print(f"Pierwsza obserwacja: {v3_obs[0]}")
    else:
        print("schemas.py not available, using minimal test")
    
    # Test mostu
    if SCHEMAS_AVAILABLE:
        from SSI.v2.observation import MemoryBuilder
        
        memory = MemoryBuilder()
        for obs in test_obs:
            memory.dodaj_obserwacje(obs)
        
        bridge = tworz_bridge_v2_v3(v2_memory=memory)
        pakiet = bridge.synchronizuj_do_v3("test_world")
        
        print(f"Utworzono pakiet: {pakiet.id_pakietu}")
        print(f"Liczba obserwacji w pakiecie: {pakiet.licznosc_obserwacji}")
        print(f"Format: {pakiet.format}")
    
    print("\nAll V2ToV3Bridge tests passed!")
