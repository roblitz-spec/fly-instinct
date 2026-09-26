# fly-instinct · 果蝇连接组“本能引擎”

一个**可复用、非学习、纯本地**的“本能”信号源：把输入刺激喂进一个**权重冻结、不训练**的递归网络（核心是**真实果蝇 MaleCNS 连接组子图**），得到一个“像活物本能反应”的信号——**既不是白噪声（死的），也不是脚本规则（可预测）**。

> 定位一句话：它是一个**有结构的、非学习的反应算子**，用于给“需要‘活的反应’”的项目提供信号。
> 它**不是智能、不是大脑、没有意识、不会学习**。

> 💎 想要**下好、接好、调好**的完整 1.05GB 果蝇连接组 **+ 一套线虫（C. elegans）本能** + 4 个预调“本能”预设 + 商业授权？
> → [Gumroad（$6.9）](https://robloxer31.gumroad.com/l/Fly-Instinct)
> （免费层 = 本仓库 + `pip install fly-instinct`，含 25MB 子集 + 全部代码；付费层 = 完整果蝇连接组即用包 **+ 线虫本能即用包**，两套真大脑一次到手）

---

## 文件结构

```
fly-instinct/
├── pyproject.toml          # 打包配置（pip install . 或从 PyPI 安装）
├── fly_instinct/           # Python 包（发布进 PyPI 的部分）
│   ├── engine.py           #   引擎（FlyInstinct）：冻结递归网络 + LIF 动力学
│   ├── loader.py           #   数据加载：真实 MaleCNS 子集 -> 冻结稀疏矩阵
│   ├── datafetch.py        #   数据下载工具（25MB 子集，断点续传+校验）
│   ├── presets.py          #   预调“本能”预设（逃避/趋糖/惊跳/探索）
│   ├── fullconnectome.py   #   完整 1.05GB 连接组接入（下载+转换+加载）
│   ├── export.py           #   导出 wav/npz/npy（零额外依赖）
│   ├── presets/            #   内置预设 JSON（随包分发）
│   └── __main__.py         #   CLI：info / list / run / export / fetch-data / get-full
├── examples/
│   ├── poc_demo.py         # PoC（替身网络版，150 节点，无需数据）
│   └── poc_real.py         # PoC（真实 MaleCNS 连接组版）
├── data/                   # 真实 MaleCNS 子集（~25 MB，不进 pip 包）
│   ├── edges.csv           #   连接权重图 pre,post,weight（1,587,930 条边）
│   ├── annotations.csv     #   细胞类型/超类（root_id,cell_type,superclass）
│   └── neurotransmitters.csv#  递质（root_id,transmitter,confidence）
├── instinct_poc.png        # 替身版三方对比图
├── instinct_poc_real.png   # 真实数据三方对比图
├── README.md               # 本文件（操作文档）
├── MODEL.md                # 模型说明（架构/数据出处/完整连接组接入）
├── LICENSE.md              # 许可与署名（数据 CC-BY 4.0 + 代码 MIT）
├── LICENSE_COMMERCIAL.md   # 商业使用授权书（随付费完整包提供）
├── SALES_COPY.md           # 上架文案（Gumroad/知乎/公众号）
├── PUBLISH.md              # 发布清单（署名/合规/商用边界）
└── PUBLISH_STEPS.md        # 逐步发布操作（GitHub/PyPI/收费渠道/内容）
```

---

## 安装

**方式 A：pip 安装（发布后）**

```bash
pip install fly-instinct          # 核心（numpy + scipy）
pip install fly-instinct[demo]    # 含 matplotlib，可跑 examples 出图
```

**方式 B：从本仓库安装**

```bash
cd fly-instinct
pip install .                      # 或 pip install .[demo]
```

**下载数据（一次性，25MB）**

```bash
python -m fly_instinct fetch-data --out data
# 或安装后的命令行入口：
fly-instinct-fetch-data --out data
```

> 数据是 **CC-BY 4.0 的 MaleCNS 子集**（上游 Janelia），体积 25MB 故不进 pip 包；
> 下载走 HuggingFace 镜像（国内可达），断点续传 + 大小校验，已存在则自动跳过。

**纯本地、无 API、无密钥、数据不外传。** 计算全部在本机 CPU 完成（唯一联网动作是上面这一次性数据下载）。

---

## 10 行跑出第一个文件（wav / npz / npy）

信号不只是数组——`render()` / `save_reaction()` 把它变成**能直接用的文件**（零额外依赖，只用 numpy + 标准库 `wave`）：

```python
from fly_instinct import render

# 一行：跑 escape 预设，存成 4 秒音频包络
# （有 data/edges.csv 就用真实连接组，没有则自动落回 150 节点替身，开箱即跑）
render("escape", "escape.wav")

# 换格式：原始反应 + 每神经元发放 + 元数据（喂合成器 / 草图 / 游戏 / 研究）
render("sugar", "sugar.npz")
```

命令行（装完即用，不用先写代码）：

```bash
python -m fly_instinct info                    # 版本 / 数据档 / 预设一览
python -m fly_instinct export escape out.wav   # 一行出 .wav / .npz / .npy
python -m fly_instinct run escape --save out.npz
python -m fly_instinct export startle out.wav --stand-in   # 强制替身（秒级，不读数据）
```

| 格式 | 内容 | 用途 |
|---|---|---|
| `.wav` | 反应拉伸成 4s 音频包络（16-bit 单声道） | 直接听 / 喂合成器 / 控制信号 |
| `.npz` | 原始 `reaction (T,)` + `spikes (n,T)` + 元数据 | 驱动代码（合成器 / 草图 / NPC / 研究） |
| `.npy` | 仅原始 `reaction (T,)` | 最小接入 |

> 完整版连接组（~1.05GB）`react()` 会自动跳过发放矩阵以省内存，此时 `.npz` 只含 `reaction` + 元数据（仍完全可用）。

---

## 快速开始：跑 PoC

```bash
cd fly-instinct

# 真实连接组版（推荐，需先 fetch-data 到 data/）
python examples/poc_real.py     # 自动选增益 + 三方对比 + 输出 instinct_poc_real.png

# 替身版（不需要数据，150 节点，秒级）
python examples/poc_demo.py     # 输出 instinct_poc.png
```

`poc_real.py` 在同一“威胁逼近”刺激下对比三种反应：

| 反应 | 响应延迟* | lag-1 自相关（结构） | 与刺激相关 | 威胁期发放率 |
|---|---|---|---|---|
| 纯随机（白噪声·死的） | 47 | ≈0 | ≈0 | — |
| 纯脚本（规则·可预测） | 131 | 1.000 | 0.998 | — |
| **真实本能（MaleCNS·非学习）** | 128 | 0.551 | −0.204 | 15.9% |

\* 响应延迟 = 相对刺激前基线上升超过 0.25 的第一个时间步（威胁在 t=120 出现）。

---

## 作为插件使用（一行）

```python
from fly_instinct import FlyInstinct

# 真实连接组（推荐）
fly = FlyInstinct.from_malecns(
    "data/edges.csv",
    ann_path="data/annotations.csv",
    nt_path="data/neurotransmitters.csv",
    seed=7, in_neurons=800, gain=2.0, spectral_radius=0.9,
)
reaction, spikes = fly.react(stimulus)   # stimulus: 1D/2D 数组
# reaction: (T,) 本能反应强度（静息基线=0，峰值=1；被抑制时可能有小幅负值）
# spikes:   (n, T) 每个神经元发放（0/1），供可视化

# 或替身版（不需要数据）
fly = FlyInstinct(n_neurons=150, seed=7, gain=6.0)
reaction, spikes = fly.react(stimulus)
```

**接口约定**
- `fly.react(stimulus, noise=0.0, smooth=1) -> (reaction, spikes)`
- 权重在构造时**永久冻结**，`react()` 不做任何学习；给定 `seed`+刺激，输出**确定性**（除非显式 `noise>0`）。
- `noise>0` 可叠加一点“热噪声”，更接近真实生物（可选）。

**典型用途**：游戏 NPC 本能行为、生成艺术/ComfyUI 的有机扰动、交互装置（“碰它，它有本能反应”）、科普 demo。

---

## 预调“本能”预设（4 种开箱即用）

内置 4 个预设，**换预设 = 换一种本能**（权重仍是同一个冻结网络，`react()` 依然不学习）：

| 预设 | 刺激 | 用途 |
|---|---|---|
| `escape` 逃避 | 突发威胁（t=120 起恒定强刺激） | 威胁→强反应（PoC 同款） |
| `sugar` 趋糖 | 渐近奖励（线性爬升后保持） | 靠近奖励源→反应逐步增强 |
| `startle` 惊跳 | 短时尖峰（仅 5 步强刺激） | 惊吓→快速自衰减反应 |
| `explore` 探索 | 持续低噪（基线+热噪声） | 无明确威胁→自发探索节律 |

```python
from fly_instinct import run_preset, list_presets

print(list_presets())   # ['escape', 'explore', 'startle', 'sugar']

# 真实连接组版（需先 fetch-data）
out = run_preset("escape", edges_path="data/edges.csv",
                 ann_path="data/annotations.csv", nt_path="data/neurotransmitters.csv")
reaction = out["reaction"]   # (T,) 反应强度，落在 [-0.5, 1]（负=抑制/冻结，正=激活）

# 替身版（不需要数据，秒级）
out = run_preset("escape", use_real=False)

# 自定义预设：写一个 JSON（结构同内置），或用完整路径加载
out = run_preset("my_preset.json")
```

> 预设输出统一压到 `[-0.5, 1]`：`1`=最强激活，`0`=静息，负值=被抑制（冻结）。要原始信号直接调 `engine.react()`。

---

## 接入完整版 MaleCNS（1.05 GB）

当前 `data/` 是**真实子集**（约 1 万节点，够跑、够真）。要升级到**完整校对版**（16.67 万神经元 / 2560 万条连接），用官方 **1.05 GB** 连接权重文件：

**一键接入（0.2.0 起内置）**

```bash
pip install "fly-instinct[full]"                 # 加 pandas+pyarrow（feather 转换）
python -m fly_instinct get-full --out data_full --to-csv   # 下载 + 转 CSV
# 或下载+转+直接用 escape 预设跑一次：
python -m fly_instinct get-full --out data_full --run
```

代码方式：

```python
from fly_instinct import from_full
fly = from_full("data_full/connectome-weights-male-cns-v1.0-minconf-0.5.feather")
reaction, spikes = fly.react(stimulus)
```

**下载地址（官方，CC-BY 4.0）**
- 官方下载页：<https://male-cns.janelia.org/download/>
- 直链（GCS，可断点续传）：
  `https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5.feather`
- 文件：`connectome-weights-male-cns-v1.0-minconf-0.5.feather`（feather 格式，列同 `pre,post,weight`）

> 说明：`storage.googleapis.com` 在部分网络（含中国大陆）可能不可达；届时可用可达的镜像/代理下载该文件，**只要列名仍是 pre/post/weight 即可**。

**接入步骤**
1. 下载 `.feather` 到本地。
2. 转成 CSV（或扩展 loader 直接读 feather）：
   ```python
   import pandas as pd
   df = pd.read_feather("connectome-weights-male-cns-v1.0-minconf-0.5.feather")
   df.to_csv("full_edges.csv", index=False)   # 列：pre,post,weight
   ```
3. 用同一接口加载（完整版的 `annotations`/`neurotransmitters` feather 同理转 CSV 后传入）：
   ```python
   from fly_instinct import FlyInstinct
   fly = FlyInstinct.from_malecns("full_edges.csv",
                                  ann_path="full_annotations.csv",
                                  nt_path="full_neurotransmitters.csv",
                                  seed=7, in_neurons=2000, gain=2.0, spectral_radius=0.9)
   reaction, spikes = fly.react(stimulus)
   ```

**代价与注意**
- 完整版稀疏矩阵约 2560 万非零元，加载后内存数百 MB；单次 `react(T)` 计算量约为当前子集的 ~16 倍，建议 T 不要太大、机器内存 ≥ 8 GB。
- 完整版的**递质符号仍是先验预测**（见 MODEL.md 诚实边界）。

---

## 附：线虫（C. elegans）本能 · 第二套真大脑（付费包内含）

> 付费 $6.9 的包里，除完整果蝇连接组外，**另附一套独立的线虫"本能"引擎**（解压后 `worm-instinct/` 与 `fly-instinct/` 平级）。
> 它是同一套方法论（权重冻结、非学习的递归反应算子）接在**另一只真实动物**的完整连接组上——
> 让一个产品里能同时驱动"果蝇"和"线虫"两种本能信号源。

**它是什么**
- 数据：**完整 C. elegans 连接组**（White, Southgate, Thomson & Brenner 1986, *Phil. Trans. R. Soc. Lond. B* 314:1-340）——309 个神经元 / 2960 条连接（2386 化学 + 575 电突触）。
- 递质标注：每个神经元的兴奋/抑制极性来自 **Wang et al. 2024 神经递质图谱**（eLife 13:RP95402，开放获取）——33 个 GABA 能神经元为抑制（占比 ~10.7%），其余兴奋/调质。
- 体积极小：连接组数据仅 **~268 KB**，**已内置**，开箱即跑，无需下载、无需联网。

**和果蝇版的区别**

| | 果蝇 fly-instinct | 线虫 worm-instinct |
|---|---|---|
| 物种 | 果蝇（MaleCNS） | 线虫（C. elegans） |
| 规模 | 16.67 万神经元 / 2560 万边（完整 1.05GB） | 309 神经元 / 2960 边（268KB） |
| 递质 | Janelia 官方先验预测 | Wang 2024 scRNA 图谱 |
| 速度 | 完整版单次反应分钟级 | **毫秒级（200 步 ~10ms，可 60fps 实时）** |
| 数据 | 需内置/下载 | 内置，零下载 |

**快速用（解压后 `worm-instinct/` 与 `fly-instinct/` 平级，各自独立安装）**

```python
# 方式 A：直接加路径
import sys; sys.path.insert(0, "../worm-instinct")   # 从 fly-instinct/ 目录指向平级的线虫目录
import worm_instinct as w

# 方式 B：先 pip install -e ../worm-instinct，然后直接 import worm_instinct

worm = w.from_white1986(seed=7)
print(worm.meta["inhibit_frac"])   # ~0.107（10.7% GABA 能抑制）

# 一行出文件（.wav 4s 音频 / .npz 原始数据）
w.render("escape", "worm_escape.wav")
w.render("forage", "worm_forage.npz")
```

内置 4 个预设：`escape` 逃避 / `forage` 觅食 / `turn` 转向 / `wander` 巡游——换预设即换一种本能，权重仍冻结、不学习。

> 诚实边界同果蝇版：输出是**冻结结构对刺激的非学习反应**，不具备智能/记忆/学习/意识；递质符号来自 Wang 2024 图谱预测而非逐突触实验测定。请勿以“线虫大脑 / 有意识 / 能学习”宣传。

---

## 许可与署名（必须）

底层连接组数据为 **MaleCNS v1.0（Janelia FlyEM），CC-BY 4.0，需署名**；本包代码为你可自定授权的衍生作品。商用/分发前请阅读 `LICENSE.md` 与 `PUBLISH.md`。

## 诚实声明

本引擎输出的是“**冻结结构对刺激给出的、非学习的本能式反应**”。它**不具备智能、记忆、学习或意识**；递质兴奋/抑制符号是**先验预测**而非实验测定。请勿以“果蝇大脑 / 有意识 / 能学习”等措辞宣传。
