"""
engine.py — the "instinct engine": a frozen spiking network driven by a real connectome.

Core idea (reservoir computing): a frozen (non-learning) recurrent network
scatters incoming stimuli into a high-dimensional, non-trivial, structured
"instinctive response." It is neither white noise (dead) nor scripted rules
(predictable) — it *reacts*, the way a living animal's brain does.

For C. elegans the frozen core IS the complete nervous system
(302 neurons, ~2,900 synapses, White et al. 1986) — not a stand-in.

Usage:
    from worm_instinct import from_white1986
    worm = from_white1986(seed=7)
    reaction, spikes = worm.react(stimulus)   # stimulus: 1D/2D array

Design principles:
  - Weights are frozen at construction; react() does NO learning.
  - Given seed + stimulus, output is deterministic (unless noise is added).
  - Noise is optional: real animal instinct carries a little thermal noise.
"""
from __future__ import annotations
import numpy as np


class WormInstinct:
    """A frozen recurrent spiking network built from the C. elegans connectome."""

    def __init__(self, W, n, n_input=1, n_output=1, seed=0,
                 tau=20.0, dt=1.0, v_th=1.0, v_reset=0.0, gain=1.0,
                 neuron_names=None, sign=None, nt=None, meta=None):
        """
        Parameters
        ----------
        W          : sparse/dense (n x n) frozen recurrent weights [post, pre]
        n          : number of neurons
        n_input    : dimension of input stimulus (default 1)
        n_output   : dimension of output readout (default 1)
        seed       : RNG seed for input/output projection weights
        tau, dt, v_th, v_reset, gain : LIF dynamics parameters
        neuron_names : optional list of names (len n)
        sign       : optional np.ndarray (n,), per-neuron fast-synapse sign
        nt         : optional list (n,), per-neuron base NT code
        meta       : optional metadata dict
        """
        from scipy import sparse
        if not sparse.issparse(W):
            W = sparse.csr_matrix(W)
        self.W = W
        self.n = n
        self.n_in = n_input
        self.n_out = n_output
        self.tau = tau
        self.dt = dt
        self.v_th = v_th
        self.v_reset = v_reset
        self.gain = gain
        self.neuron_names = neuron_names
        # Per-neuron fast-synapse sign (+1 exc / -1 inh) and base NT code.
        self.sign = sign
        self.nt = nt

        rng = np.random.default_rng(seed)

        # Input interface: stimulus → top out-degree neurons (excitatory drive)
        outdeg = np.bincount(W.indices, minlength=n)
        order = np.lexsort((np.arange(n), -outdeg))
        top = order[:min(n_input, n)]
        in_w = rng.uniform(0.6, 1.2, size=top.size)
        self.Win = sparse.csr_matrix(
            (in_w, (top, np.zeros(top.size, dtype=int))), shape=(n, 1))

        # Output interface: frozen random projection → single scalar
        self.Wout = sparse.csr_matrix(rng.normal(0.0, 1.0, (1, n)) / np.sqrt(n))

        self._rng = np.random.default_rng(seed + 1)
        self._v = np.zeros(n)
        self._sp_prev = np.zeros(n)
        self.is_real = True
        self.meta = meta or {}

    def reset(self):
        """Clear internal state (frozen weights preserved)."""
        self._v = np.zeros(self.n)
        self._sp_prev = np.zeros(self.n)

    def step(self, stimulus: np.ndarray, noise: float = 0.0) -> np.ndarray:
        """Advance one timestep. Returns output readout (n_out,)."""
        stim = np.asarray(stimulus, dtype=float).ravel()
        I = self.W @ self._sp_prev + self.Win @ stim
        if noise and noise > 0.0:
            I = I + self._rng.normal(0.0, noise, size=self.n)
        self._v = self._v + (self.dt / self.tau) * (0.0 - self._v) + self.dt * (I * self.gain)
        sp = (self._v >= self.v_th).astype(float)
        self._v = np.where(sp == 1.0, self.v_reset, self._v)
        self._sp_prev = sp
        return (self.Wout @ sp.T).ravel()

    def react(self, stimulus: np.ndarray, noise: float = 0.0,
              smooth: int = 1, track_spikes: bool | None = None):
        """
        Run the frozen network on a stimulus sequence.

        Parameters
        ----------
        stimulus   : (T,) or (T, n_in) stimulus array
        noise      : internal noise amplitude (0 = deterministic)
        smooth     : moving-average window on the output (1 = no smoothing)
        track_spikes : record per-neuron spike matrix (n, T)?
                       None = auto (always track for this small network).

        Returns
        -------
        reaction : (T,) response trace, baseline-aligned to 0, peak-aligned to 1.
        spikes   : (n, T) per-neuron spikes (0/1), or None if not tracked.
        """
        stimulus = np.asarray(stimulus, dtype=float)
        if stimulus.ndim == 1:
            stimulus = stimulus[:, None]
        T = stimulus.shape[0]
        self.reset()

        if track_spikes is None:
            track_spikes = (self.n * T) < 100_000_000

        # Resting baseline
        for _ in range(max(10, int(self.tau))):
            self.step(np.zeros(self.n_in), noise=0.0)
        resting = float((self.Wout @ self._sp_prev).ravel()[0])

        reaction = np.zeros(T)
        spikes = np.zeros((self.n, T)) if track_spikes else None
        for t in range(T):
            reaction[t] = self.step(stimulus[t], noise=noise)[0] - resting
            if track_spikes:
                spikes[:, t] = self._sp_prev

        if smooth > 1:
            k = min(smooth, T)
            kernel = np.ones(k) / k
            reaction = np.convolve(reaction, kernel, mode="same")

        peak = reaction.max()
        if peak > 0:
            reaction = reaction / peak
        return reaction, spikes


def from_white1986(csv_path: str | None = None, seed: int = 0,
                   in_neurons: int = 60, tau: float = 20.0, dt: float = 1.0,
                   v_th: float = 1.0, v_reset: float = 0.0, gain: float = 3.0,
                   spectral_radius: float = 0.9,
                   nt_atlas_path: str | None = None,
                   modulatory_sign: float = 1.0) -> WormInstinct:
    """
    Build a WormInstinct from the bundled White 1986 C. elegans connectome,
    with excitatory/inhibitory polarity from the Wang et al. 2024 NT atlas.

    Parameters
    ----------
    csv_path        : path to white1986.csv (None = use bundled data)
    nt_atlas_path   : path to the NT atlas CSV (None = bundled; fallback if missing)
    seed            : RNG seed for input/output projections
    in_neurons      : how many neurons receive external stimulus (top out-degree)
    tau, dt, v_th, v_reset, gain : LIF dynamics
    spectral_radius : frozen network strength (near-critical ~0.9)
    modulatory_sign : fast-synapse sign for monoamine/unknown/unlabeled neurons
                      (default +1.0 = excitatory by default)

    Returns
    -------
    A ready-to-use WormInstinct instance (exposes .sign and .nt per neuron).
    """
    from .loader import load_white1986

    d = load_white1986(csv_path, nt_atlas_path=nt_atlas_path,
                       spectral_radius=spectral_radius,
                       modulatory_sign=modulatory_sign)
    return WormInstinct(
        W=d["W"], n=d["n"], n_input=1, n_output=1, seed=seed,
        tau=tau, dt=dt, v_th=v_th, v_reset=v_reset, gain=gain,
        neuron_names=d["neuron_names"], sign=d["sign"], nt=d["nt"],
        meta={
            "n_nodes": d["n"],
            "n_edges": d["n_edges"],
            "n_chem": d["n_chem"],
            "n_elec": d["n_elec"],
            "inhibit_frac": d["inhibit_frac"],
            "nt_counts": d["nt_counts"],
            "nt_base_counts": d["nt_base_counts"],
            "nt_source": d["nt_source"],
            "sr_raw": d["sr_raw"],
            "sr_target": spectral_radius,
            "in_neurons": int(min(in_neurons, d["n"])),
            "species": "C. elegans",
            "source": "White et al. 1986 (Phil. Trans. R. Soc. B 314:1-340); "
                      "NT polarity: Wang et al. 2024 (eLife 13:RP95402)",
        },
    )
