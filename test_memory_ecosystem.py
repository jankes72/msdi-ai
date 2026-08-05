#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test integracyjny MemoryEcosystem - ETAP 1.2.7.3"""

from SSI_V5.memory import (
    MemoryEcosystem, MemoryEcosystemStatus, MemoryEcosystemConfig,
    MemoryRecord, MemoryQuery,
    ModelMemoryStore, AgentMemoryStore, ExperimentMemoryStore
)


def test_ecosystem_initialization():
    """Test 1: Inicjalizacja MemoryEcosystem."""
    print('Test 1: MemoryEcosystem - Inicjalizacja')
    
    # Test z auto-rejestracją (domyślne)
    ecosystem = MemoryEcosystem()
    
    print(f'  Status: {ecosystem._status}')
    assert ecosystem._status == MemoryEcosystemStatus.HEALTHY
    
    stores = ecosystem.list_stores()
    print(f'  Storey: {stores}')
    assert "model_store" in stores
    assert "agent_store" in stores
    assert "experiment_store" in stores
    
    # Test bez auto-rejestracji
    ecosystem_no_auto = MemoryEcosystem(
        config=MemoryEcosystemConfig(auto_register_stores=False)
    )
    
    print(f'  Storey (no auto): {ecosystem_no_auto.list_stores()}')
    assert len(ecosystem_no_auto.list_stores()) == 0
    assert ecosystem_no_auto._status == MemoryEcosystemStatus.DEGRADED
    
    print('  [OK] Test 1 zaliczony')


def test_store_registration():
    """Test 2: Rejestracja i zarządzanie Store'ami."""
    print('\nTest 2: Rejestracja Store''ow')
    
    ecosystem = MemoryEcosystem(config=MemoryEcosystemConfig(auto_register_stores=False))
    
    # Rejestracja ręczna
    model_store = ModelMemoryStore()
    agent_store = AgentMemoryStore()
    
    result1 = ecosystem.register_store("model_store", model_store)
    result2 = ecosystem.register_store("agent_store", agent_store)
    
    print(f'  Rejestracja model_store: {result1}')
    print(f'  Rejestracja agent_store: {result2}')
    assert result1 is True
    assert result2 is True
    
    # Sprawdzenie listy
    stores = ecosystem.list_stores()
    print(f'  Storey: {stores}')
    assert "model_store" in stores
    assert "agent_store" in stores
    
    # Pobieranie Store'a
    retrieved_model = ecosystem.get_store("model_store")
    print(f'  Pobrano model_store: {retrieved_model is not None}')
    assert retrieved_model is model_store
    
    # Próba podwójnej rejestracji
    result3 = ecosystem.register_store("model_store", ModelMemoryStore())
    print(f'  Podwojna rejestracja: {result3}')
    assert result3 is False
    
    # Usunięcie Store'a
    result4 = ecosystem.unregister_store("model_store")
    print(f'  Usunieto model_store: {result4}')
    assert result4 is True
    assert "model_store" not in ecosystem.list_stores()
    
    print('  [OK] Test 2 zaliczony')


def test_record_routing():
    """Test 3: Routing rekordów do Store'ów."""
    print('\nTest 3: Routing rekordow')
    
    ecosystem = MemoryEcosystem()
    
    # Zapis rekordu model_memory
    model_record = MemoryRecord.create(
        content={"model_name": "RF_v3", "result": "success", "accuracy": 0.85},
        memory_type="model_memory",
        source="test"
    )
    model_id = ecosystem.save(model_record)
    print(f'  Zapisano model_memory: {model_id}')
    assert model_id is not None
    
    # Zapis rekordu agent_memory
    agent_record = MemoryRecord.create(
        content={"agent_id": "agent_001", "experience_type": "success"},
        memory_type="agent_memory",
        source="test"
    )
    agent_id = ecosystem.save(agent_record)
    print(f'  Zapisano agent_memory: {agent_id}')
    assert agent_id is not None
    
    # Zapis rekordu experiment_memory
    exp_record = MemoryRecord.create(
        content={"experiment_id": "exp_001"},
        memory_type="experiment_memory",
        source="test"
    )
    exp_id = ecosystem.save(exp_record)
    print(f'  Zapisano experiment_memory: {exp_id}')
    assert exp_id is not None
    
    # Sprawdzenie, że rekordy trafiły do odpowiednich Store'ów
    model_store = ecosystem.get_store("model_store")
    agent_store = ecosystem.get_store("agent_store")
    exp_store = ecosystem.get_store("experiment_store")
    
    assert model_store.get(model_id) is not None
    assert agent_store.get(agent_id) is not None
    assert exp_store.get(exp_id) is not None
    
    print(f'  Rekordy w odpowiednich Store''ach: [OK]')
    
    print('  [OK] Test 3 zaliczony')


def test_record_retrieval():
    """Test 4: Pobieranie rekordów z ekosystemu."""
    print('\nTest 4: Pobieranie rekordow')
    
    ecosystem = MemoryEcosystem()
    
    # Zapis kilku rekordów
    record1 = MemoryRecord.create(
        content={"test": "data1", "model_name": "Model1", "result": "success"},
        memory_type="model_memory",
        source="test"
    )
    id1 = ecosystem.save(record1)
    
    record2 = MemoryRecord.create(
        content={"test": "data2", "agent_id": "agent1", "experience_type": "success"},
        memory_type="agent_memory",
        source="test"
    )
    id2 = ecosystem.save(record2)
    
    # Pobieranie po ID
    retrieved1 = ecosystem.get(id1)
    retrieved2 = ecosystem.get(id2)
    
    print(f'  Pobrano rekord 1: {retrieved1 is not None}')
    print(f'  Pobrano rekord 2: {retrieved2 is not None}')
    assert retrieved1 is not None
    assert retrieved2 is not None
    assert retrieved1.content == record1.content
    assert retrieved2.content == record2.content
    
    # Pobieranie nieistniejącego
    retrieved_none = ecosystem.get("nonexistent_id")
    print(f'  Pobrano nieistniejacy: {retrieved_none}')
    assert retrieved_none is None
    
    print('  [OK] Test 4 zaliczony')


def test_record_deletion():
    """Test 5: Usuwanie rekordów."""
    print('\nTest 5: Usuwanie rekordow')
    
    ecosystem = MemoryEcosystem()
    
    # Zapis rekordu
    record = MemoryRecord.create(
        content={"test": "to_delete", "model_name": "DeleteModel", "result": "success"},
        memory_type="model_memory",
        source="test"
    )
    memory_id = ecosystem.save(record)
    
    # Sprawdzenie, że istnieje
    assert ecosystem.get(memory_id) is not None
    print(f'  Rekord istnieje: [OK]')
    
    # Usunięcie
    deleted = ecosystem.delete(memory_id)
    print(f'  Usunieto: {deleted}')
    assert deleted is True
    
    # Sprawdzenie, że nie istnieje
    assert ecosystem.get(memory_id) is None
    print(f'  Rekord usuniety: [OK]')
    
    # Próba usunięcia nieistniejącego
    deleted_none = ecosystem.delete("nonexistent_id")
    print(f'  Usuniecie nieistniejacego: {deleted_none}')
    assert deleted_none is False
    
    print('  [OK] Test 5 zaliczony')


def test_find_functionality():
    """Test 6: Wyszukiwanie rekordów."""
    print('\nTest 6: Wyszukiwanie rekordow')
    
    ecosystem = MemoryEcosystem()
    
    # Zapis kilku rekordów
    for i in range(5):
        record = MemoryRecord.create(
            content={"test": f"data_{i}", "value": i, "model_name": f"Model_{i}", "result": "success"},
            memory_type="model_memory",
            source="test_source"
        )
        ecosystem.save(record)
    
    # Wyszukiwanie wszystkich
    all_records = ecosystem.find()
    print(f'  Wszystkie rekordy: {len(all_records)}')
    assert len(all_records) >= 5
    
    # Wyszukiwanie poźródle
    query = MemoryQuery(source="test_source")
    source_records = ecosystem.find(query)
    print(f'  Rekordy z test_source: {len(source_records)}')
    assert len(source_records) >= 5
    
    # Wyszukiwanie po typie
    query = MemoryQuery(memory_type="model_memory")
    model_records = ecosystem.find(query)
    print(f'  Rekordy model_memory: {len(model_records)}')
    assert len(model_records) >= 5
    
    print('  [OK] Test 6 zaliczony')


def test_convenience_methods():
    """Test 7: Metody skrócone (save_model_experience, etc.)."""
    print('\nTest 7: Metody skrocone')
    
    ecosystem = MemoryEcosystem()
    
    # save_model_experience
    model_id = ecosystem.save_model_experience(
        model_name="TestModel",
        result="success",
        accuracy=0.90
    )
    print(f'  save_model_experience: {model_id}')
    assert model_id is not None
    
    # Sprawdzenie, że trafił do model_store
    model_store = ecosystem.get_store("model_store")
    retrieved = model_store.get(model_id)
    assert retrieved is not None
    assert retrieved.content["model_name"] == "TestModel"
    
    # save_agent_experience
    agent_id = ecosystem.save_agent_experience(
        agent_id="test_agent",
        experience_type="success",
        decision={"type": "test"}
    )
    print(f'  save_agent_experience: {agent_id}')
    assert agent_id is not None
    
    # save_experiment_result
    exp_id = ecosystem.save_experiment_result(
        experiment_id="test_exp",
        result={"outcome": "confirming"}
    )
    print(f'  save_experiment_result: {exp_id}')
    assert exp_id is not None
    
    print('  [OK] Test 7 zaliczony')


def test_statistics_and_health():
    """Test 8: Statystyki i zdrowie ekosystemu."""
    print('\nTest 8: Statystyki i zdrowie')
    
    ecosystem = MemoryEcosystem()
    
    # Zapis kilku rekordów
    for i in range(3):
        ecosystem.save(MemoryRecord.create(
            content={"test": i, "model_name": f"StatsModel_{i}", "result": "success"},
            memory_type="model_memory",
            source="stats_test"
        ))
    
    # Statystyki ekosystemu
    stats = ecosystem.statistics()
    print(f'  Status: {stats["status"]}')
    print(f'  Liczba Store''ow: {stats["total_stores"]}')
    print(f' Storey: {stats["store_names"]}')
    assert stats["status"] == "healthy"
    assert stats["total_stores"] == 3  # model, agent, experiment
    
    # Statystyki Store'ów
    assert "model_store" in stats["stores"]
    assert stats["stores"]["model_store"]["total_records"] >= 3
    
    # Health check
    health = ecosystem.health()
    print(f'  Zdrowie: {health["status"]}')
    print(f'  Zdrowie Store''ow: {health["stores"]}')
    assert health["status"] == "healthy"
    assert len(health["stores"]) == 3
    
    print('  [OK] Test 8 zaliczony')


def test_event_callbacks():
    """Test 9: Callbacki na zdarzenia."""
    print('\nTest 9: Callbacki na zdarzenia')
    
    ecosystem = MemoryEcosystem()
    
    # Zmienna do teste callbacków
    callback_events = []
    
    def test_callback(*args, **kwargs):
        callback_events.append((args, kwargs))
    
    # Rejestracja callbacka
    ecosystem.on("memory_saved", test_callback)
    
    # Zapis rekordu (powinien wywołać callback)
    record = MemoryRecord.create(
        content={"test": "callback", "model_name": "CallbackModel", "result": "success"},
        memory_type="model_memory",
        source="test"
    )
    memory_id = ecosystem.save(record)
    
    print(f'  Liczba callbackow: {len(callback_events)}')
    assert len(callback_events) == 1
    
    # Sprawdzenie argumentów callbacka
    args, kwargs = callback_events[0]
    print(f'  Callback args: {args}')
    assert len(args) == 2  # memory_id, record
    assert args[0] == memory_id
    assert isinstance(args[1], MemoryRecord)
    
    print('  [OK] Test 9 zaliczony')


if __name__ == '__main__':
    print('=' * 60)
    print('MEMORY ECOSYSTEM - TESTY INTEGRACYJNE (ETAP 1.2.7.3)')
    print('=' * 60)
    
    try:
        test_ecosystem_initialization()
        test_store_registration()
        test_record_routing()
        test_record_retrieval()
        test_record_deletion()
        test_find_functionality()
        test_convenience_methods()
        test_statistics_and_health()
        test_event_callbacks()
        
        print('\n' + '=' * 60)
        print('[SUCCESS] WSZYSTKIE TESTY MEMORY ECOSYSTEM ZALICZONE!')
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
