"""
SSI V3 Tests - Testy V3ToV4Bridge (Finalna wersja dla Sprint 9)

Testy jednostkowe mostu V3ToV4Bridge.
Zgodnie z V3_V4_INTEGRATION.md Sekcja 11.1

Wersja: 1.0
Data: 2026-07-31
"""

import pytest
from datetime import datetime
from SSI.v3.integration.v3_to_v4_bridge import V3ToV4Bridge
from SSI.v3.integration import V3ToV4BridgeConfig


class TestV3ToV4BridgeBasic:
    """Podstawowe testy mostu V3→V4."""
    
    def test_v3_to_v4_bridge_initialization(self):
        """Test inicjalizacji mostu V3→V4."""
        bridge = V3ToV4Bridge()
        assert not bridge._initialized
        
        # Mock managerów
        mock_world_manager = type('MockWorldManager', (), {
            'get_all_world_ids': lambda: ['world1', 'world2']
        })()
        mock_memory_manager = type('MockMemoryManager', (), {
            'get_snapshot': lambda: {'memory': 'data'}
        })()
        
        bridge.initialize(mock_world_manager, mock_memory_manager)
        assert bridge._initialized

    def test_v3_to_v4_bridge_subscription(self):
        """Test subskrypcji agentów."""
        bridge = V3ToV4Bridge()
        
        bridge.subscribe_agent('Agent1', ['world1', 'world2'])
        bridge.subscribe_agent('Agent2', ['world1'])
        
        assert len(bridge._subscribers['world1']) == 2
        assert len(bridge._subscribers['world2']) == 1
        assert 'Agent1' in bridge._subscribers['world1']
        assert 'Agent2' in bridge._subscribers['world1']

    def test_v3_to_v4_bridge_unsubscribe(self):
        """Test wyrejestrowania agenta."""
        bridge = V3ToV4Bridge()
        bridge.subscribe_agent('Agent1', ['world1'])
        bridge.unsubscribe_agent('Agent1')
        
        assert len(bridge._subscribers.get('world1', [])) == 0


class TestV3ToV4BridgePublish:
    """Testy publikacji aktualizacji świata."""
    
    def test_v3_to_v4_bridge_publish(self):
        """Test publikacji aktualizacji świata."""
        bridge = V3ToV4Bridge()
        bridge.subscribe_agent('Agent1', ['world1'])
        
        timestamp = datetime.now()
        notification_count = bridge.publish_world_update(
            world_id='world1',
            data={'key': 'value'},
            timestamp=timestamp
        )
        
        assert notification_count == 1
        
        # Sprawdź bufor agenta
        updates = bridge.get_agent_updates('Agent1')
        assert len(updates) == 1
        assert updates[0]['world_id'] == 'world1'

    def test_v3_to_v4_bridge_publish_no_subscribers(self):
        """Test publikacji bez subskrybentów."""
        bridge = V3ToV4Bridge()
        
        notification_count = bridge.publish_world_update(
            world_id='world1',
            data={'key': 'value'},
            timestamp=datetime.now()
        )
        
        assert notification_count == 0


class TestV3ToV4BridgeKnowledgePackage:
    """Testy pakietu wiedzy."""
    
    def test_v3_to_v4_bridge_knowledge_package(self):
        """Test pakietu wiedzy dla agenta."""
        bridge = V3ToV4Bridge()
        
        mock_world_manager = type('MockWorldManager', (), {})()
        mock_memory_manager = type('MockMemoryManager', (), {
            'get_snapshot': lambda: {'ev': 2.5, 'risk': 0.1}
        })()
        
        bridge.initialize(mock_world_manager, mock_memory_manager)
        bridge.publish_world_update('world1', {'data': 'test'}, datetime.now())
        bridge.subscribe_agent('Agent1', ['world1'])
        
        package = bridge.get_agent_knowledge('Agent1')
        assert package.agent_id == 'Agent1'
        assert package.memory_snapshot == {'ev': 2.5, 'risk': 0.1}

    def test_v3_to_v4_bridge_contract_version(self):
        """Test wersji kontraktu."""
        bridge = V3ToV4Bridge()
        mock_world_manager = type('MockWorldManager', (), {})()
        mock_memory_manager = type('MockMemoryManager', (), {
            'get_snapshot': lambda: {}
        })()
        
        bridge.initialize(mock_world_manager, mock_memory_manager)
        package = bridge.get_agent_knowledge('test_agent')
        assert package.version == "1.0"


if __name__ == "__main__":
    # Uruchom testy
    import sys
    
    test = TestV3ToV4BridgeBasic()
    test.test_v3_to_v4_bridge_initialization()
    print("✅ test_v3_to_v4_bridge_initialization PASSED")
    
    test.test_v3_to_v4_bridge_subscription()
    print("✅ test_v3_to_v4_bridge_subscription PASSED")
    
    test.test_v3_to_v4_bridge_unsubscribe()
    print("✅ test_v3_to_v4_bridge_unsubscribe PASSED")
    
    test2 = TestV3ToV4BridgePublish()
    test2.test_v3_to_v4_bridge_publish()
    print("✅ test_v3_to_v4_bridge_publish PASSED")
    
    test2.test_v3_to_v4_bridge_publish_no_subscribers()
    print("✅ test_v3_to_v4_bridge_publish_no_subscribers PASSED")
    
    test3 = TestV3ToV4BridgeKnowledgePackage()
    test3.test_v3_to_v4_bridge_knowledge_package()
    print("✅ test_v3_to_v4_bridge_knowledge_package PASSED")
    
    test3.test_v3_to_v4_bridge_contract_version()
    print("✅ test_v3_to_v4_bridge_contract_version PASSED")
    
    print("\n✅ All V3ToV4Bridge tests PASSED!")
