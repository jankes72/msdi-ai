#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test integracyjny IFC Registry - ETAP 1.2.7.3"""

from SSI_V5.ifc import IFCRegistry, IFCMessage, IFCRouter
from SSI_V5.ifc.message import MessageType


class MockComponent:
    """Mockowy komponent do testów."""
    def __init__(self, name):
        self.name = name
    
    def receive_message(self, message):
        return f'MockComponent {self.name} received: {message.payload}'


def test_registration_and_retrieval():
    """Test 1: Rejestracja i pobieranie komponentów."""
    print('Test 1: Rejestracja i pobieranie')
    ifc = IFCRegistry()
    
    memory_ecosystem = MockComponent('MemoryEcosystem')
    pipeline = MockComponent('Pipeline')
    
    # Rejestracja
    ifc.register('memory_ecosystem', memory_ecosystem, component_type='memory')
    ifc.register('pipeline', pipeline, component_type='pipeline')
    
    components = ifc.list_components()
    print(f'  Zarejestrowane komponenty: {components}')
    assert 'memory_ecosystem' in components
    assert 'pipeline' in components
    
    # Sprawdzanie istnienia
    exists = ifc.exists('memory_ecosystem')
    print(f'  MemoryEcosystem istnieje: {exists}')
    assert exists is True
    
    # Pobieranie
    retrieved = ifc.get('memory_ecosystem')
    print(f'  Pobrano: {retrieved.name}')
    assert retrieved.name == 'MemoryEcosystem'
    
    print('  [OK] Test 1 zaliczony')


def test_message_routing():
    """Test 2: Wysyłanie wiadomości pomiędzy komponentami."""
    print('\nTest 2: Wysyłanie wiadomości')
    ifc = IFCRegistry()
    
    memory_ecosystem = MockComponent('MemoryEcosystem')
    pipeline = MockComponent('Pipeline')
    
    ifc.register('memory_ecosystem', memory_ecosystem, component_type='memory')
    ifc.register('pipeline', pipeline, component_type='pipeline')
    
    # Wysyłanie wiadomości
    result = ifc.send(
        source='pipeline',
        target='memory_ecosystem',
        message_type=MessageType.DATA,
        payload={'cycle_id': 'test_001', 'data': 'test'}
    )
    
    print(f'  Wynik routingu: success={result.success}')
    assert result.success is True
    
    print(f'  Odpowiedź: {result.response}')
    assert 'MemoryEcosystem received' in result.response
    
    print('  [OK] Test 2 zaliczony')


def test_component_metadata():
    """Test 3: Metadane komponentu."""
    print('\nTest 3: Metadane komponentu')
    ifc = IFCRegistry()
    
    memory_ecosystem = MockComponent('MemoryEcosystem')
    ifc.register('memory_ecosystem', memory_ecosystem, 
                 component_type='memory', 
                 description='Central memory system')
    
    metadata = ifc.get_metadata('memory_ecosystem')
    print(f'  Typ: {metadata.component_type}')
    assert metadata.component_type == 'memory'
    
    print(f'  Status: {metadata.status}')
    assert metadata.status == 'registered'
    
    print(f'  Liczba dostępów: {metadata.access_count}')
    assert metadata.access_count >= 0
    
    print('  [OK] Test 3 zaliczony')


def test_registry_statistics():
    """Test 4: Statystyki rejestru."""
    print('\nTest 4: Statystyki rejestru')
    ifc = IFCRegistry()
    
    # Rejestracja kilku komponentów
    for i in range(5):
        ifc.register(f'component_{i}', MockComponent(f'Component{i}'), 
                     component_type='test')
    
    stats = ifc.get_statistics()
    print(f'  Komponenty: {stats["total_components"]}')
    assert stats['total_components'] == 5
    
    print(f'  Operacje: {stats["total_operations"]}')
    assert stats['total_operations'] >= 5  # Rejestracje
    
    # Listowanie komponentów jednego typu
    test_components = ifc.list_components_by_type('test')
    print(f'  Komponenty typu "test": {test_components}')
    assert len(test_components) == 5
    
    print('  [OK] Test 4 zaliczony')


def test_error_handling():
    """Test 5: Obsługa błędów."""
    print('\nTest 5: Obsługa błędów')
    ifc = IFCRegistry()
    
    # Próba pobrania nieistniejącego komponentu
    result = ifc.get('nonexistent')
    print(f'  Pobranie nieistniejącego: {result}')
    assert result is None
    
    # Próba wysłania do nieistniejącego
    result = ifc.send('source', 'nonexistent', payload='test')
    print(f'  Wysłanie do nieistniejącego: success={result.success}, error={result.error}')
    assert result.success is False
    assert 'not found' in result.error
    
    # Próba podwójnej rejestracji
    ifc.register('test_component', MockComponent('Test'))
    try:
        ifc.register('test_component', MockComponent('Test2'))
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f'  Podwójna rejestracja: {e}')
        assert 'already registered' in str(e)
    
    print('  [OK] Test 5 zaliczony')


def test_message_structure():
    """Test 6: Struktura wiadomości IFC."""
    print('\nTest 6: Struktura wiadomości IFC')
    
    # Tworzenie wiadomości
    msg = IFCMessage(
        source='pipeline',
        target='memory_ecosystem',
        message_type='data',
        payload={'test': 'data'}
    )
    
    print(f'  Źródło: {msg.source}')
    assert msg.source == 'pipeline'
    
    print(f'  Typ: {msg.message_type}')
    assert msg.message_type == 'data'
    
    print(f'  Metadane: {msg.metadata.keys()}')
    assert 'timestamp' in msg.metadata
    assert 'message_id' in msg.metadata
    assert 'priority' in msg.metadata
    
    # Konwersja do/ze słownika
    msg_dict = msg.to_dict()
    restored = IFCMessage.from_dict(msg_dict)
    print(f'  Serializacja/Deserializacja: {restored.source == msg.source}')
    assert restored.source == msg.source
    assert restored.payload == msg.payload
    
    print('  [OK] Test 6 zaliczony')


if __name__ == '__main__':
    print('=' * 60)
    print('IFC REGISTRY - TESTY INTEGRACYJNE (ETAP 1.2.7.3)')
    print('=' * 60)
    
    try:
        test_registration_and_retrieval()
        test_message_routing()
        test_component_metadata()
        test_registry_statistics()
        test_error_handling()
        test_message_structure()
        
        print('\n' + '=' * 60)
        print('[SUCCESS] WSZYSTKIE TESTY IFC ZALICZONE!')
        print('=' * 60)
        
    except AssertionError as e:
        print(f'\n[FAIL] TEST NIEZALICZONY: {e}')
        exit(1)
    except Exception as e:
        print(f'\n[ERROR] BLAAD: {e}')
        import traceback
        traceback.print_exc()
        exit(1)
