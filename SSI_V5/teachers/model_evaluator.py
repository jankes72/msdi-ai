# SSI V5 Teacher Layer - Model Evaluator
# ==================================================
#
# Odpowiedzialny za ocenę modeli, porównywanie wyników i analizę skuteczności.
#
# Odpowiedzialność:
# - ocena modeli
# - porównywanie wyników
# - analiza skuteczności
# - generowanie raportów
#
# Data: 2026-08-03
# ETAP: 5.2.4 FAZA 3.2
#
# Zasada: Nowa warstwa dodatkowa, nie zmieniamy istniejącej logiki

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


class ModelEvaluator:
    """
    Odpowiedzialny za ocenę modeli i analizę skuteczności w systemie SSI V5.
    
    Funkcjonalności:
    - Ocena pojedynczych modeli
    - Porównywanie wielu modeli
    - Analiza skuteczności w czasie
    - Generowanie raportów porównawczych
    - Integracja z CognitiveTeacher
    
    Współpracuje z:
    - CognitiveTeacher
    - MemoryManager
    - DynamicWeightsManager
    """
    
    def __init__(self, evaluation_dir: str = None, network_name: str = "default"):
        """
        Inicjalizacja ModelEvaluator.
        
        Args:
            evaluation_dir: Katalog do zapisywania ocen (domyślnie używa config)
            network_name: Nazwa sieci/modelu
        """
        if evaluation_dir is None:
            from ..core.config import PathConfig
            evaluation_dir = PathConfig.MODELE_DATA_BASE_DIR
        
        self.evaluation_dir = evaluation_dir
        self.network_name = network_name
        self.network_evaluation_dir = os.path.join(evaluation_dir, f"evaluation_{network_name}")
        
        # Tworzymy katalog ocen
        os.makedirs(self.network_evaluation_dir, exist_ok=True)
        
        # Ścieżki plików
        self.evaluation_log_path = os.path.join(self.network_evaluation_dir, "evaluation_log.json")
        self.comparison_reports_path = os.path.join(self.network_evaluation_dir, "comparison_reports.json")
        self.performance_metrics_path = os.path.join(self.network_evaluation_dir, "performance_metrics.json")
        
        # Historia ocen
        self.evaluation_log = self._load_evaluation_log()
        self.comparison_reports = self._load_comparison_reports()
        self.performance_metrics = self._load_performance_metrics()
    
    def _load_evaluation_log(self) -> List[Dict[str, Any]]:
        """Wczytaj log ocen"""
        if os.path.exists(self.evaluation_log_path):
            try:
                with open(self.evaluation_log_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _load_comparison_reports(self) -> List[Dict[str, Any]]:
        """Wczytaj raporty porównawcze"""
        if os.path.exists(self.comparison_reports_path):
            try:
                with open(self.comparison_reports_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _load_performance_metrics(self) -> Dict[str, Any]:
        """Wczytaj metryki wydajności"""
        if os.path.exists(self.performance_metrics_path):
            try:
                with open(self.performance_metrics_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_data(self, data: Any, file_path: str) -> bool:
        """Zapisz dane do pliku JSON"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[EVALUATOR] Error saving {file_path}: {e}")
            return False
    
    def _save_all(self) -> bool:
        """Zapisz wszystkie dane"""
        success = True
        success &= self._save_data(self.evaluation_log, self.evaluation_log_path)
        success &= self._save_data(self.comparison_reports, self.comparison_reports_path)
        success &= self._save_data(self.performance_metrics, self.performance_metrics_path)
        return success
    
    # ========================================================================
    # OCENA POJEDYNCZEGO MODELU
    # ========================================================================
    
    def evaluate_model(self, model_name: str, y_true: Any, y_pred: Any,
                      additional_metrics: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Oceń pojedynczy model.
        
        Args:
            model_name: Nazwa modelu
            y_true: Rzeczywiste etykiety
            y_pred: Przewidywane etykiety
            additional_metrics: Dodatkowe metryki (opcjonalne)
            
        Returns:
            Dict: Wyniki oceny
        """
        # Konwersja do numpy array jeśli potrzebne
        if not isinstance(y_true, np.ndarray):
            y_true = np.array(y_true)
        if not isinstance(y_pred, np.ndarray):
            y_pred = np.array(y_pred)
        
        # Podstawowe metryki
        evaluation = {
            "model_name": model_name,
            "network_name": self.network_name,
            "timestamp": datetime.now().isoformat(),
            "samples_count": len(y_true),
            "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
            "f1_score": round(float(f1_score(y_true, y_pred, average='weighted', zero_division=0)), 4),
            "precision": round(float(precision_score(y_true, y_pred, average='weighted', zero_division=0)), 4),
            "recall": round(float(recall_score(y_true, y_pred, average='weighted', zero_division=0)), 4),
            "error_rate": round(float(1.0 - accuracy_score(y_true, y_pred)), 4)
        }
        
        # Dodaj dodatkowe metryki
        if additional_metrics:
            evaluation["additional_metrics"] = {}
            for metric_name, value in additional_metrics.items():
                evaluation["additional_metrics"][metric_name] = round(float(value), 4)
        
        # Dodaj do logu ocen
        self.evaluation_log.append(evaluation)
        
        # Zapisz metryki wydajności
        if model_name not in self.performance_metrics:
            self.performance_metrics[model_name] = {"history": [], "best": {}}
        
        self.performance_metrics[model_name]["history"].append({
            "timestamp": evaluation["timestamp"],
            "accuracy": evaluation["accuracy"],
            "f1_score": evaluation["f1_score"],
            "precision": evaluation["precision"],
            "recall": evaluation["recall"]
        })
        
        # Aktualizuj najlepsze wyniki
        self._update_best_metrics(model_name, evaluation)
        
        # Zapisz dane
        self._save_all()
        
        return evaluation
    
    def _update_best_metrics(self, model_name: str, evaluation: Dict[str, Any]) -> None:
        """Zaktualizuj najlepsze metryki dla modelu"""
        if model_name not in self.performance_metrics:
            self.performance_metrics[model_name] = {"history": [], "best": {}}
        
        best = self.performance_metrics[model_name]["best"]
        
        if "best" not in best or evaluation["accuracy"] > best.get("accuracy", 0):
            best["accuracy"] = evaluation["accuracy"]
            best["f1_score"] = evaluation["f1_score"]
            best["precision"] = evaluation["precision"]
            best["recall"] = evaluation["recall"]
            best["timestamp"] = evaluation["timestamp"]
            best["samples_count"] = evaluation["samples_count"]
    
    def get_model_performance(self, model_name: str) -> Dict[str, Any]:
        """
        Pobierz wydajność modelu.
        
        Args:
            model_name: Nazwa modelu
            
        Returns:
            Dict: Wydajność modelu
        """
        return self.performance_metrics.get(model_name, {"history": [], "best": {}})
    
    def get_best_model_performance(self, model_name: str) -> Dict[str, Any]:
        """
        Pobierz najlepsze wyniki modelu.
        
        Args:
            model_name: Nazwa modelu
            
        Returns:
            Dict: Najlepsze metryki
        """
        return self.performance_metrics.get(model_name, {}).get("best", {})
    
    # ========================================================================
    # PORÓWNYWANIE MODELI
    # ========================================================================
    
    def compare_models(self, model_names: List[str], 
                      metric: str = "accuracy") -> Dict[str, Any]:
        """
        Porównaj wiele modeli.
        
        Args:
            model_names: Lista nazw modeli do porównania
            metric: Metryka do porównania (accuracy, f1_score, precision, recall)
            
        Returns:
            Dict: Wyniki porównania
        """
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "network_name": self.network_name,
            "metric": metric,
            "models": []
        }
        
        for model_name in model_names:
            if model_name in self.performance_metrics:
                best = self.performance_metrics[model_name].get("best", {})
                model_result = {
                    "model_name": model_name,
                    "value": best.get(metric, 0),
                    "accuracy": best.get("accuracy", 0),
                    "f1_score": best.get("f1_score", 0),
                    "precision": best.get("precision", 0),
                    "recall": best.get("recall", 0),
                    "samples_count": best.get("samples_count", 0),
                    "timestamp": best.get("timestamp", "")
                }
                comparison["models"].append(model_result)
        
        # Sortuj po wartości metryki
        comparison["models"].sort(key=lambda x: x["value"], reverse=True)
        
        # Dodaj podsumowanie
        if comparison["models"]:
            comparison["best_model"] = comparison["models"][0]["model_name"]
            comparison["best_value"] = comparison["models"][0]["value"]
            comparison["worst_model"] = comparison["models"][-1]["model_name"]
            comparison["worst_value"] = comparison["models"][-1]["value"]
            comparison["average_value"] = round(
                np.mean([m["value"] for m in comparison["models"]]), 4
            )
        
        # Zapisz raport
        self.comparison_reports.append(comparison)
        self._save_all()
        
        return comparison
    
    def get_comparison_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Pobierz historię porównań.
        
        Args:
            limit: Maksymalna liczba raportów
            
        Returns:
            List: Historia porównań
        """
        if limit is None:
            return self.comparison_reports
        return self.comparison_reports[-limit:]
    
    # ========================================================================
    # ANALIZA SKUTEczNOŚCI W CZASIE
    # ========================================================================
    
    def analyze_performance_trend(self, model_name: str, 
                                 metric: str = "accuracy") -> Dict[str, Any]:
        """
        Analizuj trend wydajności modelu w czasie.
        
        Args:
            model_name: Nazwa modelu
            metric: Metryka do analizy
            
        Returns:
            Dict: Analiza trendu
        """
        if model_name not in self.performance_metrics:
            return {"error": "Model not found"}
        
        history = self.performance_metrics[model_name].get("history", [])
        
        if not history:
            return {"error": "No history available"}
        
        # Wyodrębnij wartości metryki
        values = [h.get(metric, 0) for h in history]
        timestamps = [h.get("timestamp", "") for h in history]
        
        analysis = {
            "model_name": model_name,
            "metric": metric,
            "history_count": len(history),
            "current_value": values[-1] if values else 0,
            "min_value": round(float(np.min(values)), 4),
            "max_value": round(float(np.max(values)), 4),
            "mean_value": round(float(np.mean(values)), 4),
            "std_value": round(float(np.std(values)), 4),
            "improvement": round(float(values[-1] - values[0]), 4) if len(values) > 1 else 0,
            "trend": "improving" if len(values) > 1 and values[-1] > values[0] else "declining"
        }
        
        # Dodaj analize stabilności
        if len(values) > 1:
            recent_values = values[-5:] if len(values) >= 5 else values
            analysis["recent_stability"] = round(float(np.std(recent_values)), 4)
        
        return analysis
    
    def detect_performance_anomalies(self, threshold_std: float = 2.0) -> Dict[str, Any]:
        """
        Wykryj anomalie w wydajności modeli.
        
        Args:
            threshold_std: Próg odchylenia standardowego (wielokrotność)
            
        Returns:
            Dict: Wykryte anomalie
        """
        anomalies = {
            "timestamp": datetime.now().isoformat(),
            "network_name": self.network_name,
            "threshold_std": threshold_std,
            "anomalies": []
        }
        
        for model_name, data in self.performance_metrics.items():
            history = data.get("history", [])
            
            if len(history) < 3:  # Potrzebujemy co najmniej 3 pomiarów
                continue
            
            # Oblicz statystyki
            metric_values = [h.get("accuracy", 0) for h in history]
            mean_val = np.mean(metric_values)
            std_val = np.std(metric_values)
            
            # Sprawdź ostatnią wartość
            last_value = metric_values[-1]
            deviation = abs(last_value - mean_val) / std_val if std_val > 0 else 0
            
            if deviation > threshold_std:
                anomaly = {
                    "model_name": model_name,
                    "current_value": last_value,
                    "mean_value": round(float(mean_val), 4),
                    "std_value": round(float(std_val), 4),
                    "deviation": round(float(deviation), 4),
                    "timestamp": history[-1].get("timestamp", ""),
                    "type": "positive" if last_value > mean_val else "negative"
                }
                anomalies["anomalies"].append(anomaly)
        
        return anomalies
    
    # ========================================================================
    # GENEROWANIE RAPORTÓW
    # ========================================================================
    
    def generate_performance_report(self, model_names: List[str] = None) -> Dict[str, Any]:
        """
        Wygeneruj raport wydajności.
        
        Args:
            model_names: Lista modeli do uwzględnienia (None = wszystkie)
            
        Returns:
            Dict: Raport wydajności
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "network_name": self.network_name,
            "models": {},
            "summary": {}
        }
        
        models_to_include = model_names or list(self.performance_metrics.keys())
        
        for model_name in models_to_include:
            if model_name in self.performance_metrics:
                data = self.performance_metrics[model_name]
                report["models"][model_name] = {
                    "best": data.get("best", {}),
                    "history_count": len(data.get("history", []))
                }
        
        # Podsumowanie
        if report["models"]:
            all_accuracies = []
            for model_data in report["models"].values():
                best = model_data.get("best", {})
                if best.get("accuracy", 0) > 0:
                    all_accuracies.append(best["accuracy"])
            
            if all_accuracies:
                report["summary"] = {
                    "total_models": len(report["models"]),
                    "best_accuracy": round(float(np.max(all_accuracies)), 4),
                    "worst_accuracy": round(float(np.min(all_accuracies)), 4),
                    "average_accuracy": round(float(np.mean(all_accuracies)), 4),
                    "median_accuracy": round(float(np.median(all_accuracies)), 4)
                }
        
        return report
    
    def generate_comparison_summary(self, comparison_result: Dict[str, Any]) -> str:
        """
        Wygeneruj podsumowanie porównania w formie tekstowej.
        
        Args:
            comparison_result: Wynik porównania z compare_models()
            
        Returns:
            str: Tekstowe podsumowanie
        """
        lines = []
        lines.append("=" * 60)
        lines.append("RAPORT PORÓWNANIA MODELI")
        lines.append("=" * 60)
        lines.append(f"Sieć: {comparison_result.get('network_name', '')}")
        lines.append(f"Data: {comparison_result.get('timestamp', '')}")
        lines.append(f"Metryka: {comparison_result.get('metric', '')}")
        lines.append("")
        lines.append("Ranking modeli:")
        lines.append("-" * 40)
        
        for i, model in enumerate(comparison_result.get("models", []), 1):
            lines.append(f"{i}. {model.get('model_name', '')}: {model.get('value', 0):.4f}")
        
        lines.append("")
        lines.append("Podsumowanie:")
        lines.append("-" * 40)
        lines.append(f"Najlepszy model: {comparison_result.get('best_model', 'N/A')}")
        lines.append(f"Najlepsza wartosc: {comparison_result.get('best_value', 0):.4f}")
        lines.append(f"Srednia wartosc: {comparison_result.get('average_value', 0):.4f}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    # ========================================================================
    # INTEGRACJA Z COGNITIVE TEACHER
    # ========================================================================
    
    def evaluate_teacher_performance(self, cognitive_teacher_result: Dict[str, Any],
                                    expected_ranking: List[str] = None) -> Dict[str, Any]:
        """
        Oceń wydajność CognitiveTeacher.
        
        Args:
            cognitive_teacher_result: Wynik z CognitiveTeacher.uruchom_analyse()
            expected_ranking: Oczekiwany ranking cech (opcjonalny)
            
        Returns:
            Dict: Ocena wydajności teachera
        """
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "network_name": self.network_name,
            "teacher_analysis": {
                "ranking_quality": 0.0,
                "correlation_strength": 0.0,
                "rule_quality": 0.0
            }
        }
        
        # Oceń ranking cech
        ranking = cognitive_teacher_result.get("ranking", [])
        if ranking and len(ranking) > 0:
            # Oblicz średnią siłę cech
            avg_strength = np.mean([r.get("sila", 0) for r in ranking])
            evaluation["teacher_analysis"]["ranking_quality"] = round(float(avg_strength), 4)
        
        # Oceń korelacje
        korelacje = cognitive_teacher_result.get("swiat", {}).get("statystyki_globalne", {})
        if korelacje:
            evaluation["teacher_analysis"]["correlation_strength"] = round(
                float(korelacje.get("korelacje_stabilnosc", 0)), 4
            )
        
        # Oceń reguły
        rules = cognitive_teacher_result.get("reguly", [])
        if rules and len(rules) > 0:
            avg_certainty = np.mean([r.get("pewnosc", 0) for r in rules])
            evaluation["teacher_analysis"]["rule_quality"] = round(float(avg_certainty), 4)
        
        # Dodaj do logu
        self.evaluation_log.append(evaluation)
        self._save_all()
        
        return evaluation
    
    def compare_teacher_performance(self, teacher_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Porównaj wydajność wielu teacherów.
        
        Args:
            teacher_results: Lista wyników teachera
            
        Returns:
            Dict: Porównanie wydajności
        """
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "network_name": self.network_name,
            "teachers": [],
            "summary": {}
        }
        
        for i, result in enumerate(teacher_results, 1):
            teacher_eval = self.evaluate_teacher_performance(result)
            comparison["teachers"].append({
                "teacher_id": f"teacher_{i}",
                "ranking_quality": teacher_eval["teacher_analysis"]["ranking_quality"],
                "correlation_strength": teacher_eval["teacher_analysis"]["correlation_strength"],
                "rule_quality": teacher_eval["teacher_analysis"]["rule_quality"],
                "overall_score": round(float(np.mean([
                    teacher_eval["teacher_analysis"]["ranking_quality"],
                    teacher_eval["teacher_analysis"]["correlation_strength"],
                    teacher_eval["teacher_analysis"]["rule_quality"]
                ])), 4)
            })
        
        # Sortuj po ogólnym wyniku
        comparison["teachers"].sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Podsumowanie
        if comparison["teachers"]:
            scores = [t["overall_score"] for t in comparison["teachers"]]
            comparison["summary"] = {
                "best_teacher": comparison["teachers"][0]["teacher_id"],
                "best_score": comparison["teachers"][0]["overall_score"],
                "average_score": round(float(np.mean(scores)), 4)
            }
        
        return comparison
    
    # ========================================================================
    # OPERACJE GLOBALNE
    # ========================================================================
    
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """Pobierz statystyki ocen"""
        return {
            "total_evaluations": len(self.evaluation_log),
            "total_comparisons": len(self.comparison_reports),
            "tracked_models": len(self.performance_metrics),
            "last_evaluation": self.evaluation_log[-1]["timestamp"] if self.evaluation_log else None,
            "last_comparison": self.comparison_reports[-1]["timestamp"] if self.comparison_reports else None
        }
    
    def clear_all_data(self) -> bool:
        """Wyczyść wszystkie dane"""
        self.evaluation_log = []
        self.comparison_reports = []
        self.performance_metrics = {}
        
        for path in [self.evaluation_log_path, self.comparison_reports_path, 
                    self.performance_metrics_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
        
        return True
    
    def integrate_with_memory_manager(self, memory_manager) -> None:
        """
        Zintegruj z MemoryManager.
        
        Args:
            memory_manager: Instancja MemoryManager
        """
        # Zapisz wyniki ocen w pamięci
        if memory_manager:
            evaluation_data = {
                "evaluation_log": self.evaluation_log,
                "comparison_reports": self.comparison_reports,
                "performance_metrics": self.performance_metrics,
                "statistics": self.get_evaluation_statistics()
            }
            memory_manager.save_world_memory(
                evaluation_data,
                f"evaluator_{self.network_name}"
            )


# ============================================================================
# TESTY MODUŁU
# ============================================================================

def test_model_evaluator():
    """Test podstawowych funkcjonalności ModelEvaluator"""
    print("\n" + "="*60)
    print("TEST: ModelEvaluator")
    print("="*60)
    
    try:
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test inicjalizacji
            evaluator = ModelEvaluator(evaluation_dir=temp_dir, network_name="test")
            assert hasattr(evaluator, 'evaluation_log')
            assert hasattr(evaluator, 'comparison_reports')
            assert hasattr(evaluator, 'performance_metrics')
            print("[OK] Test inicjalizacji - zaliczony")
            
            # Test oceny modelu
            y_true = [0, 1, 1, 0, 1]
            y_pred = [0, 1, 0, 0, 1]
            result = evaluator.evaluate_model("test_model", y_true, y_pred)
            assert result["accuracy"] > 0
            assert result["model_name"] == "test_model"
            print("[OK] Test evaluate_model - zaliczony")
            
            # Test porównania modeli
            evaluator.evaluate_model("model_1", y_true, y_pred)
            evaluator.evaluate_model("model_2", y_true, [0, 1, 1, 0, 0])
            comparison = evaluator.compare_models(["model_1", "model_2"], "accuracy")
            assert "models" in comparison
            assert len(comparison["models"]) == 2
            print("[OK] Test compare_models - zaliczony")
            
            # Test analizy trendu
            trend = evaluator.analyze_performance_trend("test_model")
            assert "model_name" in trend
            print("[OK] Test analyze_performance_trend - zaliczony")
            
            # Test generowania raportu
            report = evaluator.generate_performance_report(["test_model"])
            assert "models" in report
            assert "summary" in report
            print("[OK] Test generate_performance_report - zaliczony")
            
            # Test statystyk
            stats = evaluator.get_evaluation_statistics()
            assert "total_evaluations" in stats
            print("[OK] Test get_evaluation_statistics - zaliczony")
            
            return True
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"[FAIL] Test ModelEvaluator - error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test przypadków brzegowych"""
    print("\n" + "="*60)
    print("TEST: ModelEvaluator edge cases")
    print("="*60)
    
    try:
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            evaluator = ModelEvaluator(evaluation_dir=temp_dir)
            
            # Test z pustymi danymi
            report = evaluator.generate_performance_report()
            assert "models" in report
            print("[OK] Test empty report - zaliczony")
            
            # Test porównania z nieistniejącym modelem
            comparison = evaluator.compare_models(["nonexistent_model"])
            assert comparison["models"] == []
            print("[OK] Test compare nonexistent model - zaliczony")
            
            # Test czyszczenia danych
            evaluator.evaluate_model("temp_model", [1, 2, 3], [1, 2, 3])
            evaluator.clear_all_data()
            assert len(evaluator.evaluation_log) == 0
            print("[OK] Test clear_all_data - zaliczony")
            
            return True
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"[FAIL] Test ModelEvaluator edge cases - error: {e}")
        return False


if __name__ == "__main__":
    test_model_evaluator()
    test_edge_cases()
    print("\nModelEvaluator - Testy wykonane")