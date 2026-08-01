#!/usr/bin/env python3
"""
Test integracji walidacji z IFC Controller
"""

import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')

print('Testing IFC Integration with Validation Layer')
print('=' * 70)

# Test 1: Import IFC z nowa warstwa walidacji
print('\n[Test 1] Testing IFC with validation integration...')
try:
    from SSI.v5.core.information_flow_controller.ifc_controller import (
        InformationFlowController, get_ifc, send_message
    )
    from SSI.v5.core.information_flow_controller.message_factory import MessageFactory
    from SSI.v5.core.information_flow_controller.message_models import MessageResponse, MessageStatus
    
    # Uruchomienie IFC
    ifc = InformationFlowController.get_instance()
    ifc.start()
    
    # Rejestracja handlera dla testowego targetu
    def test_handler(message):
        return MessageResponse.success(message.message_id)
    
    ifc.register_module('system', handler=test_handler)
    
    # Utworzenie wiadomosci
    message = MessageFactory.create_message(
        source='test_module',
        target='system',
        process_type='system_status',
        payload={'test': 'integration'}
    )
    
    # Wyslane wiadomosci przez IFC (powinno uzyc nowej walidacji)
    response = ifc.send_message(message)
    
    if response.status.value in ['processed', 'sent', 'queued']:
        print(f'OK: IFC integration with validation working')
    else:
        print(f'FAIL: IFC response status: {response.status.value}')
    
    # Zatrzymanie IFC
    ifc.stop()
    
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()

# Test 2: Config IFC z opcjami walidacji
print('\n[Test 2] Testing IFC Config with validation options...')
try:
    from SSI.v5.core.information_flow_controller.ifc_controller import IFCConfig
    
    # Test konfigurowania IFC
    config = IFCConfig(
        enable_validation=True,
        enable_context_correction=True,
        enable_history=True,
        enable_integrity_layer=True
    )
    
    ifc = InformationFlowController(config)
    ifc.start()
    
    if ifc.config.enable_integrity_layer:
        print(f'OK: IFC Config with integrity layer enabled')
    else:
        print(f'FAIL: IFC Config integrity layer disabled')
    
    ifc.stop()
    
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()

# Test 3: Wyslanie wielu wiadomosci
print('\n[Test 3] Testing multiple messages through IFC...')
try:
    from SSI.v5.core.information_flow_controller.ifc_controller import InformationFlowController
    
    # Nowa instancja IFC
    InformationFlowController._instance = None
    ifc = InformationFlowController.get_instance()
    ifc.start()
    
    # Rejestracja handlerów
    def runtime_handler(message):
        return MessageResponse.success(message.message_id)
    
    ifc.register_module('runtime', handler=runtime_handler)
    
    messages = []
    for i in range(5):
        msg = MessageFactory.create_message(
            source='test_module',
            target='runtime',
            process_type='agent_request',
            payload={'index': i, 'data': f'message_{i}'}
        )
        response = ifc.send_message(msg)
        messages.append((msg.message_id, response.status.value))
    
    # Sprawdzenie czy wszystkie wiadomosci zostaty wyslane
    def get_status_value(status):
        if hasattr(status, 'value'):
            return status.value
        return status
    
    success_count = sum(1 for _, status in messages if get_status_value(status) in ['processed', 'sent', 'queued'])
    
    if success_count == 5:
        print(f'OK: All 5 messages processed through IFC with validation')
    else:
        print(f'PARTIAL: {success_count}/5 messages processed')
        for msg_id, status in messages:
            status_val = get_status_value(status)
            if status_val not in ['processed', 'sent', 'queued']:
                print(f'  FAILED: {msg_id} -> {status_val}')
    
    ifc.stop()
    
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()

# Test 4: Walidacja i odrzucanie nieprawidlowych wiadomosci
print('\n[Test 4] Testing validation rejection...')
try:
    from SSI.v5.core.information_flow_controller.ifc_controller import InformationFlowController
    
    # Nowa instancja IFC
    InformationFlowController._instance = None
    ifc = InformationFlowController.get_instance()
    ifc.start()
    
    # Rejestracja handlera
    def runtime_handler(message):
        return MessageResponse.success(message.message_id)
    
    ifc.register_module('runtime', handler=runtime_handler)
    
    # Tworzenie nieprawidlowej wiadomosci - brak wymaganych pol
    # nie mozna utworzyc przez MessageFactory, wiec robimy manualnie
    from SSI.v5.core.information_flow_controller.message_models import SSIMessage, ModuleIdentifier
    
    # Utworzenie nieprawidlowej wiadomosci z pominieciem wymaganego target
    incomplete_msg = SSIMessage(
        message_id='testinvalid-001',
        source=ModuleIdentifier(module_name='test', module_type='test'),
        target=None,  # Brak target - nieprawidlowe!
        timestamp=None,  # Brak timestamp
        system_state=None,  # Brak system_state
        session_id='default',
        cycle_id='default'
    )
    
    # Procedura send_message powinna odrzucic ta wiadomosc
    response = ifc.send_message(incomplete_msg)
    
    if response.status.value == 'failed':
        print(f'OK: Invalid message rejected by IFC')
    else:
        print(f'WARNING: Invalid message was accepted: {response.status.value}')
    
    ifc.stop()
    
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 70)
print('IFC Integration Tests completed')
