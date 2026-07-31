"""
SSI V5 - Input Layer - Knowledge Package
Uniwersalny pakiet wiedzy agregujacy dane ze wszystkich zrodel

Odpowiedzialnosc:
- Agregacja danych z V2, V3, V4 i External
- Zarzadzanie metadanymi pakietu
- Walidacja i serializacja pakietu
- Udostepnianie strukturyzowanego dostepu do danych

Wersja: 1.0
Data: 2026-07-31
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

from .data_models import DataSource
from .knowledge_metadata import KnowledgeMetadata, PackageStatus
from .external.external_models import ExternalDataPackage

logger = logging.getLogger(__name__)


@dataclass
class SSIKnowledgePackage:
    """
    Uniwersalny pakiet wiedzy SSI V5.
    
    Agreguje dane ze wszystkich zrodel:
    - V2: Modele, Predykcje, Walidacje, Interpretacje Swiata
    - V3: Pamiec, Wzorce, Relacje, Wiedza
    - V4: Agenci, Osobowosci, Strategie, Decyzje
    - External: Programista, Laboratoria, Kolektyw, System
    """
    
    metadata: KnowledgeMetadata = field(default_factory=lambda: KnowledgeMetadata(package_id=f"pkg_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"))
    
    v2_data: Optional[Any] = None
    v3_data: Optional[Any] = None
    v4_data: Optional[Any] = None
    external_data: Optional[ExternalDataPackage] = None
    
    status: PackageStatus = PackageStatus.PENDING
    _stats: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        self._update_stats()
        logger.info(f"SSIKnowledgePackage zainicjowany: {self.metadata.package_id}")
    
    def _update_stats(self) -> None:
        self._stats = {
            "v2_models": len(getattr(self.v2_data, 'models', [])) if self.v2_data else 0,
            "v3_worlds": len(getattr(self.v3_data, 'worlds', [])) if self.v3_data else 0,
            "v4_agents": len(getattr(self.v4_data, 'agents', [])) if self.v4_data else 0,
            "external_developer": len(getattr(self.external_data.developer_data, 'commands', [])) if self.external_data and self.external_data.developer_data else 0,
            "external_laboratories": len(getattr(self.external_data, 'laboratory_data', [])) if self.external_data else 0,
        }
        total = sum(self._stats.values())
        self.metadata.total_items = total
    
    def add_v2_data(self, v2_package: Any) -> None:
        self.v2_data = v2_package
        self.metadata.add_source(DataSource.V2_MODELS)
        self.metadata.mark_source_collected(DataSource.V2_MODELS)
        self._update_stats()
        logger.info(f"Dodano dane V2")
    
    def add_v3_data(self, v3_package: Any) -> None:
        self.v3_data = v3_package
        self.metadata.add_source(DataSource.V3_KNOWLEDGE)
        self.metadata.mark_source_collected(DataSource.V3_KNOWLEDGE)
        self._update_stats()
        logger.info(f"Dodano dane V3")
    
    def add_v4_data(self, v4_package: Any) -> None:
        self.v4_data = v4_package
        self.metadata.add_source(DataSource.V4_AGENTS)
        self.metadata.mark_source_collected(DataSource.V4_AGENTS)
        self._update_stats()
        logger.info(f"Dodano dane V4")
    
    def add_external_data(self, external_package: ExternalDataPackage) -> None:
        self.external_data = external_package
        self.metadata.add_source(DataSource.AGENTS)
        self.metadata.mark_source_collected(DataSource.AGENTS)
        self._update_stats()
        logger.info(f"Dodano dane External")
    
    def add_source_data(self, source_type: DataSource, data: Any) -> None:
        """Dodaje dane z dowolnego zrodla na podstawie DataSource"""
        if source_type == DataSource.V2_MODELS:
            self.add_v2_data(data)
        elif source_type == DataSource.V3_KNOWLEDGE:
            self.add_v3_data(data)
        elif source_type == DataSource.V4_AGENTS:
            self.add_v4_data(data)
        elif source_type in [DataSource.AGENTS, DataSource.LABORATORIES, DataSource.DEVELOPER, DataSource.SYSTEM]:
            # Dla zrodel external, zakladamy ze data to ExternalDataPackage
            if isinstance(data, ExternalDataPackage):
                self.add_external_data(data)
            else:
                self.external_data = data
                self.metadata.add_source(source_type)
                self.metadata.mark_source_collected(source_type)
                self._update_stats()
        else:
            # Dla innych typow, zapisuj jako external_data
            self.external_data = data
            self.metadata.add_source(source_type)
            self.metadata.mark_source_collected(source_type)
            self._update_stats()
    
    def validate(self) -> bool:
        errors = []
        if not any([self.v2_data, self.v3_data, self.v4_data, self.external_data]):
            errors.append("Brak danych w pakiecie")
        
        if self.external_data:
            # ExternalDataPackage nie ma metody validate, wiec pomijamy ten check
            # TODO: Dodac metode validate do ExternalDataPackage w przyszlosci
            pass
        
        is_valid = len(errors) == 0
        self.metadata.set_validation_result(is_valid, errors)
        self.status = PackageStatus.VALIDATED if is_valid else PackageStatus.INVALID
        return is_valid
    
    def is_valid(self) -> bool:
        return self.metadata.is_valid and self.status == PackageStatus.VALIDATED
    
    def has_data(self) -> bool:
        return any([self.v2_data, self.v3_data, self.v4_data, self.external_data])
    
    def get_statistics(self) -> Dict[str, Any]:
        self._update_stats()
        return {
            "total_items": self.metadata.total_items,
            "package_id": self.metadata.package_id,
            "status": self.status.value,
            "is_valid": self.is_valid(),
            "sources_collected": len(self.metadata.collected_sources),
            "source_details": self._stats
        }
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "metadata": self.metadata.to_dict(),
            "status": self.status.value,
            "stats": self._stats
        }
        if self.v2_data:
            result["v2_data"] = getattr(self.v2_data, 'to_dict', lambda: str(self.v2_data))()
        if self.v3_data:
            result["v3_data"] = getattr(self.v3_data, 'to_dict', lambda: str(self.v3_data))()
        if self.v4_data:
            result["v4_data"] = getattr(self.v4_data, 'to_dict', lambda: str(self.v4_data))()
        if self.external_data:
            result["external_data"] = self.external_data.to_dict()
        return result
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SSIKnowledgePackage":
        package = cls()
        package.metadata = KnowledgeMetadata.from_dict(data.get("metadata", {}))
        package.status = PackageStatus(data.get("status", "pending"))
        if "v2_data" in data:
            package.v2_data = data["v2_data"]
        if "v3_data" in data:
            package.v3_data = data["v3_data"]
        if "v4_data" in data:
            package.v4_data = data["v4_data"]
        if "external_data" in data:
            package.external_data = ExternalDataPackage.from_dict(data["external_data"])
        return package
    
    @classmethod
    def from_json(cls, json_str: str) -> "SSIKnowledgePackage":
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def display(self) -> None:
        print("=" * 60)
        print("SSI KNOWLEDGE PACKAGE")
        print("=" * 60)
        print(f"Package ID: {self.metadata.package_id}")
        print(f"Status: {self.status.value}")
        print(f"Items: {self.metadata.total_items}")
        print(f"Valid: {self.is_valid()}")
        print("=" * 60)


def create_knowledge_package(
    v2_data: Any = None,
    v3_data: Any = None,
    v4_data: Any = None,
    external_data: ExternalDataPackage = None,
    package_id: str = None
) -> SSIKnowledgePackage:
    package = SSIKnowledgePackage()
    if package_id:
        package.metadata.package_id = package_id
    if v2_data:
        package.add_v2_data(v2_data)
    if v3_data:
        package.add_v3_data(v3_data)
    if v4_data:
        package.add_v4_data(v4_data)
    if external_data:
        package.add_external_data(external_data)
    if package.has_data():
        all_collected = all(
            package.metadata.collected_sources.get(st.name, False) 
            for st in [DataSource.V2_MODELS, DataSource.V3_KNOWLEDGE, DataSource.V4_AGENTS, DataSource.AGENTS]
            if st in package.metadata.source_types
        )
        package.status = PackageStatus.COMPLETE if all_collected else PackageStatus.PARTIAL
    return package
