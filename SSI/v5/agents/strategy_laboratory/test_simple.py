#!/usr/bin/env python3
"""
Prosty test sprawdzający działanie Strategy Laboratory
"""

import sys
import os

# Ustawienie ścieżki
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test podstawowych importów."""
    print("🔍 Testowanie importów...")
    
    try:
        # Test strategy_models
        from strategy_models import (
            Strategy, StrategyParameters, StrategyResult, StrategyEvaluation,
            StrategyRanking, StrategyStatus, StrategyType, StrategyVersion,
            create_strategy, update_strategy_stats
        )
        print("[OK] strategy_models zaladowane")
        
        # Test experiment_models
        from experiment_models import (
            Experiment, ExperimentParameters, ExperimentResult,
            ExperimentComparison, ExperimentStatus, ExperimentType,
            TestMethodology, create_experiment, update_experiment_stats
        )
        print("✅ experiment_models załadowane")
        
        # Test strategy_manager
        from strategy_manager import (
            StrategyManager, StrategyManagerConfig,
            create_strategy_manager, get_strategy_manager
        )
        print("✅ strategy_manager załadowane")
        
        # Test experiment_manager
        from experiment_manager import (
            ExperimentManager, ExperimentManagerConfig,
            create_experiment_manager, get_experiment_manager
        )
        print("✅ experiment_manager załadowane")
        
        # Test strategy_ranking_engine
        from strategy_ranking_engine import (
            StrategyRankingEngine, RankingConfig, RankingWeights,
            RankingCriteria, create_ranking_engine, get_ranking_engine
        )
        print("✅ strategy_ranking_engine załadowane")
        
        # Test strategy_memory
        from strategy_memory import (
            StrategyMemory, StrategyMemoryConfig, AgentStrategyLaboratory,
            create_strategy_memory, get_strategy_memory
        )
        print("✅ strategy_memory załadowane")
        
        # Test memory_integrator
        from memory_integrator import (
            StrategyMemoryIntegrator, MemoryIntegratorConfig,
            create_memory_integrator, get_memory_integrator
        )
        print("✅ memory_integrator załadowane")
        
        # Test ifc_integrator
        from ifc_integrator import (
            StrategyIFCIntegrator, IFCIntegratorConfig,
            create_ifc_integrator, get_ifc_integrator
        )
        print("✅ ifc_integrator załadowane")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd importu: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strategy_creation():
    """Test tworzenia strategii."""
    print("\n🔍 Testowanie tworzenia strategii...")
    
    try:
        from strategy_models import Strategy, StrategyType, StrategyStatus, create_strategy
        
        # Tworzenie strategii
        strategy = create_strategy(
            agent_owner="test_agent_1",
            name="Test Strategy",
            strategy_type=StrategyType.DECISION,
            description="Test description"
        )
        
        assert strategy is not None
        assert strategy.agent_owner == "test_agent_1"
        assert strategy.name == "Test Strategy"
        assert strategy.strategy_type == StrategyType.DECISION
        assert strategy.status == StrategyStatus.DRAFT
        assert len(strategy.strategy_id) > 0
        
        print("✅ Tworzenie strategii działa")
        
        # Serializacja
        strategy_dict = strategy.to_dict()
        restored = Strategy.from_dict(strategy_dict)
        assert restored.strategy_id == strategy.strategy_id
        
        print("✅ Serializacja strategii działa")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd tworzenia strategii: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_experiment_creation():
    """Test tworzenia eksperymentu."""
    print("\n🔍 Testowanie tworzenia eksperymentu...")
    
    try:
        from experiment_models import Experiment, ExperimentType, ExperimentStatus, create_experiment
        
        # Tworzenie eksperymentu
        experiment = create_experiment(
            agent_owner="test_agent_2",
            name="Test Experiment",
            strategy_id="test_strategy_1",
            experiment_type=ExperimentType.A_B_TESTING,
            description="Test A/B experiment"
        )
        
        assert experiment is not None
        assert experiment.agent_owner == "test_agent_2"
        assert experiment.name == "Test Experiment"
        assert experiment.status == ExperimentStatus.PLANNED
        assert len(experiment.experiment_id) > 0
        
        print("✅ Tworzenie eksperymentu działa")
        
        # Serializacja
        exp_dict = experiment.to_dict()
        restored = Experiment.from_dict(exp_dict)
        assert restored.experiment_id == experiment.experiment_id
        
        print("✅ Serializacja eksperymentu działa")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd tworzenia eksperymentu: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strategy_manager():
    """Test Strategy Manager."""
    print("\n🔍 Testowanie Strategy Manager...")
    
    try:
        from strategy_manager import StrategyManager, StrategyManagerConfig
        
        # Utworzenie managera
        manager = StrategyManager(StrategyManagerConfig(
            enable_validation=False,
            max_strategies_per_agent=10
        ))
        
        # Utworzenie strategii
        strategy = manager.create_strategy(
            agent_owner="test_agent_3",
            name="Manager Test Strategy",
            description="Test through manager"
        )
        
        assert strategy is not None
        assert strategy.name == "Manager Test Strategy"
        
        print("✅ Strategy Manager - tworzenie strategii działa")
        
        # Pobranie strategii
        retrieved = manager.get_strategy(strategy.strategy_id)
        assert retrieved is not None
        assert retrieved.strategy_id == strategy.strategy_id
        
        print("✅ Strategy Manager - pobieranie strategii działa")
        
        #Ranking
        rankings = manager.rank_strategies(limit=10)
        assert isinstance(rankings, list)
        
        print("✅ Strategy Manager - ranking działa")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd Strategy Manager: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_experiment_manager():
    """Test Experiment Manager."""
    print("\n🔍 Testowanie Experiment Manager...")
    
    try:
        from experiment_manager import ExperimentManager, ExperimentManagerConfig
        
        # Utworzenie managera
        manager = ExperimentManager(ExperimentManagerConfig(
            enable_validation=False,
            max_experiments_per_agent=10
        ))
        
        # Utworzenie eksperymentu
        experiment = manager.create_experiment(
            agent_owner="test_agent_4",
            name="Manager Test Experiment",
            strategy_id="test_strategy_for_exp"
        )
        
        assert experiment is not None
        assert experiment.name == "Manager Test Experiment"
        
        print("✅ Experiment Manager - tworzenie eksperymentu działa")
        
        # Pobranie eksperymentu
        retrieved = manager.get_experiment(experiment.experiment_id)
        assert retrieved is not None
        assert retrieved.experiment_id == experiment.experiment_id
        
        print("✅ Experiment Manager - pobieranie eksperymentu działa")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd Experiment Manager: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ranking_engine():
    """Test Strategy Ranking Engine."""
    print("\n🔍 Testowanie Ranking Engine...")
    
    try:
        from strategy_ranking_engine import StrategyRankingEngine, RankingConfig
        from strategy_models import Strategy
        
        # Utworzenie engine
        engine = StrategyRankingEngine(RankingConfig())
        
        # Utworzenie strategii testowych
        strategies = []
        for i in range(3):
            strategy = Strategy(
                strategy_id=f"ranking_test_{i}",
                agent_owner="ranking_agent",
                name=f"Ranking Test Strategy {i}",
                success_rate=0.5 + i * 0.1,
                avg_score=0.5 + i * 0.1,
                confidence=0.5 + i * 0.1,
                usage_count=10 + i * 5
            )
            strategies.append(strategy)
        
        # Ranking
        rankings = engine.rank_strategies(
            strategies=strategies,
            filter_active=False,
            filter_min_usage=False,
            limit=3
        )
        
        assert len(rankings) == 3
        assert rankings[0].rank == 1
        
        print("✅ Ranking Engine - ranking strategii działa")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd Ranking Engine: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_integrator():
    """Test Memory Integrator."""
    print("\n🔍 Testowanie Memory Integrator...")
    
    try:
        from memory_integrator import StrategyMemoryIntegrator, MemoryIntegratorConfig
        from strategy_models import Strategy, StrategyType, StrategyResult
        
        # Utworzenie integratora
        integrator = StrategyMemoryIntegrator()
        
        # Utworzenie strategii i wyniku
        strategy = Strategy(
            strategy_id="memory_test_strategy",
            agent_owner="test_agent_5",
            name="Memory Test Strategy",
            strategy_type=StrategyType.DECISION,
            success_rate=0.8,
            confidence=0.9
        )
        
        result = StrategyResult(
            strategy_id=strategy.strategy_id,
            success=True,
            score=0.85,
            confidence=0.9
        )
        
        # Aktualizacja pamięci
        entries = integrator.update_from_strategy_result(strategy, result)
        
        assert len(entries) >= 1
        memory_types = [entry['memory_type'] for entry in entries]
        assert 'behavior_memory' in memory_types
        assert 'decision_layer_memory' in memory_types
        
        print("✅ Memory Integrator - aktualizacja pamięci działa")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd Memory Integrator: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_laboratory():
    """Test Agent Laboratory."""
    print("\n🔍 Testowanie Agent Laboratory...")
    
    try:
        from strategy_memory import AgentStrategyLaboratory
        from strategy_models import Strategy, create_strategy
        from experiment_models import Experiment, create_experiment
        
        # Utworzenie laboratorium agenta
        lab = AgentStrategyLaboratory(agent_id="test_lab_agent")
        
        # Dodanie strategii
        strategy = create_strategy(
            agent_owner="test_lab_agent",
            name="Lab Test Strategy"
        )
        
        strategy_id = lab.add_strategy(strategy)
        assert lab.total_strategies == 1
        
        print("✅ Agent Laboratory - dodawanie strategii działa")
        
        # Dodanie eksperymentu
        experiment = create_experiment(
            agent_owner="test_lab_agent",
            name="Lab Test Experiment",
            strategy_id=strategy_id
        )
        
        exp_id = lab.add_experiment(experiment)
        assert lab.total_experiments == 1
        assert len(lab.evolution_history) >= 1
        
        print("✅ Agent Laboratory - dodawanie eksperymentu działa")
        
        # Serializacja
        lab_dict = lab.to_dict()
        restored_lab = AgentStrategyLaboratory.from_dict(lab_dict)
        assert restored_lab.agent_id == lab.agent_id
        assert len(restored_lab.strategies) == 1
        assert len(restored_lab.experiments) == 1
        
        print("✅ Agent Laboratory - serializacja działa")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd Agent Laboratory: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ifc_integrator():
    """Test IFC Integrator."""
    print("\n🔍 Testowanie IFC Integrator...")
    
    try:
        from ifc_integrator import StrategyIFCIntegrator, IFCIntegratorConfig
        from strategy_models import StrategyType
        from SSI.v5.core.information_flow_controller.message_models import ProcessType
        
        # Utworzenie integratora (bez IFC)
        config = IFCIntegratorConfig(use_ifc=False)
        integrator = StrategyIFCIntegrator(config)
        
        # Tworzenie wiadomości
        message = integrator.create_strategy_message(
            agent_id="test_agent_ifc",
            strategy_data={
                'name': 'IFC Test Strategy',
                'strategy_type': 'DECISION'
            }
        )
        
        assert message is not None
        assert message.sender == 'strategy_laboratory'
        assert message.process_type == ProcessType.STRATEGY_CREATE
        
        print("✅ IFC Integrator - tworzenie wiadomości działa")
        
        # Wysłanie wiadomości (symulacja)
        response = integrator.send_message(message)
        assert response is not None
        assert response.status.name == 'PROCESSED'
        
        print("✅ IFC Integrator - wysyłanie wiadomości działa")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd IFC Integrator: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Uruchomienie wszystkich testów."""
    print("="*60)
    print("SSI V5 - STRATEGY LABORATORY - PROSTY TEST")
    print("="*60)
    
    tests = [
        ("Importy modułów", test_basic_imports),
        ("Tworzenie strategii", test_strategy_creation),
        ("Tworzenie eksperymentu", test_experiment_creation),
        ("Strategy Manager", test_strategy_manager),
        ("Experiment Manager", test_experiment_manager),
        ("Ranking Engine", test_ranking_engine),
        ("Memory Integrator", test_memory_integrator),
        ("Agent Laboratory", test_agent_laboratory),
        ("IFC Integrator", test_ifc_integrator),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    # Podsumowanie
    print("\n" + "="*60)
    print("PODSUMOWANIE")
    print("="*60)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, error in results:
        status = "✅ ZALICZONY" if result else "❌ NIE ZALICZONY"
        print(f"{status:20} {test_name}")
        if error:
            print(f"        Błąd: {error}")
    
    print(f"\nWynik: {passed}/{total} testów zaliczonych")
    
    if passed == total:
        print("\n🎉 Wszystkie testy ZALICZONE!")
        print("✅ Strategy Laboratory jest gotowy!")
        return True
    else:
        print("\n⚠️  Niektóre testy nie zaliczone")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
