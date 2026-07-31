"""
SSI Integration Tests - Testy integracyjne V2->V3->V4 dla Sprint 9

Proste, samodzielne testy sprawdzające integrację między warstwami.
Zgodnie z V3_V4_INTEGRATION.md i kryteriami akceptacji Sprint 9.

Wersja: 1.0
Data: 2026-07-31
"""

import sys
import os

# Dodaj root do PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_v3_imports():
    """Test importów V3."""
    from SSI.v3 import V3Integration, V3Config, V3ToV4Bridge
    print("[OK] test_v3_imports PASSED")


def test_v4_imports():
    """Test importów V4."""
    from SSI.v4 import Agent, AgentBirthSystem
    print("[OK] test_v4_imports PASSED")


def test_v4_can_access_v3():
    """Test, że V4 może korzystać z V3."""
    from SSI.v4 import Agent
    from SSI.v3 import V3Integration, V3Config, V3ToV4Bridge
    # Jeśli nie ma błędów importu, to działą
    print("[OK] test_v4_can_access_v3 PASSED")


def test_v3_to_v4_bridge_exists():
    """Test, że V3ToV4Bridge istnieje."""
    from SSI.v3.integration import V3ToV4Bridge
    # Utworzenie instancji
    bridge = V3ToV4Bridge()
    assert bridge is not None
    print("[OK] test_v3_to_v4_bridge_exists PASSED")


def test_v3_integration_exists():
    """Test, że V3Integration istnieje."""
    from SSI.v3 import V3Integration
    # Utworzenie instancji (z domyślną konfiguracją)
    integration = V3Integration()
    assert integration is not None
    print("[OK] test_v3_integration_exists PASSED")


def test_v3_config_exists():
    """Test, że V3Config istnieje."""
    from SSI.v3 import V3Config
    # Utworzenie konfiguracji
    config = V3Config()
    assert config is not None
    print("[OK] test_v3_config_exists PASSED")


def test_v2_to_v3_bridge_exists():
    """Test, że V2ToV3Bridge istnieje."""
    from SSI.v2.integration.v2_to_v3_bridge import V2ToV3Bridge
    # Utworzenie instancji (z mockami)
    v2_bridge = V2ToV3Bridge(None, None)
    assert v2_bridge is not None
    print("[OK] test_v2_to_v3_bridge_exists PASSED")


def test_v3_world_structure():
    """Test struktury światów V3."""
    from SSI.v3 import WorldManager, World
    # Utworzenie menedżera światów
    world_manager = WorldManager()
    assert world_manager is not None
    print("[OK] test_v3_world_structure PASSED")


def test_v3_memory_structure():
    """Test struktury pamięci V3."""
    from SSI.v3 import MemoryManager
    # Utworzenie menedżera pamięci
    memory_manager = MemoryManager()
    assert memory_manager is not None
    print("[OK] test_v3_memory_structure PASSED")


def test_v4_agent_creation():
    """Test tworzenia agenta V4."""
    from SSI.v4 import Agent
    # Utworzenie agenta (z domyślną konfiguracją)
    agent = Agent()
    assert agent is not None
    print("[OK] test_v4_agent_creation PASSED")


if __name__ == "__main__":
    # Uruchom wszystkie testy
    print("=" * 60)
    print("SPRINT 9: V2-V3-V4 Integration Tests")
    print("=" * 60)
    
    tests = [
        test_v3_imports,
        test_v4_imports,
        test_v4_can_access_v3,
        test_v3_to_v4_bridge_exists,
        test_v3_integration_exists,
        test_v3_config_exists,
        test_v2_to_v3_bridge_exists,
        test_v3_world_structure,
        test_v3_memory_structure,
        test_v4_agent_creation
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
        sys.exit(1)
    else:
        print("SUCCESS: All tests PASSED!")
        print(f"Total tests: {len(tests)}")
        sys.exit(0)
    print("=" * 60)
