"""
SSI Version Identifiers - Identyfikatory wersji dla lineage tracking

Wersja: 1.0
Data: 2026-07-31
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import uuid
import hashlib
import json


@dataclass
class DataVersion:
    """
    Identyfikator wersji datasetu.
    
    Używany do śledzenia pochodzenia i wersji danych wejściowych.
    """
    version: str  # np. "v1.0.0"
    data_id: str = field(default_factory=lambda: f"data_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = ""  # Źródło danych (np. "v2_models", "fixture_v1")
    description: str = ""
    checksum: str = ""  # Hash zawartości (opcjonalnie)
    
    # Lineage
    parent_versions: List[str] = field(default_factory=list)  # Wersje rodziców
    tags: List[str] = field(default_factory=list)  # Tagi (np. ["train", "test"])
    
    # Statystyki
    record_count: int = 0
    field_count: int = 0
    
    def validate(self) -> bool:
        """Waliduje wersję danych."""
        if not self.version:
            raise ValueError("Wersja danych nie może być pusta")
        if not self.data_id:
            raise ValueError("ID danych nie może być puste")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "data_id": self.data_id,
            "timestamp": self.timestamp,
            "source": self.source,
            "description": self.description,
            "checksum": self.checksum,
            "parent_versions": self.parent_versions,
            "tags": self.tags,
            "record_count": self.record_count,
            "field_count": self.field_count
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataVersion":
        return cls(
            version=data.get("version", "1.0.0"),
            data_id=data.get("data_id", f"data_{uuid.uuid4().hex[:12]}"),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            source=data.get("source", ""),
            description=data.get("description", ""),
            checksum=data.get("checksum", ""),
            parent_versions=data.get("parent_versions", []),
            tags=data.get("tags", []),
            record_count=data.get("record_count", 0),
            field_count=data.get("field_count", 0)
        )
    
    def compute_checksum(self, data: Dict[str, Any]) -> str:
        """Oblicza checksum dla danych."""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:16]


@dataclass
class ModelVersion:
    """
    Identyfikator wersji modelu.
    
    Używany do śledzenia pochodzenia i wersji modeli ML.
    """
    version: str  # np. "v1.2.0"
    model_id: str = field(default_factory=lambda: f"model_{uuid.uuid4().hex[:12]}")
    model_type: str = ""  # Typ modelu (np. "siec_01", "random_forest")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Metadane
    framework: str = ""  # np. "sklearn", "tensorflow"
    parameters: Dict[str, Any] = field(default_factory=dict)  # Hiperparametry
    
    # Metryki
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    
    # Lineage
    training_data_version: str = ""  # Wersja danych treningowych
    parent_model_id: Optional[str] = None  # ID modelu rodzica (fine-tuning)
    
    def validate(self) -> bool:
        """Waliduje wersję modelu."""
        if not self.version:
            raise ValueError("Wersja modelu nie może być pusta")
        if not self.model_id:
            raise ValueError("ID modelu nie może być puste")
        if self.accuracy is not None and not 0.0 <= self.accuracy <= 1.0:
            raise ValueError("Dokładność musi być w zakresie 0.0-1.0")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "version": self.version,
            "model_id": self.model_id,
            "model_type": self.model_type,
            "timestamp": self.timestamp,
            "framework": self.framework,
            "parameters": self.parameters,
            "training_data_version": self.training_data_version,
            "parent_model_id": self.parent_model_id
        }
        if self.accuracy is not None:
            result["accuracy"] = self.accuracy
        if self.precision is not None:
            result["precision"] = self.precision
        if self.recall is not None:
            result["recall"] = self.recall
        if self.f1_score is not None:
            result["f1_score"] = self.f1_score
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelVersion":
        return cls(
            version=data.get("version", "1.0.0"),
            model_id=data.get("model_id", f"model_{uuid.uuid4().hex[:12]}"),
            model_type=data.get("model_type", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            framework=data.get("framework", ""),
            parameters=data.get("parameters", {}),
            accuracy=data.get("accuracy"),
            precision=data.get("precision"),
            recall=data.get("recall"),
            f1_score=data.get("f1_score"),
            training_data_version=data.get("training_data_version", ""),
            parent_model_id=data.get("parent_model_id")
        )


@dataclass
class ConfigVersion:
    """
    Identyfikator wersji konfiguracji.
    
    Używany do śledzenia pochodzenia i wersji konfiguracji systemu.
    """
    version: str  # np. "1.0.0"
    config_id: str = field(default_factory=lambda: f"config_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    config_type: str = ""  # Typ konfiguracji (np. "v2", "v3", "v4")
    
    # Zmiany względem poprzedniej wersji
    changes: List[str] = field(default_factory=list)  # Lista zmian
    previous_version: Optional[str] = None
    
    # Parametry konfiguracji
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Waliduje wersję konfiguracji."""
        if not self.version:
            raise ValueError("Wersja konfiguracji nie może być pusta")
        if not self.config_id:
            raise ValueError("ID konfiguracji nie może być puste")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "config_id": self.config_id,
            "timestamp": self.timestamp,
            "config_type": self.config_type,
            "changes": self.changes,
            "previous_version": self.previous_version,
            "parameters": self.parameters
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigVersion":
        return cls(
            version=data.get("version", "1.0.0"),
            config_id=data.get("config_id", f"config_{uuid.uuid4().hex[:12]}"),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            config_type=data.get("config_type", ""),
            changes=data.get("changes", []),
            previous_version=data.get("previous_version"),
            parameters=data.get("parameters", {})
        )


@dataclass
class ResultVersion:
    """
    Identyfikator wersji wyniku.
    
    Używany do śledzenia pochodzenia i wersji wyników (decyzje, predykcje).
    """
    version: str  # np. "1.0.0"
    result_id: str = field(default_factory=lambda: f"result_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    result_type: str = ""  # Typ wyniku (np. "decision", "prediction", "evaluation")
    
    # Lineage - informacje o pochodzeniu
    data_version: str = ""  # Wersja danych użytych do wygenerowania wyniku
    model_version: str = ""  # Wersja modelu użytego do wygenerowania wyniku
    config_version: str = ""  # Wersja konfiguracji użytej do wygenerowania wyniku
    code_version: str = ""  # Wersja kodu użytego do wygenerowania wyniku
    
    # Metadane wyniku
    agent_id: Optional[str] = None  # ID agenta (jeśli dotyczy)
    world_id: Optional[str] = None  # ID świata (jeśli dotyczy)
    
    # Metryki
    confidence: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    
    def validate(self) -> bool:
        """Waliduje wersję wyniku."""
        if not self.version:
            raise ValueError("Wersja wyniku nie może być pusta")
        if not self.result_id:
            raise ValueError("ID wyniku nie może być puste")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Pewność wyniku musi być w zakresie 0.0-1.0")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "version": self.version,
            "result_id": self.result_id,
            "timestamp": self.timestamp,
            "result_type": self.result_type,
            "data_version": self.data_version,
            "model_version": self.model_version,
            "config_version": self.config_version,
            "code_version": self.code_version,
            "agent_id": self.agent_id,
            "world_id": self.world_id,
            "confidence": self.confidence,
            "success": self.success,
            "error_message": self.error_message
        }
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResultVersion":
        return cls(
            version=data.get("version", "1.0.0"),
            result_id=data.get("result_id", f"result_{uuid.uuid4().hex[:12]}"),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            result_type=data.get("result_type", ""),
            data_version=data.get("data_version", ""),
            model_version=data.get("model_version", ""),
            config_version=data.get("config_version", ""),
            code_version=data.get("code_version", ""),
            agent_id=data.get("agent_id"),
            world_id=data.get("world_id"),
            confidence=float(data.get("confidence", 0.0)),
            success=data.get("success", True),
            error_message=data.get("error_message")
        )


@dataclass
class LineageInfo:
    """
    Kompleksowe informacje o pochodzeniu (lineage).
    
    Łączy wszystkie identyfikatory wersji w jedną strukturę dla pełnego śledzenia.
    """
    data_versions: List[DataVersion] = field(default_factory=list)
    model_versions: List[ModelVersion] = field(default_factory=list)
    config_versions: List[ConfigVersion] = field(default_factory=list)
    result_versions: List[ResultVersion] = field(default_factory=list)
    
    # Informacje o przepływie
    workflow_id: str = field(default_factory=lambda: f"workflow_{uuid.uuid4().hex[:12]}")
    workflow_name: str = ""
    execution_id: str = field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Czas wykonania
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_ms: float = 0.0
    
    def validate(self) -> bool:
        """Waliduje informacje lineage."""
        for dv in self.data_versions:
            dv.validate()
        for mv in self.model_versions:
            mv.validate()
        for cv in self.config_versions:
            cv.validate()
        for rv in self.result_versions:
            rv.validate()
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_versions": [v.to_dict() for v in self.data_versions],
            "model_versions": [v.to_dict() for v in self.model_versions],
            "config_versions": [v.to_dict() for v in self.config_versions],
            "result_versions": [v.to_dict() for v in self.result_versions],
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "execution_id": self.execution_id,
            "timestamp": self.timestamp,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LineageInfo":
        return cls(
            data_versions=[DataVersion.from_dict(v) for v in data.get("data_versions", [])],
            model_versions=[ModelVersion.from_dict(v) for v in data.get("model_versions", [])],
            config_versions=[ConfigVersion.from_dict(v) for v in data.get("config_versions", [])],
            result_versions=[ResultVersion.from_dict(v) for v in data.get("result_versions", [])],
            workflow_id=data.get("workflow_id", f"workflow_{uuid.uuid4().hex[:12]}"),
            workflow_name=data.get("workflow_name", ""),
            execution_id=data.get("execution_id", f"exec_{uuid.uuid4().hex[:12]}"),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            duration_ms=float(data.get("duration_ms", 0.0))
        )
    
    def add_data_version(self, version: Union[str, DataVersion]) -> None:
        """Dodaje wersję danych."""
        if isinstance(version, str):
            self.data_versions.append(DataVersion(version=version))
        else:
            self.data_versions.append(version)
    
    def add_model_version(self, version: Union[str, ModelVersion]) -> None:
        """Dodaje wersję modelu."""
        if isinstance(version, str):
            self.model_versions.append(ModelVersion(version=version))
        else:
            self.model_versions.append(version)
    
    def add_config_version(self, version: Union[str, ConfigVersion]) -> None:
        """Dodaje wersję konfiguracji."""
        if isinstance(version, str):
            self.config_versions.append(ConfigVersion(version=version))
        else:
            self.config_versions.append(version)
    
    def add_result_version(self, version: Union[str, ResultVersion]) -> None:
        """Dodaje wersję wyniku."""
        if isinstance(version, str):
            self.result_versions.append(ResultVersion(version=version))
        else:
            self.result_versions.append(version)
    
    def finalize(self) -> "LineageInfo":
        """Finalizuje informacje lineage i zwraca nowy obiekt z ustawionym timestampem."""
        # Ustaw czas zakończenia
        self.end_time = datetime.now().isoformat()
        
        # Oblicz czas trwania jeśli start_time jest ustawione
        if self.start_time:
            start_dt = datetime.fromisoformat(self.start_time)
            end_dt = datetime.fromisoformat(self.end_time)
            self.duration_ms = (end_dt - start_dt).total_seconds() * 1000
        
        return self
    
    def get_summary(self) -> str:
        """Zwraca podsumowanie lineage."""
        summary = f"Lineage: {self.workflow_name} ({self.workflow_id})\n"
        summary += f"Data versions: {len(self.data_versions)}\n"
        summary += f"Model versions: {len(self.model_versions)}\n"
        summary += f"Config versions: {len(self.config_versions)}\n"
        summary += f"Result versions: {len(self.result_versions)}\n"
        if self.duration_ms > 0:
            summary += f"Duration: {self.duration_ms:.2f}ms"
        return summary
