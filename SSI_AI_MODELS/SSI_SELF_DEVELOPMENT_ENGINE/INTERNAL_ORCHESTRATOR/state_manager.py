import json
import os
from datetime import datetime


BASE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "INTERNAL_CONTEXT"
)

STATE_FILE = os.path.join(
    BASE_PATH,
    "ai_team_state.json"
)

DEFAULT_STATE = {
    "system_status": "IDLE",
    "current_task": None,
    "active_agent": None,
    "workflow_stage": None,
}


def ensure_memory():
    os.makedirs(BASE_PATH, exist_ok=True)

    if not os.path.exists(STATE_FILE):
        save_state(DEFAULT_STATE.copy())


def save_state(data):
    os.makedirs(BASE_PATH, exist_ok=True)

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    return data


def load_state():
    ensure_memory()

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    normalized = DEFAULT_STATE.copy()
    normalized.update(data)
    return normalized


def update_agent(agent, task, result=None, workflow_stage=None, system_status="BUSY"):
    state = load_state()

    state["active_agent"] = agent
    state["current_task"] = task
    state["system_status"] = system_status

    if workflow_stage is not None:
        state["workflow_stage"] = workflow_stage

    if result is not None:
        state.setdefault("history", []).append({
            "time": datetime.now().isoformat(),
            "agent": agent,
            "task": task,
            "result": result,
            "workflow_stage": workflow_stage,
            "system_status": system_status,
        })

    save_state(state)
    return state


def reset_state():
    state = DEFAULT_STATE.copy()
    state["history"] = []
    save_state(state)
    return state


if __name__ == "__main__":
    update_agent(
        "LANGUAGE_ARCHITECT",
        "Test pamięci",
        "Architekt zakończył analizę",
        workflow_stage="ETAP_1_CORE_FOUNDATION",
    )

    print(load_state())