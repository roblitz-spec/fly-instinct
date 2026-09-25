"""
datafetch.py — 下载 MaleCNS 真实连接组子集（25MB，3 个 CSV）
============================================================

数据出处（CC-BY-4.0，发布时须署名）：
  - 上游：MaleCNS v1.0, Janelia FlyEM, https://male-cns.janelia.org
  - 子集：nosuchstudios/fruit-fly-brain-runtime (HuggingFace)
    9,999 节点 / 1,587,930 条边，从 CX/MBON/descending 等核心类抽取。

用法：
  python -m fly_instinct fetch-data --out data
  # 或安装后：
  fly-instinct-fetch-data --out data

只标准库（urllib），无额外依赖；支持断点续传（Range 头）。
"""
from __future__ import annotations
import argparse
import os
import sys
import urllib.request

_BASE = ("https://hf-mirror.com/datasets/nosuchstudios/"
         "fruit-fly-brain-runtime/resolve/main/artifacts/malecns-v1.0")

# 文件名 -> (URL, 预期字节数；与上游 PROVENANCE.md 一致)
DATA_URLS = {
    "edges.csv": f"{_BASE}/edges.csv",
    "annotations.csv": f"{_BASE}/annotations.csv",
    "neurotransmitters.csv": f"{_BASE}/neurotransmitters.csv",
}
EXPECTED_SIZES = {
    "edges.csv": 25_207_711,
    "annotations.csv": 283_053,
    "neurotransmitters.csv": 364_160,
}

_UA = "Mozilla/5.0 (fly-instinct datafetch)"


def _download_one(url: str, dest: str) -> int:
    """下载单个文件（已存在且大小正确则跳过；否则断点续传）。返回最终字节数。"""
    expected = EXPECTED_SIZES.get(os.path.basename(dest))
    if os.path.exists(dest):
        sz = os.path.getsize(dest)
        if expected is None or sz == expected:
            print(f"  [skip] {os.path.basename(dest)} 已存在 ({sz:,} B)")
            return sz

    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    # 断点续传：若已有部分文件
    start = os.path.getsize(dest) if os.path.exists(dest) else 0
    if start > 0:
        req.add_header("Range", f"bytes={start}-")

    with urllib.request.urlopen(req, timeout=60) as resp, \
            open(dest, "ab" if start > 0 else "wb") as f:
        total = start + int(resp.headers.get("Content-Length") or 0)
        got = start
        chunk = 1024 * 256
        while True:
            b = resp.read(chunk)
            if not b:
                break
            f.write(b)
            got += len(b)
            if total:
                pct = 100.0 * got / total
                sys.stdout.write(f"\r  {os.path.basename(dest)}: "
                                 f"{got/1e6:.1f}/{total/1e6:.1f} MB "
                                 f"({pct:.0f}%)")
                sys.stdout.flush()
    sys.stdout.write("\n")
    sz = os.path.getsize(dest)
    if expected is not None and sz != expected:
        raise IOError(f"{dest}: 大小 {sz:,} != 预期 {expected:,}，"
                      f"文件可能损坏，请删除后重试")
    print(f"  [ok] {os.path.basename(dest)} ({sz:,} B)")
    return sz


def fetch_data(out_dir: str, force: bool = False) -> dict:
    """下载全部 3 个 CSV 到 out_dir，校验大小。返回 {文件名: 字节数}。"""
    os.makedirs(out_dir, exist_ok=True)
    print(f"下载 MaleCNS 子集数据 -> {os.path.abspath(out_dir)}")
    sizes = {}
    for name, url in DATA_URLS.items():
        dest = os.path.join(out_dir, name)
        if force and os.path.exists(dest):
            os.remove(dest)
        sizes[name] = _download_one(url, dest)
    print("完成。用法：FlyInstinct.from_malecns('<out_dir>/edges.csv')")
    return sizes


def main(argv=None):
    p = argparse.ArgumentParser(
        description="下载 MaleCNS 真实连接组子集 (25MB, 3 个 CSV)")
    p.add_argument("--out", default="data", help="输出目录 (默认 ./data)")
    p.add_argument("--force", action="store_true", help="删除已有文件重新下载")
    a = p.parse_args(argv)
    fetch_data(a.out, force=a.force)


if __name__ == "__main__":
    main()
