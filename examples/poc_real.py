"""
poc_real.py — 本能引擎 PoC（真实 MaleCNS 连接组）
=================================================
用【真实 MaleCNS 子集（9,999 节点 / 158 万边）】替换替身网络，
同一“威胁逼近”刺激下对比：纯随机 / 纯脚本 / 真实本能。

并自动扫描增益 gain，挑一个让网络“活而不爆”的（威胁期平均发放率接近 15%），
用它出最终对比图 instinct_poc_real.png。

指标：
  - 响应延迟(onset latency)
  - lag-1 自相关(结构度)   白噪声≈0，脚本≈1，本能居中
  - 与刺激相关度           脚本≈1(照抄)，本能<1(有自己的动力学)，随机≈0
  - 威胁期平均发放率        衡量网络是否“死(≈0)”或“爆(→1)”
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from fly_instinct import FlyInstinct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # 项目根目录（data/ 在根目录，不进 pip 包）
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "instinct_poc_real.png")

# 中文字体自动适配
_cands = ["Microsoft YaHei", "SimHei", "SimSun", "Noto Sans CJK SC",
          "WenQuanYi Zen Hei", "PingFang SC"]
_avail = {f.name for f in font_manager.fontManager.ttflist}
_pick = next((c for c in _cands if c in _avail), None)
if _pick:
    plt.rcParams["font.sans-serif"] = [_pick, "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def make_threat(T=500, onset=120, ramp=30, off=360, offramp=45):
    s = np.zeros(T)
    up = np.arange(onset, onset + ramp)
    s[up] = np.linspace(0, 1, len(up))
    s[onset + ramp:off] = 1.0
    down = np.arange(off, off + offramp)
    s[down] = np.linspace(1, 0, len(down))
    return s


def onset_latency(x, base, thr=0.25):
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


def threat_firing_rate(spikes, threat):
    on = threat > 0.5
    if on.sum() == 0:
        return 0.0
    return float(spikes[:, on].mean())


def build(gain, T):
    return FlyInstinct.from_malecns(
        os.path.join(DATA, "edges.csv"),
        ann_path=os.path.join(DATA, "annotations.csv"),
        nt_path=os.path.join(DATA, "neurotransmitters.csv"),
        seed=7, in_neurons=800, gain=gain, spectral_radius=0.9,
    )


def main():
    T = 500
    threat = make_threat(T)

    # —— 增益扫描：挑“活而不爆”的 ——
    print("增益扫描（威胁期平均发放率越接近 15% 越好）：")
    print(f"{'gain':>6}{'发放率':>10}{'lag1自相关':>12}")
    best_gain, best_score = None, 1e9
    for g in [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]:
        fly = build(g, T)
        rx, spikes = fly.react(threat, smooth=2)
        fr = threat_firing_rate(spikes, threat)
        ac = autocorr_lag1(rx)
        score = abs(fr - 0.15)
        if score < best_score:
            best_score, best_gain = score, g
        print(f"{g:>6}{fr:>10.3f}{ac:>12.3f}")
    print(f"-> 选用 gain={best_gain}\n")

    # —— 三方对比（用选定的 gain）——
    fly = build(best_gain, T)
    instinct_rx, spikes = fly.react(threat, smooth=2)
    meta = fly.meta

    rng = np.random.default_rng(0)
    random_rx = np.clip(rng.normal(0.5, 0.15, T), 0, 1)
    scripted_rx = np.clip((threat - 0.15) / 0.85, 0, 1)

    rows = [("纯随机", random_rx), ("纯脚本", scripted_rx), ("真实本能", instinct_rx)]
    print(f"{'反应':<8}{'响应延迟':>10}{'lag1自相关':>12}{'与刺激相关':>12}{'威胁期发放率':>14}")
    for name, rx in rows:
        fr = threat_firing_rate(spikes, threat) if name == "真实本能" else float("nan")
        base = np.median(rx[:60])  # 刺激前(t<120)基线
        print(f"{name:<8}{onset_latency(rx, base):>10}{autocorr_lag1(rx):>12.3f}"
              f"{corr_with(rx, threat):>12.3f}{fr:>14.3f}")

    print(f"\n[真实连接组] 节点={meta['n_nodes']}  边={meta['n_edges']:,}  "
          f"抑制占比={meta['inhibit_frac']:.1%}  输入神经元={meta['in_neurons']}")
    print(f"[真实连接组] 谱半径 raw={meta['sr_raw']:.2f} -> target={meta['sr_target']}\n"
          f"(威胁在 t={120} 出现)")

    # —— 绘图 ——
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), sharex=True,
                             gridspec_kw={"height_ratios": [2.2, 1]})
    ax = axes[0]
    ax.plot(threat, color="0.35", ls="--", lw=1.6, label="威胁刺激 (输入)")
    ax.plot(random_rx, color="0.7", lw=1.0, label="纯随机 (白噪声·死的)")
    ax.plot(scripted_rx, color="#185FA5", lw=1.4, label="纯脚本 (规则·可预测)")
    ax.plot(instinct_rx, color="#D85A30", lw=1.8,
            label=f"真实本能 (MaleCNS {meta['n_nodes']}节点·非学习)")
    ax.axvline(120, color="0.5", ls=":", lw=1)
    ax.text(121, ax.get_ylim()[1] * 0.02, "威胁出现", fontsize=8, color="0.5")
    ax.set_ylabel("反应强度")
    ax.set_ylim(-0.03, 1.08)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.set_title("同一威胁刺激下的三种“反应”：随机 / 脚本 / 真实果蝇连接组本能",
                 fontsize=12)
    ax.grid(alpha=0.25)

    ax2 = axes[1]
    raster_idx = np.linspace(0, spikes.shape[0] - 1, 240).astype(int)
    ax2.imshow(spikes[raster_idx, :], aspect="auto", cmap="gray_r",
               interpolation="none", origin="lower", extent=[0, T, 0, 240])
    ax2.set_ylabel("神经元 (抽样 240/9999)")
    ax2.set_xlabel("时间步")
    ax2.set_title(f"真实连接组内部：{meta['n_nodes']} 个冻结神经元的发放 (raster，抽样显示)",
                  fontsize=9)

    plt.tight_layout()
    plt.savefig(OUT, dpi=130, bbox_inches="tight")
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
