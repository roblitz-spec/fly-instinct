"""
loader.py — Read the C. elegans White 1986 connectome into a frozen weight matrix,
with per-neuron excitatory/inhibitory polarity from the Wang et al. 2024
neurotransmitter atlas.

Data files (worm_instinct/data/):
    white1986.csv          tab-delimited edge list:  pre, post, type, synapses
                           309 nodes, 2,960 edges (2,386 chemical + 575 electrical)
    wang2024_nt_atlas.csv  per-neuron neurotransmitter atlas derived from
                           Wang et al. 2024 (eLife 13: RP95402, supp2).
                           Columns: neuron, raw_label, nt, sign

Polarity policy (fast-synapse sign used by the engine):
    GABA               -> inhibitory  (-1)   canonical fast inhibitory transmitter
    Glutamate / ACh    -> excitatory  (+1)   fast excitatory transmitters
    monoamine/betaine/
    unknown / glia     -> `modulatory_sign` (default +1.0)
                           no clean fast sign; carried as excitatory by default and
                           reported honestly in the metadata.

Gap junctions (electrical) are bidirectional and sign-less; they are always
added as positive coupling.

Spectral radius is normalized to ~0.9 (near-critical dynamics).
"""
from __future__ import annotations
import csv
import os
import numpy as np
from scipy import sparse

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Connectome names that the Wang 2024 atlas merges / renames.
# White 1986 lists DB1 and DB3 separately; the atlas reports them as a pair.
_NT_ALIAS = {
    "DB1": "DB1/3",
    "DB3": "DB3/1",
}

# Fallback GABAergic set, used ONLY if the Wang 2024 atlas CSV is missing.
# Classic GABAergic motor/interneurons (kept small and conservative).
_GABA_FALLBACK = {
    "RIBL", "RIBR", "RIS",
    "RMEL", "RMER", "RMED", "RMEV",
    "DVBL", "DVBR",
    "RIGL", "RIGR",
    "DD1", "DD2", "DD3", "DD4", "DD5", "DD6",
    "VD1", "VD2", "VD3", "VD4", "VD5", "VD6",
    "VD7", "VD8", "VD9", "VD10", "VD11", "VD12", "VD13",
}

# Gap junction type indicators
_ELECTRICAL = {"electrical", "gap_junction", "gj"}


def _spectral_radius(M, iters: int = 60, seed: int = 0) -> float:
    """Power-iteration estimate of the spectral radius of |M|."""
    n = M.shape[0]
    v = np.abs(np.random.default_rng(seed).random(n)) + 1e-9
    v /= np.linalg.norm(v)
    sr = 0.0
    for _ in range(iters):
        w = np.abs(M @ v)
        nr = np.linalg.norm(w)
        if nr < 1e-12:
            return 0.0
        v = w / nr
        sr = float(nr)
    return sr


def load_nt_atlas(csv_path: str | None = None) -> dict:
    """
    Load the Wang et al. 2024 per-neuron neurotransmitter atlas.

    Returns
    -------
    dict with:
        by_name : {neuron_name: (nt_base, sign_label)}   (canonical atlas names)
        counts  : {sign_label: int}
        source  : provenance string
    """
    if csv_path is None:
        csv_path = os.path.join(_DATA_DIR, "wang2024_nt_atlas.csv")

    by_name = {}
    if not os.path.exists(csv_path):
        return {"by_name": by_name, "counts": {}, "source": "MISSING"}

    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("neuron") or "").strip()
            if not name:
                continue
            nt = (row.get("nt") or "UNK").strip()
            sign = (row.get("sign") or "excitatory").strip()
            by_name[name] = (nt, sign)

    counts = {}
    for _, s in by_name.values():
        counts[s] = counts.get(s, 0) + 1

    return {
        "by_name": by_name,
        "counts": counts,
        "source": "Wang et al. 2024 (eLife 13:RP95402, supp2) via wang2024_nt_atlas.csv",
    }


def load_white1986(csv_path: str | None = None,
                   nt_atlas_path: str | None = None,
                   spectral_radius: float = 0.9,
                   modulatory_sign: float = 1.0) -> dict:
    """
    Load the White 1986 C. elegans connectome with Wang 2024 NT polarity.

    Parameters
    ----------
    csv_path        : path to white1986.csv. If None, use the bundled file.
    nt_atlas_path   : path to the NT atlas CSV. If None, use the bundled file;
                      if missing, fall back to a small conservative GABA set.
    spectral_radius : target spectral radius for the frozen network (~0.9).
    modulatory_sign : fast-synapse sign for neurons whose transmitter is a
                      monoamine / betaine / unknown (or unlabeled glia/muscle).
                      Default +1.0 (excitatory by default).

    Returns
    -------
    dict with keys:
        W           : scipy.sparse.csr_matrix (n x n), signed and scaled
        n           : number of neurons
        n_edges     : number of edges (original, before bidirectional expansion)
        n_chem      : number of chemical synapses
        n_elec      : number of gap junctions
        neuron_names: list of neuron names (index -> name)
        name2idx    : dict name -> index
        sign        : np.ndarray (n,), +1 excitatory / -1 inhibitory / other
        nt          : list of base NT codes per neuron (GABA|Glu|ACh|DA|5HT|...)
        nt_counts   : {sign_label: int} over the loaded neurons
        nt_source   : provenance string
        sr_raw      : spectral radius before scaling
        sr_target   : target spectral radius
        inhibit_frac: fraction of inhibitory neurons (sign < 0)
    """
    if csv_path is None:
        csv_path = os.path.join(_DATA_DIR, "white1986.csv")

    # 1) Read edge list
    chem_edges = []   # (pre, post, weight)
    elec_edges = []   # (pre, post, weight)
    names = set()

    with open(csv_path, newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)  # pre, post, type, synapses
        for row in reader:
            if len(row) < 4:
                continue
            pre = row[0].strip()
            post = row[1].strip()
            etype = row[2].strip().lower()
            w = float(row[3])
            if w <= 0:
                continue
            names.add(pre)
            names.add(post)
            if etype in _ELECTRICAL:
                elec_edges.append((pre, post, w))
            else:
                chem_edges.append((pre, post, w))

    # 2) Build name -> index mapping (sorted for determinism)
    neuron_names = sorted(names)
    name2idx = {name: i for i, name in enumerate(neuron_names)}
    n = len(neuron_names)

    # 3) Load NT atlas and assign per-neuron sign + base code
    atlas = load_nt_atlas(nt_atlas_path)
    by_name = atlas["by_name"]
    use_atlas = len(by_name) > 0

    sign = np.ones(n, dtype=np.float64)
    nt_code = []
    for name, idx in name2idx.items():
        key = _NT_ALIAS.get(name, name)
        if use_atlas and key in by_name:
            nt, pol = by_name[key]
            nt_code.append(nt)
            if pol == "inhibitory":
                sign[idx] = -1.0
            elif pol == "excitatory":
                sign[idx] = +1.0
            else:  # modulatory / unknown
                sign[idx] = float(modulatory_sign)
        else:
            # Fallback: conservative GABA set (only when the atlas is absent).
            nt_code.append("GABA" if name in _GABA_FALLBACK else "UNK")
            if name in _GABA_FALLBACK:
                sign[idx] = -1.0
            else:
                sign[idx] = +1.0

    # 4) Build sparse matrix W[post, pre] (column = presynaptic, row = postsynaptic)
    ii, jj, data = [], [], []

    # Chemical: directed, signed by presynaptic neuron
    for pre, post, w in chem_edges:
        pi, po = name2idx[pre], name2idx[post]
        ii.append(po)
        jj.append(pi)
        data.append(w * sign[pi])

    # Electrical (gap junctions): bidirectional, always excitatory coupling
    for pre, post, w in elec_edges:
        pi, po = name2idx[pre], name2idx[post]
        ii.append(po)
        jj.append(pi)
        data.append(w)
        ii.append(pi)
        jj.append(po)
        data.append(w)

    W = sparse.csr_matrix((data, (ii, jj)), shape=(n, n))
    W.sum_duplicates()

    # 5) Spectral radius normalization
    sr_raw = _spectral_radius(W, seed=0)
    if sr_raw > 0:
        W = W * (spectral_radius / sr_raw)

    # 6) Tally the polarity actually realized over the loaded neurons
    realized = np.sign(sign)
    nt_counts = {
        "inhibitory": int((realized < 0).sum()),
        "excitatory": int((realized > 0).sum()),
        "modulatory": int((realized == 0).sum()),
    }
    # Also expose the underlying NT base distribution (full transparency).
    nt_base_counts = {}
    for code in nt_code:
        nt_base_counts[code] = nt_base_counts.get(code, 0) + 1
    if not use_atlas:
        nt_counts["atlas"] = "fallback (GABA set only)"

    return {
        "W": W,
        "n": n,
        "n_edges": len(chem_edges) + len(elec_edges),
        "n_chem": len(chem_edges),
        "n_elec": len(elec_edges),
        "n_total_edges": W.nnz,
        "neuron_names": neuron_names,
        "name2idx": name2idx,
        "sign": sign,
        "nt": nt_code,
        "nt_counts": nt_counts,
        "nt_base_counts": nt_base_counts,
        "nt_source": atlas["source"],
        "sr_raw": sr_raw,
        "sr_target": spectral_radius,
        "inhibit_frac": float((sign < 0).sum()) / n,
    }
