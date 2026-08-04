# SSI V5 Statistical Models
# Poisson, Dixon-Coles, Random Forest models
#
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 2

# Import głównych modułów
from SSI_V5.modeling.statistical.poisson import poisson, poisson_simple, poisson_probability_matrix
from SSI_V5.modeling.statistical.dixon_coles import dixon_coles, dixon_coles_alt, get_dixon_coles_correction_factor
from SSI_V5.modeling.statistical.matrix import macierz_wynikow, macierz_wynikow_alt, get_result_matrix, get_top_results, get_result_probability

# Eksportowane funkcje (dla kompatybilności wstecznej)
__all__ = [
    # Poisson
    'poisson',
    'poisson_simple', 
    'poisson_probability_matrix',
    
    # Dixon-Coles
    'dixon_coles',
    'dixon_coles_alt',
    'get_dixon_coles_correction_factor',
    
    # Matrix
    'macierz_wynikow',
    'macierz_wynikow_alt',
    'get_result_matrix',
    'get_top_results',
    'get_result_probability'
]
