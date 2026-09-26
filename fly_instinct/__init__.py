"""
fly-instinct — 基于真实果蝇连接组的“本能引擎” (Instinct Engine)
================================================================

一个可复用、非学习（权重永久冻结）的“本能”信号源：
把输入刺激打散成高维、非平凡、结构化的反应信号。
它既不是白噪声（死的），也不是脚本规则（可预测），
而是“像活物一样对刺激有反应”。

快速开始：
    # 1) 替身模式（零依赖数据，直接跑）
    >>> from fly_instinct import FlyInstinct
    >>> fly = FlyInstinct(n_neurons=150, seed=7)
    >>> reaction, spikes = fly.react(stimulus)

    # 2) 真实 MaleCNS 连接组模式
    >>> python -m fly_instinct fetch-data --out data   # 一次性下载 25MB 数据
    >>> fly = FlyInstinct.from_malecns("data/edges.csv")
    >>> reaction, spikes = fly.react(stimulus)

数据出处：MaleCNS v1.0, Janelia FlyEM (CC-BY-4.0)
"""
from .engine import FlyInstinct
from .loader import load_malecns
from .datafetch import fetch_data, DATA_URLS, EXPECTED_SIZES
from .presets import list_presets, load_preset, make_stimulus, run_preset
from .fullconnectome import (from_full, download_full, feather_to_csv,
                             FULL_URLS, FEATHER_NAME)
from .export import save_reaction, render, to_wav, to_npz

__version__ = "0.2.5"
__all__ = [
    "FlyInstinct", "load_malecns", "fetch_data",
    "DATA_URLS", "EXPECTED_SIZES",
    # 预调“本能”预设
    "list_presets", "load_preset", "make_stimulus", "run_preset",
    # 完整连接组（~1.05GB）接入
    "from_full", "download_full", "feather_to_csv",
    "FULL_URLS", "FEATHER_NAME",
    # 导出（wav/npz/npy，零额外依赖）
    "save_reaction", "render", "to_wav", "to_npz",
    "__version__",
]
