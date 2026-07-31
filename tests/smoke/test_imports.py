"""
SSI Smoke Tests - Import and Initialization Tests

Check if:
1. All SSI modules import correctly
2. Dependencies (V2, V3, V4) are available
3. Initialization does not cause errors
4. All classes and functions are available

Acceptance Criteria (Sprint 8):
- compileall, import smoke, lint, type check and pip check pass
- Tests must be deterministic and network-independent

Converted from unittest to pytest for Sprint 8 compliance.
"""

import sys
import os
import importlib
import pytest
from pathlib import Path

# Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# SSI Module Imports Tests
# ============================================================================

class TestSSIModuleImports:
    """Import tests for main SSI modules."""
    
    def test_import_ssi_core(self):
        """Test SSI.core import."""
        try:
            from SSI.core import system, logging_config
            assert system is not None
            assert logging_config is not None
        except ImportError as e:
            assert False, f"Import SSI.core failed: {e}"
    
    def test_import_ssi_contracts(self):
        """Test SSI.contracts import."""
        try:
            from SSI.contracts import (
                V2ToV3Contract,
                V3ToV4Contract,
                DataVersion,
                ModelVersion,
                ResultVersion,
                ConfigVersion,
                LineageInfo,
                ContractValidationError,
            )
        except ImportError as e:
            assert False, f"Import SSI.contracts failed: {e}"
    
    def test_import_ssi_data(self):
        """Test SSI.data import."""
        try:
            from SSI.data import data_manager, policies
            assert data_manager is not None
            assert policies is not None
        except ImportError as e:
            assert False, f"Import SSI.data failed: {e}"
    
    def test_import_ssi_v2(self):
        """Test SSI.v2 import (V2 Model Laboratory)."""
        try:
            from SSI.v2 import (
                V2Integration,
                tworz_integracje_v2,
                ModelOutputAggregator,
                V2ToV3Bridge,
            )
        except ImportError as e:
            assert False, f"Import SSI.v2 failed: {e}"
    
    def test_import_ssi_v3(self):
        """Test SSI.v3 import (V3 World Knowledge Engine)."""
        try:
            from SSI.v3 import (
                V3Integration,
                tworz_v3_integration,
                MemoryManager,
                WorldManager,
            )
        except ImportError as e:
            assert False, f"Import SSI.v3 failed: {e}"
    
    def test_import_ssi_v4(self):
        """Test SSI.v4 import (V4 Autonomous Agent Ecosystem)."""
        try:
            from SSI.v4 import (
                Agent,
                AgentBirthSystem,
                RoomCore,
                tworz_agent,
                tworz_agent_birth_system,
                tworz_room_core,
                tworz_personality_vector,
            )
        except ImportError as e:
            assert False, f"Import SSI.v4 failed: {e}"
    
    def test_import_ssi_workflows(self):
        """Test SSI.workflows import."""
        try:
            from SSI.workflows import (
                VerticalFlow,
                VerticalFlowConfig,
                FlowResult,
                LineageTracker,
                run_smoke_test,
            )
        except ImportError as e:
            assert False, f"Import SSI.workflows failed: {e}"


# ============================================================================
# SSI Initialization Tests
# ============================================================================

class TestSSIInitialization:
    """SSI system initialization tests."""
    
    def test_health_check_initialization(self):
        """Test HealthCheck initialization."""
        from SSI.core.logging_config import health_check
        assert health_check is not None
        status = health_check.get_status()
        assert "ready" in status
        assert "dependencies" in status
        assert "modules" in status
    
    def test_metrics_collector_initialization(self):
        """Test MetricsCollector initialization."""
        from SSI.core.logging_config import metrics_collector
        assert metrics_collector is not None
        metrics = metrics_collector.get_metrics()
        assert "decisions" in metrics
        assert "performance" in metrics
        assert "resources" in metrics
    
    def test_logging_config_initialization(self):
        """Test LoggingConfigurator initialization."""
        from SSI.core.logging_config import LoggingConfigurator, get_logger
        # Logging should be configured on import
        logger = get_logger(__name__)
        assert logger is not None
    
    def test_correlation_id_generation(self):
        """Test correlation_id generator."""
        from SSI.core.logging_config import generate_correlation_id, set_correlation_id
        cid = generate_correlation_id()
        assert cid is not None
        assert isinstance(cid, str)
        assert len(cid) > 0


# ============================================================================
# V2 V3 V4 Dependencies Tests
# ============================================================================

class TestV2V3V4Dependencies:
    """Dependency tests between V2, V3, V4."""
    
    def test_v2_integration_available(self):
        """Test if V2Integration is available and can be created."""
        from SSI.v2 import V2Integration
        # Check if class exists
        assert hasattr(V2Integration, '__init__')
    
    def test_v3_integration_available(self):
        """Test if V3Integration is available and can be created."""
        from SSI.v3 import V3Integration
        assert hasattr(V3Integration, '__init__')
    
    def test_v4_agent_available(self):
        """Test if Agent is available and can be created."""
        from SSI.v4.agent_core import Agent, AgentConfig, AgentType
        config = AgentConfig(
            agent_id="test_agent",
            agent_type=AgentType.ANALYST,
        )
        agent = Agent(config)
        assert agent is not None


# ============================================================================
# Entry Points Tests
# ============================================================================

class TestEntryPoints:
    """Entry points tests."""
    
    def test_main_module_import(self):
        """Test if main SSI module is importable."""
        try:
            import SSI
            assert SSI is not None
        except ImportError as e:
            assert False, f"Import SSI failed: {e}"
    
    def test_ssi_init_import(self):
        """Test if SSI.__init__.py works correctly."""
        try:
            from SSI import setup_logging, get_logger
            assert setup_logging is not None
            assert get_logger is not None
        except ImportError as e:
            assert False, f"Import from SSI.__init__ failed: {e}"


# ============================================================================
# Compile All Tests
# ============================================================================

class TestCompileAll:
    """Compile all modules tests (compileall)."""
    
    def test_compile_ssi_core(self):
        """Test if SSI.core compiles correctly."""
        import py_compile
        core_path = PROJECT_ROOT / "SSI" / "core"
        for py_file in core_path.glob("*.py"):
            py_compile.compile(str(py_file), doraise=True)
    
    def test_compile_ssi_v2(self):
        """Test if SSI.v2 compiles correctly."""
        import py_compile
        v2_path = PROJECT_ROOT / "SSI" / "v2"
        for py_file in v2_path.rglob("*.py"):
            py_compile.compile(str(py_file), doraise=True)
    
    def test_compile_ssi_v3(self):
        """Test if SSI.v3 compiles correctly."""
        import py_compile
        v3_path = PROJECT_ROOT / "SSI" / "v3"
        for py_file in v3_path.rglob("*.py"):
            py_compile.compile(str(py_file), doraise=True)
    
    def test_compile_ssi_v4(self):
        """Test if SSI.v4 compiles correctly."""
        import py_compile
        v4_path = PROJECT_ROOT / "SSI" / "v4"
        for py_file in v4_path.rglob("*.py"):
            py_compile.compile(str(py_file), doraise=True)