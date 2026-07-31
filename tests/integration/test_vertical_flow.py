"""
SSI Integration Tests - Vertical Flow V2->V3->V4

Tests for vertical flow integration and contract validation.

Converted from unittest to pytest for Sprint 8 compliance.
"""

import sys
from pathlib import Path
import pytest

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from SSI.workflows import (
    VerticalFlow,
    VerticalFlowConfig,
    FlowResult,
    LineageTracker,
    run_smoke_test,
)
from SSI.contracts import (
    V2ToV3Contract,
    V3ToV4Contract,
    DataVersion,
    ModelVersion,
    ConfigVersion,
    ResultVersion,
    LineageInfo,
    ContractVersion,
)


# ============================================================================
# Vertical Flow Config Tests
# ============================================================================

class TestVerticalFlowConfig:
    """Tests for vertical flow configuration."""
    
    def test_default_config_creation(self):
        """Test default configuration can be created."""
        config = VerticalFlowConfig()
        assert config is not None
        assert hasattr(config, 'enable_lineage')
    
    def test_custom_config_values(self):
        """Test custom configuration values are set correctly."""
        config = VerticalFlowConfig(enable_lineage=True, timeout_seconds=30)
        assert config.enable_lineage is True
        assert config.timeout_seconds == 30


# ============================================================================
# Vertical Flow Execution Tests
# ============================================================================

class TestVerticalFlowExecution:
    """Tests for vertical flow execution."""
    
    def test_flow_creation(self):
        """Test vertical flow can be created."""
        config = VerticalFlowConfig()
        flow = VerticalFlow(config)
        assert flow is not None
    
    def test_result_creation(self):
        """Test FlowResult can be created."""
        result = FlowResult()
        assert result is not None
    
    def test_lineage_tracker_creation(self):
        """Test LineageTracker can be created."""
        tracker = LineageTracker()
        assert tracker is not None


# ============================================================================
# Smoke Test Execution
# ============================================================================

class TestSmokeTestExecution:
    """Tests for smoke test execution."""
    
    def test_basic_smoke_test(self):
        """Test basic smoke test execution."""
        result = run_smoke_test()
        assert result is not None
        assert isinstance(result, FlowResult)
    
    def test_smoke_test_with_lineage_config(self):
        """Test smoke test with lineage tracking enabled."""
        config = VerticalFlowConfig(enable_lineage=True)
        result = run_smoke_test(config=config)
        assert result is not None
        assert isinstance(result, FlowResult)
    
    def test_smoke_test_completes_successfully(self):
        """Test that smoke test completes without errors."""
        # If we reach here without exception, test passes
        result = run_smoke_test()
        assert True


# ============================================================================
# Contract Validation Tests
# ============================================================================

class TestContractValidation:
    """Tests for contract validation in vertical flow."""
    
    def test_contract_versions_available(self):
        """Test that all contract versions are available."""
        assert isinstance(DataVersion("1.0"), DataVersion)
        assert isinstance(ModelVersion("1.0"), ModelVersion)
        assert isinstance(ConfigVersion("1.0"), ConfigVersion)
        assert isinstance(ResultVersion("1.0"), ResultVersion)
    
    def test_v2_to_v3_contract_available(self):
        """Test V2ToV3Contract is available."""
        assert V2ToV3Contract is not None
    
    def test_v3_to_v4_contract_available(self):
        """Test V3ToV4Contract is available."""
        assert V3ToV4Contract is not None
    
    def test_lineage_info_creation(self):
        """Test LineageInfo can be created."""
        info = LineageInfo(
            contract_version=ContractVersion("1.0"),
            data_version=DataVersion("1.0"),
        )
        assert info is not None
    
    def test_contract_version_creation(self):
        """Test ContractVersion can be created."""
        version = ContractVersion("1.0.0")
        assert version is not None