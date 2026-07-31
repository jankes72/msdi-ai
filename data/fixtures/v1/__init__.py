"""
SSI Fixture Data - Pakiet testowy v1

Małe, wersjonowane dane testowe dla smoke testów.
NIE zawiera danych produkcyjnych.

Wersja: 1.0.0
Data: 2026-07-28
Sprint: 7.1
"""

from pathlib import Path

# Ścieżka do katalogu fixture
FIXTURE_DIR = Path(__file__).parent

# Lista dostępnych fixture
FIXTURES = [
    "sample_matches.csv",
    "sample_predictions.json",
    "sample_world_metadata.yaml",
]

def get_fixture_path(name: str) -> Path:
    """Zwraca ścieżkę do fixture o podanej nazwie"""
    path = FIXTURE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Fixture '{name}' not found in {FIXTURE_DIR}")
    return path

def list_fixtures() -> list:
    """Zwraca listę dostępnych fixture"""
    return [f.name for f in FIXTURE_DIR.glob("*") if f.is_file() and not f.name.startswith("_")]
