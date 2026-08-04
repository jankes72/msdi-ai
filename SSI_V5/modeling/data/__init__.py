# SSI V5 Modeling Data Module
# Podział i zarządzanie danymi
#
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 2 - PRIORYTET 2

from SSI_V5.modeling.data.splitter import (
    podziel_dane,
    podziel_dane_standard,
    podziel_dane_chronologicznie,
    get_split_sizes,
    check_split_ratios
)

# Eksport funkcji
__all__ = [
    'podziel_dane',
    'podziel_dane_standard',
    'podziel_dane_chronologicznie',
    'get_split_sizes',
    'check_split_ratios'
]