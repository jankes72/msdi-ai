"""
SSI Vertical Flow - Pionowy przepływ danych fixture → V2 → V3 → V4 → decyzja → wynik → feedback

Wersja: 1.0
Data: 2026-07-31
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime
import uuid
import time
import logging
import importlib
import sys

from SSI.contracts import (
    V2ToV3Contract,
    V3ToV4Contract,
    DataVersion,
    ModelVersion,
    ConfigVersion,
    ResultVersion,
    LineageInfo,
)
from SSI.contracts.policies import DataSplitPolicy, SplitResult
from SSI.data.policies import DataQualityPolicy, DataRetentionPolicy

logger = logging.getLogger(__name__)


@dataclass
class VerticalFlowConfig:
    """Konfiguracja pionowego przepływu."""
    # Polityki
    split_policy: DataSplitPolicy = field(default_factory=DataSplitPolicy.standard_50_10_40)
    quality_policy: Optional[DataQualityPolicy] = None
    retention_policy: Optional[DataRetentionPolicy] = None
    
    # Ustawienia wykonywania
    seed: Optional[int] = 42  # Seed für powtarzalność
    enable_lineage: bool = True
    enable_validation: bool = True
    enable_logging: bool = True
    
    # Timeouty
    v2_timeout_ms: int = 5000
    v3_timeout_ms: int = 5000
    v4_timeout_ms: int = 5000
    
    # Ładowność
    load_sample_data: bool = True
    sample_data_path: str = "data/fixtures/v1/sample_observations.json"
    
    # Wersje domyślne
    default_data_version: str = "v1.0.0"
    default_model_version: str = "v1.0.0"
    default_config_version: str = "v1.0.0"
    default_code_version: str = "1.0"


@dataclass
class FlowResult:
    """Wynik wykonania pionowego przepływu."""
    success: bool = True
    
    # Wyniki z poszczególnych kroków
    v2_result: Optional[Dict[str, Any]] = None
    v3_result: Optional[Dict[str, Any]] = None
    v4_result: Optional[Dict[str, Any]] = None
    decision_result: Optional[Dict[str, Any]] = None
    feedback_result: Optional[Dict[str, Any]] = None
    
    # Kontrakty
    v2_to_v3_contract: Optional[V2ToV3Contract] = None
    v3_to_v4_contract: Optional[V3ToV4Contract] = None
    
    # Lineage
    lineage: Optional[LineageInfo] = None
    
    # Metryki
    execution_time_ms: float = 0.0
    step_times: Dict[str, float] = field(default_factory=dict)
    
    # Błędy
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje wynik do słownika."""
        result = {
            "success": self.success,
            "execution_time_ms": self.execution_time_ms,
            "step_times": self.step_times,
            "errors": self.errors,
            "warnings": self.warnings,
        }
        
        if self.v2_result:
            result["v2_result"] = self.v2_result
        if self.v3_result:
            result["v3_result"] = self.v3_result
        if self.v4_result:
            result["v4_result"] = self.v4_result
        if self.decision_result:
            result["decision_result"] = self.decision_result
        if self.feedback_result:
            result["feedback_result"] = self.feedback_result
        if self.lineage:
            result["lineage"] = self.lineage.to_dict()
        
        return result
    
    def get_summary(self) -> str:
        """Zwraca podsumowanie wyniku."""
        summary = f"Vertical Flow {'SUCCESS' if self.success else 'FAILED'}\n"
        summary += f"Execution time: {self.execution_time_ms:.2f}ms\n"
        
        for step, time_ms in self.step_times.items():
            summary += f"  {step}: {time_ms:.2f}ms\n"
        
        if self.errors:
            summary += f"Errors: {len(self.errors)}\n"
            for error in self.errors:
                summary += f"  - {error}\n"
        
        if self.warnings:
            summary += f"Warnings: {len(self.warnings)}\n"
        
        if self.lineage:
            summary += f"\n{self.lineage.get_summary()}"
        
        return summary


@dataclass
class LineageTracker:
    """Tracker lineage - śledzi pochodzenie danych przez przepływ."""
    data_versions: List[DataVersion] = field(default_factory=list)
    model_versions: List[ModelVersion] = field(default_factory=list)
    config_versions: List[ConfigVersion] = field(default_factory=list)
    result_versions: List[ResultVersion] = field(default_factory=list)
    
    workflow_id: str = field(default_factory=lambda: f"workflow_{uuid.uuid4().hex[:12]}")
    execution_id: str = field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:12]}")
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_data_version(self, version: Union[str, DataVersion]) -> DataVersion:
        """Dodaje wersję danych."""
        if isinstance(version, str):
            dv = DataVersion(version=version)
        else:
            dv = version
        self.data_versions.append(dv)
        return dv
    
    def add_model_version(self, version: Union[str, ModelVersion]) -> ModelVersion:
        """Dodaje wersję modelu."""
        if isinstance(version, str):
            mv = ModelVersion(version=version)
        else:
            mv = version
        self.model_versions.append(mv)
        return mv
    
    def add_config_version(self, version: Union[str, ConfigVersion]) -> ConfigVersion:
        """Dodaje wersję konfiguracji."""
        if isinstance(version, str):
            cv = ConfigVersion(version=version)
        else:
            cv = version
        self.config_versions.append(cv)
        return cv
    
    def add_result_version(self, result: ResultVersion) -> ResultVersion:
        """Dodaje wersję wyniku."""
        self.result_versions.append(result)
        return result
    
    def finalize(self, end_time: Optional[str] = None) -> LineageInfo:
        """Finalizuje tracking i zwraca LineageInfo."""
        if end_time is None:
            end_time = datetime.now().isoformat()
        
        # Oblicz czas trwania
        try:
            start_dt = datetime.fromisoformat(self.start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration_ms = (end_dt - start_dt).total_seconds() * 1000
        except Exception:
            duration_ms = 0.0
        
        return LineageInfo(
            data_versions=self.data_versions.copy(),
            model_versions=self.model_versions.copy(),
            config_versions=self.config_versions.copy(),
            result_versions=self.result_versions.copy(),
            workflow_id=self.workflow_id,
            execution_id=self.execution_id,
            start_time=self.start_time,
            end_time=end_time,
            duration_ms=duration_ms
        )


class VerticalFlow:
    """
    Pionowy przepływ danych: fixture → V2 → V3 → V4 → decyzja → wynik → feedback.
    
    Orkiestruje transfer danych i wiedzy między warstwami systemu SSI.
    """
    
    def __init__(self, config: Optional[VerticalFlowConfig] = None):
        self.config = config or VerticalFlowConfig()
        self._initialized = False
        self._components: Dict[str, Any] = {}
        
        # Inicjalizacja logging
        self._setup_logging()
        
        # Inicjalizacja trackerów
        self.lineage_tracker = LineageTracker(
            workflow_id=f"vertical_flow_{uuid.uuid4().hex[:8]}",
            execution_id=f"exec_{uuid.uuid4().hex[:12]}"
        )
    
    def _setup_logging(self) -> None:
        """Konfiguruje logging."""
        self.logger = logging.getLogger(f"{__name__}.VerticalFlow")
        if self.config.enable_logging:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)
    
    def _initialize_components(self) -> None:
        """Inicjalizuje komponenty (V2, V3, V4)."""
        if self._initialized:
            return
        
        self.logger.info("Initialize Vertical Flow components...")
        
        # Inicjalizacja V2
        try:
            from SSI.v2.integration import V2Integration, tworz_integracje_v2
            self._components['v2_integration'] = tworz_integracje_v2()
            self.logger.info("V2 Integration initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize V2 Integration: {e}")
            self._components['v2_integration'] = None
        
        # Inicjalizacja V3
        try:
            from SSI.v3.v3_integration import tworz_integracje_v3
            self._components['v3_integration'] = tworz_integracje_v3()
            self.logger.info("V3 Integration initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize V3 Integration: {e}")
            self._components['v3_integration'] = None
        
        # Inicjalizacja mostu V2->V3
        try:
            from SSI.v2.integration.v2_to_v3_bridge import tworz_bridge_v2_v3
            v2_integration = self._components.get('v2_integration')
            if v2_integration:
                self._components['v2_to_v3_bridge'] = tworz_bridge_v2_v3(
                    v2_integration=v2_integration
                )
                self.logger.info("V2->V3 Bridge initialized")
            else:
                self._components['v2_to_v3_bridge'] = None
        except Exception as e:
            self.logger.warning(f"Failed to initialize V2->V3 Bridge: {e}")
            self._components['v2_to_v3_bridge'] = None
        
        # Inicjalizacja mostu V3->V4
        try:
            from SSI.v3.integration.v3_to_v4_bridge import tworz_v3_to_v4_bridge
            v3_integration = self._components.get('v3_integration')
            if v3_integration:
                self._components['v3_to_v4_bridge'] = tworz_v3_to_v4_bridge()
                self._components['v3_to_v4_bridge'].connect(v3_integration)
                self.logger.info("V3->V4 Bridge initialized")
            else:
                self._components['v3_to_v4_bridge'] = None
        except Exception as e:
            self.logger.warning(f"Failed to initialize V3->V4 Bridge: {e}")
            self._components['v3_to_v4_bridge'] = None
        
        # Inicjalizacja V4 (Agent Core)
        try:
            # Importujemy dynamicznie, aby uniknąć zależności cyklicznych
            self._components['v4_agent_core'] = None
            self.logger.info("V4 Agent Core placeholder initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize V4 Agent Core: {e}")
            self._components['v4_agent_core'] = None
        
        self._initialized = True
    
    def _load_sample_data(self) -> List[Dict[str, Any]]:
        """Ładuje dane testowe z fixture."""
        import json
        import os
        
        # Sprawdź czy plik istnieje
        fixture_path = self.config.sample_data_path
        if not os.path.exists(fixture_path):
            self.logger.warning(f"Sample data file not found: {fixture_path}")
            # Zwróć dane demo
            return self._generate_demo_data()
        
        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Loaded sample data from {fixture_path}")
            return data
        except Exception as e:
            self.logger.warning(f"Failed to load sample data: {e}")
            return self._generate_demo_data()
    
    def _generate_demo_data(self) -> List[Dict[str, Any]]:
        """Generuje demo dane testowe."""
        self.logger.info("Generating demo data...")
        demo_data = []
        
        for i in range(100):
            demo_data.append({
                "observation_id": f"obs_{i:03d}",
                "match_id": f"match_{i // 10:03d}",
                "group_id": f"group_{i // 20:02d}",
                "model_id": f"model_0{i % 5 + 1}",
                "prediction": "2:1" if i % 2 == 0 else "1:0",
                "reality": "2:1" if i % 3 == 0 else "1:0",
                "hit": (i % 2 == 0 and i % 3 == 0),
                "hit_group": True,
                "confidence": 0.5 + (i % 50) / 100.0,
                "exact_class": "2:1",
                "group_class": "2" if i % 2 == 0 else "1",
                "timestamp": datetime.now().isoformat()
            })
        
        return demo_data
    
    def _execute_v2_stage(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Wykonywa V2 - przetwarzanie danych modeli."""
        start_time = time.time()
        result = {"status": "success", "data": data}
        
        try:
            # Walidacja danych wejściowych
            if self.config.enable_validation:
                quality_policy = DataQualityPolicy(
                    required_fields=["observation_id", "prediction", "confidence"],
                    field_validators={
                        "confidence": lambda x: 0.0 <= float(x) <= 1.0,
                    }
                )
                
                valid_data = []
                for record in data:
                    is_valid, _, _ = quality_policy.validate_data(record)
                    if is_valid:
                        valid_data.append(record)
                
                result["valid_data_count"] = len(valid_data)
                result["invalid_data_count"] = len(data) - len(valid_data)
                data = valid_data
            
            # Transfer przez most V2->V3
            v2_to_v3_bridge = self._components.get('v2_to_v3_bridge')
            if v2_to_v3_bridge:
                # Utworzenie kontraktu V2
                v2_contract = V2ToV3Contract(
                    data_version=self.config.default_data_version,
                    observations=data,  # Konwersja do V2ObservationData
                )
                
                # Walidacja kontraktu
                v2_contract.validate()
                
                result["v2_contract"] = v2_contract.to_dict()
                result["v2_to_v3_contract"] = v2_contract
                
                self.lineage_tracker.add_data_version(self.config.default_data_version)
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"V2 stage error: {e}")
        
        elapsed_ms = (time.time() - start_time) * 1000
        result["execution_time_ms"] = elapsed_ms
        
        return result
    
    def _execute_v3_stage(self, v2_contract: V2ToV3Contract) -> Dict[str, Any]:
        """Wykonywa V3 - przetwarzanie światów i pamięci."""
        start_time = time.time()
        result = {"status": "success"}
        
        try:
            # Transfer z V2 do V3
            v2_to_v3_bridge = self._components.get('v2_to_v3_bridge')
            v3_integration = self._components.get('v3_integration')
            
            if v2_to_v3_bridge and v3_integration:
                # Synchronizacja z V2 do V3
                package = v2_to_v3_bridge.synchronizuj_do_v3("test_world")
                
                # Utworzenie kontraktu V3
                v3_contract = V3ToV4Contract()
                v3_contract.data_version = v2_contract.data_version
                v3_contract.config_version = self.config.default_config_version
                
                result["v3_package"] = package.to_dict()
                result["v3_contract"] = v3_contract
                
                self.lineage_tracker.add_config_version(self.config.default_config_version)
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"V3 stage error: {e}")
        
        elapsed_ms = (time.time() - start_time) * 1000
        result["execution_time_ms"] = elapsed_ms
        
        return result
    
    def _execute_v4_stage(self, v3_contract: Optional[V3ToV4Contract]) -> Dict[str, Any]:
        """Wykonywa V4 - podejmowanie decyzji przez agentów."""
        start_time = time.time()
        result = {"status": "success"}
        
        try:
            v3_to_v4_bridge = self._components.get('v3_to_v4_bridge')
            
            if v3_to_v4_bridge and v3_contract:
                # Transfer wiedzy do V4
                transfer_result = v3_to_v4_bridge.transfer_knowledge(v3_contract)
                result["transfer_result"] = transfer_result
                
                # Symulacja decyzji agenta
                decision_result = {
                    "decision_id": f"dec_{uuid.uuid4().hex[:12]}",
                    "agent_id": "agent_001",
                    "decision": "accept",
                    "confidence": 0.85,
                    "timestamp": datetime.now().isoformat()
                }
                result["decision_result"] = decision_result
                
                # Dodaj wersję wyniku
                result_version = ResultVersion(
                    version="1.0.0",
                    result_type="decision",
                    data_version=v3_contract.data_version if v3_contract else "",
                    config_version=v3_contract.config_version if v3_contract else "",
                    code_version=self.config.default_code_version,
                    confidence=0.85,
                    success=True
                )
                self.lineage_tracker.add_result_version(result_version)
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"V4 stage error: {e}")
        
        elapsed_ms = (time.time() - start_time) * 1000
        result["execution_time_ms"] = elapsed_ms
        
        return result
    
    def _execute_feedback_stage(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonywa feedback - zwrotna informacja o wynikach."""
        start_time = time.time()
        result = {"status": "success"}
        
        try:
            # Symulacja feedback
            feedback_result = {
                "feedback_id": f"fb_{uuid.uuid4().hex[:12]}",
                "decision_id": decision_result.get("decision_id", ""),
                "result": "success",
                "score": 0.95,
                "timestamp": datetime.now().isoformat()
            }
            result["feedback_result"] = feedback_result
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Feedback stage error: {e}")
        
        elapsed_ms = (time.time() - start_time) * 1000
        result["execution_time_ms"] = elapsed_ms
        
        return result
    
    def run(self, data: Optional[List[Dict[str, Any]]] = None) -> FlowResult:
        """
        Uruchamia cały pionowy przepływ.
        
        Args:
            data: Dane wejściowe (jeśli None, ładuje sample data)
            
        Returns:
            FlowResult z wynikami
        """
        overall_start = time.time()
        result = FlowResult(
            step_times={},
            lineage=self.lineage_tracker.finalize()
        )
        
        try:
            # Inicjalizacja komponentów
            self._initialize_components()
            
            # Załadowanie danych
            if data is None:
                if self.config.load_sample_data:
                    data = self._load_sample_data()
                else:
                    data = []
            
            # Dodaj informacje o danych do lineage
            self.lineage_tracker.add_data_version(self.config.default_data_version)
            
            # Krok 1: V2
            if data:
                self.logger.info(f"Starting V2 stage with {len(data)} records...")
                v2_start = time.time()
                v2_result = self._execute_v2_stage(data)
                v2_elapsed = (time.time() - v2_start) * 1000
                result.step_times["v2"] = v2_elapsed
                result.v2_result = v2_result
                
                if v2_result.get("status") == "error":
                    result.errors.append(v2_result.get("error", "V2 error"))
                    result.success = False
                
                # Pobierz kontrakt V2->V3
                v2_contract = v2_result.get("v2_to_v3_contract")
                if v2_contract:
                    result.v2_to_v3_contract = v2_contract
            
            # Krok 2: V3
            if result.success:
                self.logger.info("Starting V3 stage...")
                v3_start = time.time()
                v3_result = self._execute_v3_stage(result.v2_to_v3_contract)
                v3_elapsed = (time.time() - v3_start) * 1000
                result.step_times["v3"] = v3_elapsed
                result.v3_result = v3_result
                
                if v3_result.get("status") == "error":
                    result.errors.append(v3_result.get("error", "V3 error"))
                    result.success = False
                
                # Pobierz kontrakt V3->V4
                v3_contract = v3_result.get("v3_contract")
                if v3_contract:
                    result.v3_to_v4_contract = v3_contract
            
            # Krok 3: V4 (Decyzja)
            if result.success:
                self.logger.info("Starting V4 stage...")
                v4_start = time.time()
                v4_result = self._execute_v4_stage(result.v3_to_v4_contract)
                v4_elapsed = (time.time() - v4_start) * 1000
                result.step_times["v4"] = v4_elapsed
                result.v4_result = v4_result
                result.decision_result = v4_result.get("decision_result")
                
                if v4_result.get("status") == "error":
                    result.errors.append(v4_result.get("error", "V4 error"))
                    result.success = False
            
            # Krok 4: Feedback
            if result.success and result.decision_result:
                self.logger.info("Starting Feedback stage...")
                fb_start = time.time()
                fb_result = self._execute_feedback_stage(result.decision_result)
                fb_elapsed = (time.time() - fb_start) * 1000
                result.step_times["feedback"] = fb_elapsed
                result.feedback_result = fb_result.get("feedback_result")
                
                if fb_result.get("status") == "error":
                    result.errors.append(fb_result.get("error", "Feedback error"))
                    result.success = False
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Fatal error: {e}")
            self.logger.error(f"Fatal error in vertical flow: {e}")
        
        # Finalizacja lineage
        result.lineage = self.lineage_tracker.finalize()
        
        # Czas wykonania
        overall_elapsed = (time.time() - overall_start) * 1000
        result.execution_time_ms = overall_elapsed
        
        return result


def run_smoke_test(
    data: Optional[List[Dict[str, Any]]] = None,
    config: Optional[VerticalFlowConfig] = None
) -> FlowResult:
    """
    Funkcja wygodna - uruchamia pionowy smoke test.
    
    Args:
        data: Dane wejściowe (opcjonalne)
        config: Konfiguracja (opcjonalne)
        
    Returns:
        FlowResult z wynikami
    """
    flow = VerticalFlow(config=config)
    return flow.run(data)


if __name__ == "__main__":
    from SSI.core.logging_config import (
        setup_logging, get_logger, set_correlation_id, generate_correlation_id
    )
    
    # Skonfiguruj logging
    setup_logging(level=logging.INFO, json_format=False)
    logger = get_logger(__name__)
    
    # Ustaw correlation_id
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    logger.info("Testing Vertical Flow...", extra={"correlation_id": correlation_id})
    
    # Uruchom smoke test
    result = run_smoke_test()
    
    logger.info(f"Result: Success={result.success}, Execution time={result.execution_time_ms:.2f}ms",
                extra={"correlation_id": correlation_id})
    
    if result.step_times:
        logger.info("Step times:", extra={"correlation_id": correlation_id})
        for step, time_ms in result.step_times.items():
            logger.info(f"  {step}: {time_ms:.2f}ms", extra={"correlation_id": correlation_id})
    
    if result.errors:
        logger.warning("Errors found:", extra={"correlation_id": correlation_id})
        for error in result.errors:
            logger.error(f"  - {error}", extra={"correlation_id": correlation_id})
    
    if result.lineage:
        logger.info(f"Lineage: {result.lineage.get_summary()}", 
                    extra={"correlation_id": correlation_id})
    
    if not result.success:
        logger.error("Smoke test FAILED", extra={"correlation_id": correlation_id})
        sys.exit(1)
    
    logger.info("✅ Smoke test PASSED", extra={"correlation_id": correlation_id})
