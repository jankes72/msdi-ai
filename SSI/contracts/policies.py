"""
SSI Data Split Policies - Polityki podziału danych

Wersja: 1.0
Data: 2026-07-31
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto
import random
import numpy as np
from collections import defaultdict


class SplitRatio(Enum):
    """Standardowe proporcje podziału danych (według wymagań: 50% train, 10% validation, 40% observation)."""
    TRAIN = 0.50
    VALIDATION = 0.10
    OBSERVATION = 0.40


@dataclass
class DataSplitPolicy:
    """
    Polityka podziału danych na zbiór treningowy, walidacyjny i obserwacyjny.
    
    Wymagania:
    - Podział musi jawnie rozróżniać 50% trening, 10% walidację i 40% obserwację
    - Polityka musi być spójna w kodzie i dokumentacji
    - Ten sam input i seed muszą dawać powtarzalny wynik
    """
    train_ratio: float = SplitRatio.TRAIN.value  # 50%
    validation_ratio: float = SplitRatio.VALIDATION.value  # 10%
    observation_ratio: float = SplitRatio.OBSERVATION.value  # 40%
    
    policy_name: str = "standard_50_10_40"
    description: str = "Standard split: 50% train, 10% validation, 40% observation"
    
    # Seed für powtarzalność
    random_seed: Optional[int] = None
    
    def __post_init__(self):
        """Walidacja i normalizacja proporcji."""
        self._validate_ratios()
        self._normalize_ratios()
    
    def _validate_ratios(self) -> None:
        """Waliduje proporcje podziału."""
        total = self.train_ratio + self.validation_ratio + self.observation_ratio
        if not 0.99 <= total <= 1.01:  # Dopuszczalna tolerancja 1%
            raise ValueError(
                f"Suma proporcji musi wynosić ~1.0, a jest {total}"
            )
        
        for ratio in [self.train_ratio, self.validation_ratio, self.observation_ratio]:
            if ratio < 0:
                raise ValueError("Proporcje nie mogą być ujemne")
    
    def _normalize_ratios(self) -> None:
        """Normalizuje proporcje, aby suma była riten 1.0."""
        total = self.train_ratio + self.validation_ratio + self.observation_ratio
        if total != 1.0:
            self.train_ratio = self.train_ratio / total
            self.validation_ratio = self.validation_ratio / total
            self.observation_ratio = self.observation_ratio / total
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje politykę do słownika."""
        return {
            "policy_name": self.policy_name,
            "description": self.description,
            "train_ratio": self.train_ratio,
            "validation_ratio": self.validation_ratio,
            "observation_ratio": self.observation_ratio,
            "random_seed": self.random_seed
        }
    
    def get_ratios(self) -> Tuple[float, float, float]:
        """Zwraca proporcje jako tuple (train, validation, observation)."""
        return (self.train_ratio, self.validation_ratio, self.observation_ratio)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataSplitPolicy":
        """Tworzy politykę z słownika."""
        return cls(
            train_ratio=data.get("train_ratio", SplitRatio.TRAIN.value),
            validation_ratio=data.get("validation_ratio", SplitRatio.VALIDATION.value),
            observation_ratio=data.get("observation_ratio", SplitRatio.OBSERVATION.value),
            policy_name=data.get("policy_name", "custom"),
            description=data.get("description", "Custom split policy"),
            random_seed=data.get("random_seed")
        )
    
    @classmethod
    def standard_50_10_40(cls) -> "DataSplitPolicy":
        """Tworzy standardową politykę 50/10/40."""
        return cls(
            train_ratio=SplitRatio.TRAIN.value,
            validation_ratio=SplitRatio.VALIDATION.value,
            observation_ratio=SplitRatio.OBSERVATION.value,
            policy_name="standard_50_10_40",
            description="Standard split: 50% train, 10% validation, 40% observation"
        )
    
    @classmethod
    def train_test_80_20(cls) -> "DataSplitPolicy":
        """Tworzy politykę 80/20 (tylko train i validation)."""
        return cls(
            train_ratio=0.80,
            validation_ratio=0.20,
            observation_ratio=0.00,
            policy_name="train_test_80_20",
            description="80% train, 20% validation"
        )
    
    @classmethod
    def train_validation_test_60_20_20(cls) -> "DataSplitPolicy":
        """Tworzy politykę 60/20/20."""
        return cls(
            train_ratio=0.60,
            validation_ratio=0.20,
            observation_ratio=0.20,
            policy_name="train_validation_test_60_20_20",
            description="60% train, 20% validation, 20% test"
        )


@dataclass
class SplitResult:
    """Wynik podziału danych."""
    train_data: List[Any] = field(default_factory=list)
    validation_data: List[Any] = field(default_factory=list)
    observation_data: List[Any] = field(default_factory=list)
    
    train_indices: List[int] = field(default_factory=list)
    validation_indices: List[int] = field(default_factory=list)
    observation_indices: List[int] = field(default_factory=list)
    
    split_policy: Optional[DataSplitPolicy] = None
    seed: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje wynik do słownika."""
        return {
            "train_size": len(self.train_data),
            "validation_size": len(self.validation_data),
            "observation_size": len(self.observation_data),
            "train_indices": self.train_indices,
            "validation_indices": self.validation_indices,
            "observation_indices": self.observation_indices,
            "policy": self.split_policy.to_dict() if self.split_policy else None,
            "seed": self.seed
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Zwraca statystyki podziału."""
        return {
            "total": len(self.train_data) + len(self.validation_data) + len(self.observation_data),
            "train": {
                "count": len(self.train_data),
                "percentage": len(self.train_data) / self.get_total() * 100 if self.get_total() > 0 else 0
            },
            "validation": {
                "count": len(self.validation_data),
                "percentage": len(self.validation_data) / self.get_total() * 100 if self.get_total() > 0 else 0
            },
            "observation": {
                "count": len(self.observation_data),
                "percentage": len(self.observation_data) / self.get_total() * 100 if self.get_total() > 0 else 0
            }
        }
    
    def get_total(self) -> int:
        """Zwraca łączną liczbę elementów."""
        return len(self.train_data) + len(self.validation_data) + len(self.observation_data)


@dataclass
class DataSplitter:
    """
    Narzędzie do dzielenia danych według polityki.
    
    Zapewnia powtarzalność przy tym samym seed.
    """
    policy: DataSplitPolicy
    
    def split_data(
        self, 
        data: List[Any], 
        seed: Optional[int] = None
    ) -> SplitResult:
        """
        Dzieli dane na zbiór treningowy, walidacyjny i obserwacyjny.
        
        Args:
            data: Lista danych do podziału
            seed: Seed dla powtarzalności (jeśli None, używa policy.random_seed)
            
        Returns:
            SplitResult z podzielonymi danymi
        """
        if seed is None:
            seed = self.policy.random_seed
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Tasuj dane dla losowego podziału
        indices = list(range(len(data)))
        random.shuffle(indices)
        
        # Oblicz rozmiary zbiorów
        total = len(data)
        train_size = int(total * self.policy.train_ratio)
        validation_size = int(total * self.policy.validation_ratio)
        # observation_size = total - train_size - validation_size
        
        # Podział indeksów
        train_indices = indices[:train_size]
        validation_indices = indices[train_size:train_size + validation_size]
        observation_indices = indices[train_size + validation_size:]
        
        # Pobierz dane
        train_data = [data[i] for i in train_indices]
        validation_data = [data[i] for i in validation_indices]
        observation_data = [data[i] for i in observation_indices]
        
        return SplitResult(
            train_data=train_data,
            validation_data=validation_data,
            observation_data=observation_data,
            train_indices=train_indices,
            validation_indices=validation_indices,
            observation_indices=observation_indices,
            split_policy=self.policy,
            seed=seed
        )
    
    def split_data_stratified(
        self,
        data: List[Any],
        labels: List[Any],
        seed: Optional[int] = None
    ) -> SplitResult:
        """
        Dzieli dane stratyfikowanie (zachowując proporcje klas).
        
        Args:
            data: Lista danych do podziału
            labels: Lista etykiet odpowiednich do danych
            seed: Seed dla powtarzalności
            
        Returns:
            SplitResult z podzielonymi danymi
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Grupuj po etykietach
        label_groups = defaultdict(list)
        for idx, label in enumerate(labels):
            label_groups[label].append(idx)
        
        train_indices = []
        validation_indices = []
        observation_indices = []
        
        # Podział dla każdej grupy
        for label, indices in label_groups.items():
            random.shuffle(indices)
            train_size = int(len(indices) * self.policy.train_ratio)
            validation_size = int(len(indices) * self.policy.validation_ratio)
            
            train_indices.extend(indices[:train_size])
            validation_indices.extend(indices[train_size:train_size + validation_size])
            observation_indices.extend(indices[train_size + validation_size:])
        
        # Pobierz dane
        train_data = [data[i] for i in train_indices]
        validation_data = [data[i] for i in validation_indices]
        observation_data = [data[i] for i in observation_indices]
        
        return SplitResult(
            train_data=train_data,
            validation_data=validation_data,
            observation_data=observation_data,
            train_indices=train_indices,
            validation_indices=validation_indices,
            observation_indices=observation_indices,
            split_policy=self.policy,
            seed=seed
        )
    
    def split_by_group(
        self,
        data: List[Any],
        group_key_func: callable,
        seed: Optional[int] = None
    ) -> Dict[str, SplitResult]:
        """
        Dzieli dane pogrupowane według klucza.
        
        Args:
            data: Lista danych do podziału
            group_key_func: Funkcja zwracająca klucz grupy dla elementu
            seed: Seed dla powtarzalności
            
        Returns:
            Słownik: klucz grupy -> SplitResult
        """
        groups = defaultdict(list)
        for item in data:
            key = group_key_func(item)
            groups[key].append(item)
        
        results = {}
        for key, group_data in groups.items():
            result = self.split_data(group_data, seed)
            results[key] = result
        
        return results


def standard_split(
    data: List[Any],
    seed: Optional[int] = None
) -> SplitResult:
    """
    Funkcja wygodna - dzieli dane według standardowej polityki 50/10/40.
    
    Args:
        data: Lista danych do podziału
        seed: Seed dla powtarzalności
        
    Returns:
        SplitResult z podzielonymi danymi
    """
    splitter = DataSplitter(DataSplitPolicy.standard_50_10_40())
    return splitter.split_data(data, seed)


def validate_split_result(
    result: SplitResult,
    policy: DataSplitPolicy,
    tolerance: float = 0.01
) -> bool:
    """
    Waliduje, czy podział jest zgodny z polityką.
    
    Args:
        result: Wynik podziału
        policy: Polityka podziału
        tolerance: Tolerancja odchylenia w jej
        
    Returns:
        True jeśli podział jest poprawny
        
    Raises:
        ValueError: Jeśli podział nie jest zgodny z polityką
    """
    total = result.get_total()
    if total == 0:
        raise ValueError("Brak danych do walidacji")
    
    expected_train = total * policy.train_ratio
    expected_validation = total * policy.validation_ratio
    expected_observation = total * policy.observation_ratio
    
    actual_train = len(result.train_data)
    actual_validation = len(result.validation_data)
    actual_observation = len(result.observation_data)
    
    # Sprawdź czy rozmiary są zgodne z oczekiwaniami (z tolerancją)
    if abs(actual_train - expected_train) > tolerance * total:
        raise ValueError(
            f"Rozmiar zbioru treningowego: oczekiwano ~{expected_train}, a jest {actual_train}"
        )
    if abs(actual_validation - expected_validation) > tolerance * total:
        raise ValueError(
            f"Rozmiar zbioru walidacyjnego: oczekiwano ~{expected_validation}, a jest {actual_validation}"
        )
    if abs(actual_observation - expected_observation) > tolerance * total:
        raise ValueError(
            f"Rozmiar zbioru obserwacyjnego: oczekiwano ~{expected_observation}, a jest {actual_observation}"
        )
    
    return True
