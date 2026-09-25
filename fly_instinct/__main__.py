"""支持：
    python -m fly_instinct fetch-data [--out data] [--force]
    python -m fly_instinct [--out data] [--force]   # 省略子命令亦可
"""
import sys

from .datafetch import main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fetch-data":
        sys.argv.pop(1)
    main()
