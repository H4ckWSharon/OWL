"""
OWL — State management (consent, sim mode, active interface, etc.)
Created by Sharon Anil
"""
import json
import os
from pathlib import Path

STATE_FILE = Path.home() / ".owl_state.json"

DEFAULT_STATE = {
    "consent_given": False,
    "sim_mode": True,
    "interface": "wlan0mon",
    "capture_interface": "wlan0",
    "log_level": "INFO",
    "sessions": [],
    "captures": [],
}


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                saved = json.load(f)
            state = DEFAULT_STATE.copy()
            state.update(saved)
            return state
        except Exception:
            pass
    return DEFAULT_STATE.copy()


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def give_consent(state: dict) -> None:
    state["consent_given"] = True
    save_state(state)


def add_session(state: dict, entry: dict) -> None:
    state.setdefault("sessions", []).append(entry)
    if len(state["sessions"]) > 100:
        state["sessions"] = state["sessions"][-100:]
    save_state(state)


def add_capture(state: dict, capture: dict) -> None:
    state.setdefault("captures", []).append(capture)
    save_state(state)


def update_capture_status(state: dict, filename: str, status: str, psk: str = "") -> None:
    for cap in state.get("captures", []):
        if cap.get("filename") == filename:
            cap["status"] = status
            if psk:
                cap["psk"] = psk
    save_state(state)
