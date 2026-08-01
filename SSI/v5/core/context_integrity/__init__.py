"""
SSI V5 - Context Integrity Layer

Warstwa zapewniajaca integralnosc i spójnosc kontekstu w systemie SSI V5.

Struktura:
- context_integrity_layer.py: Glowna warstwa integralnosci
- dynamic_context_correction.py:iatyczna korekta kontekstu
- context_monitor.py: Monitorowanie kontekstu i wykrywanie anomalii

Zasady:
1. Brak kontekstu = NIE wykonuj dzialania
2. Najpierw: korekta kontekstu -> walidacja -> wykonanie
3. Wszystko przez IFC

Wersja: 2.0.0
Data: 2026-08-01
"""

from SSI.v5.core.context_integrity.context_integrity_layer import (
    ContextIntegrityLayer,
    IntegrityCheckLevel,
    IntegrityStatus,
    IntegrityCheckResult,
    IntegrityConfig,
    get_integrity_layer,
    check_integrity,
    check_and_fix_integrity,
    is_integral,
    ensure_integrity
)

from SSI.v5.core.context_integrity.dynamic_context_correction import (
    DynamicContextCorrection,
    CorrectionAction,
    CorrectionStrategy,
    CorrectionResult,
    CorrectionConfig,
    get_corrector,
    correct_context,
    ensure_context_complete
)

from SSI.v5.core.context_integrity.context_monitor import (
    ContextMonitor,
    ContextEvent,
    ContextEventType,
    ContextAnomaly,
    MonitorStatus,
    AnomalyDetector,
    AnomalyDetectionStrategy,
    get_monitor,
    start_monitoring,
    stop_monitoring,
    emit_context_event,
    check_for_context_anomalies,
    monitor_message
)

# Eksport klas i funkcji
__all__ = [
    # Context Integrity Layer
    'ContextIntegrityLayer',
    'IntegrityCheckLevel',
    'IntegrityStatus',
    'IntegrityCheckResult',
    'IntegrityConfig',
    'get_integrity_layer',
    'check_integrity',
    'check_and_fix_integrity',
    'is_integral',
    'ensure_integrity',
    
    # Dynamic Context Correction
    'DynamicContextCorrection',
    'CorrectionAction',
    'CorrectionStrategy',
    'CorrectionResult',
    'CorrectionConfig',
    'get_corrector',
    'correct_context',
    'ensure_context_complete',
    
    # Context Monitor
    'ContextMonitor',
    'ContextEvent',
    'ContextEventType',
    'ContextAnomaly',
    'MonitorStatus',
    'AnomalyDetector',
    'AnomalyDetectionStrategy',
    'get_monitor',
    'start_monitoring',
    'stop_monitoring',
    'emit_context_event',
    'check_for_context_anomalies',
    'monitor_message'
]


def init_context_integrity_layer() -> bool:
    """
    Inicjalizacja warstwy integralnosci kontekstu.
    
    Returns:
        bool: True jeśli inicjalizacja powiodła się
    """
    try:
        # Inicjalizacja komponentów (lazy loading)
        get_integrity_layer()
        get_corrector()
        get_monitor()
        
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Blad podczas inicjalizacji warstwy integralnosci kontekstu: {e}")
        return False
