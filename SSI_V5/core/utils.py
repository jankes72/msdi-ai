# =====================================================
# SSI V5 CORE UTILS
# Modul funkcji technicznych i uniwersalnych
# Data: 2026-08-03
# Etap: 5.2.3 - Ekstrakcja funkcji wspolnych
# =====================================================

import csv
import json
import math
import os
import sys
from datetime import datetime
from collections import defaultdict

# =============================================================================
# FUNKCJE KONWERSJI I PARSOWANIA - CONVERSION AND PARSING FUNCTIONS
# =============================================================================

def liczba(x):
    """
    Konwertuje wartość na liczbę zmiennoprzecinkową.
    
    Args:
        x: Wartość do konwersji (str, int, float)
        
    Returns:
        float: Przekonwertowana wartość, 0.0 w przypadku błędu
        
    Example:
        >>> liczba("3.14")
        3.14
        >>> liczba("abc")
        0.0
    """
    try:
        return float(x)
    except:
        return 0.0


def rozbij_wynik(x):
    """
    Rozbija wynik w formacie "X:Y" na tuple (gospodarz, goście).
    
    Args:
        x (str): Wynik w formacie "X:Y" (np. "2:1")
        
    Returns:
        tuple: (int, int) - liczba goli gospodarza i gości
        
    Example:
        >>> rozbij_wynik("2:1")
        (2, 1)
        >>> rozbij_wynik("0:0")
        (0, 0)
        >>> rozbij_wynik("invalid")
        (0, 0)
    """
    try:
        a, b = x.split(":")
        return int(a), int(b)
    except:
        return 0, 0


def popraw_wynik(wynik):
    """
    Poprawia format wyniku, zamieniając kropki na dwukropki.
    
    Args:
        wynik (str): Wynik do poprawy (np. "2.1" -> "2:1")
        
    Returns:
        str: Poprawiony format wyniku
        
    Example:
        >>> popraw_wynik("2.1")
        '2:1'
        >>> popraw_wynik("1:0")
        '1:0'
    """
    wynik = wynik.strip()
    if "." in wynik:
        wynik = wynik.replace(".", ":")
    return wynik



# =============================================================================
# FUNKCJE MATEMATYCZNE - MATHEMATICAL FUNCTIONS
# =============================================================================

def odleglosc(a, b):
    """
    Oblicza odległość euklidesową między dwoma wektorami.
    
    Args:
        a (iterable): Pierwszy wektor
        b (iterable): Drugi wektor
        
    Returns:
        float: Odległość euklidesowa
        
    Example:
        >>> odleglosc([1, 2], [4, 6])
        5.0
    """
    suma = 0
    for x, y in zip(a, b):
        suma += (x - y) ** 2
    return math.sqrt(suma)


def bezpieczny_log(value):
    """
    Oblicza logarytm naturalny z zabezpieczeniem przed zerem.
    
    Args:
        value (float): Wartość do obliczenia logarytmu
        
    Returns:
        float: log(value) z minimum 1.01
        
    Example:
        >>> bezpieczny_log(10)
        2.302585092994046
        >>> bezpieczny_log(0.5)
        0.0
    """
    return math.log(max(value, 1.01))


def normalize(value, min_val, max_val):
    """
    Normalizuje wartość do zakresu [0, 1].
    
    Args:
        value (float): Wartość do znormalizowania
        min_val (float): Minimalna wartość zakresu
        max_val (float): Maksymalna wartość zakresu
        
    Returns:
        float: Znormalizowana wartość w zakresie [0, 1]
        
    Example:
        >>> normalize(5, 0, 10)
        0.5
        >>> normalize(0, 0, 10)
        0.0
    """
    if max_val - min_val == 0:
        return 0.5
    return max(
        0,
        min(
            1,
            (value - min_val) / (max_val - min_val)
        )
    )



# =============================================================================
# FUNKCJE WYNIKÓW - RESULT FUNCTIONS
# =============================================================================

def wynik_1x2(x):
    """
    Klasyfikuje wynik na: 1 (gospodarz wygrywa), 0 (remis), 2 (goście wygrywają).
    
    Args:
        x (str): Wynik w formacie "X:Y" (np. "2:1")
        
    Returns:
        int: 1 (gospodarz), 0 (remis), 2 (goście)
        
    Example:
        >>> wynik_1x2("2:1")
        1
        >>> wynik_1x2("1:1")
        0
        >>> wynik_1x2("0:2")
        2
    """
    a, b = rozbij_wynik(x)
    if a > b:
        return 1
    elif a == b:
        return 0
    else:
        return 2


def wynik_gole(x):
    """
    Oblicza całkowitą liczbę goli w wyniku.
    
    Args:
        x (str): Wynik w formacie "X:Y" (np. "2:1")
        
    Returns:
        int: Suma goli (gospodarz + goście)
        
    Example:
        >>> wynik_gole("2:1")
        3
        >>> wynik_gole("0:0")
        0
    """
    a, b = rozbij_wynik(x)
    return a + b


def wynik_liczbowy(wynik):
    """
    Konwertuje wynik na wartość liczbową: 1 (gospodarz), 0 (remis), -1 (goście).
    
    Args:
        wynik (str): Wynik w formacie "X:Y" (np. "2:1")
        
    Returns:
        int: 1, 0 lub -1
        
    Example:
        >>> wynik_liczbowy("2:1")
        1
        >>> wynik_liczbowy("1:1")
        0
        >>> wynik_liczbowy("0:2")
        -1
    """
    try:
        g1, g2 = wynik.split(":")
        g1 = int(g1)
        g2 = int(g2)
        if g1 > g2:
            return 1
        elif g1 == g2:
            return 0
        else:
            return -1
    except:
        return 0



# =============================================================================
# FUNKCJE ŁADOWANIA DANYCH - DATA LOADING FUNCTIONS
# =============================================================================

def load_csv(file_path, delimiter=';', encoding='utf-8'):
    """
    Wczytuje dane z pliku CSV.
    
    Args:
        file_path (str): Ścieżka do pliku CSV
        delimiter (str): Separator kolumn (domyślnie ';')
        encoding (str): Kodowanie pliku (domyślnie 'utf-8')
        
    Returns:
        list: Lista wierszy z pliku CSV
        
    Example:
        >>> data = load_csv("dane.csv", delimiter=';')
        >>> len(data)
        100
    """
    data = []
    with open(
        file_path,
        'r',
        encoding=encoding,
        errors="ignore",
        newline=""
    ) as file:
        reader = csv.reader(file, delimiter=delimiter)
        for row in reader:
            if len(row) >= 3:
                # Popraw format wyniku w trzeciej kolumnie
                row[2] = popraw_wynik(row[2])
                data.append(row)
    return data


def save_csv(
        data,
        file_path,
        delimiter=';',
        encoding='utf-8',
        include_header=True,
        header=None
):
    """
    Zapisuje dane do pliku CSV
    
    Args:
        data: Dane do zapisu (lista wierszy)
        file_path: Sciezka do pliku CSV
        delimiter: Znak podzialu (domyslnie ';')
        encoding: Kodowanie pliku (domyslnie 'utf-8')
        include_header: Czy zapisywać nagłówek
        header: Nagłówek (lista nazw kolumn)
        
    Returns:
        bool: True jezeli udalo sie zapisać
    """
    try:
        with open(
            file_path,
            'w',
            encoding=encoding,
            newline=""
        ) as file:
            
            writer = csv.writer(
                file,
                delimiter=delimiter
            )
            
            if include_header and header:
                writer.writerow(header)
                
            for row in data:
                writer.writerow(row)
        return True
    except Exception as e:
        print(f"Blad podczas zapisywania CSV {file_path}: {e}")
        return False


def load_json(path):
    """
    Wczytuje dane z pliku JSON.
    
    Args:
        path (str): Ścieżka do pliku JSON
        
    Returns:
        dict: Załadowane dane JSON, pusta słownik w przypadku braku pliku
        
    Example:
        >>> data = load_json("config.json")
        >>> data.keys()
        dict_keys(['param1', 'param2'])
    """
    if not os.path.exists(path):
        print("Brak pliku:", path)
        return {}
    
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, path, indent=2, encoding='utf-8'):
    """
    Zapisuje dane do pliku JSON
    
    Args:
        data: Dane do zapisu
        path: Sciezka do pliku JSON
        indent: Poziom wciecia (domyslnie 2)
        encoding: Kodowanie pliku (domyslnie 'utf-8')
        
    Returns:
        bool: True jezeli udalo sie zapisać
    """
    try:
        with open(
            path,
            "w",
            encoding=encoding
        ) as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Blad podczas zapisywania JSON {path}: {e}")
        return False


# =====================================================
# FUNKCJE WALIDACJI DANYCH
# =====================================================

def is_valid_number(value):
    """
    Sprawdza czy wartosc jest poprawna liczba (nie None, nie NaN)
    
    Args:
        value: Wartosc do sprawdzenia
        
    Returns:
        bool: True jezeli wartosc jest poprawna liczba
    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def validate_csv_structure(file_path, min_columns=3, delimiter=';'):
    """
    Waliduje strukture pliku CSV
    
    Args:
        file_path: Sciezka do pliku CSV
        min_columns: Minimalna liczba kolumn
        delimiter: Znak podzialu
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', newline="") as file:
            reader = csv.reader(file, delimiter=delimiter)
            
            # Sprawdzenie pierwszej linii
            first_row = next(reader, None)
            if first_row is None:
                return False, "Plik jest pusty"
            
            if len(first_row) < min_columns:
                return False, f" Za malo kolumn: {len(first_row)} < {min_columns}"
            
            return True, "OK"
            
    except Exception as e:
        return False, str(e)


# =====================================================
# FUNKCJE OGOLNEGO ZASTOSOWANIA
# =====================================================

def get_timestamp():
    """
    Zwraca aktualny timestamp jako string
    
    Returns:
        str: Aktualny timestamp w formacie ISO
    """
    return str(datetime.now())


def format_duration(seconds):
    """
    Formatuje czas trwania w sekundach do czytelnego formatu
    
    Args:
        seconds: Czas trwania w sekundach
        
    Returns:
        str: Sformatowany czas (np. "1h 23m 45s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:  # Pokazuj sekundy jezeli nic innego
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def ensure_directory(path):
    """
    Upewnia sie ze katalog istnieje, tworzy go jezeli nie
    
    Args:
        path: Sciezka do katalogu
        
    Returns:
        bool: True jezeli katalog istnieje lub zostal utworzony
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Blad podczas tworzenia katalogu {path}: {e}")
        return False


# =====================================================
# FUNKCJE STATYSTYCZNE
# =====================================================

def safe_mean(values):
    """
    Bezpieczne obliczanie sredniej
    
    Args:
        values: Lista wartosci
        
    Returns:
        float: Srednia lub 0.0 jezeli lista jest pusta
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def safe_std(values, mean=None):
    """
    Bezpieczne obliczanie odchylenia standardowego
    
    Args:
        values: Lista wartosci
        mean: Opjonalna srednia (jesli znana)
        
    Returns:
        float: Odchylenie standardowe lub 0.0 jezeli lista ma mniej niz 2 elementy
    """
    if len(values) < 2:
        return 0.0
    
    if mean is None:
        mean = safe_mean(values)
    
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


# =============================================================================
# EKSPORT FUNKCJI
# =============================================================================

__all__ = [
    # Funkcje konwersji i parsowania
    'liczba',
    'rozbij_wynik', 
    'popraw_wynik',
    
    # Funkcje matematyczne
    'odleglosc',
    'bezpieczny_log',
    'normalize',
    
    # Funkcje wyników
    'wynik_1x2',
    'wynik_gole',
    'wynik_liczbowy',
    
    # Funkcje ładowania danych
    'load_csv',
    'save_csv',
    'load_json',
    'save_json',
    
    # Funkcje walidacji danych
    'is_valid_number',
    'validate_csv_structure',
    
    # Funkcje ogolnego zastosowania
    'get_timestamp',
    'format_duration',
    'ensure_directory',
    
    # Funkcje statystyczne
    'safe_mean',
    'safe_std'
]



# =============================================================================
# INFORMACJE DIAGNOSTYCZNE
# =============================================================================

if __name__ == "__main__":
    print("SSI V5 Core Utils Module")
    print("=" * 40)
    
    # Testy funkcji
    print("\n=== Testy Funkcji ===")
    
    # Testy konwersji
    print(f"liczba('3.14') = {liczba('3.14')}")
    print(f"liczba('abc') = {liczba('abc')}")
    
    # Testy parsowania
    print(f"rozbij_wynik('2:1') = {rozbij_wynik('2:1')}")
    print(f"popraw_wynik('2.1') = {popraw_wynik('2.1')}")
    
    # Testy matematyczne
    print(f"odleglosc([1,2], [4,6]) = {odleglosc([1,2], [4,6])}")
    print(f"bezpieczny_log(10) = {bezpieczny_log(10)}")
    print(f"normalize(5, 0, 10) = {normalize(5, 0, 10)}")
    
    # Testy wyników
    print(f"wynik_1x2('2:1') = {wynik_1x2('2:1')}")
    print(f"wynik_gole('2:1') = {wynik_gole('2:1')}")
    print(f"wynik_liczbowy('2:1') = {wynik_liczbowy('2:1')}")
    
    print("\nAll tests passed!")