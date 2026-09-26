"""worm-instinct — a real C. elegans connectome wired into a living signal source.

The complete nervous system of the nematode *Caenorhabditis elegans*
(302 neurons, ~2,900 synapses, White et al. 1986) loaded into a frozen
spiking-dynamics engine. It does not learn. It does not think. But it
*reacts* — with the wiring of a real animal's brain.
"""
from .engine import WormInstinct, from_white1986
from .presets import list_presets, load_preset, make_stimulus, run_preset
from .export import to_wav, to_npz, save_reaction, render

__version__ = "0.2.1"

__all__ = [
    "WormInstinct",
    "from_white1986",
    "list_presets",
    "load_preset",
    "make_stimulus",
    "run_preset",
    "to_wav",
    "to_npz",
    "save_reaction",
    "render",
]
