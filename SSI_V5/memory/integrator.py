# SSI V5 - Memory Integrator
# ETAP 1.2.7.3: Adaptive Knowledge Ecosystem

"""
MemoryIntegrator - Warstwa wejścia dla systemu pamięci.

Odpowiada za:
- Przetwarzanie wyników cykli i eksperymentów
- Normalizację danych z różnych źródeł do formatu MemoryRecord
- Przekazywanie rekordów do MemoryEcosystem
- **NIE ZNA** żadnego konkretnego Store'a

Architektura:
    Pipeline/Agents
          |
          v
    wynik cyklu/eksperymentu
          |
          v
    MemoryIntegrator (normalizacja -> MemoryRecord)
          |
          v
    MemoryEcosystem.save(record)
          |
          v
    Routing do odpowiedniego Store'a

Kontrakt:
    - Zależność TYLKO od MemoryEcosystem (nie od Store'ów)
    - Przetwarza: cycle_result, experiment_result, agent_decision, phase_transition
    - Publikuje zdarzenia przez IFC (opcjonalnie)

Użycie:
    integrator = MemoryIntegrator(memory_ecosystem, ifc=None)
    
    # Przetwarzanie wyniku cyklu
    memory_ids = integrator.process_cycle_result(cycle_data)
    
    # Przetwarzanie eksperymentu
    memory_id = integrator.process_experiment_result(exp_data)
    
    # Przetwarzanie decyzji agenta
    memory_id = integrator.process_agent_decision(decision_data)
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

# Import lokalny (unikanie circular imports)
from .stores.base_store import MemoryRecord


@dataclass
class IntegrationResult:
    """Wynik integracji danych z pamięcią."""
    success: bool
    memory_ids: List[str] = field(default_factory=list)
    record_count: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'success': self.success,
            'memory_ids': self.memory_ids.copy(),
            'record_count': self.record_count,
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy(),
            'timestamp': self.timestamp
        }


class MemoryIntegrator:
    """
    Warstwa wejścia systemu pamięci.
    
    Jest **jedynym** punktem wejścia do MemoryEcosystem.
    **Nie zna** żadnych konkretnych Store'ów.
    """
    
    # Typy rekordów dla różnych źródeł
    # Mapowanie do istniejących Store'ów:
    # - cycle_memory -> system_memory (dla rekordów cyklu, ETAP 1.2.7.3)
    # - phase_transition -> system_memory (dla przejść faz, ETAP 1.2.7.3)
    # - experiment -> experiment_memory (dla eksperymentów)
    # - decision_memory -> agent_store (decyzje są podejmowane przez agentów)
    # - knowledge_record -> experiment_store (na razie, ETAP 1.5 będzie miał knowledge_store)
    # 
    # UWAGA: system_memory nie ma jeszcze dedykowanego Store'a
    # Tymczasowo rekordy system_memorry trafiają do experiment_store
    # Docelowo (przyszłe etapy) będą miały SystemMemoryStore
    RECORD_TYPES = {
        "cycle": "system_memory",
        "experiment": "experiment_memory",
        "agent": "agent_memory",
        "model": "model_memory",
        "phase_transition": "system_memory",
        "decision": "agent_memory",
        "knowledge": "knowledge_record",
        "default": "experiment_memory"
    }
    
    def __init__(
        self,
        memory_ecosystem: Any,
        ifc: Optional[Any] = None,
        source: str = "memory_integrator"
    ):
        """
        Inicjalizacja MemoryIntegrator.
        
        Args:
            memory_ecosystem: Referencja do MemoryEcosystem
            ifc: Referencja do IFCRegistry (opcjonalna)
            source: Nazwa źródła (dla metadanych rekordów)
        """
        self.memory_ecosystem = memory_ecosystem
        self.ifc = ifc
        self.source = source
        self._integration_log: List[Dict[str, Any]] = []
        self._stats = {
            'total_integrations': 0,
            'successful_integrations': 0,
            'failed_integrations': 0,
            'total_records_created': 0
        }
        
        # Rejestracja w IFC (jeśli dostępne)
        if ifc is not None:
            ifc.register("memory_integrator", self, component_type="memory")
    
    # ==================== MAIN INTEGRATION METHODS ====================
    
    def process_cycle_result(self, cycle_data: Dict[str, Any]) -> IntegrationResult:
        """
        Przetwarzanie wyniku cyklu na rekord/y pamięci.
        
        Tworzy jeden lub więcej rekordów na podstawie:
        - world_data
        - modeling_data
        - teacher_data
        - agent_data
        - collective_data
        - trust_data
        - observation_data
        
        Args:
            cycle_data: Słownik z danymi cyklu
            
        Returns:
            IntegrationResult z listą memory_id
        """
        result = IntegrationResult(success=True)
        memory_ids = []
        
        try:
            # Wyodrębnienie danych z cyklu
            cycle_id = cycle_data.get('cycle_id', 'unknown_cycle')
            timestamp = cycle_data.get('timestamp', datetime.now().isoformat())
            
            # 1. Rekord cyklu (główny)
            cycle_record = self._create_cycle_record(cycle_data, cycle_id, timestamp)
            if cycle_record:
                memory_id = self.memory_ecosystem.save(cycle_record)
                memory_ids.append(memory_id)
                result.record_count += 1
            
            # 2. Rekordy agentów (jeśli dostępne)
            agent_data = cycle_data.get('agent_data', {})
            if agent_data:
                agent_ids = self._process_agent_data(agent_data, cycle_id, timestamp)
                memory_ids.extend(agent_ids)
                result.record_count += len(agent_ids)
            
            # 3. Rekord eksperymentu (jeśli dostępne)
            exp_data = cycle_data.get('experiment_data', {})
            if exp_data:
                exp_id = self._process_experiment_data(exp_data, cycle_id, timestamp)
                if exp_id:
                    memory_ids.append(exp_id)
                    result.record_count += 1
            
            # 4. Rekord ModelMemory (jeśli dostępne)
            model_data = cycle_data.get('model_data', {})
            if model_data:
                model_ids = self._process_model_data(model_data, cycle_id, timestamp)
                memory_ids.extend(model_ids)
                result.record_count += len(model_ids)
            
            result.memory_ids = memory_ids
            self._stats['successful_integrations'] += 1
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            self._stats['failed_integrations'] += 1
        
        self._stats['total_integrations'] += 1
        self._stats['total_records_created'] += result.record_count
        self._log_integration("cycle_result", result)
        
        return result
    
    def process_experiment_result(self, experiment_data: Dict[str, Any]) -> IntegrationResult:
        """
        Przetwarzanie wyniku eksperymentu na rekord pamięci.
        
        Args:
            experiment_data: Słownik z danymi eksperymentu
            
        Returns:
            IntegrationResult
        """
        result = IntegrationResult(success=True)
        
        try:
            # Konwersja do MemoryRecord
            record = self._experiment_to_record(experiment_data)
            memory_id = self.memory_ecosystem.save(record)
            result.memory_ids = [memory_id]
            result.record_count = 1
            self._stats['successful_integrations'] += 1
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            self._stats['failed_integrations'] += 1
        
        self._stats['total_integrations'] += 1
        self._stats['total_records_created'] += result.record_count
        self._log_integration("experiment_result", result)
        
        return result
    
    def process_agent_decision(self, decision_data: Dict[str, Any]) -> IntegrationResult:
        """
        Przetwarzanie decyzji agenta na rekord pamięci.
        
        Args:
            decision_data: Słownik z danymi decyzji
            
        Returns:
            IntegrationResult
        """
        result = IntegrationResult(success=True)
        
        try:
            # Konwersja do MemoryRecord
            record = self._agent_decision_to_record(decision_data)
            memory_id = self.memory_ecosystem.save(record)
            result.memory_ids = [memory_id]
            result.record_count = 1
            self._stats['successful_integrations'] += 1
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            self._stats['failed_integrations'] += 1
        
        self._stats['total_integrations'] += 1
        self._stats['total_records_created'] += result.record_count
        self._log_integration("agent_decision", result)
        
        return result
    
    def process_phase_transition(
        self,
        from_phase: str,
        to_phase: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntegrationResult:
        """
        Rejestracja przejścia między fazami jako rekord pamięci.
        
        Args:
            from_phase: Faza początowa
            to_phase: Faza docelowa
            context: Kontekst przejścia
            
        Returns:
            IntegrationResult
        """
        result = IntegrationResult(success=True)
        
        try:
            record = self._phase_transition_to_record(from_phase, to_phase, context)
            memory_id = self.memory_ecosystem.save(record)
            result.memory_ids = [memory_id]
            result.record_count = 1
            self._stats['successful_integrations'] += 1
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            self._stats['failed_integrations'] += 1
        
        self._stats['total_integrations'] += 1
        self._stats['total_records_created'] += result.record_count
        self._log_integration("phase_transition", result)
        
        return result
    
    def process_knowledge_object(self, knowledge_data: Dict[str, Any]) -> IntegrationResult:
        """
        Przetwarzanie obiektu wiedzy (przyszłe - ETAP 1.5).
        
        Args:
            knowledge_data: Słownik z obiektem wiedzy
            
        Returns:
            IntegrationResult
        """
        result = IntegrationResult(success=True)
        
        try:
            record = self._knowledge_to_record(knowledge_data)
            memory_id = self.memory_ecosystem.save(record)
            result.memory_ids = [memory_id]
            result.record_count = 1
            self._stats['successful_integrations'] += 1
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            self._stats['failed_integrations'] += 1
        
        self._stats['total_integrations'] += 1
        self._stats['total_records_created'] += result.record_count
        self._log_integration("knowledge_object", result)
        
        return result
    
    # ==================== RECORD CONVERSION METHODS ====================
    
    def _create_cycle_record(
        self,
        cycle_data: Dict[str, Any],
        cycle_id: str,
        timestamp: str
    ) -> Optional[MemoryRecord]:
        """Tworzenie rekordu cyklu.
        
        Rekord cyklu jest typem system_memory - przetrzymuje informacje o wykonaniu cyklu.
        Nie wymaga eksperymentów ani hipotez.
        """
        content = {
            'cycle_id': cycle_id,
            'timestamp': timestamp,
            'status': cycle_data.get('status', 'completed'),
            'duration': cycle_data.get('duration', 0.0),
            'steps': cycle_data.get('steps', {}),
            'errors': cycle_data.get('errors', []),
            'metadata': cycle_data.get('metadata', {})
        }
        
        # Dodaj podsumowanie
        if 'steps' in cycle_data:
            content['summary'] = self._extract_step_summary(cycle_data['steps'])
        
        return MemoryRecord.create(
            content=content,
            memory_type=self.RECORD_TYPES.get("cycle", self.RECORD_TYPES["default"]),
            source=self.source,
            metadata={
                'integration_type': 'cycle_result',
                'processed_at': datetime.now().isoformat()
            }
        )
    
    def _process_agent_data(
        self,
        agent_data: Dict[str, Any],
        cycle_id: str,
        timestamp: str
    ) -> List[str]:
        """Przetwarzanie danych agentów na rekordy."""
        memory_ids = []
        
        # Jeśli agent_data to lista
        if isinstance(agent_data, list):
            for agent_item in agent_data:
                record = self._agent_decision_to_record(agent_item)
                # Dodaj kontekst cyklu
                record.metadata['cycle_id'] = cycle_id
                record.metadata['cycle_timestamp'] = timestamp
                memory_id = self.memory_ecosystem.save(record)
                memory_ids.append(memory_id)
        
        # Jeśli agent_data to słownik
        elif isinstance(agent_data, dict):
            # Jeśli zawiera listę decyzji
            if 'decisions' in agent_data:
                for decision in agent_data['decisions']:
                    decision['agent_id'] = agent_data.get('agent_id', 'unknown')
                    record = self._agent_decision_to_record(decision)
                    record.metadata['cycle_id'] = cycle_id
                    memory_id = self.memory_ecosystem.save(record)
                    memory_ids.append(memory_id)
            else:
                # Traktuj jako pojedynczego agenta
                record = self._agent_decision_to_record(agent_data)
                record.metadata['cycle_id'] = cycle_id
                memory_id = self.memory_ecosystem.save(record)
                memory_ids.append(memory_id)
        
        return memory_ids
    
    def _process_experiment_data(
        self,
        exp_data: Dict[str, Any],
        cycle_id: str,
        timestamp: str
    ) -> Optional[str]:
        """Przetwarzanie danych eksperymentu."""
        record = self._experiment_to_record(exp_data)
        record.metadata['cycle_id'] = cycle_id
        record.metadata['cycle_timestamp'] = timestamp
        return self.memory_ecosystem.save(record)
    
    def _process_model_data(
        self,
        model_data: Dict[str, Any],
        cycle_id: str,
        timestamp: str
    ) -> List[str]:
        """Przetwarzanie danych modeli."""
        memory_ids = []
        
        if isinstance(model_data, list):
            for model_item in model_data:
                record = self._model_to_record(model_item)
                record.metadata['cycle_id'] = cycle_id
                memory_id = self.memory_ecosystem.save(record)
                memory_ids.append(memory_id)
        elif isinstance(model_data, dict):
            if 'models' in model_data:
                for model_item in model_data['models']:
                    record = self._model_to_record(model_item)
                    record.metadata['cycle_id'] = cycle_id
                    memory_id = self.memory_ecosystem.save(record)
                    memory_ids.append(memory_id)
            else:
                record = self._model_to_record(model_data)
                record.metadata['cycle_id'] = cycle_id
                memory_id = self.memory_ecosystem.save(record)
                memory_ids.append(memory_id)
        
        return memory_ids
    
    def _experiment_to_record(self, exp_data: Dict[str, Any]) -> MemoryRecord:
        """Konwersja danych eksperymentu do MemoryRecord."""
        content = {
            'experiment_id': exp_data.get('experiment_id', f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            'cycle_id': exp_data.get('cycle_id'),
            'hypothesis': exp_data.get('hypothesis', {}),
            'design': exp_data.get('design', {}),
            'result': exp_data.get('result', {}),
            'conclusion': exp_data.get('conclusion', {}),
            'knowledge_impact': exp_data.get('knowledge_impact', {})
        }
        
        return MemoryRecord.create(
            content=content,
            memory_type=self.RECORD_TYPES.get("experiment", self.RECORD_TYPES["default"]),
            source=self.source,
            metadata={
                'integration_type': 'experiment_result',
                'processed_at': datetime.now().isoformat()
            }
        )
    
    def _agent_decision_to_record(self, decision_data: Dict[str, Any]) -> MemoryRecord:
        """Konwersja decyzji agenta do MemoryRecord."""
        content = {
            'agent_id': decision_data.get('agent_id', 'unknown'),
            'decision_id': decision_data.get('decision_id', f"dec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            'decision_type': decision_data.get('type', decision_data.get('decision_type', 'unknown')),
            'confidence': decision_data.get('confidence'),
            'reasoning': decision_data.get('reasoning', ''),
            'context': decision_data.get('context', {}),
            'outcome': decision_data.get('outcome', {}),
            'profit': decision_data.get('profit'),
            'success': decision_data.get('success')
        }
        
        # Warszawianie doświadczenia
        experience_type = self._classify_agent_experience(decision_data)
        content['experience_type'] = experience_type
        
        return MemoryRecord.create(
            content=content,
            memory_type=self.RECORD_TYPES.get("agent", self.RECORD_TYPES["default"]),
            source=self.source,
            metadata={
                'integration_type': 'agent_decision',
                'processed_at': datetime.now().isoformat()
            }
        )
    
    def _model_to_record(self, model_data: Dict[str, Any]) -> MemoryRecord:
        """Konwersja danych modelu do MemoryRecord."""
        content = {
            'model_name': model_data.get('model_name', model_data.get('name', 'unknown')),
            'model_version': model_data.get('version', model_data.get('model_version', '1.0.0')),
            'strategy': model_data.get('strategy', 'unknown'),
            'result': model_data.get('result', model_data.get('status', 'unknown')),
            'accuracy': model_data.get('accuracy'),
            'confidence': model_data.get('confidence'),
            'performance_metrics': model_data.get('performance_metrics', {}),
            'context': model_data.get('context', {}),
            'lessons_learned': model_data.get('lessons_learned', [])
        }
        
        return MemoryRecord.create(
            content=content,
            memory_type=self.RECORD_TYPES.get("model", self.RECORD_TYPES["default"]),
            source=self.source,
            metadata={
                'integration_type': 'model_experience',
                'processed_at': datetime.now().isoformat()
            }
        )
    
    def _phase_transition_to_record(
        self,
        from_phase: str,
        to_phase: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MemoryRecord:
        """Konwersja przejścia fazy do MemoryRecord.
        
        Rekord przejścia fazy jest typem system_memory - przetrzymuje informacje o zmianach faz.
        """
        transition_id = f"phase_{from_phase}_to_{to_phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        content = {
            'transition_id': transition_id,
            'from_phase': from_phase,
            'to_phase': to_phase,
            'transition_time': datetime.now().isoformat(),
            'context': context or {}
        }
        
        return MemoryRecord.create(
            content=content,
            memory_type=self.RECORD_TYPES.get("phase_transition", self.RECORD_TYPES["default"]),
            source=self.source,
            metadata={
                'integration_type': 'phase_transition',
                'processed_at': datetime.now().isoformat()
            }
        )
    
    def _knowledge_to_record(self, knowledge_data: Dict[str, Any]) -> MemoryRecord:
        """Konwersja obiektu wiedzy do MemoryRecord (ETAP 1.5).
        
        Rekord wiedzy jest typem knowledge_record.
        """
        knowledge_id = knowledge_data.get('knowledge_id', f"know_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        content = {
            'knowledge_id': knowledge_id,
            'problem': knowledge_data.get('problem', ''),
            'participants': knowledge_data.get('participants', []),
            'hypotheses': knowledge_data.get('hypotheses', []),
            'consensus_decision': knowledge_data.get('consensus_decision', ''),
            'validation_result': knowledge_data.get('validation_result'),
            'future_reference': knowledge_data.get('future_reference', True)
        }
        
        return MemoryRecord.create(
            content=content,
            memory_type=self.RECORD_TYPES.get("knowledge", self.RECORD_TYPES["default"]),
            source=self.source,
            metadata={
                'integration_type': 'knowledge_object',
                'processed_at': datetime.now().isoformat()
            }
        )
    
    # ==================== HELPER METHODS ====================
    
    def _extract_step_summary(self, steps: Dict[str, Any]) -> Dict[str, Any]:
        """Wyodrębnienie podsumowania z kroków cyklu."""
        summary = {}
        for step_name, step_data in steps.items():
            if isinstance(step_data, dict):
                summary[step_name] = {
                    'status': step_data.get('status'),
                    'duration': step_data.get('duration'),
                    'error': step_data.get('error')
                }
        return summary
    
    def _classify_agent_experience(self, decision_data: Dict[str, Any]) -> str:
        """Klasyfikacja doświadczenia agenta."""
        # Sprawdź czy jest jawny typ
        exp_type = decision_data.get('experience_type')
        if exp_type:
            return exp_type
        
        # Klasyfikacja na podstawie wyniku
        outcome = decision_data.get('outcome', {}).get('result', '')
        success = decision_data.get('success')
        profit = decision_data.get('profit', 0)
        
        if outcome == 'success' or success is True or profit > 0:
            return 'success'
        elif outcome == 'failure' or success is False or profit < 0:
            return 'failure'
        elif outcome == 'error':
            return 'error'
        else:
            return 'decision'  # Domyślnie jako decyzja
    
    def _log_integration(self, operation: str, result: IntegrationResult) -> None:
        """Logowanie integracji."""
        log_entry = {
            'timestamp': result.timestamp,
            'operation': operation,
            'success': result.success,
            'memory_ids': result.memory_ids.copy(),
            'record_count': result.record_count,
            'errors': result.errors.copy()
        }
        self._integration_log.append(log_entry)
        
        # Ograniczenie logu
        if len(self._integration_log) > 10000:
            self._integration_log = self._integration_log[-10000:]
    
    # ==================== STATISTICS & HEALTH ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Pobranie statystyk integratora.
        
        Returns:
            Słownik ze statystykami
        """
        return {
            **self._stats,
            'integration_log_size': len(self._integration_log),
            'memory_ecosystem_status': self.memory_ecosystem._status.value if hasattr(self.memory_ecosystem, '_status') else 'unknown'
        }
    
    def get_integration_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Pobranie historii integracji.
        
        Args:
            limit: Maksymalna liczba wpisów
            
        Returns:
            Lista wpisów historii
        """
        return self._integration_log[-limit:] if limit else self._integration_log.copy()
    
    def clear_history(self) -> None:
        """Wyczyszczenie historii integracji."""
        self._integration_log.clear()
    
    def reset_statistics(self) -> None:
        """Resetowanie statystyk."""
        self._stats = {
            'total_integrations': 0,
            'successful_integrations': 0,
            'failed_integrations': 0,
            'total_records_created': 0
        }
    
    def shutdown(self) -> None:
        """Zamknięcie integratora."""
        self.clear_history()
        self.reset_statistics()
        
        # Usunięcie z IFC
        if self.ifc:
            self.ifc.unregister("memory_integrator")
