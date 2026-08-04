# SSI V5 Preprocessing Module - Normalizer
# =================================================
# 
# Moduł implementujący normalizację danych wektorowych (pandas/numpy).
# Normalizacja min-max: (x - min) / (max - min)
# 
# UWAGA: To NIE JEST to samo co normalize() z core/utils.py!
# - normalize() - normalizacja standardowa (z-score)
# - normalizuj() - normalizacja min-max dla danych wektorowych
# 
# Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 2 - PRIORYTET 2
# 
# Zasada: Zachowana oryginalna logika z głównego generatora

import pandas as pd
import numpy as np


def normalizuj(x):
    """
    Normalizacja min-max dla wektora/serii danych.
    
    Przekształca dane tak, aby mieściły się w zakresie [0, 1].
    
    Args:
        x (pandas.Series or numpy.ndarray): Wejściowy wektor danych
        
    Returns:
        pandas.Series or numpy.ndarray: Znormalizowany wektor
        
    Note:
        Jeśli max == min (stały wektor), zwraca wektor zerowy.
        Zachowuje typ wejściowy (pandas Series lub numpy array).
    """
    # Sprawdź, czy max == min (przypadek stałego wektora)
    if x.max() == x.min():
        # Zwróć wektor zerowy tego samego typu co wejście
        if isinstance(x, pd.Series):
            return x * 0
        elif isinstance(x, np.ndarray):
            return x * 0
        else:
            # Dla innych typów (np. listy) konwertuj na numpy array
            return np.array(x) * 0
    
    # Normalizacja min-max
    if isinstance(x, pd.Series):
        return (x - x.min()) / (x.max() - x.min())
    elif isinstance(x, np.ndarray):
        return (x - x.min()) / (x.max() - x.min())
    else:
        # Dla list i innych typów konwertuj na numpy array
        x_array = np.array(x)
        return (x_array - x_array.min()) / (x_array.max() - x_array.min())


def normalizuj_series(x):
    """
    Normalizacja min-max dla pandas Series (specyficzna wersja).
    
    Args:
        x (pandas.Series): Wejściowa seria pandas
        
    Returns:
        pandas.Series: Znormalizowana seria
    """
    if x.max() == x.min():
        return x * 0
    
    return (x - x.min()) / (x.max() - x.min())


def normalizuj_array(x):
    """
    Normalizacja min-max dla numpy array (specyficzna wersja).
    
    Args:
        x (numpy.ndarray): Wejściowa tablica numpy
        
    Returns:
        numpy.ndarray: Znormalizowana tablica
    """
    if x.max() == x.min():
        return x * 0
    
    return (x - x.min()) / (x.max() - x.min())


def normalizuj_dataframe(df, columns=None):
    """
    Normalizacja min-max dla wybranych kolumn DataFrame.
    
    Args:
        df (pandas.DataFrame): Wejściowy DataFrame
        columns (list, optional): Lista kolumn do normalizacji.
                                 Jeśli None, normalizuje wszystkie kolumny numeryczne.
        
    Returns:
        pandas.DataFrame: DataFrame z znormalizowanymi kolumnami
    """
    df_copy = df.copy()
    
    if columns is None:
        # Wybierz wszystkie kolumny numeryczne
        columns = df.select_dtypes(include=[np.number]).columns
    
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = normalizuj(df_copy[col])
    
    return df_copy


def denormalizuj(x, x_original):
    """
    Denormalizacja danych z użyciem oryginalnego zakresu.
    
    Args:
        x (pandas.Series or numpy.ndarray): Znormalizowany wektor
        x_original (pandas.Series or numpy.ndarray): Oryginalny wektor
        
    Returns:
        pandas.Series or numpy.ndarray: Zdenormalizowany wektor
    """
    x_min = x_original.min()
    x_max = x_original.max()
    
    if isinstance(x, pd.Series):
        return x * (x_max - x_min) + x_min
    elif isinstance(x, np.ndarray):
        return x * (x_max - x_min) + x_min
    else:
        x_array = np.array(x)
        return x_array * (x_max - x_min) + x_min


# =================================================
# FUNKCJE POMOCNICZE DO DIAGNOSTYKI
# =================================================

def check_normalization(x, x_normalized):
    """
    Sprawdza, czy normalizacja została wykonana poprawnie.
    
    Args:
        x (array-like): Oryginalny wektor
        x_normalized (array-like): Znormalizowany wektor
        
    Returns:
        dict: Informacje o normalizacji
    """
    result = {
        'original_min': float(x.min()),
        'original_max': float(x.max()),
        'normalized_min': float(x_normalized.min()),
        'normalized_max': float(x_normalized.max()),
        'is_normalized': (
            abs(x_normalized.min()) < 1e-10 and 
            abs(x_normalized.max() - 1.0) < 1e-10
        )
    }
    return result


# =================================================
# TESTY MODUŁU
# =================================================

def test_normalizuj():
    """Test podstawowych funkcjonalności modułu normalizer.py."""
    
    # Test 1: Stały wektor (max == min)
    import pandas as pd
    import numpy as np
    
    constant_series = pd.Series([5, 5, 5, 5])
    result_constant = normalizuj(constant_series)
    assert all(result_constant == 0), "Stały wektor powinien dać same zera"
    
    # Test 2: Normalna normalizacja - pandas Series
    test_series = pd.Series([0, 1, 2, 3, 4])
    result_series = normalizuj(test_series)
    expected_min = 0.0
    expected_max = 1.0
    assert abs(result_series.min() - expected_min) < 1e-10
    assert abs(result_series.max() - expected_max) < 1e-10
    
    # Test 3: Normalna normalizacja - numpy array
    test_array = np.array([0, 1, 2, 3, 4])
    result_array = normalizuj(test_array)
    assert abs(result_array.min() - expected_min) < 1e-10
    assert abs(result_array.max() - expected_max) < 1e-10
    
    # Test 4: Zachowanie typu
    assert isinstance(result_series, pd.Series), "Powinien zachować typ Series"
    assert isinstance(result_array, np.ndarray), "Powinien zachować typ ndarray"
    
    # Test 5: Denormalizacja
    denormalized = denormalizuj(result_series, test_series)
    assert all(abs(denormalized - test_series) < 1e-10), "Denormalizacja powinna przywrócić oryginał"
    
    # Test 6: Normalizacja DataFrame
    test_df = pd.DataFrame({'A': [0, 1, 2], 'B': [10, 20, 30]})
    result_df = normalizuj_dataframe(test_df)
    assert result_df['A'].min() >= 0 and result_df['A'].max() <= 1
    assert result_df['B'].min() >= 0 and result_df['B'].max() <= 1
    
    # Test 7: Sprawdzenie normalizacji
    check = check_normalization(test_series, result_series)
    assert check['is_normalized'], "Diagnostyka powinna potwierdzić normalizację"
    
    print("[OK] Wszystkie testy modułu normalizer.py zaliczone")


if __name__ == "__main__":
    test_normalizuj()
    print("Moduł normalizer.py - Test wykonany pomyslnie")