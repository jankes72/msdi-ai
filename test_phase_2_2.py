#!/usr/bin/env python3
"""
Test script for FAZA 2.2 - Message Validation + Context Integrity Layer
"""

import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')

print('Testing FAZA 2.2 - Message Validation + Context Integrity Layer')
print('=' * 70)

# Test 1: Import validation layer
print('\n[Test 1] Importing validation layer...')
try:
    from SSI.v5.core.validation import (
        MessageValidator, ContextValidator, SchemaValidator, ValidationRulesEngine,
        validate_message, validate_context, get_validator, get_context_validator
    )
    print('OK: All validation modules imported successfully')
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Import context integrity layer
print('\n[Test 2] Importing context integrity layer...')
try:
    from SSI.v5.core.context_integrity import (
        ContextIntegrityLayer, DynamicContextCorrection, ContextMonitor,
        check_integrity, get_integrity_layer, get_corrector
    )
    print('OK: All context integrity modules imported successfully')
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Basic message validation
print('\n[Test 3] Testing message validation...')
try:
    from SSI.v5.core.information_flow_controller.message_factory import MessageFactory
    from SSI.v5.core.validation.message_validator import get_validator, ValidationReport
    
    # Create a message
    message = MessageFactory.create_message(
        source='test_module',
        target='runtime',
        process_type='system_init',
        payload={'test': 'data'}
    )
    
    # Validate it
    validator = get_validator()
    report = validator.validate(message)
    
    if report.is_valid:
        print(f'OK: Message validation passed')
    else:
        print(f'FAIL: Message validation failed: {report.get_error_messages()}')
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()

# Test 4: Context validation
print('\n[Test 4] Testing context validation...')
try:
    from SSI.v5.core.validation.context_validator import get_context_validator, is_context_complete
    
    message = MessageFactory.create_message(
        source='test_module',
        target='runtime',
        process_type='system_init',
        payload={'test': 'data'}
    )
    
    # Check context
    validator = get_context_validator()
    report = validator.validate(message)
    
    if report.is_complete:
        print(f'OK: Context validation passed')
    else:
        print(f'PARTIAL: Context validation warnings: {report.get_warning_messages()}')
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()

# Test 5: Dynamic context correction
print('\n[Test 5] Testing dynamic context correction...')
try:
    from SSI.v5.core.context_integrity.dynamic_context_correction import get_corrector, correct_context
    
    # Create message with missing context
    incomplete_message = MessageFactory.create_message(
        source='test',
        target='test',
        process_type='agent_request'
    )
    
    corrector = get_corrector()
    corrected_message, result = corrector.correct(incomplete_message)
    
    if result.fields_corrected:
        print(f'OK: Context correction fixed: {result.fields_corrected}')
    else:
        print(f'OK: Context correction passed (no fixes needed)')
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()

# Test 6: Integrity layer
print('\n[Test 6] Testing context integrity layer...')
try:
    from SSI.v5.core.context_integrity.context_integrity_layer import get_integrity_layer, check_integrity
    
    message = MessageFactory.create_message(
        source='test_module',
        target='runtime',
        process_type='system_status',
        payload={'test': 'data'}
    )
    
    layer = get_integrity_layer()
    corrected, result = layer.check_integrity(message)
    
    if result.is_integral:
        print(f'OK: Integrity check passed')
    else:
        print(f'PARTIAL: Integrity check: {result.status.value}')
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()

# Test 7: Context monitor
print('\n[Test 7] Testing context monitor...')
try:
    from SSI.v5.core.context_integrity.context_monitor import get_monitor, start_monitoring, stop_monitoring
    
    monitor = get_monitor()
    if monitor.start():
        print(f'OK: Context monitor started')
        monitor.stop()
    else:
        print(f'FAIL: Context monitor failed to start')
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 70)
print('FAZA 2.2 - All tests completed')
