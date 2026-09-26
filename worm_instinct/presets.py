"""
presets.py — canned "instinct" stimulus patterns for the C. elegans engine.

Each preset is a JSON file describing:
- name, description
- a stimulus waveform (list of floats, length T)
- optional: which neurons are "sensory" (get the stimulus directly)

The presets encode known behavioral circuits:
- escape:  nociceptive touch → forward/reverse locomotion switch
- forage:  bacterial sensing → approach
- turn:    dorsal/ventral motor switch (locomotory turn)
- rest:    baseline wandering (low-level sensory noise)
"""
from __future__ import annotations
import json
import os
import numpy as np

_PRESETS_DIR = os.path.join(os.path.dirname(__file__), "presets")


def list_presets() -> list[dict]:
    """Return metadata for all available presets."""
    out = []
    if not os.path.isdir(_PRESETS_DIR):
        return out
    for fn in sorted(os.listdir(_PRESETS_DIR)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(_PRESETS_DIR, fn)) as f:
            d = json.load(f)
        out.append({
            "name": d.get("name", fn.replace(".json", "")),
            "description": d.get("description", ""),
            "duration": len(d.get("stimulus", [])),
        })
    return out


def load_preset(name: str) -> dict:
    """Load a preset by name (without .json extension)."""
    path = os.path.join(_PRESETS_DIR, f"{name}.json")
    if not os.path.exists(path):
        available = [p["name"] for p in list_presets()]
        raise ValueError(f"Preset '{name}' not found. Available: {available}")
    with open(path) as f:
        return json.load(f)


def make_stimulus(preset: dict) -> np.ndarray:
    """Convert a preset dict to a stimulus array."""
    return np.asarray(preset["stimulus"], dtype=float)


def run_preset(worm, name: str, noise: float = 0.0, smooth: int = 3):
    """
    Run a named preset on a WormInstinct engine.

    Returns (reaction, spikes) from worm.react().
    """
    p = load_preset(name)
    stim = make_stimulus(p)
    # Clip to valid range
    stim = np.clip(stim, -0.5, 1.0)
    return worm.react(stim, noise=noise, smooth=smooth)
