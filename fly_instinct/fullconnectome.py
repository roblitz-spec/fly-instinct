"""
fullconnectome.py — 接入【完整】MaleCNS v1.0 连接组（~1.05 GB feather）
======================================================================

`data/` 里的 25MB 是子集（~1 万节点，够跑够真）。本模块负责把
**完整校对版**（~16.67 万神经元 / ~2560 万条连接）接进来：

  1. download_full() : 从官方 GCS 直链下载 .feather（断点续传 + 大小校验）。
  2. feather_to_csv() : 把 feather 转成 CSV（pre,post,weight），喂给现有 loader。
  3. from_full()     : 下载 + 转换 + 加载一条龙，返回 FlyInstinct。

数据出处（CC-BY-4.0，发布时须署名）：
  MaleCNS v1.0, Janelia FlyEM, https://male-cns.janelia.org

注意：
  - 官方直链在 storage.googleapis.com，**中国大陆网络可能不可达**；
    不可达时请用可达的镜像/代理下载同名文件，只要列仍是 pre/post/weight 即可。
  - feather→CSV 需要 `pandas`（+ `pyarrow`），这是一次性转换依赖：
        pip install pandas pyarrow
  - 完整版稀疏矩阵约 2560 万非零元，加载后内存数百 MB，建议内存 ≥ 8 GB。

用法（CLI）：
  python -m fly_instinct get-full --out data_full          # 只下载
  python -m fly_instinct get-full --out data_full --to-csv # 下载并转 CSV
  python -m fly_instinct get-full --out data_full --run    # 下载+转+跑 escape 预设

用法（代码）：
  from fly_instinct import from_full
  fly = from_full("data_full/connectome-....feather",
                  ann_feather=".../annotations-....feather",
                  nt_feather=".../neurotransmitters-....feather")
  reaction, spikes = fly.react(stimulus)
"""
from __future__ import annotations
import argparse
import os
import sys
import urllib.request

# 官方 GCS 直链（CC-BY 4.0）。文件名以官方下载页为准。
FULL_URLS = {
    "edges": ("https://storage.googleapis.com/flyem-male-cns/v1.0/"
              "connectome-data/flat-connectome/"
              "connectome-weights-male-cns-v1.0-minconf-0.5.feather"),
}
# 完整版体积约 1.05 GB；这里给个下限做粗校验（>=0.9GB 视为下载完整量级），
# 精确字节数以官方文件为准，不强制等值（避免上游更新导致误判）。
FULL_MIN_BYTES = 900_000_000
FEATHER_NAME = "connectome-weights-male-cns-v1.0-minconf-0.5.feather"

_UA = "Mozilla/5.0 (fly-instinct fullconnectome)"


def download_full(out_dir: str, url: str = FULL_URLS["edges"],
                  force: bool = False) -> str:
    """
    下载完整连接组 feather 到 out_dir（断点续传 + 量级校验）。返回文件路径。
    """
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, FEATHER_NAME)
    if force and os.path.exists(dest):
        os.remove(dest)
    if os.path.exists(dest) and os.path.getsize(dest) >= FULL_MIN_BYTES:
        print(f"  [skip] {FEATHER_NAME} 已存在 "
              f"({os.path.getsize(dest)/1e9:.2f} GB)")
        return dest

    print(f"下载完整连接组 ({FEATHER_NAME}) -> {os.path.abspath(dest)}")
    print("  来源: " + url)
    print("  若长时间无响应：storage.googleapis.com 可能不可达，"
          "请改用镜像/代理下载同名文件。")
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    start = os.path.getsize(dest) if os.path.exists(dest) else 0
    if start > 0:
        req.add_header("Range", f"bytes={start}-")
        print(f"  [resume] 从 {start/1e6:.1f} MB 续传")

    with urllib.request.urlopen(req, timeout=120) as resp, \
            open(dest, "ab" if start > 0 else "wb") as f:
        total = start + int(resp.headers.get("Content-Length") or 0)
        got = start
        chunk = 1024 * 1024  # 1MB
        last = 0.0
        import time
        while True:
            b = resp.read(chunk)
            if not b:
                break
            f.write(b)
            got += len(b)
            now = time.time()
            if total and (now - last) > 1.0:
                pct = 100.0 * got / total
                sys.stdout.write(f"\r  {got/1e9:.2f}/{total/1e9:.2f} GB "
                                 f"({pct:.1f}%)")
                sys.stdout.flush()
                last = now
    sys.stdout.write("\n")
    sz = os.path.getsize(dest)
    if sz < FULL_MIN_BYTES:
        raise IOError(f"{dest}: 只有 {sz/1e6:.1f} MB (< {FULL_MIN_BYTES/1e6:.0f} MB)，"
                      f"下载可能不完整，请删除后重试或检查网络。")
    print(f"  [ok] {FEATHER_NAME} ({sz/1e9:.2f} GB)")
    return dest


def _find_col(columns, *keys, exclude=()):
    """按子串找列名（小写匹配），优先精确命中。"""
    cols = list(columns)
    for c in cols:
        if c in keys:
            return c
    for k in keys:
        for c in cols:
            lc = c.lower()
            if k in lc and not any(x in lc for x in exclude):
                return c
    return None


def load_full_feather(edges_feather: str, nt_feather: str | None = None,
                      ann_feather: str | None = None,
                      spectral_radius: float = 0.9, seed: int = 7) -> dict:
    """
    内存高效地加载【完整】feather 连接组，直接建稀疏矩阵 W[post,pre]。

    与 load_malecns（CSV、逐行、会堆全部行进 list）不同：本函数用 pyarrow
    直接把整列读成 numpy，用 searchsorted 向量化做 id->idx 映射，**不落地 CSV、
    不逐行 append**，因此能扛住完整版 1.5 亿条边而不爆内存。

    返回 dict 与 load_malecns 兼容：
      W(稀疏 CSR, post x pre, 带符号已缩放), n, n_edges, node_ids, id2idx,
      inhibit_frac, sr_raw, sr_target, cell_type
    """
    import numpy as np
    from scipy import sparse
    import pyarrow.feather as pf
    from .loader import _spectral_radius

    INHIBIT = {"gaba", "glycine"}

    # 1) 边表：body_pre / body_post / weight（int32 节点 + float32 权重，省一半内存）
    te = pf.read_table(edges_feather)
    pre_c = _find_col(te.column_names, "body_pre", "pre", exclude=["post"])
    post_c = _find_col(te.column_names, "body_post", "post", exclude=["pre"])
    w_c = _find_col(te.column_names, "weight")
    if not (pre_c and post_c and w_c):
        raise ValueError(f"edges feather 列无法识别: {te.column_names}")
    n_edges = int(te.num_rows)
    pre = te.column(pre_c).to_numpy(zero_copy_only=False).astype(np.int32)
    post = te.column(post_c).to_numpy(zero_copy_only=False).astype(np.int32)
    w = te.column(w_c).to_numpy(zero_copy_only=False).astype(np.float32)
    del te  # 立刻放掉 pyarrow 原始缓冲

    # 2) 节点 ID -> idx（只取边上出现过的神经元；np.unique 已排序，int32）
    ids = np.unique(np.concatenate([pre, post]))
    n = int(ids.shape[0])
    pre_idx = np.searchsorted(ids, pre).astype(np.int32)
    post_idx = np.searchsorted(ids, post).astype(np.int32)
    del pre, post

    # 3) 每个（突触前）神经元的符号（默认兴奋，递质命中抑制则 -1）
    sign = np.ones(n, dtype=np.float32)
    if nt_feather and os.path.exists(nt_feather):
        tn = pf.read_table(nt_feather)
        body_c = _find_col(tn.column_names, "body", exclude=["bodyid"])
        nt_c = _find_col(tn.column_names, "consensus_nt", "predicted_nt", "nt")
        if body_c and nt_c:
            body_arr = tn.column(body_c).to_numpy(zero_copy_only=False).astype(np.int32)
            nt_vals = (tn.column(nt_c).to_pandas().astype(str)
                       .str.strip().str.lower().values)
            inh_bodies = body_arr[np.isin(nt_vals, list(INHIBIT))]
            inh_idx = np.searchsorted(ids, inh_bodies)
            valid = (inh_idx < n) & (ids[inh_idx] == inh_bodies)
            sign[inh_idx[valid]] = -1.0
        del tn

    # 4) 组装 W[post,pre]（符号乘在突触前神经元上），尽早释放中间数组
    data = (w * sign[pre_idx]).astype(np.float32, copy=False)
    del w
    W = sparse.csr_matrix((data, (post_idx, pre_idx)), shape=(n, n))
    del data, pre_idx, post_idx
    W.sum_duplicates()

    # 5) 谱半径归一到临界点附近
    sr_raw = _spectral_radius(W, seed=seed)
    if sr_raw > 0:
        W = W * (spectral_radius / sr_raw)

    inhibit_frac = float((sign < 0).mean())
    del sign

    # 6) 细胞类型注释（可选；整表 ~14MB/21 万行）
    cell_type = {}
    if ann_feather and os.path.exists(ann_feather):
        ta = pf.read_table(ann_feather)
        aid_c = _find_col(ta.column_names, "bodyid", "body_id", "root_id")
        typ_c = _find_col(ta.column_names, "type")
        sup_c = _find_col(ta.column_names, "superclass")
        if aid_c:
            aids = ta.column(aid_c).to_numpy(zero_copy_only=False).astype(np.int32)
            types = (ta.column(typ_c).to_pandas().astype(str).values
                     if typ_c else np.array([""] * ta.num_rows))
            sups = (ta.column(sup_c).to_pandas().astype(str).values
                    if sup_c else np.array([""] * ta.num_rows))
            id2idx = {int(i): k for k, i in enumerate(ids)}
            for i in range(ta.num_rows):
                idx = id2idx.get(int(aids[i]))
                if idx is not None:
                    cell_type[idx] = (str(types[i]), str(sups[i]))
        del ta

    return {
        "W": W,
        "n": n,
        "n_edges": n_edges,
        "node_ids": [int(i) for i in ids],
        "inhibit_frac": inhibit_frac,
        "sr_raw": sr_raw,
        "sr_target": spectral_radius,
        "cell_type": cell_type,
    }


def feather_to_csv(feather_path: str, csv_path: str) -> tuple:
    """
    把 .feather 连接组转成 CSV（列 pre,post,weight）。需要 pandas(+pyarrow)。
    返回 (csv_path, 行数)。
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("feather→CSV 需要 pandas 和 pyarrow："
                          "pip install pandas pyarrow")
    df = pd.read_feather(feather_path)
    # 官方列名即 pre/post/weight；若列名不同，按位置取前三列兜底
    if {"pre", "post", "weight"} <= set(df.columns):
        df = df[["pre", "post", "weight"]]
    else:
        df = df.iloc[:, :3]
        df.columns = ["pre", "post", "weight"]
    df.to_csv(csv_path, index=False)
    return csv_path, len(df)


def from_full(feather_path: str, ann_feather: str | None = None,
              nt_feather: str | None = None, out_dir: str | None = None,
              seed: int = 7, in_neurons: int = 2000,
              gain: float = 2.0, spectral_radius: float = 0.9):
    """
    从【完整】feather 连接组构建 FlyInstinct（下载已在外部完成时用本函数）。
    自动转 CSV（缓存在 out_dir，默认 feather 同目录）再走 from_malecns。

    ann_feather / nt_feather : 完整版的注释、递质 feather（可选，列同理）。
    """
    from . import FlyInstinct

    if not os.path.exists(feather_path):
        raise FileNotFoundError(f"找不到 feather: {feather_path}")

    # 直接 feather -> 稀疏矩阵（内存高效，不落 CSV、不堆 list）
    d = load_full_feather(feather_path, nt_feather=nt_feather,
                          ann_feather=ann_feather,
                          spectral_radius=spectral_radius, seed=seed)
    return FlyInstinct.from_loaded(d, seed=seed, in_neurons=in_neurons,
                                   gain=gain, spectral_radius=spectral_radius)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="接入完整 MaleCNS v1.0 连接组 (~1.05GB feather)")
    p.add_argument("--out", default="data_full", help="输出目录 (默认 ./data_full)")
    p.add_argument("--force", action="store_true", help="删除已有 feather 重新下载")
    p.add_argument("--to-csv", action="store_true", help="下载后转 CSV")
    p.add_argument("--run", action="store_true", help="下载+转+用 escape 预设跑一次")
    a = p.parse_args(argv)

    fe = download_full(a.out, force=a.force)
    if a.to_csv or a.run:
        csv = os.path.join(a.out, "full_edges.csv")
        if not os.path.exists(csv):
            feather_to_csv(fe, csv)
        print(f"  [ok] 转 CSV: {csv}")
    if a.run:
        from .presets import run_preset
        csv = os.path.join(a.out, "full_edges.csv")
        out = run_preset("escape", edges_path=csv, use_real=True)
        r = out["reaction"]
        print(f"  [run] escape 预设 @ 完整连接组: peak={r.max():.2f} "
              f"nodes={out['meta']['n_nodes']} edges={out['meta']['n_edges']:,}")


if __name__ == "__main__":
    main()
