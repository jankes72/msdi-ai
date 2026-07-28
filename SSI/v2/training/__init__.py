"""
SSI V2 Training - Trenowanie modeli

Moduł odpowiedzialny za:
- Trenowanie modeli V2 na danych treningowych (60%)
- Walidację modeli
- Cross-validation
- Optymalizację hiperparametrów

Wersja: 1.0
Data: 2026-07-28
"""

from .model_trainer import (
    ModelTrainer, TrainingConfig, TrainingResult,
    ValidationResult, CrossValidationConfig
)

__all__ = [
    'ModelTrainer', 'TrainingConfig', 'TrainingResult',
    'ValidationResult', 'CrossValidationConfig'
]
