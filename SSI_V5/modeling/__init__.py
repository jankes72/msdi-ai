# SSI V5 Modeling Module
# Statistical and neural network models
#
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 2 - PRIORYTET 2

# Import modułów statystycznych
from SSI_V5.modeling.statistical import (
    poisson,
    poisson_simple,
    poisson_probability_matrix,
    dixon_coles,
    dixon_coles_alt,
    get_dixon_coles_correction_factor,
    macierz_wynikow,
    macierz_wynikow_alt,
    get_result_matrix,
    get_top_results,
    get_result_probability
)

# Import modułów preprocessing
from SSI_V5.modeling.preprocessing import (
    normalizuj,
    normalizuj_series,
    normalizuj_array,
    normalizuj_dataframe,
    denormalizuj,
    check_normalization
)

# Import modułów data
from SSI_V5.modeling.data import (
    podziel_dane,
    podziel_dane_standard,
    podziel_dane_chronologicznie,
    get_split_sizes,
    check_split_ratios
)

# Eksportowane funkcje
__all__ = [
    # Statistical
    'poisson',
    'poisson_simple', 
    'poisson_probability_matrix',
    'dixon_coles',
    'dixon_coles_alt',
    'get_dixon_coles_correction_factor',
    'macierz_wynikow',
    'macierz_wynikow_alt',
    'get_result_matrix',
    'get_top_results',
    'get_result_probability',
    
    # Preprocessing
    'normalizuj',
    'normalizuj_series',
    'normalizuj_array',
    'normalizuj_dataframe',
    'denormalizuj',
    'check_normalization',
    
    # Data
    'podziel_dane',
    'podziel_dane_standard',
    'podziel_dane_chronologicznie',
    'get_split_sizes',
    'check_split_ratios'
]
