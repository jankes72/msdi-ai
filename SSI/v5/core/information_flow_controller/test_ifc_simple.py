"""
SSI V5 - Simple IFC Initialization Test

Prosty test inicjalizacji Information Flow Controller.

Wersja: 2.0.0
Data: 2026-08-01
"""

import sys
import os

# Ensure the parent directory is in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

print("=" * 80)
print("SSI V5 - SIMPLE IFC INITIALIZATION TEST")
print("=" * 80)

# Test 1: Import all IFC modules
print("\n[TEST 1] Importing IFC modules...")
try:
    from SSI.v5.core.information_flow_controller import (
        SSIMessage,
        MessageResponse,
        MessageStatus,
        PriorityLevel,
        ProcessType,
        SystemStateSnapshot,
        ModuleIdentifier,
        MessageFactory,
        MessageRouter,
        get_router,
        MessageHistory,
        MessageRecord,
        HistoryConfig,
        get_history,
        ContextManager,
        ContextSnapshot,
        ContextUpdate,
        ExecutionMode,
        SystemStatus,
        get_context_manager,
        get_current_context,
        InformationFlowController,
        IFCConfig,
        IFCTStatistics,
        get_ifc,
        send_message,
        receive_message
    )
    print("✅ All IFC modules imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Create SSIMessage
print("\n[TEST 2] Creating SSIMessage...")
try:
    message = SSIMessage(
        source=ModuleIdentifier(module_name="test_agent", module_type="agent"),
        target=ModuleIdentifier(module_name="runtime_controller", module_type="runtime"),
        process_type=ProcessType.AGENT_ACTION,
        payload={"action": "test", "data": {"value": 42}}
    )
    print(f"✅ Message created: {message.message_id}")
    print(f"   Source: {message.source}")
    print(f"   Target: {message.target}")
    print(f"   Process Type: {message.process_type.value}")
    print(f"   Payload: {message.payload}")
    print(f"   Is valid: {message.is_valid()}")
except Exception as e:
    print(f"❌ Message creation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: MessageFactory
print("\n[TEST 3] Testing MessageFactory...")
try:
    factory_message = MessageFactory.create_message(
        source="agent_01",
        target="teacher_engine",
        process_type="teacher_observation",
        payload={"observation": "test observation"}
    )
    print(f"✅ Factory created message: {factory_message.message_id}")
    print(f"   Source: {factory_message.source}")
    print(f"   Target: {factory_message.target}")
    print(f"   Is valid: {factory_message.is_valid()}")
    assert factory_message.is_valid(), "Message is not valid"
    print("✅ MessageFactory works correctly")
except Exception as e:
    print(f"❌ MessageFactory error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: MessageRouter
print("\n[TEST 4] Testing MessageRouter...")
try:
    router = get_router()
    
    # Register a test module with a handler
    handler_data = {"called": False, "message": None}
    
    def test_handler(msg):
        handler_data["called"] = True
        handler_data["message"] = msg
        return MessageResponse.success(msg.message_id, {"result": "processed"})
    
    router.register_module("test_module", test_handler)
    
    # Create a message to the test module
    test_msg = MessageFactory.create_message(
        source="system",
        target="test_module",
        process_type=ProcessType.SYSTEM_INIT,
        payload={"test": "data"}
    )
    
    # Route the message
    response = router.route_message(test_msg)
    print(f"✅ Router routed message: {response.status.value}")
    assert handler_data["called"], "Handler was not called"
    assert handler_data["message"] is not None, "Message was not passed"
    print("✅ MessageRouter works correctly")
except Exception as e:
    print(f"❌ MessageRouter error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: ContextManager
print("\n[TEST 5] Testing ContextManager...")
try:
    ctx_manager = get_context_manager()
    
    # Get default context
    context = ctx_manager.get_context()
    print(f"✅ Got context: session={context.session_id}, cycle={context.cycle_id}")
    
    # Update context
    update = ContextUpdate(
        session_id="test_session_001",
        cycle_id="test_cycle_001",
        active_agent="agent_01",
        execution_mode=ExecutionMode.TEST
    )
    updated_context = ctx_manager.update_context(update)
    print(f"✅ Updated context: session={updated_context.session_id}")
    
    # Check changes
    new_context = ctx_manager.get_context()
    assert new_context.session_id == "test_session_001", "Session not updated"
    assert new_context.cycle_id == "test_cycle_001", "Cycle not updated"
    assert new_context.active_agent == "agent_01", "Agent not updated"
    print("✅ ContextManager works correctly")
except Exception as e:
    print(f"❌ ContextManager error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: MessageHistory
print("\n[TEST 6] Testing MessageHistory...")
try:
    history = get_history()
    history.initialize()
    
    # Store a message
    test_msg = MessageFactory.create_message(
        source="system",
        target="history_test",
        process_type=ProcessType.SYSTEM_HEARTBEAT,
        payload={"heartbeat": True}
    )
    
    message_id = history.store_message(
        message=test_msg,
        status=MessageStatus.PROCESSED,
        processing_time_ms=10.5
    )
    print(f"✅ Stored message in history: {message_id}")
    
    # Retrieve message
    retrieved = history.get_message(message_id)
    assert retrieved is not None, "Message not stored"
    assert retrieved.message.message_id == message_id, "Wrong message ID"
    print("✅ MessageHistory works correctly")
    
    # Statistics
    stats = history.get_statistics()
    print(f"   Statistics: {stats['total_messages']} messages")
except Exception as e:
    print(f"❌ MessageHistory error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: InformationFlowController (Full IFC)
print("\n[TEST 7] Testing InformationFlowController...")
try:
    ifc = get_ifc()
    
    # Start IFC
    ifc.start()
    assert ifc.is_running(), "IFC not running"
    print("✅ IFC started")
    
    # Get status
    status = ifc.status()
    print(f"✅ IFC status: running={status['running']}")
    print(f"   Registered modules: {len(status['registered_modules'])}")
    
    # Get context
    ifc_context = ifc.get_context()
    print(f"✅ IFC context: session={ifc_context.session_id}")
    
    # Create and send message
    msg = ifc.create_message(
        source="test_source",
        target="system",
        process_type=ProcessType.SYSTEM_STATUS,
        payload={"status": "test"}
    )
    
    response = ifc.send_message(msg)
    print(f"✅ Sent message through IFC: {response.status.value}")
    print(f"   Processing time: {response.processing_time_ms:.2f}ms")
    
    # IFC Statistics
    ifc_stats = ifc.get_statistics()
    print(f"   IFC stats: {ifc_stats['messages_sent']} messages sent")
    
    # Stop IFC
    ifc.stop()
    assert not ifc.is_running(), "IFC should be stopped"
    print("✅ IFC stopped")
    
    print("✅ InformationFlowController works correctly")
except Exception as e:
    print(f"❌ InformationFlowController error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Helper functions (send_message, receive_message)
print("\n[TEST 8] Testing helper functions...")
try:
    ifc = get_ifc()
    ifc.start()
    
    # Use send_message helper
    response = send_message(
        source="helper_test",
        target="system",
        process_type="developer_command",
        payload={"command": "test"}
    )
    print(f"✅ Helper send_message: {response.status.value}")
    
    # Use receive_message helper
    receive_response = receive_message(
        source="external_system",
        process_type="external_event",
        payload={"event": "test_event"}
    )
    print(f"✅ Helper receive_message: {receive_response.status.value}")
    
    ifc.stop()
    print("✅ Helper functions work correctly")
except Exception as e:
    print(f"❌ Helper functions error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 9: Complete message flow
print("\n[TEST 9] Testing complete message flow: Agent -> IFC -> Router -> History -> Response")
try:
    ifc = get_ifc()
    ifc.start()
    
    # Register a handler for test agent
    agent_handler_data = {"messages": []}
    
    def agent_handler(message):
        agent_handler_data["messages"].append(message)
        print(f"   Agent received: {message.message_id} from {message.source}")
        return MessageResponse.success(
            message.message_id,
            {"agent_response": "received"}
        )
    
    ifc.register_module("test_agent", agent_handler)
    
    # Send a message from system to agent
    msg = ifc.create_message(
        source="runtime_controller",
        target="test_agent",
        process_type=ProcessType.AGENT_ACTION,
        payload={"action": "test_action", "data": {"test": True}}
    )
    
    print(f"   Sending message: {msg.message_id}")
    response = ifc.send_message(msg)
    print(f"   Response: {response.status.value}")
    
    # Check if agent received the message
    assert len(agent_handler_data["messages"]) == 1, "Agent did not receive message"
    assert agent_handler_data["messages"][0].message_id == msg.message_id, "Wrong message received"
    
    # Check history
    history = get_history()
    history_msgs = history.query_messages(
        source="runtime_controller",
        target="test_agent",
        limit=10
    )
    assert len(history_msgs) >= 1, "Message not stored in history"
    
    print("✅ Complete message flow works correctly")
    print(f"   Agent received message and responded")
    print(f"   Message was stored in history")
    
    ifc.stop()
except Exception as e:
    print(f"❌ Complete flow error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED")
print("=" * 80)
print("\nSummary:")
print("  ✅ Module imports")
print("  ✅ SSIMessage creation and validation")
print("  ✅ MessageFactory")
print("  ✅ MessageRouter")
print("  ✅ ContextManager")
print("  ✅ MessageHistory")
print("  ✅ InformationFlowController")
print("  ✅ Helper functions")
print("  ✅ Complete message flow")
print("\nETAP 2.1: INFORMATION FLOW CONTROLLER - READY FOR USE")
print("=" * 80)