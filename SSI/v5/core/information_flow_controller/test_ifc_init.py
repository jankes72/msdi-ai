"""
SSI V5 - Test IFC Initialization

Test inicjalizacji i podstawowych funkcjonalnosci Information Flow Controller.
Testuje przeszlo: Message Models → Factory → Router → History → Context Manager → IFC Controller

Wersja: 2.0.0
Data: 2026-08-01
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("SSI V5 - IFC INITIALIZATION TEST")
print("=" * 80)

# Test 1: Import wszystkich modułów
print("\n[TEST 1] Importowanie modułów IFC...")
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
    print("✅ Wszystkie moduły zaimportowane poprawnie")
except Exception as e:
    print(f"❌ Błąd importu: {e}")
    sys.exit(1)

# Test 2: Tworzenie SSIMessage
print("\n[TEST 2] Tworzenie SSIMessage...")
try:
    message = SSIMessage(
        source=ModuleIdentifier(module_name="test_agent", module_type="agent"),
        target=ModuleIdentifier(module_name="runtime_controller", module_type="runtime"),
        process_type=ProcessType.AGENT_ACTION,
        payload={"action": "test", "data": {"value": 42}}
    )
    print(f"✅ Utworzono wiadomosc: {message.message_id}")
    print(f"   Source: {message.source}")
    print(f"   Target: {message.target}")
    print(f"   Process Type: {message.process_type.value}")
    print(f"   Payload: {message.payload}")
except Exception as e:
    print(f"❌ Błąd tworzenia wiadomosci: {e}")
    sys.exit(1)

# Test 3: MessageFactory
print("\n[TEST 3] Test MessageFactory...")
try:
    factory_message = MessageFactory.create_message(
        source="agent_01",
        target="teacher_engine",
        process_type="teacher_observation",
        payload={"observation": "test observation"}
    )
    print(f"✅ Factory utworzyło wiadomosc: {factory_message.message_id}")
    print(f"   Source (string): {factory_message.source}")
    print(f"   Target (string): {factory_message.target}")
    assert factory_message.is_valid(), "Wiadomosc nie jest poprawna"
    print("✅ MessageFactory działa poprawnie")
except Exception as e:
    print(f"❌ Błąd MessageFactory: {e}")
    sys.exit(1)

# Test 4: MessageRouter
print("\n[TEST 4] Test MessageRouter...")
try:
    router = get_router()
    
    # Rejestracja testowego modułu
    test_handler_called = False
    test_handler_message = None
    
    def test_handler(msg):
        nonlocal test_handler_called, test_handler_message
        test_handler_called = True
        test_handler_message = msg
        return MessageResponse.success(msg.message_id, {"result": "processed"})
    
    router.register_module("test_module", test_handler)
    
    # Utworzenie wiadomosci do testowego modułu
    test_msg = MessageFactory.create_message(
        source="system",
        target="test_module",
        process_type=ProcessType.SYSTEM_INIT,
        payload={"test": "data"}
    )
    
    # Przekierowanie wiadomosci
    response = router.route_message(test_msg)
    print(f"✅ Router przekierował wiadomosc: {response.status.value}")
    assert test_handler_called, "Handler nie został wywołany"
    assert test_handler_message is not None, "Message nie został przekazany"
    print("✅ MessageRouter działa poprawnie")
except Exception as e:
    print(f"❌ Błąd MessageRouter: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: ContextManager
print("\n[TEST 5] Test ContextManager...")
try:
    ctx_manager = get_context_manager()
    
    # Pobranie domyslnego kontekstu
    context = ctx_manager.get_context()
    print(f"✅ Pobrano kontekst: session={context.session_id}, cycle={context.cycle_id}")
    
    # Aktualizacja kontekstu
    update = ContextUpdate(
        session_id="test_session_001",
        cycle_id="test_cycle_001",
        active_agent="agent_01",
        execution_mode=ExecutionMode.TEST
    )
    updated_context = ctx_manager.update_context(update)
    print(f"✅ Zaktualizowano kontekst: session={updated_context.session_id}")
    
    # Sprawdzenie zmian
    new_context = ctx_manager.get_context()
    assert new_context.session_id == "test_session_001", "Sesja nie została zaktualizowana"
    assert new_context.cycle_id == "test_cycle_001", "Cykl nie został zaktualizowany"
    assert new_context.active_agent == "agent_01", "Agent nie został zaktualizowany"
    print("✅ ContextManager działa poprawnie")
except Exception as e:
    print(f"❌ Błąd ContextManager: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: MessageHistory
print("\n[TEST 6] Test MessageHistory...")
try:
    history = get_history()
    history.initialize()
    
    # Zapisanie wiadomosci
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
    print(f"✅ Zapisano wiadomosc w historii: {message_id}")
    
    # Pobranie wiadomosci
    retrieved = history.get_message(message_id)
    assert retrieved is not None, "Wiadomosc nie została zapisana"
    assert retrieved.message.message_id == message_id, "Zły ID wiadomosci"
    print("✅ MessageHistory działa poprawnie")
    
    # Statystyki
    stats = history.get_statistics()
    print(f"   Statystyki: {stats['total_messages']} wiadomosci")
except Exception as e:
    print(f"❌ Błąd MessageHistory: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: InformationFlowController (Full IFC)
print("\n[TEST 7] Test InformationFlowController...")
try:
    ifc = get_ifc()
    
    # Uruchomienie IFC
    ifc.start()
    assert ifc.is_running(), "IFC nie jest uruchomiony"
    print("✅ IFC uruchomiony")
    
    # Pobranie stanu
    status = ifc.status()
    print(f"✅ Status IFC: running={status['running']}")
    print(f"   Zarejestrowane moduły: {len(status['registered_modules'])}")
    
    # Pobranie kontekstu
    ifc_context = ifc.get_context()
    print(f"✅ Kontekst IFC: session={ifc_context.session_id}")
    
    # Utworzenie i wysłanie wiadomosci
    msg = ifc.create_message(
        source="test_source",
        target="system",
        process_type=ProcessType.SYSTEM_STATUS,
        payload={"status": "test"}
    )
    
    response = ifc.send_message(msg)
    print(f"✅ Wysłano wiadomosc przez IFC: {response.status.value}")
    print(f"   Czas przetwarzania: {response.processing_time_ms:.2f}ms")
    
    # Statystyki IFC
    ifc_stats = ifc.get_statistics()
    print(f"   Statystyki IFC: {ifc_stats['messages_sent']} wiadomosci wysłanych")
    
    # Zatrzymanie IFC
    ifc.stop()
    assert not ifc.is_running(), "IFC powinien być zatrzymany"
    print("✅ IFC zatrzymany")
    
    print("✅ InformationFlowController działa poprawnie")
except Exception as e:
    print(f"❌ Błąd InformationFlowController: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Funkcje helper (send_message, receive_message)
print("\n[TEST 8] Test funkcji helper...")
try:
    ifc = get_ifc()
    ifc.start()
    
    # Uzycie helpera send_message
    response = send_message(
        source="helper_test",
        target="system",
        process_type="developer_command",
        payload={"command": "test"}
    )
    print(f"✅ Helper send_message: {response.status.value}")
    
    # Uzycie helpera receive_message
    receive_response = receive_message(
        source="external_system",
        process_type="external_event",
        payload={"event": "test_event"}
    )
    print(f"✅ Helper receive_message: {receive_response.status.value}")
    
    ifc.stop()
    print("✅ Funkcje helper działają poprawnie")
except Exception as e:
    print(f"❌ Błąd funkcji helper: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 9: Kompletny przepływ wiadomosci
print("\n[TEST 9] Test kompletnego przepływu: Agent → IFC → Router → History → Response")
try:
    ifc = get_ifc()
    ifc.start()
    
    # Rejestracja handlera dla testowego agenta
    agent_received_messages = []
    
    def agent_handler(message):
        agent_received_messages.append(message)
        print(f"   Agent odebrał: {message.message_id} od {message.source}")
        return MessageResponse.success(
            message.message_id,
            {"agent_response": "received"}
        )
    
    ifc.register_module("test_agent", agent_handler)
    
    # Wysłanie wiadomosci od systemu do agenta
    msg = ifc.create_message(
        source="runtime_controller",
        target="test_agent",
        process_type=ProcessType.AGENT_ACTION,
        payload={"action": "test_action", "data": {"test": True}}
    )
    
    print(f"   Wysyłam wiadomosc: {msg.message_id}")
    response = ifc.send_message(msg)
    print(f"   Odpowiedź: {response.status.value}")
    
    # Sprawdzenie czy agent odebrał wiadomosc
    assert len(agent_received_messages) == 1, "Agent nie odebrał wiadomosci"
    assert agent_received_messages[0].message_id == msg.message_id, "Zła wiadomosc odebrana"
    
    # Sprawdzenie historii
    history = get_history()
    history_msgs = history.query_messages(
        source="runtime_controller",
        target="test_agent",
        limit=10
    )
    assert len(history_msgs) >= 1, "Wiadomosc nie została zapisana w historii"
    
    print("✅ Kompletny przepływ wiadomosci działa poprawnie")
    print(f"   Agent odebrał wiadomosc i odpowiedział")
    print(f"   Wiadomosc została zapisana w historii")
    
    ifc.stop()
except Exception as e:
    print(f"❌ Błąd kompletnego przepływu: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Podsumowanie
print("\n" + "=" * 80)
print("✅ WSZYSTKIE TESTY ZALICZONE")
print("=" * 80)
print("\nPodsumowanie:")
print("  ✅ Import modułów")
print("  ✅ SSIMessage tworzenie i walidacja")
print("  ✅ MessageFactory")
print("  ✅ MessageRouter")
print("  ✅ ContextManager")
print("  ✅ MessageHistory")
print("  ✅ InformationFlowController")
print("  ✅ Funkcje helper")
print("  ✅ Kompletny przepływ wiadomosci")
print("\nETAP 2.1: INFORMATION FLOW CONTROLLER - GOTOWY DO UŻYCIA")
print("=" * 80)