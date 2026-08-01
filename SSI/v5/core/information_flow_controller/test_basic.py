"""
SSI V5 - Basic IFC Test

Podstawowy test Information Flow Controller.

Wersja: 2.0.0
Data: 2026-08-01
"""

import sys
import os

# Ustawienie ścieżki
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

print("=" * 80)
print("SSI V5 - BASIC IFC TEST")
print("=" * 80)

# Test: Import IFC modules directly
print("\n[TEST] Importing IFC modules directly...")
try:
    # Import bezpośrednio z pakietu
    from SSI.v5.core.information_flow_controller.message_models import (
        SSIMessage, MessageResponse, MessageStatus, PriorityLevel, 
        ProcessType, SystemStateSnapshot, ModuleIdentifier
    )
    from SSI.v5.core.information_flow_controller.message_factory import MessageFactory
    from SSI.v5.core.information_flow_controller.message_router import MessageRouter, get_router
    from SSI.v5.core.information_flow_controller.message_history import MessageHistory, get_history
    from SSI.v5.core.information_flow_controller.context_manager import (
        ContextManager, ContextSnapshot, ContextUpdate, ExecutionMode, SystemStatus,
        get_context_manager
    )
    from SSI.v5.core.information_flow_controller.ifc_controller import (
        InformationFlowController, IFCConfig, IFCTStatistics, get_ifc
    )
    
    print("✅ All IFC modules imported successfully")
    
    # Test SSIMessage
    msg = SSIMessage(
        source=ModuleIdentifier(module_name="test_agent", module_type="agent"),
        target=ModuleIdentifier(module_name="runtime", module_type="runtime"),
        process_type=ProcessType.AGENT_ACTION,
        payload={"action": "test"}
    )
    print(f"✅ Created SSIMessage: {msg.message_id}")
    assert msg.is_valid(), "Message should be valid"
    
    # Test MessageFactory
    factory_msg = MessageFactory.create_message(
        source="agent_01",
        target="teacher",
        process_type="teacher_observation",
        payload={"obs": "test"}
    )
    print(f"✅ MessageFactory created: {factory_msg.message_id}")
    
    # Test ContextManager
    ctx_mgr = get_context_manager()
    ctx = ctx_mgr.get_context()
    print(f"✅ ContextManager: session={ctx.session_id}, cycle={ctx.cycle_id}")
    
    # Test IFCController
    ifc = get_ifc()
    ifc.start()
    assert ifc.is_running(), "IFC should be running"
    print("✅ IFCController started")
    
    # Test message flow
    test_msg = ifc.create_message(
        source="system",
        target="runtime_controller", 
        process_type=ProcessType.SYSTEM_STATUS,
        payload={"status": "ok"}
    )
    response = ifc.send_message(test_msg)
    print(f"✅ Message sent: {response.status.value}")
    
    ifc.stop()
    print("✅ IFCController stopped")
    
    print("\n" + "=" * 80)
    print("✅ ALL BASIC TESTS PASSED")
    print("ETAP 2.1: INFORMATION FLOW CONTROLLER - WORKING")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)