"""
SSI Contract Validation - Walidacja kontraktów danych

Wersja: 1.0
Data: 2026-07-31
"""

from typing import Dict, List, Any, Optional, Type, Union, Callable, TypeVar
from dataclasses import is_dataclass, fields
import json

from .data_contracts import (
    V2ToV3Contract,
    V3ToV4Contract,
    DataContract,
    ContractValidationError,
    ContractVersion,
    ContractMetadata,
)
from .version_identifiers import (
    DataVersion,
    ModelVersion,
    ConfigVersion,
    ResultVersion,
    LineageInfo,
)

T = TypeVar('T', bound=DataContract)


class ContractValidator:
    """
    Walidator kontraktów danych.
    
    Obsługuje:
    - Walidację struktury kontraktów
    - Walidację zakresów wartości
    - Walidację wersji kompatybilności
    - Walidację lineage
    """
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, contract: DataContract) -> bool:
        """
        Waliduje kontrakt.
        
        Args:
            contract: Kontrakt do walidacji
            
        Returns:
            True jeśli kontrakt jest poprawny
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            # Walidacja ogólna
            self._validate_metadata(contract)
            self._validate_structure(contract)
            self._validate_ranges(contract)
            self._validate_versions(contract)
            self._validate_lineage(contract)
            
            return len(self.errors) == 0
            
        except ContractValidationError as e:
            self.errors.append(str(e))
            return False
        except Exception as e:
            self.errors.append(f"Nieoczekiwany błąd walidacji: {e}")
            return False
    
    def _validate_metadata(self, contract: DataContract) -> None:
        """Waliduje metadane kontraktu."""
        try:
            contract.metadata.validate()
        except ContractValidationError as e:
            self.errors.append(str(e))
    
    def _validate_structure(self, contract: DataContract) -> None:
        """Waliduje strukturę kontraktu (obecność wymaganych pól)."""
        # Sprawdź czy kontrakt ma wymagane atrybuty
        if not hasattr(contract, 'metadata'):
            self.errors.append("Kontrakt nie ma atrybutu 'metadata'")
        
        if not hasattr(contract, 'validate'):
            self.errors.append("Kontrakt nie ma metody 'validate'")
        
        if not hasattr(contract, 'to_dict'):
            self.warnings.append("Kontrakt nie ma metody 'to_dict' (nie jest serializowalny)")
    
    def _validate_ranges(self, contract: DataContract) -> None:
        """Waliduje zakresy wartości numerycznych."""
        # Walidacja dla V2ToV3Contract
        if isinstance(contract, V2ToV3Contract):
            for obs in contract.observations:
                try:
                    obs.validate()
                except ContractValidationError as e:
                    self.errors.append(str(e))
        
        # Walidacja dla V3ToV4Contract
        from .data_contracts import V3WorldData, V3PatternData
        if isinstance(contract, V3ToV4Contract):
            for world in contract.worlds:
                try:
                    world.validate()
                except ContractValidationError as e:
                    self.errors.append(str(e))
            
            for pattern in contract.patterns:
                try:
                    pattern.validate()
                except ContractValidationError as e:
                    self.errors.append(str(e))
    
    def _validate_versions(self, contract: DataContract) -> None:
        """Waliduje wersje kompatybilności."""
        # Sprawdź czy wersja kontraktu jest wspierana
        supported_versions = [v.value for v in ContractVersion]
        
        if contract.metadata.version.value not in supported_versions:
            self.errors.append(
                f"Niewspierana wersja kontraktu: {contract.metadata.version.value}. "
                f"Wspierane: {supported_versions}"
            )
    
    def _validate_lineage(self, contract: DataContract) -> None:
        """Waliduje informacje lineage."""
        # Dla V2ToV3Contract
        if isinstance(contract, V2ToV3Contract):
            if contract.data_version:
                try:
                    DataVersion(version=contract.data_version)
                except Exception as e:
                    self.errors.append(f"Nieprawidłowa wersja danych: {e}")
        
        # Dla V3ToV4Contract
        if isinstance(contract, V3ToV4Contract):
            if contract.data_version:
                try:
                    DataVersion(version=contract.data_version)
                except Exception as e:
                    self.errors.append(f"Nieprawidłowa wersja danych: {e}")
            
            if contract.config_version:
                try:
                    ConfigVersion(version=contract.config_version)
                except Exception as e:
                    self.errors.append(f"Nieprawidłowa wersja konfiguracji: {e}")
    
    def get_errors(self) -> List[str]:
        """Zwraca listę błędów."""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Zwraca listę ostrzeżeń."""
        return self.warnings


def validate_contract(contract: DataContract) -> bool:
    """
    Funkcja wygodna - waliduje kontrakt.
    
    Args:
        contract: Kontrakt do walidacji
        
    Returns:
        True jeśli kontrakt jest poprawny
        
    Raises:
        ContractValidationError: Jeśli kontrakt jest nieprawidłowy
    """
    validator = ContractValidator()
    if not validator.validate(contract):
        errors = "\n".join(validator.get_errors())
        raise ContractValidationError(
            type(contract).__name__,
            "validation",
            "multiple",
            f"Walidacja nie powiodła się:\n{errors}"
        )
    return True


def validate_data_version(version: str) -> bool:
    """
    Waliduje wersję danych.
    
    Args:
        version: Wersja do walidacji
        
    Returns:
        True jeśli wersja jest poprawna
    """
    try:
        DataVersion(version=version)
        return True
    except Exception:
        return False


def validate_model_version(version: str) -> bool:
    """
    Waliduje wersję modelu.
    
    Args:
        version: Wersja do walidacji
        
    Returns:
        True jeśli wersja jest poprawna
    """
    try:
        ModelVersion(version=version)
        return True
    except Exception:
        return False


def validate_config_version(version: str) -> bool:
    """
    Waliduje wersję konfiguracji.
    
    Args:
        version: Wersja do walidacji
        
    Returns:
        True jeśli wersja jest poprawna
    """
    try:
        ConfigVersion(version=version)
        return True
    except Exception:
        return False


class VersionCompatibilityChecker:
    """
    Sprawdza kompatybilność wersji.
    """
    
    def __init__(self):
        # Definicje kompatybilności
        self.compatible_versions: Dict[str, List[str]] = {
            "1.0": ["1.0", "1.1"],  # V1.0 kompatybilne z V1.1
            "1.1": ["1.0", "1.1"],  # V1.1 kompatybilne z V1.0
            "2.0": ["2.0"],          # V2.0 niekompatybilne z V1.x
        }
    
    def is_compatible(self, version1: str, version2: str) -> bool:
        """
        Sprawdza czy dwie wersje są kompatybilne.
        
        Args:
            version1: Pierwsza wersja
            version2: Druga wersja
            
        Returns:
            True jeśli wersje są kompatybilne
        """
        # Sprawdź czy version1 akceptuje version2
        if version1 in self.compatible_versions:
            if version2 in self.compatible_versions[version1]:
                return True
        
        # Sprawdź odwrotnie
        if version2 in self.compatible_versions:
            if version1 in self.compatible_versions[version2]:
                return True
        
        return False
    
    def get_compatible_versions(self, version: str) -> List[str]:
        """
        Zwraca listę wersji kompatybilnych z podaną wersją.
        
        Args:
            version: Wersja dla której szukamy kompatybilnych
            
        Returns:
            Lista kompatybilnych wersji
        """
        return self.compatible_versions.get(version, [])
    
    def check_contract_compatibility(
        self, 
        source_version: str, 
        target_version: str
    ) -> bool:
        """
        Sprawdza kompatybilność wersji kontraktu.
        
        Args:
            source_version: Wersja źródła
            target_version: Wersja celu
            
        Returns:
            True jeśli wersje są kompatybilne
        """
        return self.is_compatible(source_version, target_version)


class ContractMigrationPath:
    """
    Definiuje ścieżki migracji między wersjami kontraktów.
    """
    
    MIGRATION_PATHS: Dict[str, List[str]] = {
        "1.0": ["1.0", "1.1", "2.0"],  # V1.0 -> V1.1 -> V2.0
        "1.1": ["1.1", "2.0"],          # V1.1 -> V2.0
        "2.0": ["2.0"],                 # V2.0 (najnowsza)
    }
    
    @classmethod
    def get_migration_path(cls, from_version: str, to_version: str) -> List[str]:
        """
        Zwraca ścieżkę migracji między wersjami.
        
        Args:
            from_version: Wersja źródłowa
            to_version: Wersja docelowa
            
        Returns:
            Lista wersji pośrednich lub pusta lista jeśli migracja nie jest możliwa
        """
        if from_version == to_version:
            return [from_version]
        
        # Spróbuj znaleźć najkrótszą ścieżkę
        from_path = cls.MIGRATION_PATHS.get(from_version, [])
        to_path = cls.MIGRATION_PATHS.get(to_version, [])
        
        # Znajdź wspólny punkt
        common_points = set(from_path) & set(to_path)
        if not common_points:
            return []
        
        # Najkrótsza ścieżka
        from_idx = from_path.index(from_version)
        for cp in common_points:
            if cp in from_path[from_idx:]:
                to_idx = to_path.index(cp)
                path = from_path[from_idx:from_path.index(cp) + 1] + to_path[to_idx + 1:]
                return path
        
        return []
    
    @classmethod
    def is_migration_possible(cls, from_version: str, to_version: str) -> bool:
        """
        Sprawdza czy migracja między wersjami jest możliwa.
        
        Args:
            from_version: Wersja źródłowa
            to_version: Wersja docelowa
            
        Returns:
            True jeśli migracja jest możliwa
        """
        path = cls.get_migration_path(from_version, to_version)
        return len(path) > 0
