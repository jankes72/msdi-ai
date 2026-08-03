# SSI V5 Neural Network Models
# Network building and training
#
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 2 PRIORYTET 3
#
# Import glownych modulow
from SSI_V5.modeling.neural.network_builder import (
    # Funkcje budowy sieci
    buduj_siec,
    buduj_siec_v1,
    buduj_siec_v2,
    buduj_siec_v3,
    buduj_siec_v4,
    buduj_siec_v5,
    
    # Funkcje pomocnicze
    podziel_dane,
    podziel_dane_chronologicznie,
    
    # Klasy i funkcje dla integracji z Teacherem
    CognitiveTeacher,
    generuj_pamiec_swiatow
)

# Eksportowane funkcje (dla kompatybilnosci wstecznej)
__all__ = [
    # Funkcje budowy sieci
    'buduj_siec',
    'buduj_siec_v1',
    'buduj_siec_v2',
    'buduj_siec_v3',
    'buduj_siec_v4',
    'buduj_siec_v5',
    
    # Funkcje pomocnicze
    'podziel_dane',
    'podziel_dane_chronologicznie',
    
    # Klasy i funkcje Teacher
    'CognitiveTeacher',
    'generuj_pamiec_swiatow'
]
