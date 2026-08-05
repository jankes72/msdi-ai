#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test integracyjny Memory Stores - ETAP 1.2.7.3"""

from SSI_V5.memory.stores import (
    BaseMemoryStore, MemoryRecord, MemoryQuery,
    ModelMemoryStore, AgentMemoryStore, ExperimentMemoryStore
)


def test_base_store_functionality():
    """Test 1: Podstawowa funkcjonalność BaseMemoryStore."""
    print('Test 1: BaseMemoryStore - Podstawowa funkcjonalnosc')
    
    # Tworzymy konkretną implementację do testu
    class TestStore(BaseMemoryStore):
        def _get_memory_type(self) -> str:
            return "test_memory"
        def _validate_record(self, record: MemoryRecord) -> bool:
            return 'test_field' in record.content
    
    store = TestStore()
    
    # Test zapisywania
    record = MemoryRecord.create(
        content={'test_field': 'test_value'},
        memory_type='test_memory',
        source='test'
    )
    memory_id = store.save(record)
    print(f'  Zapisano rekord: {memory_id}')
    assert memory_id is not None
    
    # Test pobierania
    retrieved = store.get(memory_id)
    print(f'  Pobrano rekord: {retrieved.content}')
    assert retrieved is not None
    assert retrieved.content['test_field'] == 'test_value'
    
    # Test liczenia
    count = store.count()
    print(f'  Liczba rekordow: {count}')
    assert count == 1
    
    # Test wyszukiwania
    query = MemoryQuery(content_key='test_field', content_value='test_value')
    results = store.find(query)
    print(f'  Znaleziono rekordow: {len(results)}')
    assert len(results) == 1
    
    # Test usuwania
    deleted = store.delete(memory_id)
    print(f'  Usunieto: {deleted}')
    assert deleted is True
    assert store.count() == 0
    
    # Test wyczyszczenia
    store.save(record)
    store.clear()
    assert store.count() == 0
    
    print('  [OK] Test 1 zaliczony')


def test_model_store():
    """Test 2: ModelMemoryStore."""
    print('\nTest 2: ModelMemoryStore')
    
    store = ModelMemoryStore()
    
    # Test zapisywania doświadczenia modelu
    memory_id = store.save_model_experience(
        model_name="RandomForest_v3",
        model_version="1.2.0",
        strategy="trend_follow",
        result="success",
        accuracy=0.82,
        confidence=0.78,
        context={"league": "Premier League", "market": "BTTS"},
        performance_metrics={"precision": 0.85, "recall": 0.78},
        lessons_learned=["Works best with sample_size > 100"]
    )
    print(f'  Zapisano doswiadczenie modelu: {memory_id}')
    assert memory_id is not None
    
    # Test pobierania po modelu
    model_records = store.get_by_model("RandomForest_v3")
    print(f'  Rekordy RandomForest_v3: {len(model_records)}')
    assert len(model_records) == 1
    
    # Test pobierania po strategii
    strategy_records = store.get_by_strategy("trend_follow")
    print(f'  Rekordy strategii trend_follow: {len(strategy_records)}')
    assert len(strategy_records) == 1
    
    # Test pobierania udanych
    successful = store.get_successful()
    print(f'  Udane doświadczenia: {len(successful)}')
    assert len(successful) == 1
    
    # Test statystyk modelu
    stats = store.get_model_statistics("RandomForest_v3")
    print(f'  Statystyki modelu: {stats}')
    assert stats['total_experiences'] == 1
    assert stats['success_rate'] == 1.0
    
    # Test zapisywania drugiej próby (nieudanej)
    store.save_model_experience(
        model_name="RandomForest_v3",
        strategy="counter_trend",
        result="failure",
        accuracy=0.45
    )
    
    stats = store.get_model_statistics("RandomForest_v3")
    print(f'  Statystyki po drugiej probie: {stats}')
    assert stats['total_experiences'] == 2
    assert stats['success_rate'] == 0.5
    
    # Test najlepszych modeli
    best_models = store.get_best_models(limit=10, min_experiences=1)
    print(f'  Najlepsze modele: {len(best_models)}')
    assert len(best_models) >= 1
    
    print('  [OK] Test 2 zaliczony')


def test_agent_store():
    """Test 3: AgentMemoryStore."""
    print('\nTest 3: AgentMemoryStore')
    
    store = AgentMemoryStore()
    
    # Test zapisywania doświadczenia agenta
    memory_id = store.save_agent_experience(
        agent_id="agent_001",
        experience_type="failed_prediction",
        decision={"type": "BTTS_Yes", "confidence": 0.75},
        outcome={"result": "BTTS_No", "profit": -1.0},
        lesson={
            "title": "Overconfidence in low-scoring teams",
            "confidence": 0.76,
            "tags": ["overconfidence", "BTTS"]
        }
    )
    print(f'  Zapisano doswiadczenie agenta: {memory_id}')
    assert memory_id is not None
    
    # Test pobierania po agencie
    agent_records = store.get_by_agent("agent_001")
    print(f'  Rekordy agent_001: {len(agent_records)}')
    assert len(agent_records) == 1
    
    # Test pobierania po typie doświadczenia
    failure_records = store.get_by_experience_type("failed_prediction")
    print(f'  Rekordy failed_prediction: {len(failure_records)}')
    assert len(failure_records) == 1
    
    # Test statystyk agenta
    stats = store.get_agent_statistics("agent_001")
    print(f'  Statystyki agenta: {stats}')
    assert stats['total_experiences'] == 1
    assert stats['failure_count'] == 1
    
    # Test zapisywania sukcesu
    store.save_agent_experience(
        agent_id="agent_001",
        experience_type="success",
        outcome={"result": "BTTS_Yes", "profit": 2.5}
    )
    
    stats = store.get_agent_statistics("agent_001")
    print(f'  Statystyki po sukcesie: {stats}')
    assert stats['total_experiences'] == 2
    assert stats['success_count'] == 1
    assert stats['success_rate'] == 0.5
    
    # Test najlepszych agentów
    store.save_agent_experience(
        agent_id="agent_002",
        experience_type="success",
        outcome={"profit": 3.0}
    )
    
    best_agents = store.get_best_agents(limit=10, min_experiences=1)
    print(f'  Najlepszy agent: {best_agents[0]["agent_id"] if best_agents else "none"}')
    assert len(best_agents) >= 1
    
    print('  [OK] Test 3 zaliczony')


def test_experiment_store():
    """Test 4: ExperimentMemoryStore."""
    print('\nTest 4: ExperimentMemoryStore')
    
    store = ExperimentMemoryStore()
    
    # Test zapisywania względu eksperymentu
    memory_id = store.save_experiment_result(
        experiment_id="exp_001",
        cycle_id="cycle_001",
        hypothesis={
            "title": "Market reacts slower after odds movement",
            "category": "market_behavior",
            "confidence": 0.75
        },
        design={"type": "A/B_test"},
        result={
            "outcome": "confirming",
            "confidence": 0.82,
            "metrics": {"accuracy": 0.78, "profit_factor": 1.25}
        },
        conclusion={
            "verdict": "accept_hypothesis",
            "recommendation": "Implement new strategy"
        }
    )
    print(f'  Zapisano eksperyment: {memory_id}')
    assert memory_id is not None
    
    # Test pobierania po eksperymencie
    exp_records = store.get_by_experiment("exp_001")
    print(f'  Rekordy exp_001: {len(exp_records)}')
    assert len(exp_records) == 1
    
    # Test pobierania po cyklu
    cycle_records = store.get_by_cycle("cycle_001")
    print(f'  Rekordy cycle_001: {len(cycle_records)}')
    assert len(cycle_records) == 1
    
    # Test pobierania po kategorii hipotezy
    cat_records = store.get_by_hypothesis_category("market_behavior")
    print(f'  Rekordy market_behavior: {len(cat_records)}')
    assert len(cat_records) == 1
    
    # Test pobierania po wyniku
    confirming = store.get_by_outcome("confirming")
    print(f'  Rekordy confirming: {len(confirming)}')
    assert len(confirming) == 1
    
    # Test pobierania po werdykcie
    accepted = store.get_by_verdict("accept_hypothesis")
    print(f'  Rekordy accept_hypothesis: {len(accepted)}')
    assert len(accepted) == 1
    
    # Test statystyk eksperymentu
    stats = store.get_experiment_statistics("exp_001")
    print(f'  Statystyki eksperymentu: {stats}')
    assert stats['total_records'] == 1
    assert stats['outcome'] == 'confirming'
    
    # Test zapisywania drugiego eksperymentu (zaprzeczającego)
    store.save_experiment_result(
        experiment_id="exp_002",
        hypothesis={"category": "market_behavior"},
        result={"outcome": "denying"},
        conclusion={"verdict": "reject_hypothesis"}
    )
    
    # Test statystyk kategorii
    cat_stats = store.get_hypothesis_statistics("market_behavior")
    print(f'  Statystyki kategorii: {cat_stats}')
    assert cat_stats['total_experiments'] == 2
    assert cat_stats['confirming'] == 1
    assert cat_stats['denying'] == 1
    
    print('  [OK] Test 4 zaliczony')


def test_memory_record_structure():
    """Test 5: Struktura MemoryRecord."""
    print('\nTest 5: MemoryRecord - Struktura i serializacja')
    
    # Tworzenie rekordu
    record = MemoryRecord.create(
        content={"test": "data", "value": 42},
        memory_type="test_memory",
        source="test_source",
        metadata={"extra": "info"}
    )
    
    print(f'  ID: {record.memory_id[:8]}...')
    print(f'  Typ: {record.type}')
    print(f'  Zrodlo: {record.source}')
    print(f'  Timestamp: {record.timestamp[:16]}...')
    assert record.type == "test_memory"
    assert record.source == "test_source"
    assert record.timestamp is not None and len(record.timestamp) > 0
    
    # Serializacja do dict
    record_dict = record.to_dict()
    print(f'  Kit: {list(record_dict.keys())}')
    assert 'memory_id' in record_dict
    assert 'type' in record_dict
    assert 'content' in record_dict
    
    # Deserializacja
    restored = MemoryRecord.from_dict(record_dict)
    print(f'  Restored: {restored.content}')
    assert restored.content == record.content
    assert restored.source == record.source
    
    # Serializacja do JSON
    json_str = record.to_json()
    print(f'  JSON length: {len(json_str)}')
    assert len(json_str) > 0
    
    # Deserializacja z JSON
    from_json = MemoryRecord.from_json(json_str)
    assert from_json.memory_id == record.memory_id
    
    print('  [OK] Test 5 zaliczony')


def test_query_functionality():
    """Test 6: MemoryQuery - Filtrowanie."""
    print('\nTest 6: MemoryQuery - Filtrowanie')
    
    class TestStore(BaseMemoryStore):
        def _get_memory_type(self) -> str:
            return "test_query"
        def _validate_record(self, record: MemoryRecord) -> bool:
            return True
    
    store = TestStore()
    
    # Zapisujemy kilka rekordów
    store.save(MemoryRecord.create(
        content={"value": 10, "category": "A"},
        memory_type="test_query",
        source="source1",
        metadata={"priority": "high"}
    ))
    
    store.save(MemoryRecord.create(
        content={"value": 20, "category": "B"},
        memory_type="test_query",
        source="source2",
        metadata={"priority": "low"}
    ))
    
    store.save(MemoryRecord.create(
        content={"value": 30, "category": "A"},
        memory_type="test_query",
        source="source1",
        metadata={"priority": "medium"}
    ))
    
    # Test filtrowania po source
    query = MemoryQuery(source="source1")
    results = store.find(query)
    print(f'  Filtrowanie po source=source1: {len(results)}')
    assert len(results) == 2
    
    # Test filtrowania po content_key
    query = MemoryQuery(content_key="category", content_value="A")
    results = store.find(query)
    print(f'  Filtrowanie po category=A: {len(results)}')
    assert len(results) == 2
    
    # Test filtrowania po metadata
    query = MemoryQuery(metadata_key="priority", metadata_value="high")
    results = store.find(query)
    print(f'  Filtrowanie po priority=high: {len(results)}')
    assert len(results) == 1
    
    # Test limitowania
    query = MemoryQuery(limit=2)
    results = store.find(query)
    print(f'  Limit 2: {len(results)}')
    assert len(results) == 2
    
    print('  [OK] Test 6 zaliczony')


if __name__ == '__main__':
    print('=' * 60)
    print('MEMORY STORES - TESTY INTEGRACYJNE (ETAP 1.2.7.3)')
    print('=' * 60)
    
    try:
        test_base_store_functionality()
        test_model_store()
        test_agent_store()
        test_experiment_store()
        test_memory_record_structure()
        test_query_functionality()
        
        print('\n' + '=' * 60)
        print('[SUCCESS] WSZYSTKIE TESTY MEMORY STORES ZALICZONE!')
        print('=' * 60)
        
    except AssertionError as e:
        print(f'\n[FAIL] TEST NIEZALICZONY: {e}')
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f'\n[ERROR] BLAAD: {e}')
        import traceback
        traceback.print_exc()
        exit(1)
