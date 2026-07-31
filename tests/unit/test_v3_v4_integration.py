"""
SSI Tests - Testy integracji V3-V4 dla Sprint 9

Testy jednostkowe dla komponentów integracyjnych V3-V4.
Zgodnie z V3_V4_INTEGRATION.md i kryteriami akceptacji Sprint 9.

Wersja: 1.0
Data: 2026-07-31
"""

import sys
import os

# Dodaj root do PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime


def test_v3_integration_imports():
    """Test importów V3 Integration."""
    from SSI.v3 import V3Integration, V3Config, V3ToV4Bridge
    assert V3Integration is not None
    assert V3Config is not None
    assert V3ToV4Bridge is not None
    print("✅ test_v3_integration_imports PASSED")


def test_v3_to_v4_bridge_import():
    """Test importu V3ToV4Bridge."""
    from SSI.v3.integration import V3ToV4Bridge, V3ToV4BridgeConfig, AgentKnowledgePackage
    assert V3ToV4Bridge is not None
    assert V3ToV4BridgeConfig is not None
    assert AgentKnowledgePackage is not None
    print("✅ test_v3_to_v4_bridge_import PASSED")


def test_v3_integration_import_from_main_module():
    """Test importu z głównego modułu V3."""
    from SSI.v3 import (
        V3Integration, V3Config, V3ToV4Bridge,
        V3IntegrationConfig, IntegrationStatistics,
        ComponentStatus
    )
    assert all([
        V3Integration, V3Config, V3ToV4Bridge,
        V3IntegrationConfig, IntegrationStatistics,
        ComponentStatus
    ])
    print("✅ test_v3_integration_import_from_main_module PASSED")


def test_v4_agent_imports():
    """Test importów V4 Agent."""
    from SSI.v4 import Agent, AgentCore, AgentBirthSystem
    assert Agent is not None
    assert AgentCore is not None
    assert AgentBirthSystem is not None
    print("✅ test_v4_agent_imports PASSED")


def test_v4_can_import_v3_components():
    """Test, że V4 może importować komponenty V3."""
    from SSI.v4.agent_core import Agent
    from SSI.v3 import V3Integration, V3Config, V3ToV4Bridge
    assert Agent is not None
    assert V3Integration is not None
    assert V3Config is not None
    assert V3ToV4Bridge is not None
    print("✅ test_v4_can_import_v3_components PASSED")


def test_v3_to_v4_bridge_basic_functionality():
    """Test podstawowej funkcjonalności V3ToV4Bridge."""
    from SSI.v3.integration.v3_to_v4_bridge import V3ToV4Bridge
    
    # Utworzenie mostu
    bridge = V3ToV4Bridge()
    
    # Subskrypcja agenta
    bridge.subscribe_agent('Agent1', ['world1', 'world2'])
    bridge.subscribe_agent('Agent2', ['world1'])
    
    # Sprawdzenie subskrypcji
    assert len(bridge._subscribers['world1']) == 2
    assert len(bridge._subscribers['world2']) == 1
    
    # Publikacja aktualizacji
    timestamp = datetime.now()
    notification_count = bridge.publish_world_update(
        world_id='world1',
        data={'test': 'data'},
        timestamp=timestamp
    )
    
    assert notification_count == 2
    
    # Sprawdzenie bufora agenta
    updates = bridge.get_agent_updates('Agent1')
    assert len(updates) == 1
    assert updates[0]['world_id'] == 'world1'
    
    print("✅ test_v3_to_v4_bridge_basic_functionality PASSED")


def test_agent_knowledge_package_structure():
    """Test struktury AgentKnowledgePackage."""
    from SSI.v3.integration.v3_to_v4_bridge import AgentKnowledgePackage
    from datetime import datetime
    
    # Utworzenie pakietu
    package = AgentKnowledgePackage(
        agent_id='Agent1',
        world_data=[{'world_id': 'world1', 'data': 'test'}],
        memory_snapshot={'ev': 2.5, 'risk': 0.1},
        timestamp=datetime.now(),
        version='1.0'
    )
    
    # Sprawdzenie struktur
    assert package.agent_id == 'Agent1'
    assert len(package.world_data) == 1
    assert package.memory_snapshot['ev'] == 2.5
    assert package.version == '1.0'
    
    # Sprawdzenie metody to_dict
    data = package.to_dict()
    assert 'agent_id' in data
    assert 'worlds' in data
    assert 'memory' in data
    assert 'timestamp' in data
    
    print("✅ test_agent_knowledge_package_structure PASSED")


def test_v3_config_structure():
    """Test struktury V3Config."""
    from SSI.v3 import V3Config
    
    # Utworzenie konfiguracji
    config = V3Config(
        world_config={'test': 'value'},
        memory_config={'test': 'value'},
        send_to_v4=True
    )
    
    assert config.world_config is not None
    assert config.memory_config is not None
    assert config.send_to_v4 is True
    
    print("✅ test_v3_config_structure PASSED")


def test_v3_integration_structure():
    """Test struktury V3Integration."""
    from SSI.v3 import V3Integration, V3Config
    
    # Utworzenie konfiguracji
    config = V3Config(
        world_config={},
        memory_config={},
        send_to_v4=True
    )
    
    # Utworzenie instancji (lazy initialization)
    integration = V3Integration(config)
    
    assert integration is not None
    assert hasattr(integration, 'initialize')
    
    print("✅ test_v3_integration_structure PASSED")


if __name__ == "__main__":
    # Uruchom wszystkie testy
    print("=" * 60)
    print("SPRINT 9: V3-V4 Integration Tests")
    print("=" * 60)
    
    tests = [
        test_v3_integration_imports,
        test_v3_to_v4_bridge_import,
        test_v3_integration_import_from_main_module,
        test_v4_agent_imports,
        test_v4_can_import_v3_components,
        test_v3_to_v4_bridge_basic_functionality,
        test_agent_knowledge_package_structure,
        test_v3_config_structure,
        test_v3_integration_structure
    ]
    
    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"[FAIL] {test.__name__} FAILED: {e}")
            failed.append(test.__name__)
    
    print("\n" + "=" * 60)
    if failed:
        print(f"FAILED: {len(failed)} tests failed")
        for name in failed:
            print(f"  - {name}")
    else:
        print("SUCCESS: All tests PASSED!")
        print(f"Total tests: {len(tests)}")
    print("=" * 60)
