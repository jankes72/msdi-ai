"""
SSI Contract Migration - Polityka kompatybilności i migracji kontraktów

Wersja: 1.0
Data: 2026-07-31
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Type
from enum import Enum, auto
from datetime import datetime
import logging

from .data_contracts import (
    V2ToV3Contract,
    V3ToV4Contract,
    DataContract,
    ContractVersion,
    ContractValidationError,
)
from .validation import ContractValidator, ContractMigrationPath

logger = logging.getLogger(__name__)


class CompatibilityLevel(Enum):
    """Poziomy kompatybilności."""
    FULL = auto()        # Pełna kompatybilność dwukierunkowa
    BACKWARD = auto()    # Kompatybilność wsteczna (nowsze zumeist z starszymi)
    FORWARD = auto()     # Kompatybilność w przód (starsze mogą odczytywać nowsze)
    PARTIAL = auto()     # Częściowa kompatybilność (wymaga konwersji)
    NONE = auto()        # Brak kompatybilności (wymaga migracji)


class MigrationStrategy(Enum):
    """Strategie migracji."""
    AUTOMATIC = auto()   # Migracja automatyczna
    MANUAL = auto()      # Migracja ręczna
    CONVERT = auto()     # Konwersja formatu
    SKIP = auto()        # Pomijanie niekompatybilnych danych
    FAIL = auto()        # Zgłaszanie błędu


@dataclass
class CompatibilityRule:
    """Reguła kompatybilności między wersjami."""
    source_version: str
    target_version: str
    compatibility_level: CompatibilityLevel = CompatibilityLevel.NONE
    migration_strategy: MigrationStrategy = MigrationStrategy.FAIL
    converter: Optional[Callable] = None
    description: str = ""
    
    def can_migrate(self) -> bool:
        """Sprawdza czy migracja jest możliwa."""
        if self.compatibility_level in [CompatibilityLevel.FULL, CompatibilityLevel.PARTIAL]:
            return self.migration_strategy in [MigrationStrategy.AUTOMATIC, MigrationStrategy.CONVERT]
        return False
    
    def requires_conversion(self) -> bool:
        """Sprawdza czy potrzebna jest konwersja."""
        return self.migration_strategy == MigrationStrategy.CONVERT


@dataclass
class CompatibilityPolicy:
    """
    Polityka kompatybilności kontraktów.
    
    Definiuje reguły kompatybilności między wersjami kontraktów
    i strategie migracji.
    """
    name: str = "default_compatibility_policy"
    description: str = "Default compatibility policy for SSI contracts"
    
    # Reguły kompatybilności
    rules: List[CompatibilityRule] = field(default_factory=list)
    
    # Domyślne strategie
    default_strategy: MigrationStrategy = MigrationStrategy.CONVERT
    default_level: CompatibilityLevel = CompatibilityLevel.BACKWARD
    
    def __post_init__(self):
        """Dodaj domyślne reguły."""
        if not self.rules:
            self._add_default_rules()
    
    def _add_default_rules(self) -> None:
        """Dodaje domyślne reguły kompatybilności."""
        # V2ToV3Contract rules
        self.rules.append(CompatibilityRule(
            source_version="1.0",
            target_version="1.0",
            compatibility_level=CompatibilityLevel.FULL,
            migration_strategy=MigrationStrategy.AUTOMATIC,
            description="V1.0 jest w pełni kompatybilne z V1.0"
        ))
        
        self.rules.append(CompatibilityRule(
            source_version="1.0",
            target_version="1.1",
            compatibility_level=CompatibilityLevel.BACKWARD,
            migration_strategy=MigrationStrategy.CONVERT,
            converter=self._convert_v1_0_to_v1_1,
            description="V1.0 jest kompatybilne wstecz z V1.1 (wymaga konwersji)"
        ))
        
        # V3ToV4Contract rules
        self.rules.append(CompatibilityRule(
            source_version="1.0",
            target_version="1.0",
            compatibility_level=CompatibilityLevel.FULL,
            migration_strategy=MigrationStrategy.AUTOMATIC,
            description="V3ToV4 V1.0 jest w pełni kompatybilne z V1.0"
        ))
        
        # Niekompatybilne wersje
        self.rules.append(CompatibilityRule(
            source_version="1.0",
            target_version="2.0",
            compatibility_level=CompatibilityLevel.NONE,
            migration_strategy=MigrationStrategy.FAIL,
            description="V1.0 nie jest kompatybilne z V2.0"
        ))
        
        self.rules.append(CompatibilityRule(
            source_version="1.1",
            target_version="2.0",
            compatibility_level=CompatibilityLevel.NONE,
            migration_strategy=MigrationStrategy.FAIL,
            description="V1.1 nie jest kompatybilne z V2.0"
        ))
        
        self.rules.append(CompatibilityRule(
            source_version="2.0",
            target_version="1.0",
            compatibility_level=CompatibilityLevel.NONE,
            migration_strategy=MigrationStrategy.FAIL,
            description="V2.0 nie jest kompatybilne z V1.0"
        ))
        
        self.rules.append(CompatibilityRule(
            source_version="2.0",
            target_version="1.1",
            compatibility_level=CompatibilityLevel.NONE,
            migration_strategy=MigrationStrategy.FAIL,
            description="V2.0 nie jest kompatybilne z V1.1"
        ))
    
    @staticmethod
    def _convert_v1_0_to_v1_1(data: Dict[str, Any]) -> Dict[str, Any]:
        """Konwertuje kontrakt z V1.0 na V1.1."""
        # Dodaj brakujące pola z wartościami domyślnymi
        converted = data.copy()
        
        if "metadata" not in converted:
            converted["metadata"] = {
                "version": "1.1",
                "contract_id": "",
                "timestamp": "",
                "source": "",
                "target": ""
            }
        
        if "data_version" not in converted:
            converted["data_version"] = ""
        
        return converted
    
    def get_compatibility(
        self, 
        source_version: str, 
        target_version: str
    ) -> CompatibilityLevel:
        """
        Zwraca poziom kompatybilności między wersjami.
        
        Args:
            source_version: Wersja źródłowa
            target_version: Wersja docelowa
            
        Returns:
            Poziom kompatybilności
        """
        # Szukaj reguły dla konkretnych wersji
        for rule in self.rules:
            if (rule.source_version == source_version and 
                rule.target_version == target_version):
                return rule.compatibility_level
        
        # Szukaj reguły odwrotnej
        for rule in self.rules:
            if (rule.source_version == target_version and 
                rule.target_version == source_version):
                # Jeśli kompatybilność jest pełna, zwróć ją
                if rule.compatibility_level == CompatibilityLevel.FULL:
                    return CompatibilityLevel.FULL
                # Inaczej zwróć partial
                return CompatibilityLevel.PARTIAL
        
        # Domyślna kompatybilność
        return self.default_level
    
    def get_migration_strategy(
        self, 
        source_version: str, 
        target_version: str
    ) -> MigrationStrategy:
        """
        Zwraca strategię migracji między wersjami.
        
        Args:
            source_version: Wersja źródłowa
            target_version: Wersja docelowa
            
        Returns:
            Strategia migracji
        """
        for rule in self.rules:
            if (rule.source_version == source_version and 
                rule.target_version == target_version):
                return rule.migration_strategy
        
        return self.default_strategy
    
    def get_converter(
        self, 
        source_version: str, 
        target_version: str
    ) -> Optional[Callable]:
        """
        Zwraca funkcję konwersji między wersjami.
        
        Args:
            source_version: Wersja źródłowa
            target_version: Wersja docelowa
            
        Returns:
            Funkcja konwersji lub None
        """
        for rule in self.rules:
            if (rule.source_version == source_version and 
                rule.target_version == target_version):
                return rule.converter
        return None
    
    def can_migrate(
        self, 
        source_version: str, 
        target_version: str
    ) -> bool:
        """
        Sprawdza czy migracja między wersjami jest możliwa.
        
        Args:
            source_version: Wersja źródłowa
            target_version: Wersja docelowa
            
        Returns:
            True jeśli migracja jest możliwa
        """
        strategy = self.get_migration_strategy(source_version, target_version)
        return strategy in [MigrationStrategy.AUTOMATIC, MigrationStrategy.CONVERT]
    
    def migrate_contract(
        self, 
        contract: DataContract, 
        target_version: str
    ) -> DataContract:
        """
        Konwertuje kontrakt do docelowej wersji.
        
        Args:
            contract: Kontrakt do konwersji
            target_version: Docelowa wersja
            
        Returns:
            Skonwertowany kontrakt
            
        Raises:
            ContractValidationError: Jeśli migracja nie jest możliwa
        """
        source_version = contract.metadata.version.value
        
        # Sprawdź czy migracja jest możliwa
        if not self.can_migrate(source_version, target_version):
            raise ContractValidationError(
                type(contract).__name__,
                "version",
                source_version,
                f"Migracja z {source_version} do {target_version} nie jest możliwa"
            )
        
        # Jeśli wersje są takie same, zwróć oryginał
        if source_version == target_version:
            return contract
        
        # uzyskaj konwerter
        converter = self.get_converter(source_version, target_version)
        
        if converter is None:
            raise ContractValidationError(
                type(contract).__name__,
                "converter",
                f"{source_version}_to_{target_version}",
                "Brak konwertera dla tych wersji"
            )
        
        # Konwersja
        contract_dict = contract.to_dict()
        converted_dict = converter(contract_dict)
        
        # Zaktualizuj wersję
        converted_dict["metadata"]["version"] = target_version
        
        # Utwórz nowy kontrakt
        if isinstance(contract, V2ToV3Contract):
            return V2ToV3Contract.from_dict(converted_dict)
        elif isinstance(contract, V3ToV4Contract):
            return V3ToV4Contract.from_dict(converted_dict)
        else:
            raise ContractValidationError(
                type(contract).__name__,
                "conversion",
                "unknown",
                f"Nieznany typ kontraktu: {type(contract).__name__}"
            )


@dataclass
class MigrationPolicy:
    """
    Polityka migracji kontraktów.
    
    Definiuje ogólne zasady migracji między wersjami kontraktów.
    """
    compatibility_policy: CompatibilityPolicy = field(
        default_factory=CompatibilityPolicy
    )
    
    # Ustawienia ogólne
    allow_automatic_migration: bool = True
    allow_version_mismatch: bool = False
    log_migration_events: bool = True
    
    # Historia migracji
    migration_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def migrate(
        self, 
        contract: DataContract, 
        target_version: str
    ) -> DataContract:
        """
        Wykonywa migrację kontraktu do docelowej wersji.
        
        Args:
            contract: Kontrakt do migracji
            target_version: Docelowa wersja
            
        Returns:
            Skonwertowany kontrakt
        """
        source_version = contract.metadata.version.value
        
        if self.log_migration_events:
            logger.info(f"Migrating contract from {source_version} to {target_version}")
        
        result = self.compatibility_policy.migrate_contract(contract, target_version)
        
        # Zarejestruj migrację
        self._record_migration(contract, target_version)
        
        return result
    
    def _record_migration(
        self, 
        contract: DataContract, 
        target_version: str
    ) -> None:
        """Rejestruje migrację w historii."""
        if len(self.migration_history) >= 1000:
            self.migration_history = self.migration_history[-500:]
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "contract_type": type(contract).__name__,
            "source_version": contract.metadata.version.value,
            "target_version": target_version,
            "contract_id": contract.metadata.contract_id
        }
        self.migration_history.append(record)
    
    def validate_compatibility(
        self, 
        contract: DataContract, 
        expected_version: str
    ) -> bool:
        """
        Waliduje kompatybilność kontraktu z oczekiwaną wersją.
        
        Args:
            contract: Kontrakt do sprawdzenia
            expected_version: Oczekiwana wersja
            
        Returns:
            True jeśli kontrakt jest kompatybilny
        """
        source_version = contract.metadata.version.value
        
        if source_version == expected_version:
            return True
        
        level = self.compatibility_policy.get_compatibility(source_version, expected_version)
        
        if level in [CompatibilityLevel.FULL, CompatibilityLevel.BACKWARD]:
            return True
        
        if self.allow_version_mismatch:
            logger.warning(
                f"Version mismatch: contract is {source_version}, expected {expected_version}"
            )
            return True
        
        return False


def create_default_compatibility_policy() -> CompatibilityPolicy:
    """Tworzy domyślną politykę kompatybilności."""
    return CompatibilityPolicy()


def create_default_migration_policy() -> MigrationPolicy:
    """Tworzy domyślną politykę migracji."""
    return MigrationPolicy()
