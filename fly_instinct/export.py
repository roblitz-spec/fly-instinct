"""
export.py — 把"本能反应"变成你真正能用的文件
==============================================

一个 *reaction* 是冻结果蝇连接组对一段刺激产生的 1D 时间序列（T 个采样点）。
它本身只是一个数组；这些辅助函数把它变成可用的产物：

  - .wav  : 把反应拉伸成固定时长的音频包络（重采样到目标时长，16-bit 单声道 PCM）。零依赖。
  - .npz  : 原始反应 + 每神经元发放矩阵 + 关键元数据，用于驱动代码（合成器/草图/游戏智能体/研究）。
  - .npy  : 仅原始反应数组（向后兼容）。

只用 numpy + 标准库（wave），因此本包无需任何额外依赖即可安装。

注：完整版连接组（~1.05GB，8.8e7 节点量级）react() 会自动跳过发放矩阵以省内存，
此时 spikes=None，.npz 里只存 reaction + meta（仍完全可用）。
"""
from __future__ import annotations
import os
import wave
import numpy as np


def to_wav(reaction, path, sr: int = 22050, duration: float = 4.0,
           amplitude: float = 0.8) -> str:
    """
    把反应轨迹重采样成固定时长的 16-bit 单声道 WAV 文件。

    原始反应只有 T 个采样（网络时间步），直接写成音频只有几毫秒长，
    因此把包络线性插值拉伸到 ``duration`` 秒。得到一个可听的幅度轮廓，
    可喂给合成器，或用作控制/纹理信号。

    参数
    ----
    reaction   : (T,) 数组（任意值域，内部按峰值归一）
    path       : 输出 .wav 路径
    sr         : 采样率（默认 22050 Hz）
    duration   : 目标音频时长（秒，默认 4.0）
    amplitude  : 输出电平 0..1（默认 0.8，留余量）

    返回输出路径。
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
    把原始反应 + 每神经元发放 + 关键元数据存成 .npz。

    参数
    ----
    reaction : (T,) 反应轨迹
    spikes   : (n, T) 每神经元 0/1 发放矩阵，或 None（大网络跳过时）
    path     : 输出 .npz 路径
    meta     : 可选 dict；只嵌入标量/字符串值（dict/list 跳过，保持归档简单）

    返回输出路径。
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
    按扩展名分发：
      .wav -> 音频包络，  .npz -> 原始数据 + 元数据，  .npy -> 原始反应。
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


def render(preset_name: str, path: str, data: str = "data",
           stand_in: bool = False, noise: float = 0.0,
           smooth: int = 3, sr: int = 22050, duration: float = 4.0) -> str:
    """
    一步到位：构建引擎、跑一个预设、把结果存到 ``path``。

    从零到可用文件的最短路径：
        from fly_instinct import render
        render("escape", "escape.wav")

    参数
    ----
    preset_name : 预设 id（escape/sugar/startle/explore）
    path        : 输出路径（.wav/.npz/.npy）
    data        : 25MB 子集所在目录（默认 ./data；存在 edges.csv 即用真实连接组）
    stand_in    : True=强制用 150 节点替身（不读数据，秒级）
    noise/smooth/sr/duration : 传给 run_preset / 音频参数

    注：网络种子由预设 JSON 固定（确定性），这里不另设 seed 参数。
    """
    from .presets import run_preset

    if stand_in:
        out = run_preset(preset_name, use_real=False,
                         noise=noise, smooth=smooth)
    else:
        edges = os.path.join(data, "edges.csv")
        ann = os.path.join(data, "annotations.csv")
        nt = os.path.join(data, "neurotransmitters.csv")
        # use_real=None：有 edges.csv 就用真实子集，否则自动落回替身版
        out = run_preset(preset_name, edges_path=edges, ann_path=ann,
                         nt_path=nt, use_real=None, noise=noise, smooth=smooth)
    return save_reaction(out["reaction"], out["spikes"], path,
                         sr=sr, duration=duration, meta=out["meta"])
