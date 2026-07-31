"""
SSI Data Contracts - Kontrakty danych między V2, V3 i V4

Wersja: 1.0
Data: 2026-07-31
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Type, Union
from datetime import datetime
from enum import Enum, auto
import uuid
import hashlib
import json


class ContractValidationError(Exception):
    """Wyjątek walidacji kontraktu."""
    
    def __init__(self, contract_type: str, field_name: str, field_value: Any, message: str):
        self.contract_type = contract_type
        self.field_name = field_name
        self.field_value = field_value
        self.message = message
        super().__init__(f"[{contract_type}] {field_name}={field_value}: {message}")


class ContractVersion(Enum):
    """Wersje kontraktów."""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"


@dataclass
class ContractMetadata:
    """Metadane kontraktu - obowiązkowe dla wszystkich kontraktów."""
    version: ContractVersion = ContractVersion.V1_0
    contract_id: str = field(default_factory=lambda: f"contract_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    target: str = ""
    
    def validate(self) -> bool:
        """Waliduje metadane kontraktu."""
        if not self.version:
            raise ContractValidationError(
                "ContractMetadata", "version", self.version, "Wersja kontraktu nie może być pusta"
            )
        if not self.source:
            raise ContractValidationError(
                "ContractMetadata", "source", self.source, "Źródło kontraktu nie może być puste"
            )
        if not self.target:
            raise ContractValidationError(
                "ContractMetadata", "target", self.target, "Cel kontraktu nie może być pusty"
            )
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version.value,
            "contract_id": self.contract_id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "target": self.target
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContractMetadata":
        return cls(
            version=ContractVersion(data.get("version", "1.0")),
            contract_id=data.get("contract_id", f"contract_{uuid.uuid4().hex[:12]}"),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            source=data.get("source", ""),
            target=data.get("target", "")
        )


# =============================================================================
# KONTRAKT V2 -> V3 (Obserwacje, Statystyki, Wzorce)
# =============================================================================

@dataclass
class V2ObservationData:
    """Dane pojedynczej obserwacji z V2."""
    observation_id: str
    match_id: str
    group_id: str
    model_id: str
    prediction: str
    reality: str
    hit: bool
    hit_group: bool
    confidence: float
    exact_class: Optional[str] = None
    group_class: str = "X"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def validate(self) -> bool:
        """Waliduje dane obserwacji."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ContractValidationError(
                "V2ObservationData", "confidence", self.confidence, 
                f"Confidence必须在 0.0-1.0 zakresie, a jest {self.confidence}"
            )
        if not self.observation_id:
            raise ContractValidationError(
                "V2ObservationData", "observation_id", self.observation_id, 
                "ID obserwacji nie może być puste"
            )
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "match_id": self.match_id,
            "group_id": self.group_id,
            "model_id": self.model_id,
            "prediction": self.prediction,
            "reality": self.reality,
            "hit": self.hit,
            "hit_group": self.hit_group,
            "confidence": self.confidence,
            "exact_class": self.exact_class,
            "group_class": self.group_class,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V2ObservationData":
        return cls(
            observation_id=data.get("observation_id", str(uuid.uuid4())),
            match_id=data.get("match_id", ""),
            group_id=data.get("group_id", ""),
            model_id=data.get("model_id", ""),
            prediction=data.get("prediction", "0:0"),
            reality=data.get("reality", "0:0"),
            hit=data.get("hit", False),
            hit_group=data.get("hit_group", False),
            confidence=float(data.get("confidence", 0.5)),
            exact_class=data.get("exact_class"),
            group_class=data.get("group_class", "X"),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        )


@dataclass
class V2StatisticsData:
    """Statystyki modeli z V2."""
    stats_id: str = field(default_factory=lambda: f"stats_{uuid.uuid4().hex[:8]}")
    total_observations: int = 0
    class_count: int = 0
    average_accuracy: float = 0.0
    average_confidence: float = 0.0
    model_count: int = 0
    version: str = "v2_std"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def validate(self) -> bool:
        """Waliduje statystyki."""
        if not 0.0 <= self.average_accuracy <= 1.0:
            raise ContractValidationError(
                "V2StatisticsData", "average_accuracy", self.average_accuracy,
                "Średnia dokładność musi być w zakresie 0.0-1.0"
            )
        if not 0.0 <= self.average_confidence <= 1.0:
            raise ContractValidationError(
                "V2StatisticsData", "average_confidence", self.average_confidence,
                "Średnia pewność musi być w zakresie 0.0-1.0"
            )
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "stats_id": self.stats_id,
            "total_observations": self.total_observations,
            "class_count": self.class_count,
            "average_accuracy": self.average_accuracy,
            "average_confidence": self.average_confidence,
            "model_count": self.model_count,
            "version": self.version,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V2StatisticsData":
        return cls(
            stats_id=data.get("stats_id", f"stats_{uuid.uuid4().hex[:8]}"),
            total_observations=data.get("total_observations", 0),
            class_count=data.get("class_count", 0),
            average_accuracy=float(data.get("average_accuracy", 0.0)),
            average_confidence=float(data.get("average_confidence", 0.0)),
            model_count=data.get("model_count", 0),
            version=data.get("version", "v2_std"),
            created_at=data.get("created_at", datetime.now().isoformat())
        )


@dataclass
class V2PatternData:
    """Wzorce zachowań z V2."""
    pattern_id: str = field(default_factory=lambda: f"pattern_{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    frequency: int = 0
    examples: List[Dict[str, Any]] = field(default_factory=list)
    characteristics: Dict[str, Any] = field(default_factory=dict)
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def validate(self) -> bool:
        """Waliduje wzorzec."""
        if not self.name:
            raise ContractValidationError(
                "V2PatternData", "name", self.name, "Nazwa wzorca nie może być pusta"
            )
        if self.frequency < 0:
            raise ContractValidationError(
                "V2PatternData", "frequency", self.frequency, 
                "Częstotliwość nie może być ujemna"
            )
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "examples": self.examples,
            "characteristics": self.characteristics,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V2PatternData":
        return cls(
            pattern_id=data.get("pattern_id", f"pattern_{uuid.uuid4().hex[:8]}"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            frequency=data.get("frequency", 0),
            examples=data.get("examples", []),
            characteristics=data.get("characteristics", {}),
            first_seen=data.get("first_seen", datetime.now().isoformat()),
            last_seen=data.get("last_seen", datetime.now().isoformat())
        )


@dataclass
class V2ToV3Contract:
    """
    Kontrakt danych V2 -> V3.
    
    Zawiera dane z systemu V2 (Modele, Pamięć) przygotowane do transferu do V3 (Światy).
    """
    metadata: ContractMetadata = field(default_factory=ContractMetadata)
    observations: List[V2ObservationData] = field(default_factory=list)
    statistics: Dict[str, V2StatisticsData] = field(default_factory=dict)
    patterns: List[V2PatternData] = field(default_factory=list)
    
    # Lineage - informacje o pochodzeniu danych
    data_version: Optional[str] = None
    model_versions: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ustawia domyślne metadane."""
        if self.metadata.source == "":
            self.metadata.source = "V2"
        if self.metadata.target == "":
            self.metadata.target = "V3"
    
    def validate(self) -> bool:
        """Waliduje cały kontrakt."""
        # Waliduj metadane
        self.metadata.validate()
        
        # Waliduj obserwacje
        for obs in self.observations:
            obs.validate()
        
        # Waliduj statystyki
        for stats in self.statistics.values():
            stats.validate()
        
        # Waliduj wzorce
        for pattern in self.patterns:
            pattern.validate()
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "data_version": self.data_version,
            "model_versions": self.model_versions,
            "observations": [obs.to_dict() for obs in self.observations],
            "statistics": {k: v.to_dict() for k, v in self.statistics.items()},
            "patterns": [p.to_dict() for p in self.patterns]
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V2ToV3Contract":
        metadata = ContractMetadata.from_dict(data.get("metadata", {}))
        return cls(
            metadata=metadata,
            data_version=data.get("data_version"),
            model_versions=data.get("model_versions", {}),
            observations=[V2ObservationData.from_dict(obs) for obs in data.get("observations", [])],
            statistics={k: V2StatisticsData.from_dict(v) for k, v in data.get("statistics", {}).items()},
            patterns=[V2PatternData.from_dict(p) for p in data.get("patterns", [])]
        )
    
    @classmethod
    def from_legacy_dict(cls, data: Dict[str, Any]) -> "V2ToV3Contract":
        """Tworzy kontrakt z dziedzictwa (starszego formatu)."""
        # Konwersja z formatu WorldDataPackage
        contract = cls()
        contract.metadata.source = "V2"
        contract.metadata.target = "V3"
        
        # Konwersja obserwacji
        for obs in data.get("obserwacje", []):
            try:
                v2_obs = V2ObservationData(
                    observation_id=obs.get("id", str(uuid.uuid4())),
                    match_id=obs.get("mecz_id", ""),
                    group_id=obs.get("grupa_id", ""),
                    model_id=obs.get("model_id", ""),
                    prediction=obs.get("predykcja", "0:0"),
                    reality=obs.get("rzeczywistosc", "0:0"),
                    hit=obs.get("trafienie", False),
                    hit_group=obs.get("trafienie_grupa", False),
                    confidence=float(obs.get("confidence", 0.5)),
                    group_class=obs.get("klasa_grupa", "X")
                )
                contract.observations.append(v2_obs)
            except Exception as e:
                # Pomijamy nieprawidłowe obserwacje
                continue
        
        # Konwersja statystyk
        if "statystyki_modeli" in data:
            stats = data["statystyki_modeli"]
            v2_stats = V2StatisticsData(
                total_observations=stats.get("calkowita_liczba_obserwacji", 0),
                class_count=stats.get("liczba_klas", 0),
                average_accuracy=stats.get("srednia_skutecznosc", 0.0),
                average_confidence=stats.get("sredni_confidence", 0.0),
                model_count=stats.get("liczba_modeli", 0)
            )
            contract.statistics["global"] = v2_stats
        
        return contract


# =============================================================================
# KONTRAKT V3 -> V4 (Światy, Wzorce, Relacje, Metadane)
# =============================================================================

@dataclass
class V3WorldData:
    """Dane świecie z V3."""
    world_id: str
    name: str
    world_type: str
    status: str
    created_at: str
    updated_at: str
    observations_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.7
    type_specific: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Waliduje dane świata."""
        if not self.world_id:
            raise ContractValidationError(
                "V3WorldData", "world_id", self.world_id, "ID świata nie może być puste"
            )
        if not self.name:
            raise ContractValidationError(
                "V3WorldData", "name", self.name, "Nazwa świata nie może być pusta"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ContractValidationError(
                "V3WorldData", "confidence", self.confidence,
                "Pewność świata musi być w zakresie 0.0-1.0"
            )
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "name": self.name,
            "world_type": self.world_type,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "observations_count": self.observations_count,
            "metadata": self.metadata,
            "confidence": self.confidence,
            "type_specific": self.type_specific
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V3WorldData":
        return cls(
            world_id=data.get("world_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            world_type=data.get("world_type", "unknown"),
            status=data.get("status", "UNKNOWN"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            observations_count=data.get("observations_count", 0),
            metadata=data.get("metadata", {}),
            confidence=float(data.get("confidence", 0.7)),
            type_specific=data.get("type_specific", {})
        )


@dataclass
class V3PatternData:
    """Wzorce z V3."""
    pattern_id: str
    pattern_type: str
    frequency: int = 1
    confidence: float = 0.8
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    world_ids: List[str] = field(default_factory=list)
    
    def validate(self) -> bool:
        """Waliduje wzorzec V3."""
        if not self.pattern_id:
            raise ContractValidationError(
                "V3PatternData", "pattern_id", self.pattern_id, "ID wzorca nie może być puste"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ContractValidationError(
                "V3PatternData", "confidence", self.confidence,
                "Pewność wzorca musi być w zakresie 0.0-1.0"
            )
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "frequency": self.frequency,
            "confidence": self.confidence,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "data": self.data,
            "world_ids": self.world_ids
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V3PatternData":
        return cls(
            pattern_id=data.get("pattern_id", str(uuid.uuid4())),
            pattern_type=data.get("pattern_type", "unknown"),
            frequency=data.get("frequency", 1),
            confidence=float(data.get("confidence", 0.8)),
            first_seen=data.get("first_seen", datetime.now().isoformat()),
            last_seen=data.get("last_seen", datetime.now().isoformat()),
            data=data.get("data", {}),
            world_ids=data.get("world_ids", [])
        )


@dataclass
class V3RelationshipData:
    """Relacje między obiektami w V3."""
    relationship_id: str
    source_id: str
    target_id: str
    relationship_type: str
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Waliduje relację."""
        if not self.relationship_id:
            raise ContractValidationError(
                "V3RelationshipData", "relationship_id", self.relationship_id,
                "ID relacji nie może być puste"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ContractValidationError(
                "V3RelationshipData", "confidence", self.confidence,
                "Pewność relacji musi być w zakresie 0.0-1.0"
            )
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "confidence": self.confidence,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V3RelationshipData":
        return cls(
            relationship_id=data.get("relationship_id", str(uuid.uuid4())),
            source_id=data.get("source_id", ""),
            target_id=data.get("target_id", ""),
            relationship_type=data.get("relationship_type", "unknown"),
            confidence=float(data.get("confidence", 0.8)),
            metadata=data.get("metadata", {})
        )


@dataclass
class V3ToV4Contract:
    """
    Kontrakt danych V3 -> V4.
    
    Zawiera wiedzę z systemu V3 (Światy, Wzorce, Relacje) przygotowaną do transferu do V4 (Agenci).
    """
    metadata: ContractMetadata = field(default_factory=ContractMetadata)
    worlds: List[V3WorldData] = field(default_factory=list)
    patterns: List[V3PatternData] = field(default_factory=list)
    relationships: List[V3RelationshipData] = field(default_factory=list)
    metadata_bundle: Dict[str, Any] = field(default_factory=dict)
    
    # Confidence scores
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Lineage - informacje o pochodzeniu
    data_version: Optional[str] = None
    config_version: Optional[str] = None
    
    def __post_init__(self):
        """Ustawia domyślne metadane."""
        if self.metadata.source == "":
            self.metadata.source = "V3"
        if self.metadata.target == "":
            self.metadata.target = "V4"
    
    def validate(self) -> bool:
        """Waliduje cały kontrakt."""
        # Waliduj metadane
        self.metadata.validate()
        
        # Waliduj światy
        for world in self.worlds:
            world.validate()
        
        # Waliduj wzorce
        for pattern in self.patterns:
            pattern.validate()
        
        # Waliduj relacje
        for relationship in self.relationships:
            relationship.validate()
        
        # Waliduj confidence scores
        for key, value in self.confidence_scores.items():
            if not 0.0 <= value <= 1.0:
                raise ContractValidationError(
                    "V3ToV4Contract", f"confidence_scores[{key}]", value,
                    f"Wartość pewności musi być w zakresie 0.0-1.0"
                )
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "data_version": self.data_version,
            "config_version": self.config_version,
            "worlds": [w.to_dict() for w in self.worlds],
            "patterns": [p.to_dict() for p in self.patterns],
            "relationships": [r.to_dict() for r in self.relationships],
            "metadata_bundle": self.metadata_bundle,
            "confidence_scores": self.confidence_scores,
            "quality_metrics": self.quality_metrics
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V3ToV4Contract":
        metadata = ContractMetadata.from_dict(data.get("metadata", {}))
        return cls(
            metadata=metadata,
            data_version=data.get("data_version"),
            config_version=data.get("config_version"),
            worlds=[V3WorldData.from_dict(w) for w in data.get("worlds", [])],
            patterns=[V3PatternData.from_dict(p) for p in data.get("patterns", [])],
            relationships=[V3RelationshipData.from_dict(r) for r in data.get("relationships", [])],
            metadata_bundle=data.get("metadata_bundle", {}),
            confidence_scores=data.get("confidence_scores", {}),
            quality_metrics=data.get("quality_metrics", {})
        )
    
    @classmethod
    def from_legacy_dict(cls, data: Dict[str, Any]) -> "V3ToV4Contract":
        """Tworzy kontrakt z dziedzictwa (AgentKnowledgePackage)."""
        contract = cls()
        contract.metadata.source = "V3"
        contract.metadata.target = "V4"
        
        # Konwersja światów
        for world in data.get("worlds", []):
            try:
                v3_world = V3WorldData(
                    world_id=world.get("world_id", str(uuid.uuid4())),
                    name=world.get("name", world.get("nazwa", "unknown")),
                    world_type=world.get("world_type", world.get("type", "unknown")),
                    status=world.get("status", "UNKNOWN"),
                    created_at=world.get("created_at", ""),
                    updated_at=world.get("updated_at", ""),
                    observations_count=world.get("observations_count", 0),
                    metadata=world.get("metadata", {}),
                    confidence=float(world.get("confidence", 0.7)),
                    type_specific=world.get("type_specific", {})
                )
                contract.worlds.append(v3_world)
            except Exception as e:
                continue
        
        # Konwersja wzorców
        for pattern in data.get("patterns", []):
            try:
                v3_pattern = V3PatternData(
                    pattern_id=pattern.get("pattern_id", str(uuid.uuid4())),
                    pattern_type=pattern.get("pattern_type", "unknown"),
                    frequency=pattern.get("frequency", 1),
                    confidence=float(pattern.get("confidence", 0.8)),
                    first_seen=pattern.get("first_seen", ""),
                    last_seen=pattern.get("last_seen", ""),
                    data=pattern.get("data", {}),
                    world_ids=pattern.get("world_ids", [])
                )
                contract.patterns.append(v3_pattern)
            except Exception as e:
                continue
        
        # Konwersja relacji (opcjonalnie)
        # ...
        
        # Konwersja confidence scores
        contract.confidence_scores = data.get("confidence_scores", {})
        contract.quality_metrics = data.get("quality_metrics", {})
        
        return contract


# =============================================================================
# BAZOWA KLASA KONTRAKTU (dla rozszerzalności)
# =============================================================================

@dataclass
class DataContract:
    """Bazowa klasa dla wszystkich kontraktów danych."""
    metadata: ContractMetadata
    
    def validate(self) -> bool:
        """Waliduje kontrakt."""
        self.metadata.validate()
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {"metadata": self.metadata.to_dict()}
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls: Type['DataContract'], data: Dict[str, Any]) -> 'DataContract':
        metadata = ContractMetadata.from_dict(data.get("metadata", {}))
        return cls(metadata=metadata)
