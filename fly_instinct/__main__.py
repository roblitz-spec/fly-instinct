"""支持：
    python -m fly_instinct fetch-data [--out data] [--force]   # 下载 25MB 子集
    python -m fly_instinct get-full  [--out data_full] [--to-csv] [--run]  # 完整 1.05GB
    python -m fly_instinct [--out data] [--force]              # 省略子命令 = fetch-data
"""
import sys

from .datafetch import main as _fetch_main
from .fullconnectome import main as _full_main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "get-full":
        sys.argv.pop(1)
        _full_main()
    else:
        if len(sys.argv) > 1 and sys.argv[1] == "fetch-data":
            sys.argv.pop(1)
        _fetch_main()
