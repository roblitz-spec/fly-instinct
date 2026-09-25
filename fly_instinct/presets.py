"""
presets.py — 预调好的“本能”预设（刺激 + 引擎参数 + 读出）
=========================================================

把"某种本能"打包成一个 JSON 预设：
  - stimulus : 刺激信号怎么生成（突发威胁 / 渐近奖励 / 短时惊跳 / 持续低噪探索）
  - engine   : 引擎参数（seed / gain / in_neurons / spectral_radius）
  - react    : react() 的 noise / smooth

用法：
    from fly_instinct import run_preset

    # 真实连接组版（需先 fetch-data 到 data/）
    out = run_preset("escape", edges_path="data/edges.csv",
                     ann_path="data/annotations.csv",
                     nt_path="data/neurotransmitters.csv")
    reaction = out["reaction"]      # (T,) 反应强度
    spikes   = out["spikes"]        # (n, T) 发放
    stimulus = out["stimulus"]      # (T,) 输入的预设刺激

    # 替身版（不需要数据，秒级）
    out = run_preset("escape", use_real=False)

    # 列出所有内置预设
    from fly_instinct import list_presets
    print(list_presets())

预设是【数据 + 参数】，不是模型；换预设 = 换一种"本能"，
权重仍是同一个冻结网络，react() 依然不学习。
"""
from __future__ import annotations
import json
import os
import numpy as np

_PRESET_DIR = os.path.join(os.path.dirname(__file__), "presets")


def _bundled_presets() -> list:
    if not os.path.isdir(_PRESET_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(_PRESET_DIR) if f.endswith(".json"))


def list_presets() -> list:
    """返回内置预设 id 列表（如 ['escape','explore','startle','sugar']）。"""
    return _bundled_presets()


def load_preset(name: str) -> dict:
    """
    读一个预设 JSON。

    name : 内置预设 id（如 "escape"）或 .json 文件的完整/相对路径。
    返回 : 解析后的 dict（含 id/label_zh/description/stimulus/engine/react）。
    """
    path = name if (name.endswith(".json") or os.path.exists(name)) \
        else os.path.join(_PRESET_DIR, name + ".json")
    if not os.path.exists(path):
        avail = ", ".join(_bundled_presets()) or "(空)"
        raise FileNotFoundError(f"找不到预设 '{name}'（路径 {path}）。内置预设：{avail}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def make_stimulus(cfg: dict) -> np.ndarray:
    """
    按预设的 stimulus 配置生成一维刺激信号 (T,)。

    支持的 type：
      step  : 前静默，onset 起出现持续 duration 的恒定幅值（突发威胁）
      ramp  : onset 起在 duration 内线性 0->amplitude，之后保持（渐近奖励）
      pulse : 仅 [onset, onset+width) 为幅值，其余为 0（短时惊跳）
      noise : 全程 baseline + 高斯噪声(std=noise_std)（持续低噪探索）
    """
    stype = cfg.get("type", "step")
    T = int(cfg.get("T", 200))
    amp = float(cfg.get("amplitude", 1.0))
    s = np.zeros(T)
    if stype == "step":
        onset = int(cfg.get("onset", T // 2))
        dur = int(cfg.get("duration", T - onset))
        s[onset:onset + dur] = amp
    elif stype == "ramp":
        onset = int(cfg.get("onset", 0))
        dur = int(cfg.get("duration", max(1, T - onset)))
        ramp = np.linspace(0.0, amp, dur)
        s[onset:onset + dur] = ramp
        if onset + dur < T:
            s[onset + dur:] = amp
    elif stype == "pulse":
        onset = int(cfg.get("onset", T // 2))
        width = int(cfg.get("width", 5))
        s[onset:onset + width] = amp
    elif stype == "noise":
        base = float(cfg.get("baseline", 0.3))
        nstd = float(cfg.get("noise_std", 0.15))
        seed = int(cfg.get("seed", 0))
        rng = np.random.default_rng(seed)
        s[:] = base + rng.normal(0.0, nstd, size=T)
        s = np.clip(s, 0.0, None)
    else:
        raise ValueError(f"未知刺激类型: {stype}")
    return s


def run_preset(name: str, edges_path: str | None = None,
               ann_path: str | None = None, nt_path: str | None = None,
               use_real: bool | None = None,
               noise: float | None = None, smooth: int | None = None) -> dict:
    """
    用一个预设跑一次“本能反应”，返回信号 + 元信息。

    参数
    ----
    name      : 预设 id（"escape"/"sugar"/"startle"/"explore"）或 .json 路径
    edges_path: 真实连接组 edges.csv（use_real=True 时必填）
    ann_path / nt_path : 真实连接组注释/递质（可选）
    use_real  : True=真实连接组，False=150 节点替身版；
                None=有 edges_path 就用真实，否则替身版
    noise / smooth : 覆盖预设里 react 的对应参数

    返回
    ----
    dict: preset(预设 dict), stimulus((T,)), reaction((T,)),
          spikes((n,T)), engine(替身 or 真实), meta(引擎 meta)
    """
    from . import FlyInstinct

    preset = load_preset(name)
    if use_real is None:
        use_real = edges_path is not None and os.path.exists(edges_path)

    eng_cfg = preset.get("engine", {})
    if use_real:
        if not (edges_path and os.path.exists(edges_path)):
            raise FileNotFoundError(
                "use_real=True 需要有效的 edges_path（先 `python -m fly_instinct fetch-data --out data`）")
        engine = FlyInstinct.from_malecns(
            edges_path, ann_path=ann_path, nt_path=nt_path,
            seed=int(eng_cfg.get("seed", 7)),
            in_neurons=int(eng_cfg.get("in_neurons", 800)),
            gain=float(eng_cfg.get("gain", 2.0)),
            spectral_radius=float(eng_cfg.get("spectral_radius", 0.9)))
    else:
        engine = FlyInstinct(n_neurons=150,
                             seed=int(eng_cfg.get("seed", 7)),
                             gain=float(eng_cfg.get("gain", 6.0)))

    stimulus = make_stimulus(preset.get("stimulus", {}))
    r_cfg = preset.get("react", {})
    if noise is None:
        noise = float(r_cfg.get("noise", 0.0))
    if smooth is None:
        smooth = int(r_cfg.get("smooth", 3))

    reaction, spikes = engine.react(stimulus, noise=noise, smooth=smooth)
    # 稳健下限：react() 是“峰值对齐 1”，但强抑制时负谷可能很深（如 ramp/惊跳后）。
    # 预设输出压到 [-0.5, 1]，保证画出来/接入项目时干净；要原始信号直接调 engine.react()。
    reaction = np.clip(reaction, -0.5, 1.0)
    return {
        "preset": preset,
        "stimulus": stimulus,
        "reaction": reaction,
        "spikes": spikes,
        "engine": engine,
        "meta": getattr(engine, "meta", None),
    }
