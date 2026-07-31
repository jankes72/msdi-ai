"""
SSI V5 Input Layer - Data Models
Modele danych dla warstwy wejścia V5

Odpowiedzialność:
- Definicja struktur danych wejściowych
- Typy danych z V2, V3, V4
- Modele dla informacji zewnętrznych

Zależności:
- dataclasses
- typing
- datetime
- enum

Wersja: 1.0
Data: 2026-07-31
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


# =============================================================================
# ENUMY: Typy źródeł danych i kategorii
# =============================================================================

class DataSource(Enum):
    """Źródła danych dla warstwy wejścia V5"""
    V2_MODELS = "v2_models"           # V2 Model Laboratory
    V3_KNOWLEDGE = "v3_knowledge"       # V3 World Memory System
    V4_AGENTS = "v4_agents"           # V4 Agent Evolution
    AGENTS = "agents"                 # Informacje od agentów
    LABORATORIES = "laboratories"     # Informacje z laboratoriów
    DEVELOPER = "developer"           # Informacje od programisty
    SYSTEM = "system"                 # Informacje systemowe


class DataCategory(Enum):
    """Kategorie danych (używane później w Sprint 14 - Klasyfikacja)"""
    MODEL = "model"                   # Dane o modelach
    PREDICTION = "prediction"         # Predykcje
    KNOWLEDGE = "knowledge"           # Wiedza
    AGENT = "agent"                   # Agenci
    COLLECTIVE = "collective"         # Kolektyw
    LABORATORY = "laboratory"         # Laboratoria
    USER = "user"                   # Użytkownik
    DEVELOPER = "developer"           # Programista
    SYSTEM = "system"                 # System
    CODE = "code"                     # Kod
    ANALYSIS = "analysis"             # Analiza


class DataStatus(Enum):
    """Status danych wejściowych"""
    RAW = "raw"                       # Surowy
    VALIDATED = "validated"           # Zwalidowany
    NORMALIZED = "normalized"         # Znormalizowany
    PROCESSED = "processed"           # Przetworzony
    ERROR = "error"                   # Błąd


# =============================================================================
# MODELE DANYCH DLA V2
# =============================================================================

@dataclass
class ModelInfo:
    """Informacje o jednym modelu V2"""
    name: str
    model_type: str
    status: str
    version: str
    last_trained: Optional[datetime] = None
    accuracy: Optional[float] = None
    description: str = ""
    source: DataSource = DataSource.V2_MODELS
    category: DataCategory = DataCategory.MODEL
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "name": self.name,
            "model_type": self.model_type,
            "status": self.status,
            "version": self.version,
            "last_trained": self.last_trained.isoformat() if self.last_trained else None,
            "accuracy": self.accuracy,
            "description": self.description,
            "source": self.source.value,
            "category": self.category.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        """Konwersja ze słownika"""
        return cls(
            name=data.get("name", ""),
            model_type=data.get("model_type", ""),
            status=data.get("status", ""),
            version=data.get("version", "1.0"),
            last_trained=datetime.fromisoformat(data["last_trained"]) if data.get("last_trained") else None,
            accuracy=data.get("accuracy"),
            description=data.get("description", ""),
            source=DataSource(data.get("source", DataSource.V2_MODELS.value)),
            category=DataCategory(data.get("category", DataCategory.MODEL.value))
        )


@dataclass
class PredictionData:
    """Dane predykcji z modelu V2"""
    model_name: str
    timestamp: datetime
    prediction: Dict[str, Any]
    confidence: Optional[float] = None
    input_data_hash: str = ""
    source: DataSource = DataSource.V2_MODELS
    category: DataCategory = DataCategory.PREDICTION
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "timestamp": self.timestamp.isoformat(),
            "prediction": self.prediction,
            "confidence": self.confidence,
            "input_data_hash": self.input_data_hash,
            "source": self.source.value,
            "category": self.category.value
        }


@dataclass
class ValidationResult:
    """Wynik walidacji modelu V2"""
    model_name: str
    metric: str
    value: float
    dataset: str = "validation"
    timestamp: datetime = field(default_factory=datetime.now)
    source: DataSource = DataSource.V2_MODELS
    category: DataCategory = DataCategory.ANALYSIS
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "metric": self.metric,
            "value": self.value,
            "dataset": self.dataset,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source.value,
            "category": self.category.value
        }


@dataclass
class WorldInterpretation:
    """Interpretacja świata z modelu V2"""
    model_name: str
    world_name: str
    interpretation: Dict[str, Any]
    confidence: Optional[float] = None
    created: datetime = field(default_factory=datetime.now)
    source: DataSource = DataSource.V2_MODELS
    category: DataCategory = DataCategory.KNOWLEDGE
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "world_name": self.world_name,
            "interpretation": self.interpretation,
            "confidence": self.confidence,
            "created": self.created.isoformat(),
            "source": self.source.value,
            "category": self.category.value
        }


@dataclass
class V2Metadata:
    """Metadane systemu V2"""
    v2_version: str
    data_split_policy: str
    models_count: int
    last_update: datetime
    collection_timestamp: datetime = field(default_factory=datetime.now)
    source: DataSource = DataSource.V2_MODELS
    category: DataCategory = DataCategory.SYSTEM
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "v2_version": self.v2_version,
            "data_split_policy": self.data_split_policy,
            "models_count": self.models_count,
            "last_update": self.last_update.isoformat(),
            "collection_timestamp": self.collection_timestamp.isoformat(),
            "source": self.source.value,
            "category": self.category.value
        }


# =============================================================================
# PAKIET DANYCH V2
# =============================================================================

@dataclass
class V2DataPackage:
    """Kompletny pakiet danych zebranych z V2"""
    timestamp: datetime = field(default_factory=datetime.now)
    models: List[ModelInfo] = field(default_factory=list)
    predictions: List[PredictionData] = field(default_factory=list)
    validation_results: List[ValidationResult] = field(default_factory=list)
    world_interpretations: List[WorldInterpretation] = field(default_factory=list)
    metadata: Optional[V2Metadata] = None
    status: DataStatus = DataStatus.RAW
    source: DataSource = DataSource.V2_MODELS
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja całego pakietu do słownika"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "models": [m.to_dict() for m in self.models],
            "predictions": [p.to_dict() for p in self.predictions],
            "validation_results": [v.to_dict() for v in self.validation_results],
            "world_interpretations": [w.to_dict() for w in self.world_interpretations],
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "status": self.status.value,
            "source": self.source.value
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Konwersja do JSON"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V2DataPackage":
        """Konwersja ze słownika"""
        package = cls(
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            status=DataStatus(data.get("status", DataStatus.RAW.value)),
            source=DataSource(data.get("source", DataSource.V2_MODELS.value))
        )
        
        if data.get("models"):
            package.models = [ModelInfo.from_dict(m) for m in data["models"]]
        
        if data.get("predictions"):
            for p in data["predictions"]:
                package.predictions.append(PredictionData(
                    model_name=p.get("model_name", ""),
                    timestamp=datetime.fromisoformat(p["timestamp"]) if p.get("timestamp") else datetime.now(),
                    prediction=p.get("prediction", {}),
                    confidence=p.get("confidence"),
                    input_data_hash=p.get("input_data_hash", ""),
                    source=DataSource(p.get("source", DataSource.V2_MODELS.value)),
                    category=DataCategory(p.get("category", DataCategory.PREDICTION.value))
                ))
        
        if data.get("validation_results"):
            for v in data["validation_results"]:
                package.validation_results.append(ValidationResult(
                    model_name=v.get("model_name", ""),
                    metric=v.get("metric", ""),
                    value=v.get("value", 0.0),
                    dataset=v.get("dataset", "validation"),
                    timestamp=datetime.fromisoformat(v["timestamp"]) if v.get("timestamp") else datetime.now(),
                    source=DataSource(v.get("source", DataSource.V2_MODELS.value)),
                    category=DataCategory(v.get("category", DataCategory.ANALYSIS.value))
                ))
        
        if data.get("world_interpretations"):
            for w in data["world_interpretations"]:
                package.world_interpretations.append(WorldInterpretation(
                    model_name=w.get("model_name", ""),
                    world_name=w.get("world_name", ""),
                    interpretation=w.get("interpretation", {}),
                    confidence=w.get("confidence"),
                    created=datetime.fromisoformat(w["created"]) if w.get("created") else datetime.now(),
                    source=DataSource(w.get("source", DataSource.V2_MODELS.value)),
                    category=DataCategory(w.get("category", DataCategory.KNOWLEDGE.value))
                ))
        
        if data.get("metadata"):
            package.metadata = V2Metadata(
                v2_version=data["metadata"].get("v2_version", "1.0"),
                data_split_policy=data["metadata"].get("data_split_policy", "60/40"),
                models_count=data["metadata"].get("models_count", 0),
                last_update=datetime.fromisoformat(data["metadata"]["last_update"]) if data["metadata"].get("last_update") else datetime.now(),
                collection_timestamp=datetime.fromisoformat(data["metadata"]["collection_timestamp"]) if data["metadata"].get("collection_timestamp") else datetime.now()
            )
        
        return package


# =============================================================================
# MODELE DANYCH DLA V3
# =============================================================================

@dataclass
class WorldInfo:
    """Informacje o jednym świecie w V3"""
    world_name: str
    world_type: str
    status: str
    version: str
    description: str = ""
    classification: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created: datetime = field(default_factory=datetime.now)
    source: DataSource = DataSource.V3_KNOWLEDGE
    category: DataCategory = DataCategory.KNOWLEDGE
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "world_name": self.world_name,
            "world_type": self.world_type,
            "status": self.status,
            "version": self.version,
            "description": self.description,
            "classification": self.classification,
            "dependencies": self.dependencies,
            "created": self.created.isoformat(),
            "source": self.source.value,
            "category": self.category.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldInfo":
        """Konwersja ze słownika"""
        return cls(
            world_name=data.get("world_name", ""),
            world_type=data.get("world_type", ""),
            status=data.get("status", ""),
            version=data.get("version", "1.0"),
            description=data.get("description", ""),
            classification=data.get("classification", {}),
            dependencies=data.get("dependencies", []),
            created=datetime.fromisoformat(data["created"]) if data.get("created") else datetime.now(),
            source=DataSource(data.get("source", DataSource.V3_KNOWLEDGE.value)),
            category=DataCategory(data.get("category", DataCategory.KNOWLEDGE.value))
        )


@dataclass
class PatternInfo:
    """Informacje o wykrytym wzorcu w V3"""
    pattern_name: str
    pattern_type: str
    detection_timestamp: datetime = field(default_factory=datetime.now)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    confidence: Optional[float] = None
    frequency: Optional[float] = None
    source: DataSource = DataSource.V3_KNOWLEDGE
    category: DataCategory = DataCategory.KNOWLEDGE
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "pattern_name": self.pattern_name,
            "pattern_type": self.pattern_type,
            "detection_timestamp": self.detection_timestamp.isoformat(),
            "examples": self.examples,
            "statistics": self.statistics,
            "confidence": self.confidence,
            "frequency": self.frequency,
            "source": self.source.value,
            "category": self.category.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatternInfo":
        """Konwersja ze słownika"""
        return cls(
            pattern_name=data.get("pattern_name", ""),
            pattern_type=data.get("pattern_type", ""),
            detection_timestamp=datetime.fromisoformat(data["detection_timestamp"]) if data.get("detection_timestamp") else datetime.now(),
            examples=data.get("examples", []),
            statistics=data.get("statistics", {}),
            confidence=data.get("confidence"),
            frequency=data.get("frequency"),
            source=DataSource(data.get("source", DataSource.V3_KNOWLEDGE.value)),
            category=DataCategory(data.get("category", DataCategory.KNOWLEDGE.value))
        )


@dataclass
class RelationshipInfo:
    """Informacje o relacji między elementami systemu w V3"""
    relationship_id: str
    source_element: str
    target_element: str
    relationship_type: str
    strength: Optional[float] = None
    description: str = ""
    created: datetime = field(default_factory=datetime.now)
    properties: Dict[str, Any] = field(default_factory=dict)
    source: DataSource = DataSource.V3_KNOWLEDGE
    category: DataCategory = DataCategory.KNOWLEDGE
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "relationship_id": self.relationship_id,
            "source_element": self.source_element,
            "target_element": self.target_element,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "description": self.description,
            "created": self.created.isoformat(),
            "properties": self.properties,
            "source": self.source.value,
            "category": self.category.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelationshipInfo":
        """Konwersja ze słownika"""
        return cls(
            relationship_id=data.get("relationship_id", ""),
            source_element=data.get("source_element", ""),
            target_element=data.get("target_element", ""),
            relationship_type=data.get("relationship_type", ""),
            strength=data.get("strength"),
            description=data.get("description", ""),
            created=datetime.fromisoformat(data["created"]) if data.get("created") else datetime.now(),
            properties=data.get("properties", {}),
            source=DataSource(data.get("source", DataSource.V3_KNOWLEDGE.value)),
            category=DataCategory(data.get("category", DataCategory.KNOWLEDGE.value))
        )


@dataclass
class V3Metadata:
    """Metadane systemu V3"""
    v3_version: str
    knowledge_engine_version: str
    worlds_count: int
    patterns_count: int
    relationships_count: int
    last_update: datetime
    collection_timestamp: datetime = field(default_factory=datetime.now)
    source: DataSource = DataSource.V3_KNOWLEDGE
    category: DataCategory = DataCategory.SYSTEM
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "v3_version": self.v3_version,
            "knowledge_engine_version": self.knowledge_engine_version,
            "worlds_count": self.worlds_count,
            "patterns_count": self.patterns_count,
            "relationships_count": self.relationships_count,
            "last_update": self.last_update.isoformat(),
            "collection_timestamp": self.collection_timestamp.isoformat(),
            "source": self.source.value,
            "category": self.category.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V3Metadata":
        """Konwersja ze słownika"""
        return cls(
            v3_version=data.get("v3_version", "1.0"),
            knowledge_engine_version=data.get("knowledge_engine_version", "1.0"),
            worlds_count=data.get("worlds_count", 0),
            patterns_count=data.get("patterns_count", 0),
            relationships_count=data.get("relationships_count", 0),
            last_update=datetime.fromisoformat(data["last_update"]) if data.get("last_update") else datetime.now(),
            collection_timestamp=datetime.fromisoformat(data["collection_timestamp"]) if data.get("collection_timestamp") else datetime.now(),
            source=DataSource(data.get("source", DataSource.V3_KNOWLEDGE.value)),
            category=DataCategory(data.get("category", DataCategory.SYSTEM.value))
        )


@dataclass
class V3DataPackage:
    """Kompletny pakiet danych zebranych z V3"""
    timestamp: datetime = field(default_factory=datetime.now)
    worlds: List[WorldInfo] = field(default_factory=list)
    patterns: List[PatternInfo] = field(default_factory=list)
    relationships: List[RelationshipInfo] = field(default_factory=list)
    metadata: Optional[V3Metadata] = None
    status: DataStatus = DataStatus.RAW
    source: DataSource = DataSource.V3_KNOWLEDGE
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja całego pakietu do słownika"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "worlds": [w.to_dict() for w in self.worlds],
            "patterns": [p.to_dict() for p in self.patterns],
            "relationships": [r.to_dict() for r in self.relationships],
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "status": self.status.value,
            "source": self.source.value
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Konwersja do JSON"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V3DataPackage":
        """Konwersja ze słownika"""
        package = cls(
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            status=DataStatus(data.get("status", DataStatus.RAW.value)),
            source=DataSource(data.get("source", DataSource.V3_KNOWLEDGE.value))
        )
        
        if data.get("worlds"):
            package.worlds = [WorldInfo.from_dict(w) for w in data["worlds"]]
        
        if data.get("patterns"):
            package.patterns = [PatternInfo.from_dict(p) for p in data["patterns"]]
        
        if data.get("relationships"):
            package.relationships = [RelationshipInfo.from_dict(r) for r in data["relationships"]]
        
        if data.get("metadata"):
            package.metadata = V3Metadata.from_dict(data["metadata"])
        
        return package


# =============================================================================
# FUNKCJE UTILITY
# =============================================================================

def validate_v2_package(package: V2DataPackage) -> bool:
    """Walidacja pakietu danych V2"""
    if not package.models:
        return False
    
    # Sprawdź czy wszystkie modele mają poprawne dane
    for model in package.models:
        if not model.name or not model.model_type:
            return False
    
    package.status = DataStatus.VALIDATED
    return True


def get_v2_package_summary(package: V2DataPackage) -> Dict[str, Any]:
    """Podsumowanie pakietu V2"""
    return {
        "total_models": len(package.models),
        "total_predictions": len(package.predictions),
        "total_validation_results": len(package.validation_results),
        "total_world_interpretations": len(package.world_interpretations),
        "status": package.status.value,
        "timestamp": package.timestamp.isoformat()
    }


# =============================================================================
# FUNKCJE UTILITY DLA V3
# =============================================================================

def validate_v3_package(package: V3DataPackage) -> bool:
    """Walidacja pakietu danych V3"""
    if not package.worlds:
        return False
    
    # Sprawdź czy wszystkie światy mają poprawne dane
    for world in package.worlds:
        if not world.world_name or not world.world_type:
            return False
    
    package.status = DataStatus.VALIDATED
    return True


def get_v3_package_summary(package: V3DataPackage) -> Dict[str, Any]:
    """Podsumowanie pakietu V3"""
    return {
        "total_worlds": len(package.worlds),
        "total_patterns": len(package.patterns),
        "total_relationships": len(package.relationships),
        "status": package.status.value,
        "timestamp": package.timestamp.isoformat()
    }
