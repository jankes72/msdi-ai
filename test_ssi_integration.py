#!/usr/bin/env python
# Test integracji SSI V5 Pipeline + AgentRuntimeManager
import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')

from SSI_V5.runtime.start_ssi_test import TestLauncher

if __name__ == "__main__":
    print("=" * 80)
    print("TEST INTEGRACJI SSI V5: Pipeline + AgentRuntimeManager")
    print("=" * 80)
    
    launcher = TestLauncher()
    result = launcher.run()
    
    print(f"\nFinal result status: {result.get('status', 'unknown')}")
    print(f"Summary: {result.get('summary', {}).get('status', 'unknown')}")
    
    sys.exit(0 if result.get('status') == 'success' else 1)
