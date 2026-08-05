import json

from SSI_AI_MODELS.SSI_SELF_DEVELOPMENT_ENGINE.INTERNAL_ORCHESTRATOR import state_manager


def test_state_manager_uses_plan_format(tmp_path, monkeypatch):
    state_dir = tmp_path / "INTERNAL_CONTEXT"
    state_file = state_dir / "ai_team_state.json"

    monkeypatch.setattr(state_manager, "BASE_PATH", str(state_dir))
    monkeypatch.setattr(state_manager, "STATE_FILE", str(state_file))

    state = state_manager.load_state()

    assert state["system_status"] == "IDLE"
    assert state["current_task"] is None
    assert state["active_agent"] is None
    assert state["workflow_stage"] is None

    state_manager.update_agent(
        agent="LANGUAGE_ARCHITECT",
        task="Test pamięci",
        result="Architekt zakończył analizę",
        workflow_stage="ETAP_1_CORE_FOUNDATION",
    )

    saved = json.loads(state_file.read_text(encoding="utf-8"))
    assert saved["active_agent"] == "LANGUAGE_ARCHITECT"
    assert saved["current_task"] == "Test pamięci"
    assert saved["workflow_stage"] == "ETAP_1_CORE_FOUNDATION"
    assert saved["system_status"] == "BUSY"
