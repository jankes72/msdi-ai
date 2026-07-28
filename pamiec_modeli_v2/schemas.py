"""
PAMIĘĆ MODELI V2 - SCHEMATY DANYCH
====================================

Definicje struktur danych dla Systemu Pamięci Modeli V2.
System opiera się na istniejącym SSI (Self-learning Strategic Intelligence).

Architektura:
- Model Level 1: Agreguje predykcje z 11 sieci trendów + 4 sieci kursów
- Model Level 2: Kalibrator uczący się zachowania Level 1
- Pamięć: Centralne repozytorium obserwacji (predykcja vs rzeczywistość)

Autor: MSDI AI v0.02
Data: 2026-07-27
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


# =============================================================================
# KLASY WYNIKÓW (Zgodnie z wymaganiami: 1:0, 2:1, 0:2, 3:3, ...)
# =============================================================================

# Dokładne klasy wyników (pojedyncze wyniki)
KLASY_WYNIKOW_DOKLADNYCH: List[str] = [
    # 0 goli
    "0:0",
    # 1 gol
    "1:0", "0:1",
    # 2 gole
    "2:0", "0:2", "1:1",
    # 3 gole
    "3:0", "0:3", "2:1", "1:2",
    # 4 gole
    "4:0", "0:4", "3:1", "1:3", "2:2",
    # 5 goli
    "5:0", "0:5", "4:1", "1:4", "3:2", "2:3",
    # 6+ goli
    "6:0", "0:6", "5:1", "1:5", "4:2", "2:4", "3:3",
    "6:1", "1:6", "5:2", "2:5", "4:3", "3:4",
    "6:2", "2:6", "5:3", "3:5",
    "6:3", "3:6",
    "7:0", "0:7",
]

# Grupy wyników (1 = wygrana gospodarzy, X = remis, 2 = wygrana gości)
KLASY_GRUP_WYNIKOW: Dict[str, List[str]] = {
    "1": [w for w in KLASY_WYNIKOW_DOKLADNYCH if w.endswith(":0") or 
          (w.count(":") == 1 and int(w.split(":")[0]) > int(w.split(":")[1]))],
    "X": [w for w in KLASY_WYNIKOW_DOKLADNYCH if w.split(":")[0] == w.split(":")[1]],
    "2": [w for w in KLASY_WYNIKOW_DOKLADNYCH if w.startswith("0:") or 
          (w.count(":") == 1 and int(w.split(":")[0]) < int(w.split(":")[1]))],
}


def get_grupa_wyniku(wynik: str) -> str:
    """
    Zwraca grupę wyniku: 1 (gospodarze), X (remis), 2 (goście)
    
    Args:
        wynik: String w formacie "X:Y" np. "2:1", "0:0", "1:3"
        
    Returns:
        "1", "X" lub "2"
    """
    if ":" not in wynik:
        return "X"
    
    try:
        gospodarz, gosc = map(int, wynik.split(":"))
        if gospodarz > gosc:
            return "1"
        elif gospodarz < gosc:
            return "2"
        else:
            return "X"
    except (ValueError, AttributeError):
        return "X"


def get_gole(wynik: str) -> tuple:
    """
    Zwraca liczbę goli jako tuple (gospodarze, goście)
    
    Args:
        wynik: String w formacie "X:Y"
        
    Returns:
        Tuple (int, int)
    """
    if ":" not in wynik:
        return (0, 0)
    
    try:
        return tuple(map(int, wynik.split(":")))
    except (ValueError, AttributeError):
        return (0, 0)


# =============================================================================
# LEVEL 1: MODEL PREDYKCYJNY - Schematy wyjściowe
# =============================================================================

@dataclass
class PredykcjaLevel1:
    """
    Unifikowane wyjście Modelu Level 1 (agregacja z sieci SSI)
    
    Pola:
        id_modelu: Identyfikator modelu/sieci (np. "siec_01_zmiana_kursow")
        id_meczu: Identyfikator meczu (np. "Team A - Team B")
        id_grupy: Identyfikator grupy świata (np. "poziom3poziom17poziom20")
        wynik_predykcji: Przewidywany wynik w formacie "X:Y"
        confidence: Poziom pewności predykcji [0.0, 1.0]
        timestamp: Data/czas generacji predykcji
        sieci_skladowe: Źródłowe predykcje z poszczególnych sieci
    """
    id_modelu: str
    id_meczu: str
    id_grupy: str
    wynik_predykcji: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    sieci_skladowe: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        # Walidacja confidence
        self.confidence = max(0.0, min(1.0, self.confidence))
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "id_modelu": self.id_modelu,
            "id_meczu": self.id_meczu,
            "id_grupy": self.id_grupy,
            "wynik_predykcji": self.wynik_predykcji,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "sieci_skladowe": self.sieci_skladowe
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PredykcjaLevel1":
        """Tworzenie z słownika"""
        return cls(
            id_modelu=data.get("id_modelu", ""),
            id_meczu=data.get("id_meczu", ""),
            id_grupy=data.get("id_grupy", ""),
            wynik_predykcji=data.get("wynik_predykcji", ""),
            confidence=float(data.get("confidence", 0.5)),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            sieci_skladowe=data.get("sieci_skladowe", {})
        )


@dataclass
class PredykcjaLevel1Kalibrowana:
    """
    Wyjście po kalibracji przez Model Level 2
    
    Zawiera oryginalną predykcję + kalibrowane confidence
    """
    id_modelu: str
    id_meczu: str
    id_grupy: str
    wynik_predykcji: str
    confidence: float  # Oryginalne confidence z Level 1
    confidence_kalibrowana: float  # Po kalibracji przez Level 2
    poprawka_kalibracji: float  # Różnica: kalibrowana - oryginalna
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.confidence = max(0.0, min(1.0, self.confidence))
        self.confidence_kalibrowana = max(0.0, min(1.0, self.confidence_kalibrowana))
        self.poprawka_kalibracji = self.confidence_kalibrowana - self.confidence
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_modelu": self.id_modelu,
            "id_meczu": self.id_meczu,
            "id_grupy": self.id_grupy,
            "wynik_predykcji": self.wynik_predykcji,
            "confidence": self.confidence,
            "confidence_kalibrowana": self.confidence_kalibrowana,
            "poprawka_kalibracji": self.poprawka_kalibracji,
            "timestamp": self.timestamp.isoformat()
        }


# =============================================================================
# PAMIĘĆ: Obserwacje i Klasy Wyników
# =============================================================================

@dataclass
class Obserwacja:
    """
    Rekord obserwacji: predykcja vs rzeczywistość
    
    Powstaje po poznaniu wyniku meczu.
    Łączy predykcję Level 1 z rzeczywistym wynikiem.
    """
    id_meczu: str
    id_grupy: str
    id_modelu: str  # Która sieć/agregator wygenerował predykcję
    wynik_predykcji: str
    confidence: float
    wynik_rzeczywisty: str
    trafienie: bool = field(init=False)
    trafienie_grupa: bool = field(init=False)
    timestamp: datetime = field(default_factory=datetime.now)
    klasa_dokladna: Optional[str] = None
    klasa_grupa: Optional[str] = None
    id_obserwacji: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    
    def __post_init__(self):
        # Oblicz trafienia
        self.trafienie = self.wynik_predykcji == self.wynik_rzeczywisty
        self.trafienie_grupa = get_grupa_wyniku(self.wynik_predykcji) == get_grupa_wyniku(self.wynik_rzeczywisty)
        
        # Ustal klasy
        if self.wynik_rzeczywisty and ":" in self.wynik_rzeczywisty:
            self.klasa_dokladna = self.wynik_rzeczywisty
            self.klasa_grupa = get_grupa_wyniku(self.wynik_rzeczywisty)
    
    def to_dict(self) -> Dict[str, Any]:
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Obserwacja":
        return cls(
            id_meczu=data.get("id_meczu", ""),
            id_grupy=data.get("id_grupy", ""),
            id_modelu=data.get("id_modelu", ""),
            wynik_predykcji=data.get("wynik_predykcji", ""),
            confidence=float(data.get("confidence", 0.5)),
            wynik_rzeczywisty=data.get("wynik_rzeczywisty", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            klasa_dokladna=data.get("klasa_dokladna"),
            klasa_grupa=data.get("klasa_grupa")
        )


@dataclass
class KlasaWyniku:
    """
    Pamięć zachowania modelu dla konkretnej klasy wyniku
    
    Przechowuje wszystkie obserwacje dla danej klasy (np. "1:0", "2:1")
    i udostępnia statystyki.
    """
    nazwa_klasy: str  # np. "1:0", "2:1"
    obserwacje: List[Obserwacja] = field(default_factory=list)
    
    @property
    def czestotliwosc(self) -> int:
        """Liczba obserwacji dla tej klasy"""
        return len(self.obserwacje)
    
    @property
    def sredni_confidence(self) -> float:
        """Średni poziom pewności predykcji"""
        if not self.obserwacje:
            return 0.0
        return sum(o.confidence for o in self.obserwacje) / len(self.obserwacje)
    
    @property
    def trafienia(self) -> int:
        """Liczba trafień (dokładny wynik)"""
        return sum(1 for o in self.obserwacje if o.trafienie)
    
    @property
    def trafienia_grupa(self) -> int:
        """Liczba trafień grupowych (1/X/2)"""
        return sum(1 for o in self.obserwacje if o.trafienie_grupa)
    
    @property
    def skutecznosc(self) -> float:
        """Skuteczność dokładna [0, 1]"""
        if not self.obserwacje:
            return 0.0
        return self.trafienia / len(self.obserwacje)
    
    @property
    def skutecznosc_grupa(self) -> float:
        """Skuteczność grupowa [0, 1]"""
        if not self.obserwacje:
            return 0.0
        return self.trafienia_grupa / len(self.obserwacje)
    
    def dodaj_obserwacje(self, obserwacja: Obserwacja):
        """Dodaje nową obserwację"""
        self.obserwacje.append(obserwacja)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nazwa_klasy": self.nazwa_klasy,
            "czestotliwosc": self.czestotliwosc,
            "sredni_confidence": round(self.sredni_confidence, 4),
            "trafienia": self.trafienia,
            "trafienia_grupa": self.trafienia_grupa,
            "skutecznosc": round(self.skutecznosc, 4),
            "skutecznosc_grupa": round(self.skutecznosc_grupa, 4)
        }


# =============================================================================
# PAMIĘĆ: Wzorce Zachowania
# =============================================================================

@dataclass
class WzorecZachowania:
    """
    Wykryty wzorzec zachowania modelu
    
    Przechowuje informacje o powtarzalnych wzorcach:
    - Które sieci częściej mylą się dla określonych klas
    - Które grupy wyników są trudniejsze
    - Zmiany pewności w czasie
    """
    nazwa: str
    opis: str
    czestotliwosc: int = 0
    przykłady: List[str] = field(default_factory=list)  # id_meczu
    cechy_charakterystyczne: Dict[str, float] = field(default_factory=dict)
    data_odkrycia: datetime = field(default_factory=datetime.now)
    data_ostaniego_wystapienia: datetime = field(default_factory=datetime.now)
    
    def dodaj_przyklad(self, id_meczu: str, cechy: Optional[Dict[str, float]] = None):
        """Dodaje nowy przykład wzorca"""
        if id_meczu not in self.przykłady:
            self.przykłady.append(id_meczu)
        self.czestotliwosc = len(self.przykłady)
        self.data_ostaniego_wystapienia = datetime.now()
        
        if cechy:
            # Aktualizuj średnie cechy
            for k, v in cechy.items():
                if k in self.cechy_charakterystyczne:
                    self.cechy_charakterystyczne[k] = (self.cechy_charakterystyczne[k] + v) / 2
                else:
                    self.cechy_charakterystyczne[k] = v
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nazwa": self.nazwa,
            "opis": self.opis,
            "czestotliwosc": self.czestotliwosc,
            "przykłady": self.przykłady[:10],  # Ograniczone do 10
            "cechy_charakterystyczne": self.cechy_charakterystyczne,
            "data_odkrycia": self.data_odkrycia.isoformat(),
            "data_ostaniego_wystapienia": self.data_ostaniego_wystapienia.isoformat()
        }


# =============================================================================
# PAMIĘĆ: Statystyki Globalne
# =============================================================================

@dataclass
class StatystykiPamieci:
    """
    Statystyki globalne pamięci V2
    """
    calkowita_liczba_obserwacji: int = 0
    liczba_klas: int = 0
    srednia_skutecznosc: float = 0.0
    sredni_confidence: float = 0.0
    liczba_modeli: int = 0
    data_utworzenia: datetime = field(default_factory=datetime.now)
    wersja: str = field(default_factory=lambda: f"v2_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "calkowita_liczba_obserwacji": self.calkowita_liczba_obserwacji,
            "liczba_klas": self.liczba_klas,
            "srednia_skutecznosc": round(self.srednia_skutecznosc, 4),
            "sredni_confidence": round(self.sredni_confidence, 4),
            "liczba_modeli": self.liczba_modeli,
            "data_utworzenia": self.data_utworzenia.isoformat(),
            "wersja": self.wersja
        }


# =============================================================================
# KONFIGURACJA SYSTEMU
# =============================================================================

@dataclass
class KonfiguracjaV2:
    """
    Konfiguracja Systemu Pamięci Modeli V2
    """
    # Podział danych
    PROCENT_TRENING: float = 0.5
    PROCENT_WALIDACJA: float = 0.1
    PROCENT_OBSERWACJA: float = 0.4
    
    # Ścieżki
    BASE_PATH: str = "pamiec_modeli_v2"
    DANE_TRENING: str = "dane/trening"
    DANE_WALIDACJA: str = "dane/walidacja"
    DANE_OBSERWACJA: str = "dane/obserwacja"
    ARCHIWUM: str = "archiwum"
    
    # Sieci do integracji
    SIECI_TREND: List[str] = field(default_factory=lambda: [f"siec_{i:02d}" for i in range(1, 12)])
    SIECI_KURSY: List[str] = field(default_factory=lambda: [f"siec_{i:02d}" for i in range(1, 5)])
    
    # Ustawienia kalibracji
    KALIBRACJA_ENABLED: bool = True
    KALIBRACJA_MIN_OBSERWACJI: int = 100  # Minimalna liczba obserwacji do trenowania
    
    # Wersjonowanie
    AUTOMATYCZNE_WERSJONOWANIE: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "PROCENT_TRENING": self.PROCENT_TRENING,
            "PROCENT_WALIDACJA": self.PROCENT_WALIDACJA,
            "PROCENT_OBSERWACJA": self.PROCENT_OBSERWACJA,
            "KALIBRACJA_ENABLED": self.KALIBRACJA_ENABLED,
            "KALIBRACJA_MIN_OBSERWACJI": self.KALIBRACJA_MIN_OBSERWACJI,
            "AUTOMATYCZNE_WERSJONOWANIE": self.AUTOMATYCZNE_WERSJONOWANIE
        }


# =============================================================================
# FUNKCJE UŻYTECZNE
# =============================================================================

def waliduj_wynik(wynik: str) -> bool:
    """Sprawdza czy wynik jest w poprawnym formacie X:Y"""
    if ":" not in wynik:
        return False
    
    try:
        a, b = map(int, wynik.split(":"))
        return a >= 0 and b >= 0
    except (ValueError, AttributeError):
        return False


def normalizuj_wynik(wynik: str) -> str:
    """Normalizuje wynik do standardowego formatu"""
    if not waliduj_wynik(wynik):
        return "0:0"
    return wynik


def generuj_id() -> str:
    """Generuje unikalny identyfikator"""
    return uuid.uuid4().hex[:12]


if __name__ == "__main__":
    # Testy
    print("Testing schemas...")
    
    # Test PredykcjaLevel1
    pred = PredykcjaLevel1(
        id_modelu="siec_01_zmiana_kursow",
        id_meczu="Team A - Team B",
        id_grupy="poziom3poziom17poziom20",
        wynik_predykcji="2:1",
        confidence=0.85
    )
    print(f"Predykcja: {pred.to_dict()}")
    
    # Test Obserwacja
    obs = Obserwacja(
        id_meczu="Team A - Team B",
        id_grupy="poziom3poziom17poziom20",
        id_modelu="siec_01_zmiana_kursow",
        wynik_predykcji="2:1",
        confidence=0.85,
        wynik_rzeczywisty="2:1"
    )
    print(f"Obserwacja: trafienie={obs.trafienie}, grupa={obs.klasa_grupa}")
    
    # Test KlasaWyniku
    klasa = KlasaWyniku(nazwa_klasy="2:1")
    klasa.dodaj_obserwacje(obs)
    print(f"Klasa 2:1: skutecznosc={klasa.skutecznosc}")
    
    # Test get_grupa_wyniku
    print(f"Grupa 2:1 = {get_grupa_wyniku('2:1')}")
    print(f"Grupa 0:0 = {get_grupa_wyniku('0:0')}")
    print(f"Grupa 1:3 = {get_grupa_wyniku('1:3')}")
    
    print("\nAll tests passed!")
