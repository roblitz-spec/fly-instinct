"""
fly-instinct 命令行入口
========================

数据命令（沿用原有）：
    python -m fly_instinct fetch-data [--out data] [--force]      # 下载 25MB 子集
    python -m fly_instinct get-full [--out data_full] [--to-csv] [--run]  # 完整 1.05GB

跑/导出命令（新增，和 worm-instinct 对齐）：
    python -m fly_instinct info                     # 版本 / 数据档 / 预设一览
    python -m fly_instinct list                     # 列出内置预设
    python -m fly_instinct run escape [--save x.npz]   # 跑一个预设并打印摘要
    python -m fly_instinct export escape out.wav  # 一行出文件（.wav/.npz/.npy）

默认用 25MB 真实子集（若 ./data/edges.csv 存在）；没有则自动落回 150 节点替身版，
装完开箱即跑，不需要先下数据。加 --stand-in 可强制替身（秒级）。
"""
import argparse
import os
import sys

# 数据档探测用的候选路径
_SUBSET_DIR = "data"
_FULL_DIR = "data_full"
_FEATHER_NAME = "connectome-weights-male-cns-v1.0-minconf-0.5.feather"


def _subset_edges(data_dir: str):
    p = os.path.join(data_dir, "edges.csv")
    return p if os.path.exists(p) else None


def _full_feather(full_dir: str):
    p = os.path.join(full_dir, _FEATHER_NAME)
    return p if os.path.exists(p) else None


def _build(preset: str, data: str, stand_in: bool,
           noise: float, smooth: int):
    """按参数构建引擎并跑一个预设，返回 run_preset 的 dict。"""
    from .presets import run_preset
    if stand_in:
        return run_preset(preset, use_real=False, noise=noise, smooth=smooth)
    edges = _subset_edges(data)
    ann = os.path.join(data, "annotations.csv")
    nt = os.path.join(data, "neurotransmitters.csv")
    return run_preset(preset, edges_path=edges,
                      ann_path=ann if os.path.exists(ann) else None,
                      nt_path=nt if os.path.exists(nt) else None,
                      use_real=None, noise=noise, smooth=smooth)


def main():
    argv = sys.argv[1:]

    # 数据命令：委托给原有 main（保留它们各自的完整参数）
    if argv and argv[0] in ("fetch-data", "get-full"):
        if argv[0] == "fetch-data":
            from .datafetch import main as _m
        else:
            from .fullconnectome import main as _m
        _m(argv[1:])
        return

    p = argparse.ArgumentParser(
        prog="fly-instinct",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="果蝇 MaleCNS 连接组“本能引擎”——把刺激变成“活的反应”信号。",
        epilog=("数据命令（同入口）:\n"
                "  fetch-data [--out data] [--force]         下载 25MB 真实子集\n"
                "  get-full [--out data_full] [--to-csv] [--run]  完整 1.05GB"),
    )
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("info", help="版本 / 数据档 / 预设一览")
    sub.add_parser("list", help="列出内置预设")

    def _add_run_args(sp):
        sp.add_argument("preset", help="预设名 (escape/sugar/startle/explore)")
        sp.add_argument("--data", default=_SUBSET_DIR,
                        help="25MB 子集目录 (默认 ./data)")
        sp.add_argument("--stand-in", action="store_true",
                        help="强制用 150 节点替身（不读数据，秒级）")
        sp.add_argument("--noise", type=float, default=0.0)
        sp.add_argument("--smooth", type=int, default=3)

    run_p = sub.add_parser("run", help="跑一个预设并打印摘要")
    _add_run_args(run_p)
    run_p.add_argument("--save", help="保存反应为 .npy / .npz / .wav")

    ex_p = sub.add_parser("export", help="跑一个预设并存成 .wav/.npz/.npy")
    _add_run_args(ex_p)
    ex_p.add_argument("out", help="输出路径 (.wav/.npz/.npy)")
    ex_p.add_argument("--sr", type=int, default=22050, help="WAV 采样率")
    ex_p.add_argument("--duration", type=float, default=4.0, help="WAV 时长(秒)")

    a = p.parse_args()

    from . import __version__, list_presets, load_preset, save_reaction

    if a.cmd == "info":
        print(f"fly-instinct v{__version__}  —  MaleCNS connectome instinct engine")
        se = _subset_edges(_SUBSET_DIR)
        fe = _full_feather(_FULL_DIR)
        print("  数据档:")
        print(f"    子集 25MB : {'✓ ' + se if se else '✗ 未下载 (python -m fly_instinct fetch-data)'}")
        print(f"    完整 1.05GB: {'✓ ' + fe if fe else '✗ 未下载 (python -m fly_instinct get-full)'}")
        presets = list_presets()
        print(f"  预设 ({len(presets)}): " + ", ".join(presets))
        return

    if a.cmd == "list":
        for name in list_presets():
            pr = load_preset(name)
            T = pr.get("stimulus", {}).get("T", "?")
            desc = pr.get("description", "")
            print(f"  {name:<10} T={T}  {desc}")
        return

    if a.cmd in ("run", "export"):
        out = _build(a.preset, a.data, a.stand_in,
                     noise=a.noise, smooth=a.smooth)
        reaction, spikes = out["reaction"], out["spikes"]
        meta = out.get("meta") or {}
        real = meta.get("n_nodes", 0) >= 1000
        src = ("真实子集" if real else "替身 150 节点")
        if a.cmd == "run":
            print(f"preset   : {a.preset}   [{src}]")
            if real:
                print(f"nodes    : {meta.get('n_nodes'):,}   edges: {meta.get('n_edges'):,}")
                print(f"inhibit  : {meta.get('inhibit_frac', 0):.2%}")
            print(f"duration : {len(reaction)} steps")
            print(f"peak     : {reaction.max():.4f}")
            print(f"baseline : {reaction[:10].mean():.4f}")
            print(f"spikes   : {'tracked' if spikes is not None else 'skipped'}")
            if a.save:
                o = save_reaction(reaction, spikes, a.save, meta=meta)
                print(f"saved    : {o}  ({os.path.getsize(o)} bytes)")
        else:  # export
            o = save_reaction(reaction, spikes, a.out, sr=a.sr,
                              duration=a.duration, meta=meta)
            print(f"saved: {o}  ({os.path.getsize(o)} bytes)   [{src}]")
        return

    p.print_help()


if __name__ == "__main__":
    main()
