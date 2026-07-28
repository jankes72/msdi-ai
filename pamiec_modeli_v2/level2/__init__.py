"""
PAMIĘĆ MODELI V2 - LEVEL 2 (KALIBRATOR)
========================================

Moduł Modelu Level 2 - Kalibrator uczący się zachowania Modelu Level 1.

Architektura:
- Model Level 1: Generuje predykcje (agregacja z 15 sieci SSI)
- Model Level 2: Kalibruje confidence, wykrywa wzorce zachowania
- Pamięć: Centralne repozytorium obserwacji (predykcja vs rzeczywistość)

Zasady:
- Level 2 NIE przewiduje meczów
- Level 2 uczy się NA podstawie historii Level 1
- Każdy trening tworzy NOWĄ wersję modelu (nie nadpisujemy!)

Autor: MSDI AI v0.02
Data: 2026-07-27
"""

from pamiec_modeli_v2.level2.kalibrator import KalibratorLevel2

__all__ = ['KalibratorLevel2']
