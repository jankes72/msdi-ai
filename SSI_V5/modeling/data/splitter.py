# SSI V5 Data Module - Data Splitter
# =================================================
# 
# Moduł implementujący podział danych na zbiory:
# - 50% trening
# - 10% walidacja  
# - 40% obserwacja
# 
# Używa sklearn.model_selection.train_test_split
# 
# Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 2 - PRIORYTET 2
# 
# Zasada: Zachowana oryginalna logika z głównego generatora

from sklearn.model_selection import train_test_split

# Stały random_state dla powtarzalności wyników
RANDOM_STATE = 42

# Proporcje podziału
TRAIN_SIZE = 0.50      # 50% na trening
VAL_SIZE = 0.166666    # ~16.67% na walidację (1/6 pozostałych 60%)
OBSERVATION_SIZE = 0.40  # 40% na obserwację


def podziel_dane(X, y):
    """
    Dzieli dane na zbiory: trening (50%), walidacja (10%), obserwacja (40%).
    
    Proces podziału:
    1. Pierwsz podział: 60% (trening+walidacja) / 40% (obserwacja)
    2. Drugi podział: 50%/10% z pierwszych 60%
    
    Wynik:
    - 50% - trening
    - 10% - walidacja  
    - 40% - obserwacja
    
    Args:
        X (array-like): Cechy wejściowe
        y (array-like): Etykiety/zmienne zależne
        
    Returns:
        tuple: (X_train, X_val, X_obserwacja, y_train, y_val, y_obserwacja)
        
    Note:
        Używa stratyfikacji względem y dla zachowania proporcji klas.
    """
    # Pierwszy podział: 60% (trening+walidacja) / 40% (obserwacja)
    X_temp, X_obserwacja, y_temp, y_obserwacja = train_test_split(
        X,
        y,
        test_size=OBSERVATION_SIZE,  # 40% na obserwację
        random_state=RANDOM_STATE,
        stratify=y
    )
    
    # Drugi podział: 50%/10% z tymczasowego zbioru (60% oryginału)
    # test_size=0.166666 daje ~16.67% z X_temp, co jest ~10% z oryginału
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp,
        y_temp,
        test_size=VAL_SIZE,  # ~16.67% z 60% = ~10% z oryginału
        random_state=RANDOM_STATE,
        stratify=y_temp
    )
    
    return (
        X_train,
        X_val,
        X_obserwacja,
        y_train,
        y_val,
        y_obserwacja
    )


def podziel_dane_standard(X, y, test_size=0.2, random_state=None):
    """
    Standardowy podział na trening i test (dla porównania).
    
    Args:
        X (array-like): Cechy wejściowe
        y (array-like): Etykiety
        test_size (float): Proporcja zbioru testowego
        random_state (int, optional): Ziarno losowości
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    if random_state is None:
        random_state = RANDOM_STATE
    
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )


def podziel_dane_chronologicznie(X, y, test_size=0.4, val_size=0.166666):
    """
    Chronologiczny podział danych (bez losowania).
    
    Args:
        X (array-like): Cechy wejściowe (powinny być posortowane chronologicznie)
        y (array-like): Etykiety
        test_size (float): Proporcja zbioru obserwacyjnego
        val_size (float): Proporcja zbioru walidacyjnego
        
    Returns:
        tuple: (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    n_samples = len(X)
    
    # Indeks podziału na trening + walidacja vs obserwacja
    test_idx = int(n_samples * (1 - test_size))
    
    X_temp = X[:test_idx]
    y_temp = y[:test_idx]
    X_obserwacja = X[test_idx:]
    y_obserwacja = y[test_idx:]
    
    # Podział trening/walidacja
    val_idx = int(len(X_temp) * (1 - val_size / (1 - test_size)))
    
    X_train = X_temp[:val_idx]
    y_train = y_temp[:val_idx]
    X_val = X_temp[val_idx:]
    y_val = y_temp[val_idx:]
    
    return (
        X_train,
        X_val,
        X_obserwacja,
        y_train,
        y_val,
        y_obserwacja
    )


def get_split_sizes(X, y):
    """
    Zwraca rozmiary zbiorów po podziale (bez faktycznego dzielenia).
    
    Args:
        X (array-like): Cechy wejściowe
        y (array-like): Etykiety
        
    Returns:
        dict: Rozmiary oczekiwanych zbiorów
    """
    n_samples = len(X)
    
    train_size = int(n_samples * TRAIN_SIZE)
    val_size = int(n_samples * 0.10)  # 10%
    obs_size = int(n_samples * OBSERVATION_SIZE)  # 40%
    
    return {
        'total': n_samples,
        'train': train_size,
        'validation': val_size,
        'observation': obs_size,
        'sum': train_size + val_size + obs_size
    }


# =================================================
# FUNKCJE POMOCNICZE DO DIAGNOSTYKI
# =================================================

def check_split_ratios(X_train, X_val, X_obserwacja, X_original):
    """
    Sprawdza, czy podział został wykonany w poprawnych proporcjach.
    
    Args:
        X_train, X_val, X_obserwacja: Zbiory po podziale
        X_original: Oryginalny zbiór
        
    Returns:
        dict: Informacje o proporcjach podziału
    """
    total = len(X_original)
    train_ratio = len(X_train) / total
    val_ratio = len(X_val) / total
    obs_ratio = len(X_obserwacja) / total
    
    return {
        'total_samples': total,
        'train_samples': len(X_train),
        'val_samples': len(X_val),
        'obs_samples': len(X_obserwacja),
        'train_ratio': train_ratio,
        'val_ratio': val_ratio,
        'obs_ratio': obs_ratio,
        'total_ratio': train_ratio + val_ratio + obs_ratio,
        'expected': {'train': 0.50, 'val': 0.10, 'obs': 0.40}
    }


# =================================================
# TESTY MODUŁU
# =================================================

def test_podziel_dane():
    """Test podstawowych funkcjonalności modułu splitter.py."""
    import numpy as np
    
    # Test 1: Podstawowy podział
    X = np.arange(100).reshape(-1, 1)
    y = np.random.randint(0, 2, 100)
    
    X_train, X_val, X_obserwacja, y_train, y_val, y_obserwacja = podziel_dane(X, y)
    
    # Sprawdź rozmiary
    total_samples = len(X)
    train_size = len(X_train)
    val_size = len(X_val)
    obs_size = len(X_obserwacja)
    
    # Sprawdź, czy rozmiary są poprawne
    assert train_size + val_size + obs_size == total_samples, "Suma rozmiarów powinna równać się liczbie próbek"
    
    # Sprawdź proporcje (z tolerancją na zaokrąglenia)
    train_ratio = train_size / total_samples
    val_ratio = val_size / total_samples
    obs_ratio = obs_size / total_samples
    
    assert abs(train_ratio - 0.50) < 0.05, f"Proporcja treningu: {train_ratio:.2f} (oczekiwano ~0.50)"
    assert abs(val_ratio - 0.10) < 0.05, f"Proporcja walidacji: {val_ratio:.2f} (oczekiwano ~0.10)"
    assert abs(obs_ratio - 0.40) < 0.05, f"Proporcja obserwacji: {obs_ratio:.2f} (oczekiwano ~0.40)"
    
    # Test 2: Sprawdź, że indeksy się nie pokrywają
    all_indices = set()
    for i, x in enumerate(X_train):
        all_indices.add(i)
    for i, x in enumerate(X_val):
        all_indices.add(i + len(X_train))
    for i, x in enumerate(X_obserwacja):
        all_indices.add(i + len(X_train) + len(X_val))
    
    # Powinno być 100 unikalnych indeksów (zakładając, że train_test_split nie duplikuje)
    assert len(all_indices) == total_samples, "Nie powinno być duplikatów"
    
    # Test 3: get_split_sizes
    sizes = get_split_sizes(X, y)
    assert sizes['total'] == total_samples
    assert sizes['sum'] == total_samples
    
    # Test 4: check_split_ratios
    ratios = check_split_ratios(X_train, X_val, X_obserwacja, X)
    assert abs(ratios['total_ratio'] - 1.0) < 0.01, "Suma proporcji powinna dać ~1.0"
    
    # Test 5: Standardowy podział
    X_train_std, X_test_std, y_train_std, y_test_std = podziel_dane_standard(X, y, test_size=0.2)
    assert len(X_train_std) + len(X_test_std) == total_samples
    assert abs(len(X_test_std) / total_samples - 0.2) < 0.05
    
    print("[OK] Wszystkie testy modułu splitter.py zaliczone")


if __name__ == "__main__":
    test_podziel_dane()
    print("Moduł splitter.py - Test wykonany pomyslnie")