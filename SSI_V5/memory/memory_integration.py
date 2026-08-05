# SSI V5 - Memory Integration Layer
# ==================================================
#
# ETAP: 0 KROK 1 - Agent Memory Integration
# Data: 2026-08-04
# 
# Odpowiedzialnosc:
# - Adapter pomiedzy AgentRuntime a CollectiveMemoryManager
# - Pobieranie kontekstu pamieci dla agentow
# - Zapis doświadczen i decyzji do pamieci kolektywnej
# - Ukrycie zlozonosci CollectiveMemoryManager
#
# ZASADY:
# 1. NIE modyfikowac istniejacych modułow pamieci
# 2. TYLKO dodawac warstwe abstrakcji
# 3. NIE zmieniac Decision Engine w tym kroku
# 4. Wszystkie operacje thread-safe
#
# Uzycie:
#   from SSI_V5.memory.memory_integration import MemoryIntegrationLayer
#   
#   memory_layer = MemoryIntegrationLayer(collective_manager)
#   context = memory_layer.retrieve_context(agent_id, current_situation)
#   memory_layer.store_decision(agent_id, decision_data)
#

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import threading
import logging
import copy
import uuid

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class MemoryIntegrationError(Exception):
    """Wyvjatki dla warstwy integracji pamieci"""
    pass


class MemoryIntegrationLayer:
    """
    Warstwa integracji pamieci - adapter pomiedzy AgentRuntime a CollectiveMemoryManager.
    
    Odpowiedzialnosc:
    - Pobieranie kontekstu pamieci dla agentow PRZED podjeciem decyzji
    - Zapis doświadczen i decyzji do pamieci kolektywnej PO podjeciu decyzji
    - Ukrycie szczegolow implementacji CollectiveMemoryManager
    - Zapewnienie jednolitego API dla wszystkich agentow
    
    Uzycie:
        # Inicjalizacja
        from SSI_V5.memory.collective_memory.collective_memory_manager import CollectiveMemoryManager
        collective_manager = CollectiveMemoryManager()
        memory_layer = MemoryIntegrationLayer(collective_manager)
        
        # Pobranie kontekstu dla agenta
        context = memory_layer.retrieve_context(
            agent_id="agent_01",
            current_situation={"world_state": "active", "phase": "prediction"}
        )
        
        # Zapis decyzji
        memory_layer.store_decision(
            agent_id="agent_01",
            decision_data={"decision_type": "model_selection", "parameters": {...}}
        )
    """
    
    def __init__(self, collective_memory_manager: Any):
        """
        Inicjalizacja warstwy integracji pamieci.
        
        Args:
            collective_memory_manager: Instancja CollectiveMemoryManager
        
        Raises:
            MemoryIntegrationError: Jesli collective_memory_manager jest None
        """
        if collective_memory_manager is None:
            raise MemoryIntegrationError("CollectiveMemoryManager cannot be None")
        
        self._collective_manager = collective_memory_manager
        self._lock = threading.RLock()
        self._initialized = False
        
        # Statystyki operacji
        self._stats = {
            'retrieve_operations': 0,
            'store_operations': 0,
            'search_operations': 0,
            'success_count': 0,
            'error_count': 0
        }
        
        logger.info("MemoryIntegrationLayer initialized")
    
    def initialize(self) -> Dict[str, Any]:
        """
        Inicjalizacja warstwy integracji.
        
        Returns:
            Status inicjalizacji
        """
        with self._lock:
            if self._initialized:
                return {
                    'status': 'success',
                    'message': 'Already initialized',
                    'timestamp': datetime.now().isoformat()
                }
            
            try:
                # Sprawdzenie czy CollectiveMemoryManager jest gotowy
                if not hasattr(self._collective_manager, 'store_memory'):
                    raise MemoryIntegrationError("CollectiveMemoryManager missing store_memory method")
                
                if not hasattr(self._collective_manager, 'search_memories'):
                    raise MemoryIntegrationError("CollectiveMemoryManager missing search_memories method")
                
                if not hasattr(self._collective_manager, 'build_agent_context'):
                    raise MemoryIntegrationError("CollectiveMemoryManager missing build_agent_context method")
                
                self._initialized = True
                logger.info("MemoryIntegrationLayer successfully initialized")
                
                return {
                    'status': 'success',
                    'message': 'MemoryIntegrationLayer initialized',
                    'collective_manager_type': type(self._collective_manager).__name__,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"MemoryIntegrationLayer initialization failed: {str(e)}")
                return {
                    'status': 'error',
                    'message': f'Initialization failed: {str(e)}',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    @property
    def is_initialized(self) -> bool:
        """Czy warstwa jest zainicjalizowana?"""
        return self._initialized
    
    @property
    def collective_manager(self) -> Any:
        """Zwraca instancje CollectiveMemoryManager"""
        return self._collective_manager
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Zwraca statystyki operacji"""
        with self._lock:
            return copy.deepcopy(self._stats)
    
    def retrieve_context(
        self,
        agent_id: str,
        current_situation: Dict[str, Any],
        top_k: int = 5,
        min_similarity: float = 0.6
    ) -> Dict[str, Any]:
        """
        Pobiera kontekst pamieci dla agenta na podstawie biezej sytuacji.
        
        Ta metoda jest wywolywana PRZED podjeciem decyzji przez agenta,
        aby dostarczyc historyczny kontekst i podobne przypadki z przeszlosci.
        
        Args:
            agent_id: Unikalny identyfikator agenta
            current_situation: Biezaca sytuacja agenta (slownik z danymi)
            top_k: Maksymalna liczba pamięci do pobrania (domyslnie 5)
            min_similarity: Minimalne podobienstwo (0.0-1.0, domyslnie 0.6)
            
        Returns:
            Slownik z statusem, kontekstem pamieci i statystykami
            
        Example:
            context = memory_layer.retrieve_context(
                agent_id="agent_01",
                current_situation={
                    "world_name": "PremierLeague",
                    "phase": "prediction_window",
                    "available_models": ["model_v1", "model_v2"],
                    "risk_level": "medium"
                }
            )
        """
        with self._lock:
            self._stats['retrieve_operations'] += 1
            
            try:
                start_time = datetime.now()
                
                # Walidacja inputu
                if not agent_id or not isinstance(agent_id, str):
                    raise MemoryIntegrationError("Invalid agent_id")
                
                if not current_situation or not isinstance(current_situation, dict):
                    raise MemoryIntegrationError("Invalid current_situation")
                
                # Pobranie kontekstu z CollectiveMemoryManager
                # Uzywamy build_agent_context, ktory zwraca strukturalny kontekst
                agent_context = self._collective_manager.build_agent_context(
                    agent_id=agent_id,
                    current_situation=current_situation,
                    max_context_length=2000
                )
                
                # Dodatkowe wyszukiwanie podobnych pamięci
                related_memories = self._collective_manager.get_relevant_memories(
                    current_context=current_situation,
                    top_k=top_k,
                    min_similarity=min_similarity
                )
                
                # Formatowanie wyniku
                result = {
                    'status': 'success',
                    'agent_id': agent_id,
                    'memory_context': agent_context,
                    'related_memories': [
                        self._format_memory_document(mem) for mem in related_memories
                    ],
                    'memory_count': len(related_memories),
                    'retrieval_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                    'timestamp': datetime.now().isoformat()
                }
                
                self._stats['success_count'] += 1
                logger.debug(f"Retrieved context for agent {agent_id}: {len(related_memories)} memories")
                
                return result
                
            except Exception as e:
                self._stats['error_count'] += 1
                logger.error(f"Error retrieving context for agent {agent_id}: {str(e)}")
                return {
                    'status': 'error',
                    'agent_id': agent_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    def store_experience(
        self,
        agent_id: str,
        experience_data: Dict[str, Any],
        experience_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Zapisuje doswiadczenie agenta do pamieci kolektywnej.
        
        Ta metoda jest wywolywana PO podjeciu decyzji i wykonaniu akcji,
        aby zapamic doświadczenie agenta.
        
        Args:
            agent_id: Unikalny identyfikator agenta
            experience_data: Dane doswiadczenia (moze zawierac: observation, action, result, outcome)
            experience_type: Typ doswiadczenia (np: "decision_outcome", "strategy_analysis")
            context: Dodatkowy kontekst zwiazany z doswiadczeniem
            
        Returns:
            Slownik z statusem operacji i ID zapisanego dokumentu
            
        Experience Data Structure:
            {
                "experience_id": "exp_xxx",  # opcjonalne, zostanie wygenerowane
                "type": "decision_outcome",   # lub z experience_type
                "agent_id": "agent_01",
                "action": "select_model",
                "result": {"success": True, "score": 0.85},
                "outcome": "positive",
                "confidence": 0.75,
                "metadata": {"cycle_id": "cycle_001", "timestamp": "..."}
            }
        """
        with self._lock:
            self._stats['store_operations'] += 1
            
            try:
                start_time = datetime.now()
                
                # Walidacja inputu
                if not agent_id or not isinstance(agent_id, str):
                    raise MemoryIntegrationError("Invalid agent_id")
                
                if not experience_data or not isinstance(experience_data, dict):
                    raise MemoryIntegrationError("Invalid experience_data")
                
                # Przygotowanie dokumentu pamieci
                experience_record = self._prepare_experience_record(
                    agent_id=agent_id,
                    experience_data=experience_data,
                    experience_type=experience_type,
                    context=context
                )
                
                # Zapis do pamieci kolektywnej
                document_id = self._collective_manager.store_memory(experience_record)
                
                result = {
                    'status': 'success',
                    'agent_id': agent_id,
                    'experience_id': experience_record.get('experience_id'),
                    'document_id': document_id,
                    'stored_data': {
                        'type': experience_record.get('type'),
                        'agent_id': experience_record.get('agent_id'),
                        'timestamp': experience_record.get('timestamp')
                    },
                    'store_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                    'timestamp': datetime.now().isoformat()
                }
                
                self._stats['success_count'] += 1
                logger.debug(f"Stored experience for agent {agent_id}: {document_id}")
                
                return result
                
            except Exception as e:
                self._stats['error_count'] += 1
                logger.error(f"Error storing experience for agent {agent_id}: {str(e)}")
                return {
                    'status': 'error',
                    'agent_id': agent_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    def store_decision(
        self,
        agent_id: str,
        decision_data: Dict[str, Any],
        contract: Optional[Dict[str, Any]] = None,
        outcome: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Zapisuje decyzje agenta do pamieci kolektywnej.
        
        Ta metoda jest wywolywana PO podjeciu decyzji, aby zapamic:
        - Samej decyzji
        - Kontekstu w jakim zostala podjeta
        - Powiazanych danych kontraktu
        - Wyniku (jesli dostepny)
        
        Args:
            agent_id: Unikalny identyfikator agenta
            decision_data: Dane decyzji (powinny zawierac: decision_id, decision_type, parameters)
            contract: Powiazany kontrakt (opcjonalnie)
            outcome: Wynik decyzji (opcjonalnie, moze byc dodany pozniej)
            
        Returns:
            Slownik z statusem operacji i ID zapisanego dokumentu
            
        Decision Data Structure:
            {
                "decision_id": "dec_xxx",
                "decision_type": "model_selection",
                "agent_id": "agent_01",
                "parameters": {"model_name": "v2", "confidence": 0.85},
                "context": {"world_state": "...", "available_models": [...]},
                "confidence": 0.75,
                "priority": 1,
                "timestamp": "..."
            }
        """
        with self._lock:
            self._stats['store_operations'] += 1
            
            try:
                start_time = datetime.now()
                
                # Walidacja inputu
                if not agent_id or not isinstance(agent_id, str):
                    raise MemoryIntegrationError("Invalid agent_id")
                
                if not decision_data or not isinstance(decision_data, dict):
                    raise MemoryIntegrationError("Invalid decision_data")
                
                # Przygotowanie dokumentu decyzji
                decision_record = self._prepare_decision_record(
                    agent_id=agent_id,
                    decision_data=decision_data,
                    contract=contract,
                    outcome=outcome
                )
                
                # Zapis do pamieci kolektywnej
                document_id = self._collective_manager.store_memory(decision_record)
                
                result = {
                    'status': 'success',
                    'agent_id': agent_id,
                    'decision_id': decision_data.get('decision_id'),
                    'document_id': document_id,
                    'stored_data': {
                        'decision_type': decision_record.get('decision_type'),
                        'agent_id': decision_record.get('agent_id'),
                        'confidence': decision_record.get('confidence'),
                        'timestamp': decision_record.get('timestamp')
                    },
                    'store_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                    'timestamp': datetime.now().isoformat()
                }
                
                self._stats['success_count'] += 1
                logger.debug(f"Stored decision for agent {agent_id}: {document_id}")
                
                return result
                
            except Exception as e:
                self._stats['error_count'] += 1
                logger.error(f"Error storing decision for agent {agent_id}: {str(e)}")
                return {
                    'status': 'error',
                    'agent_id': agent_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    def search_related_memories(
        self,
        query: str,
        agent_id: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.5,
        source_type_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Wyszukuje powiazane pamięci na podstawie zapytania tekstowego.
        
        Ta metoda uzywa semantycznego wyszukiwania VectorIndex,
        aby znalezc podobne przypadki z przeszlosci.
        
        Args:
            query: Zapytanie tekstowe (np: "Liverpool vs Arsenal high risk")
            agent_id: Opcjonalny filtr po ID agenta
            top_k: Maksymalna liczba wynikow
            min_similarity: Minimalne podobienstwo (0.0-1.0)
            source_type_filter: Filtr po typie zrodla (np: "decision", "experience")
            
        Returns:
            Slownik z lista pasujacych pamięci i statystykami
        """
        with self._lock:
            self._stats['search_operations'] += 1
            
            try:
                start_time = datetime.now()
                
                # Walidacja inputu
                if not query or not isinstance(query, str):
                    raise MemoryIntegrationError("Invalid query")
                
                # Wyszukiwanie w pamieci kolektywnej
                search_results = self._collective_manager.search_memories(
                    query=query,
                    top_k=top_k * 2,  # Pobierz wiecej, pozniej zfiltrujemy
                    min_similarity=min_similarity,
                    source_type_filter=source_type_filter
                )
                
                # Filtruj po agent_id jesli zostaardless podany
                if agent_id:
                    search_results = [
                        doc for doc in search_results
                        if hasattr(doc, 'source_metadata') and 
                        doc.source_metadata.get('agent_id') == agent_id
                    ]
                
                # Ogranicz do top_k
                search_results = search_results[:top_k]
                
                result = {
                    'status': 'success',
                    'query': query,
                    'agent_id': agent_id,
                    'results': [
                        self._format_memory_document(doc) for doc in search_results
                    ],
                    'result_count': len(search_results),
                    'search_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                    'timestamp': datetime.now().isoformat()
                }
                
                self._stats['success_count'] += 1
                logger.debug(f"Searched memories for query '{query[:50]}...': {len(search_results)} results")
                
                return result
                
            except Exception as e:
                self._stats['error_count'] += 1
                logger.error(f"Error searching memories for query '{query[:50]}...': {str(e)}")
                return {
                    'status': 'error',
                    'query': query[:100] if query else "",
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    def batch_store(
        self,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Zapisuje wiele rekordow pamieci wsadowo.
        
        Args:
            records: Lista rekordow do zapisu (kazdy powinien zawierac agent_id i type)
            
        Returns:
            Slownik z statusem i lista ID zapisanych dokumentow
        """
        with self._lock:
            try:
                start_time = datetime.now()
                
                if not records or not isinstance(records, list):
                    raise MemoryIntegrationError("Invalid records list")
                
                # Przygotowanie rekordow do formatu akceptowanego przez CollectiveMemoryManager
                prepared_records = []
                for record in records:
                    if not isinstance(record, dict):
                        continue
                    
                    record_type = record.get('type', 'unknown')
                    agent_id = record.get('agent_id')
                    
                    if record_type == 'experience':
                        prepared_records.append(self._prepare_experience_record(
                            agent_id=agent_id,
                            experience_data=record.get('data', {}),
                            experience_type=record.get('subtype'),
                            context=record.get('context')
                        ))
                    elif record_type == 'decision':
                        prepared_records.append(self._prepare_decision_record(
                            agent_id=agent_id,
                            decision_data=record.get('data', {}),
                            contract=record.get('contract'),
                            outcome=record.get('outcome')
                        ))
                    else:
                        # Domyslnie traktuj jako ogolny rekord pamieci
                        prepared_records.append(self._prepare_generic_record(record))
                
                # Zapis wsadowy
                document_ids = self._collective_manager.store_batch(prepared_records)
                
                result = {
                    'status': 'success',
                    'batch_size': len(records),
                    'stored_count': len(document_ids),
                    'document_ids': document_ids,
                    'batch_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"Batch stored {len(document_ids)}/{len(records)} records")
                return result
                
            except Exception as e:
                logger.error(f"Error in batch store: {str(e)}")
                return {
                    'status': 'error',
                    'batch_size': len(records) if records else 0,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Pobiera statystyki pamieci kolektywnej.
        
        Returns:
            Statystyki pamieci i operacji
        """
        try:
            # Statystyki z CollectiveMemoryManager
            cm_stats = {}
            if hasattr(self._collective_manager, '_stats'):
                cm_stats = copy.deepcopy(self._collective_manager._stats)
            
            return {
                'status': 'success',
                'integration_layer_stats': self.stats,
                'collective_memory_stats': cm_stats,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    # ============================================================================
    # PRYWATNE METODY POMOCNICZE
    # ============================================================================
    
    def _prepare_experience_record(
        self,
        agent_id: str,
        experience_data: Dict[str, Any],
        experience_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Przygotowuje rekord doswiadczenia do zapisu w pamieci kolektywnej"""
        
        # Generowanie ID jesli nie zostalo podane
        experience_id = experience_data.get('experience_id', f"exp_{uuid.uuid4().hex[:12]}")
        
        # Okreslenie typu
        record_type = experience_type or experience_data.get('type') or "experience"
        
        # Budowa dokumentu pamieci
        record = {
            'experience_id': experience_id,
            'type': record_type,
            'source_type': 'agent_experience',
            'source_id': experience_id,
            'agent_id': agent_id,
            'data': copy.deepcopy(experience_data),
            'context': copy.deepcopy(context) if context else {},
            'timestamp': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'source': 'memory_integration_layer',
                'integration_step': 'etap_0_krok_1',
                'agent_id': agent_id
            }
        }
        
        # Dodanie dodatkowych pol jesli sa dostepne
        if 'action' in experience_data:
            record['action'] = experience_data['action']
        if 'result' in experience_data:
            record['result'] = experience_data['result']
        if 'outcome' in experience_data:
            record['outcome'] = experience_data['outcome']
        if 'confidence' in experience_data:
            record['confidence'] = experience_data['confidence']
        
        return record
    
    def _prepare_decision_record(
        self,
        agent_id: str,
        decision_data: Dict[str, Any],
        contract: Optional[Dict[str, Any]] = None,
        outcome: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Przygotowuje rekord decyzji do zapisu w pamieci kolektywnej"""
        
        # Generowanie ID jesli nie zostalo podane
        decision_id = decision_data.get('decision_id', f"dec_{uuid.uuid4().hex[:12]}")
        
        # Budowa dokumentu pamieci
        record = {
            'decision_id': decision_id,
            'type': 'decision',
            'source_type': 'agent_decision',
            'source_id': decision_id,
            'agent_id': agent_id,
            'decision_type': decision_data.get('decision_type', 'unknown'),
            'parameters': copy.deepcopy(decision_data.get('parameters', {})),
            'context': copy.deepcopy(decision_data.get('context', {})),
            'confidence': decision_data.get('confidence', 0.0),
            'priority': decision_data.get('priority', 0),
            'timestamp': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'source': 'memory_integration_layer',
                'integration_step': 'etap_0_krok_1',
                'agent_id': agent_id
            }
        }
        
        # Dodanie powiazanych danych
        if contract:
            record['contract_data'] = copy.deepcopy(contract)
            record['cycle_id'] = contract.get('cycle_id')
            record['world_name'] = contract.get('world_name')
        
        if outcome:
            record['outcome'] = copy.deepcopy(outcome)
            record['outcome_timestamp'] = datetime.now().isoformat()
        
        return record
    
    def _prepare_generic_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Przygotowuje ogolny rekord pamieci"""
        
        # Upewnij sie ze są wymagane pola
        if 'source_type' not in record:
            record['source_type'] = 'generic_memory'
        if 'source_id' not in record:
            record['source_id'] = f"mem_{uuid.uuid4().hex[:12]}"
        if 'timestamp' not in record:
            record['timestamp'] = datetime.now().isoformat()
        if 'metadata' not in record:
            record['metadata'] = {
                'source': 'memory_integration_layer',
                'integration_step': 'etap_0_krok_1'
            }
        
        return copy.deepcopy(record)
    
    def _format_memory_document(self, document: Any) -> Dict[str, Any]:
        """Formatuje dokument pamieci do standardowego formatu wyjsciowego"""
        
        if document is None:
            return {}
        
        # Pobranie atrybutow z dokumentu
        formatted = {
            'document_id': getattr(document, 'document_id', None) or document.get('document_id'),
            'source_type': getattr(document, 'source_type', None) or document.get('source_type'),
            'source_id': getattr(document, 'source_id', None) or document.get('source_id'),
            'agent_id': getattr(document, 'agent_id', None) or document.get('agent_id'),
            'type': getattr(document, 'type', None) or document.get('type'),
            'content': getattr(document, 'content', None) or document.get('content', ''),
            'data': getattr(document, 'data', None) or document.get('data', {}),
            'timestamp': getattr(document, 'timestamp', None) or document.get('timestamp'),
            'confidence': getattr(document, 'confidence', None) or document.get('confidence'),
            'metadata': getattr(document, 'source_metadata', None) or document.get('metadata', {})
        }
        
        # Usuniecie None'y
        formatted = {k: v for k, v in formatted.items() if v is not None}
        
        return formatted