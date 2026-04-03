import json
import os
import random

# Load gear catalogue once at import time
_gear_path = os.path.join(os.path.dirname(__file__), "gear.json")
with open(_gear_path) as f:
    GEAR = json.load(f)


def _pick(lst: list) -> str:
    """Pick a random item from a list."""
    return random.choice(lst)


def generate_chain(centroid: float, zcr: float) -> dict:

    # 🎸 CLEAN
    if centroid < 2000 and zcr < 0.05:
        return {
            "noise_gate": {"enabled": True, "threshold": -50},
            "efx":        {"type": "None", "gain": 0},
            "amp":        {"type": _pick(GEAR["amps"]["clean"]), "gain": 2, "volume": 6},
            "ir":         {"cab": _pick(GEAR["cabs"]["clean"]), "mic": "SM57"},
            "mod":        {"type": _pick(GEAR["modulation"]["chorus"]), "depth": 5},
            "reverb":     {"type": _pick(GEAR["reverb"]), "level": 5},
            "delay":      {"type": "analog", "time": 300},
        }

    # 🔥 CRUNCH
    elif centroid < 3000:
        return {
            "noise_gate": {"enabled": True, "threshold": -45},
            "efx":        {"type": _pick(GEAR["drive_fx"]), "gain": 5},
            "amp":        {"type": _pick(GEAR["amps"]["crunch"]), "gain": 5, "volume": 6},
            "ir":         {"cab": _pick(GEAR["cabs"]["rock"]), "mic": "SM57"},
            "mod":        {"type": _pick(GEAR["modulation"]["phaser"]), "depth": 4},
            "reverb":     {"type": "room", "level": 4},
            "delay":      {"type": "None"},
        }

    # ⚡ METAL / HIGH GAIN
    elif zcr > 0.1:
        return {
            "noise_gate": {"enabled": True, "threshold": -40},
            "efx":        {"type": _pick(GEAR["drive_fx"]), "gain": 9},
            "amp":        {"type": _pick(GEAR["amps"]["high_gain"]), "gain": 9, "volume": 7},
            "ir":         {"cab": _pick(GEAR["cabs"]["metal"]), "mic": "SM57"},
            "mod":        {"type": "None"},
            "reverb":     {"type": "plate", "level": 5},
            "delay":      {"type": "digital", "time": 400},
        }

    # 🎯 DEFAULT
    else:
        return {
            "noise_gate": {"enabled": True, "threshold": -50},
            "efx":        {"type": "None"},
            "amp":        {"type": _pick(GEAR["amps"]["clean"]), "gain": 3, "volume": 5},
            "ir":         {"cab": _pick(GEAR["cabs"]["clean"])},
            "mod":        {"type": "None"},
            "reverb":     {"type": "room", "level": 3},
            "delay":      {"type": "None"},
        }
