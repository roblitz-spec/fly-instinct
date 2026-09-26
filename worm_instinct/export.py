"""
export.py — turn an "instinct reaction" into files you can actually use.

A *reaction* is a 1-D time series (T samples) produced by the frozen
C. elegans connectome in response to a stimulus. On its own it's just an
array; these helpers make it a usable artifact:

  - .wav  : the reaction stretched into a fixed-length audio envelope
            (resampled to a target duration, 16-bit mono PCM). No deps.
  - .npz  : the raw reaction + per-neuron spike matrix + key metadata,
            for driving code (synths, sketches, game agents, research).
  - .npy  : the raw reaction array only (backward-compatible).

Only numpy + the Python standard library (wave) are used, so the package
stays installable with zero extra dependencies.
"""
from __future__ import annotations
import os
import wave
import numpy as np


def to_wav(reaction, path, sr: int = 22050, duration: float = 4.0,
           amplitude: float = 0.8) -> str:
    """
    Resample a reaction trace to a fixed-duration 16-bit mono WAV file.

    The raw reaction has only T samples (the network's timesteps). Writing
    those straight to audio would be a few milliseconds long, so the envelope
    is stretched (linear interpolation) to ``duration`` seconds. The result
    is a listenable amplitude contour you can feed a synth or use as a
    control/texture signal.

    Parameters
    ----------
    reaction   : (T,) array (any range; peak-normalized internally)
    path       : output .wav path
    sr         : sample rate (default 22050 Hz)
    duration   : target audio length in seconds (default 4.0)
    amplitude  : output level 0..1 (default 0.8, leaves headroom)

    Returns the output path.
    """
    x = np.asarray(reaction, dtype=float).ravel()
    if x.size < 2:
        raise ValueError("reaction too short to render")
    peak = np.abs(x).max()
    if peak > 0:
        x = x / peak
    n_out = max(2, int(sr * duration))
    x_old = np.linspace(0.0, 1.0, x.size)
    x_new = np.linspace(0.0, 1.0, n_out)
    y = np.interp(x_new, x_old, x) * amplitude
    y = np.clip(y, -1.0, 1.0)
    pcm = (y * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(sr))
        w.writeframes(pcm.tobytes())
    return str(path)


def to_npz(reaction, spikes, path, meta=None) -> str:
    """
    Save raw reaction + per-neuron spikes + key metadata to a .npz file.

    Parameters
    ----------
    reaction : (T,) response trace
    spikes   : (n, T) per-neuron 0/1 spike matrix, or None
    path     : output .npz path
    meta     : optional dict; only scalar/str values are embedded
               (dicts/lists are skipped to keep the archive simple)

    Returns the output path.
    """
    arrs: dict = {"reaction": np.asarray(reaction, dtype=float)}
    if spikes is not None:
        arrs["spikes"] = np.asarray(spikes, dtype=np.float32)
    if meta:
        for k, v in meta.items():
            if isinstance(v, (bool, int, float, str)):
                arrs[f"meta_{k}"] = np.asarray(v)
            elif isinstance(v, np.generic):
                arrs[f"meta_{k}"] = np.asarray(v)
    np.savez(str(path), **arrs)
    return str(path)


def save_reaction(reaction, spikes, path, sr: int = 22050,
                  duration: float = 4.0, meta=None) -> str:
    """
    Dispatch on file extension:
      .wav -> audio envelope,  .npz -> raw data + meta,  .npy -> raw reaction.
    """
    ext = os.path.splitext(str(path))[1].lower()
    if ext == ".wav":
        return to_wav(reaction, path, sr=sr, duration=duration)
    if ext == ".npz":
        return to_npz(reaction, spikes, path, meta=meta)
    if ext == ".npy":
        np.save(str(path), np.asarray(reaction, dtype=float))
        return str(path)
    raise ValueError(f"Unsupported export type '{ext}'. Use .wav, .npz, or .npy.")


def render(preset_name: str, path: str, seed: int = 7, noise: float = 0.0,
           smooth: int = 3, sr: int = 22050, duration: float = 4.0) -> str:
    """
    One-shot: build the worm, run a preset, save the result to ``path``.

    The shortest path from zero to a usable file:
        from worm_instinct import render
        render("escape", "escape.wav")
    """
    from .engine import from_white1986
    from .presets import run_preset
    w = from_white1986(seed=seed)
    reaction, spikes = run_preset(w, preset_name, noise=noise, smooth=smooth)
    return save_reaction(reaction, spikes, path, sr=sr, duration=duration,
                         meta=w.meta)
