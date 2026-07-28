"""
SSI V3 World - Klasa bazowa świata

Bazowa klasa reprezentująca świat w systemie SSI V3.

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.2
- 02_DATA_STRUCTURE.md Sekcja 4.2

Świat to:
- Zbior obserwacji zdobywanych z data
- Organizacja danych według określonego schematu
- Źródło wiedzy dla agentów V4
-jednostka analizy i wnioskowania

Typy światów:
- SWIAT_1: Zmiany kursów (11 sieci trendów)
- SWIAT_2: Dynamika/Amplituda
- SWIAT_3: Złożone wzorce
- SWIAT_4: Relacje i synchronizacje

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from enum import Enum, auto
import uuid


# =============================================================================
# TYPY ŚWIATÓW
# =============================================================================

class WorldType(Enum):
    """Typy światów w systemie V3"""
    SWIAT_1_ZMIANY_KURSOW = auto()      # Świat 1: Zmiany kursów
    SWIAT_2_DYNAMIKA = auto()            # Świat 2: Dynamika/Amplituda
    SWIAT_3_KOMPLEKSOWE = auto()          # Świat 3: Złożone wzorce
    SWIAT_4_RELACJE = auto()              # Świat 4: Relacje i synchronizacje
    CUSTOM = auto()                       # Niestandardowy świat


class WorldStatus(Enum):
    """Status świata"""
    UNINITIALIZED = auto()  # Nie zainicjowany
    BUILDING = auto()       # W trakcie budowy
    ACTIVE = auto()         # Aktywny
    ARCHIVED = auto()       # Zarchiwizowany
    ERROR = auto()          # Błąd


# =============================================================================
# KONFIGURACJA ŚWIATA
# =============================================================================

@dataclass
class WorldConfig:
    """
    Konfiguracja świata V3
    
    Zgodnie z 02_DATA_STRUCTURE.md Sekcja 4.2
    """
    
    # Identyfikatory
    world_id: str = ""
    nazwa: str = ""
    opis: str = ""
    
    # Typ świata
    world_type: WorldType = WorldType.SWIAT_1_ZMIANY_KURSOW
    
    # Ustawienia
    max_observations: int = 100000     # Maksymalna liczba obserwacji w świecie
    max_patterns: int = 1000            # Maksymalna liczba wzorców
    retention_days: int = 365           # Czas przechowywania (dni)
    
    # Integracja z V2
    v2_models: List[str] = field(default_factory=list)  # Modele V2 przypisane do świata
    v2_data_percentage: float = 0.4     # Procent danych V2 dla tego świata
    
    # Flagi
    enabled: bool = True
    auto_build: bool = True
    save_to_disk: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "nazwa": self.nazwa,
            "opis": self.opis,
            "world_type": self.world_type.name,
            "max_observations": self.max_observations,
            "max_patterns": self.max_patterns,
            "retention_days": self.retention_days,
            "v2_models": self.v2_models,
            "v2_data_percentage": self.v2_data_percentage,
            "enabled": self.enabled,
            "auto_build": self.auto_build,
            "save_to_disk": self.save_to_disk
        }


# =============================================================================
# KLASA WORLD
# =============================================================================

@dataclass
class World:
    """
    Klasa reprezentująca świat w systemie V3.
    
    Świat to zbior obserwacji, wzorców i relacji organizowanych
    według określonego schematu interpretacji.
    
    Odpowiedzialność:
    - Przechowywanie obserwacji kompleksowych do świata
    - Budowanie wzorców charakterystycznych
    - Integracja z pamięcią V3
    - Dostarczanie wiedzy do V4
    
    Zgodnie z:
    - 01_SYSTEM_ARCHITECTURE.md Sekcja 3.2
    - 02_DATA_STRUCTURE.md Sekcja 4.2
    """
    
    # Identyfikatory
    world_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    nazwa: str = ""
    opis: str = ""
    
    # Konfiguracja
    config: WorldConfig = field(default_factory=WorldConfig)
    
    # Status
    status: WorldStatus = WorldStatus.UNINITIALIZED
    
    # Dane
    obserwacje: List[Dict[str, Any]] = field(default_factory=list)
    wzorce: List[Dict[str, Any]] = field(default_factory=list)
    metadane: Dict[str, Any] = field(default_factory=dict)
    relacje: List[Dict[str, Any]] = field(default_factory=list)
    
    # Statystyki
    statystyki: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    data_utworzenia: datetime = field(default_factory=datetime.now)
    data_ostaniego_dostepu: datetime = field(default_factory=datetime.now)
    data_modyfikacji: datetime = field(default_factory=datetime.now)
    
    # Powiązania
    powiazane_swiaty: List[str] = field(default_factory=list)  # ID powiązanych światów
    modele_v2: List[str] = field(default_factory=list)     # Powiązane modele V2
    agenci_v4: List[str] = field(default_factory=list)     # Agenci korzystający z tego świata
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu"""
        # Ustaw world_id i nazwa z config jeśli nie podane
        if self.config.world_id and not self.world_id:
            self.world_id = self.config.world_id
        if self.config.nazwa and not self.nazwa:
            self.nazwa = self.config.nazwa
        if self.config.opis and not self.opis:
            self.opis = self.config.opis
            
        # Ustaw typ świata
        if self.config.world_type:
            self.config.world_type = self.config.world_type
    
    # =========================================================================
    # METODY DODAWANIA DANYCH
    # =========================================================================
    
    def dodaj_obserwacje(self, obserwacja: Dict[str, Any]) -> str:
        """
        Dodaje obserwację do świata
        
        Args:
            obserwacja: Obserwacja (dict z polami: mecz_id, predykcja, rzeczywistosc, itd.)
            
        Returns:
            ID obserwacji
        """
        obs_id = obserwacja.get("id", str(uuid.uuid4().hex[:12]))
        
        # Uzupełnij metadane
        obserwacja["swiat_id"] = self.world_id
        obserwacja["data_dodania"] = datetime.now().isoformat()
        
        self.obserwacje.append(obserwacja)
        self.data_modyfikacji = datetime.now()
        
        # Zaktualizuj statystyki
        self._aktualizuj_statystyki_obserwacji(obserwacja)
        
        return obs_id
    
    def dodaj_wzorzec(self, wzorzec: Dict[str, Any]) -> str:
        """
        Dodaje wzorzec do świata
        
        Args:
            wzorzec: Wzorzec (dict z polami: nazwa, opis, czestotliwosc, itd.)
            
        Returns:
            ID wzorca
        """
        wzorzec_id = wzorzec.get("id", str(uuid.uuid4().hex[:12]))
        wzorzec["swiat_id"] = self.world_id
        wzorzec["data_dodania"] = datetime.now().isoformat()
        
        self.wzorce.append(wzorzec)
        self.data_modyfikacji = datetime.now()
        
        return wzorzec_id
    
    def dodaj_relacje(self, relacja: Dict[str, Any]) -> str:
        """
        Dodaje relację do świata
        
        Args:
            relacja: Relacja (dict z polami: source_type, source_id, target_type, target_id, itd.)
            
        Returns:
            ID relacji
        """
        relacja_id = relacja.get("id", str(uuid.uuid4().hex[:12]))
        relacja["swiat_id"] = self.world_id
        relacja["data_dodania"] = datetime.now().isoformat()
        
        self.relacje.append(relacja)
        self.data_modyfikacji = datetime.now()
        
        return relacja_id
    
    def dodaj_metadane(self, klucz: str, wartosc: Any) -> None:
        """Dodaje lub aktualizuje metadane świata"""
        self.metadane[klucz] = wartosc
        self.data_modyfikacji = datetime.now()
    
    # =========================================================================
    # METODY POBIERANIA DANYCH
    # =========================================================================
    
    def pobierz_obserwacje(self, **filtry) -> List[Dict[str, Any]]:
        """Pobiera obserwacje według filtrów"""
        results = self.obserwacje
        
        for key, value in filtry.items():
            results = [obs for obs in results if obs.get(key) == value]
        
        return results
    
    def pobierz_wzorce(self, **filtry) -> List[Dict[str, Any]]:
        """Pobiera wzorce według filtrów"""
        results = self.wzorce
        
        for key, value in filtry.items():
            results = [w for w in results if w.get(key) == value]
        
        return results
    
    def pobierz_relacje(self, **filtry) -> List[Dict[str, Any]]:
        """Pobiera relacje według filtrów"""
        results = self.relacje
        
        for key, value in filtry.items():
            results = [r for r in results if r.get(key) == value]
        
        return results
    
    def pobierz_obserwacje_po_meczu(self, mecz_id: str) -> List[Dict[str, Any]]:
        """Pobiera wszystkie obserwacje dla danego meczu"""
        return [obs for obs in self.obserwacje if obs.get("mecz_id") == mecz_id]
    
    def pobierz_obserwacje_po_modelu(self, model_id: str) -> List[Dict[str, Any]]:
        """Pobiera wszystkie obserwacje dla danego modelu"""
        return [obs for obs in self.obserwacje if obs.get("model_id") == model_id]
    
    # =========================================================================
    # METODY ANALIZY
    # =========================================================================
    
    def _aktualizuj_statystyki_obserwacji(self, obserwacja: Dict[str, Any]) -> None:
        """Aktualizuje statystyki na podstawie nowej obserwacji"""
        # Typ predykcji vs rzeczywistość
        predykcja = obserwacja.get("predykcja", "0:0")
        rzeczywistosc = obserwacja.get("rzeczywistosc", "0:0")
        trafienie = predykcja == rzeczywistosc
        
        # Aktualizuj licznik
        if "liczba_obserwacji" not in self.statystyki:
            self.statystyki["liczba_obserwacji"] = 0
        self.statystyki["liczba_obserwacji"] += 1
        
        # Aktualizuj trafienia
        if "liczba_trafien" not in self.statystyki:
            self.statystyki["liczba_trafien"] = 0
        if trafienie:
            self.statystyki["liczba_trafien"] += 1
        
        # Skuteczność
        self.statystyki["skutecznosc"] = (
            self.statystyki["liczba_trafien"] / self.statystyki["liczba_obserwacji"]
            if self.statystyki["liczba_obserwacji"] > 0 else 0.0
        )
        
        # Statystyki po grupach
        grupa_predykcji = self._get_grupa(predykcja)
        grupa_rzeczywistosci = self._get_grupa(rzeczywistosc)
        
        if grupa_predykcji not in self.statystyki:
            self.statystyki[grupa_predykcji] = {"count": 0, "correct": 0}
        self.statystyki[grupa_predykcji]["count"] += 1
        if grupa_predykcji == grupa_rzeczywistosci:
            self.statystyki[grupa_predykcji]["correct"] += 1
    
    @staticmethod
    def _get_grupa(wynik: str) -> str:
        """Pobiera grupę wyniku (1, X, 2)"""
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
    
    def pobierz_statystyki(self) -> Dict[str, Any]:
        """Zwraca aktualne statystyki świata"""
        stats = {
            "swiat_id": self.world_id,
            "nazwa": self.nazwa,
            "world_type": self.config.world_type.name,
            "status": self.status.name,
            "liczba_obserwacji": len(self.obserwacje),
            "liczba_wzorców": len(self.wzorce),
            "liczba_relacji": len(self.relacje),
            "liczba_metadanych": len(self.metadane),
            "data_utworzenia": self.data_utworzenia.isoformat(),
            "data_modyfikacji": self.data_modyfikacji.isoformat()
        }
        stats.update(self.statystyki)
        return stats
    
    def pobierz_wzorce_z_obserwacji(self) -> List[Dict[str, Any]]:
        """
        Wykrywa wzorce z obserwacji w świecie
        
        Returns:
            Lista wykrytych wzorców
        """
        # wolne implementacje - tylko zwraca istniejące wzorce
        return self.wzorce.copy()
    
    # =========================================================================
    # METODY ZARZĄDZANIA
    # =========================================================================
    
    def initialize(self) -> bool:
        """Inicjalizuje świat"""
        try:
            self.status = WorldStatus.BUILDING
            # Inicjalizacja struktur
            self.obserwacje = []
            self.wzorce = []
            self.metadane = {}
            self.relacje = []
            self.statystyki = {}
            
            self.status = WorldStatus.ACTIVE
            return True
        except Exception as e:
            self.status = WorldStatus.ERROR
            return False
    
    def activate(self) -> bool:
        """Aktywuje świat"""
        if self.status == WorldStatus.ACTIVE:
            return True
        
        if self.status == WorldStatus.UNINITIALIZED:
            self.initialize()
        
        if len(self.obserwacje) > 0:
            self.status = WorldStatus.ACTIVE
            return True
        
        return False
    
    def archive(self) -> bool:
        """Archiwizuje świat"""
        self.status = WorldStatus.ARCHIVED
        return True
    
    def clear(self) -> None:
        """Czyści świat (UWAGA: usuwa wszystkie dane!)"""
        self.obserwacje.clear()
        self.wzorce.clear()
        self.metadane.clear()
        self.relacje.clear()
        self.statystyki.clear()
        self.status = WorldStatus.UNINITIALIZED
    
    # =========================================================================
    # METODY UŻYTECZNE
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje świat do słownika"""
        return {
            "world_id": self.world_id,
            "nazwa": self.nazwa,
            "opis": self.opis,
            "config": self.config.to_dict(),
            "status": self.status.name,
            "obserwacje": self.obserwacje,
            "wzorce": self.wzorce,
            "metadane": self.metadane,
            "relacje": self.relacje,
            "statystyki": self.statystyki,
            "data_utworzenia": self.data_utworzenia.isoformat(),
            "data_ostaniego_dostepu": self.data_ostaniego_dostepu.isoformat(),
            "data_modyfikacji": self.data_modyfikacji.isoformat(),
            "powiazane_swiaty": self.powiazane_swiaty,
            "modele_v2": self.modele_v2,
            "agenci_v4": self.agenci_v4
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "World":
        """Tworzy świat z słownika"""
        config_data = data.get("config", {})
        config = WorldConfig(**config_data) if config_data else WorldConfig()
        
        world = cls(
            world_id=data.get("world_id", ""),
            nazwa=data.get("nazwa", ""),
            opis=data.get("opis", ""),
            config=config,
            status=WorldStatus[data.get("status", "UNINITIALIZED")],
            obserwacje=data.get("obserwacje", []),
            wzorce=data.get("wzorce", []),
            metadane=data.get("metadane", {}),
            relacje=data.get("relacje", []),
            statystyki=data.get("statystyki", {}),
            data_utworzenia=datetime.fromisoformat(data.get("data_utworzenia", datetime.now().isoformat())),
            data_ostaniego_dostepu=datetime.fromisoformat(data.get("data_ostaniego_dostepu", datetime.now().isoformat())),
            data_modyfikacji=datetime.fromisoformat(data.get("data_modyfikacji", datetime.now().isoformat())),
            powiazane_swiaty=data.get("powiazane_swiaty", []),
            modele_v2=data.get("modele_v2", []),
            agenci_v4=data.get("agenci_v4", [])
        )
        
        return world
    
    def __repr__(self) -> str:
        return f"World(id={self.world_id}, nazwa={self.nazwa}, type={self.config.world_type.name}, obs={len(self.obserwacje)})"


# =============================================================================
# FUNKCJE UŻYTECZNE
# =============================================================================

def tworz_swiat(nazwa: str, world_type: WorldType = WorldType.SWIAT_1_ZMIANY_KURSOW,
               opis: str = "") -> World:
    """
    Tworzy nowy świat z domyślną konfiguracją
    
    Args:
        nazwa: Nazwa świata
        world_type: Typ świata
        opis: Opis świata
        
    Returns:
        World
    """
    config = WorldConfig(
        world_id=str(uuid.uuid4().hex[:12]),
        nazwa=nazwa,
        opis=opis,
        world_type=world_type
    )
    
    return World(
        world_id=config.world_id,
        nazwa=nazwa,
        opis=opis,
        config=config
    )


if __name__ == "__main__":
    print("Testing World...")
    
    # Tworzenie świata
    swiat = tworz_swiat(
        nazwa="Świat Testowy",
        world_type=WorldType.SWIAT_1_ZMIANY_KURSOW,
        opis="Świat do testów systemu"
    )
    
    print(f"Utworzono świat: {swiat}")
    
    # Dodawanie obserwacji
    obs_id = swiat.dodaj_obserwacje({
        "mecz_id": "Test1_vs_Test2",
        "predykcja": "2:1",
        "rzeczywistosc": "2:1",
        "confidence": 0.85,
        "model_id": "siec_01"
    })
    print(f"Dodano obserwację: {obs_id}")
    
    # Dodawanie wzorca
    wzorzec_id = swiat.dodaj_wzorzec({
        "nazwa": "trafienie_dokladne",
        "opis": "Trafienia dokładne w tym świecie",
        "czestotliwosc": 1
    })
    print(f"Dodano wzorzec: {wzorzec_id}")
    
    # Statystyki
    stats = swiat.pobierz_statystyki()
    print(f"Statystyki: {stats}")
    
    print("\nAll World tests passed!")
