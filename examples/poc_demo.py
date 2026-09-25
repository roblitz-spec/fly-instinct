"""
poc_demo.py — 本能引擎 PoC：同一刺激下对比 纯随机 / 纯脚本 / 本能引擎
=====================================================================
跑一个“威胁逼近”的刺激，看三种“反应”的区别，并量化：
  - 响应延迟(onset latency)   越快越好
  - lag-1 自相关(结构度)      白噪声≈0，脚本高，本能居中
  - 与刺激相关度              脚本≈1(照抄)，本能<1(有自己的动力学)，随机≈0
输出：instinct_poc.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from fly_instinct import FlyInstinct

# 中文字体自动适配（Windows 常见：微软雅黑 / 黑体 / 宋体）
_cands = ["Microsoft YaHei", "SimHei", "SimSun", "Noto Sans CJK SC",
          "WenQuanYi Zen Hei", "PingFang SC"]
_avail = {f.name for f in font_manager.fontManager.ttflist}
_pick = next((c for c in _cands if c in _avail), None)
if _pick:
    plt.rcParams["font.sans-serif"] = [_pick, "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = "instinct_poc.png"


def make_threat(T=600, onset=150, ramp=30, off=430, offramp=45):
    """一个“威胁逼近”刺激：0 -> 上升 -> 保持 -> 下降。"""
    s = np.zeros(T)
    up = np.arange(onset, onset + ramp)
    s[up] = np.linspace(0, 1, len(up))
    s[onset + ramp:off] = 1.0
    down = np.arange(off, off + offramp)
    s[down] = np.linspace(1, 0, len(down))
    return s


def onset_latency(x, base, thr=0.2):
    """响应延迟：相对刺激前基线(base)上升超过 thr 的第一个时刻。"""
    idx = np.where(x >= base + thr)[0]
    return int(idx[0]) if len(idx) else -1


def autocorr_lag1(x):
    x = x - x.mean()
    if np.std(x) < 1e-9:
        return 0.0
    return float(np.corrcoef(x[1:], x[:-1])[0, 1])


def corr_with(x, s):
    s = s.ravel()
    if np.std(x) < 1e-9 or np.std(s) < 1e-9:
        return 0.0
    return float(np.corrcoef(x, s)[0, 1])


def main():
    T = 600
    threat = make_threat(T)

    # 1) 纯随机：白噪声（死的）
    rng = np.random.default_rng(0)
    random_rx = np.clip(rng.normal(0.5, 0.15, T), 0, 1)

    # 2) 纯脚本：固定规则（可预测），照抄刺激 + 阈值
    scripted_rx = np.clip((threat - 0.15) / 0.85, 0, 1)

    # 3) 本能引擎：冻结递归网络，非学习
    fly = FlyInstinct(n_neurons=150, seed=7, gain=6.0, spectral_radius=0.95)
    instinct_rx, spikes = fly.react(threat, smooth=2)

    # —— 指标 ——
    rows = [
        ("纯随机", random_rx),
        ("纯脚本", scripted_rx),
        ("本能引擎", instinct_rx),
    ]
    print(f"{'反应':<8}{'响应延迟':>10}{'lag1自相关':>12}{'与刺激相关':>12}")
    for name, rx in rows:
        base = np.median(rx[:90])  # 刺激前(t<150)基线
        print(f"{name:<8}{onset_latency(rx, base):>10}{autocorr_lag1(rx):>12.3f}{corr_with(rx, threat):>12.3f}")
    print(f"(威胁在 t={150} 出现)")

    # —— 绘图 ——
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True,
                             gridspec_kw={"height_ratios": [2.2, 1]})
    ax = axes[0]
    ax.plot(threat, color="0.35", ls="--", lw=1.6, label="威胁刺激 (输入)")
    ax.plot(random_rx, color="0.7", lw=1.0, label="纯随机 (白噪声·死的)")
    ax.plot(scripted_rx, color="#185FA5", lw=1.4, label="纯脚本 (规则·可预测)")
    ax.plot(instinct_rx, color="#D85A30", lw=1.8, label="本能引擎 (冻结网络·非学习)")
    ax.axvline(150, color="0.5", ls=":", lw=1)
    ax.text(151, ax.get_ylim()[1] * 0.02, "威胁出现", fontsize=8, color="0.5")
    ax.set_ylabel("反应强度")
    ax.set_ylim(-0.03, 1.08)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.set_title("同一威胁刺激下的三种“反应”：随机 / 脚本 / 本能", fontsize=12)
    ax.grid(alpha=0.25)

    ax2 = axes[1]
    ax2.imshow(spikes, aspect="auto", cmap="gray_r", interpolation="none",
               origin="lower", extent=[0, T, 0, spikes.shape[0]])
    ax2.set_ylabel("神经元 (#)")
    ax2.set_xlabel("时间步")
    ax2.set_title("本能引擎内部：150 个冻结神经元的发放 (raster)", fontsize=9)

    plt.tight_layout()
    plt.savefig(OUT, dpi=130, bbox_inches="tight")
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
