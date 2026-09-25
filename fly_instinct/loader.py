"""
malecns_loader.py — 读取 MaleCNS 真实连接组子集，产出“冻结”稀疏权重矩阵
=======================================================================

只做数据这一件事：
  - 读 edges.csv (pre, post, weight) -> 节点 ID 映射 -> scipy 稀疏矩阵 W[post, pre]
  - 用 neurotransmitters.csv 给突触赋符号：GABA/glycine = 抑制(-)，其余 = 兴奋(+)
      * 注意（PROVENANCE 明确）：递质符号是“先验预测”，不是 ground truth
  - 按谱半径把 |W| 归一到临界点附近，保证递归网络有丰富而不爆炸的动力学
  - 权重一经生成即视为“冻结”（本模块不做任何学习）

不依赖引擎代码，可单独测试。返回一个 dict（W + 元信息），交给 FlyInstinct 组装。
"""
from __future__ import annotations
import csv
import os
import numpy as np
from scipy import sparse

# 抑制性递质（小写比对）
INHIBIT = {"gaba", "glycine"}


def _spectral_radius(M, iters: int = 60, seed: int = 0) -> float:
    """用幂迭代近似 |M| 的谱半径（M 为稀疏矩阵，速度快）。"""
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


def load_malecns(edges_path: str, ann_path: str | None = None,
                 nt_path: str | None = None,
                 spectral_radius: float = 0.9) -> dict:
    """
    加载 MaleCNS 真实连接组子集。

    参数
    ----
    edges_path : edges.csv，列 pre,post,weight
    ann_path   : annotations.csv（root_id,cell_type,superclass），可选
    nt_path    : neurotransmitters.csv（root_id,transmitter,confidence），可选
    spectral_radius : 目标谱半径（递归强度的标尺，近临界 ~0.9）

    返回
    ----
    dict: W(稀疏 CSR, post x pre, 带符号已缩放), n, n_edges, node_ids,
          id2idx, inhibit_frac, sr_raw, sr_target, cell_type
    """
    # 1) 读边表，收集节点
    rows = []
    ids = set()
    with open(edges_path, newline="") as f:
        r = csv.reader(f)
        next(r)  # header
        for row in r:
            if len(row) < 3:
                continue
            pre, post, w = int(row[0]), int(row[1]), float(row[2])
            rows.append((pre, post, w))
            ids.add(pre)
            ids.add(post)

    # 2) 读细胞类型注释（顺带把注释里的节点也纳入，保证 ID 覆盖）
    cell_type = {}
    if ann_path and os.path.exists(ann_path):
        with open(ann_path, newline="") as f:
            r = csv.reader(f)
            next(r)
            for row in r:
                if len(row) < 2:
                    continue
                rid = int(row[0])
                ids.add(rid)
                ct = row[1]
                sup = row[2] if len(row) > 2 else ""
                cell_type[rid] = (ct, sup)

    id2idx = {i: k for k, i in enumerate(sorted(ids))}
    n = len(id2idx)

    # 3) 每个（突触前）神经元的符号
    sign = np.ones(n)  # 默认兴奋
    if nt_path and os.path.exists(nt_path):
        with open(nt_path, newline="") as f:
            r = csv.reader(f)
            next(r)
            for row in r:
                if len(row) < 2:
                    continue
                rid = int(row[0])
                tr = row[1].strip().lower()
                if rid in id2idx and tr in INHIBIT:
                    sign[id2idx[rid]] = -1.0

    # 4) 组装 W[post, pre]
    ii, jj, data = [], [], []
    for pre, post, w in rows:
        if pre in id2idx and post in id2idx:
            ii.append(id2idx[post])
            jj.append(id2idx[pre])
            data.append(w * sign[id2idx[pre]])
    W = sparse.csr_matrix((data, (ii, jj)), shape=(n, n))
    W.sum_duplicates()

    # 5) 谱半径归一到临界点附近
    sr_raw = _spectral_radius(W, seed=0)
    if sr_raw > 0:
        W = W * (spectral_radius / sr_raw)

    n_inhib = int((sign < 0).sum())
    return {
        "W": W,
        "n": n,
        "n_edges": len(rows),
        "node_ids": sorted(ids),
        "id2idx": id2idx,
        "inhibit_frac": n_inhib / n,
        "sr_raw": sr_raw,
        "sr_target": spectral_radius,
        "cell_type": cell_type,
    }
