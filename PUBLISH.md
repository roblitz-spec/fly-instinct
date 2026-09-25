# PUBLISH.md · 发布清单

## 0. 发布物清单（打包内容）

```
fly-instinct/
├── fly_instinct.py          引擎
├── malecns_loader.py        数据加载
├── poc_demo.py              替身版 PoC（无数据依赖）
├── poc_real.py              真实数据 PoC
├── instinct_poc.png         替身版对比图
├── instinct_poc_real.png    真实数据对比图（对外展示主图）
├── data/                    真实 MaleCNS 子集（~25 MB，CC-BY 4.0）
│   ├── edges.csv
│   ├── annotations.csv
│   └── neurotransmitters.csv
├── README.md                操作文档
├── MODEL.md                 模型说明
├── LICENSE.md               许可与署名
└── PUBLISH.md               本文件
```

## 1. 发布前 checklist（逐项打勾）

- [ ] **署名到位**：README/MODEL/LICENSE 均含 MaleCNS v1.0 + Janelia + CC-BY 4.0 + 子集出处（见 LICENSE.md A 部分）。
- [ ] **数据保持 CC-BY 4.0**：未对 `data/` 施加“禁止再分发/禁止商用”等更严条款。
- [ ] **代码授权已选定**：MIT（开源）或专有（闭源卖产品）——二选一并写入 LICENSE.md B 部分，替换 `<你的名字/团队>`。
- [ ] **无夸大措辞**：全篇无“果蝇大脑 / 有意识 / 能学习 / AGI”；统一用“基于真实连接组的本能式反应源 / 有机扰动源”。
- [ ] **完整性**：`data/` 三个 CSV 的 sha256 与 MODEL.md 记录一致。
- [ ] **可复现**：干净环境 `pip install numpy scipy matplotlib` 后 `python poc_real.py` 能跑出图。
- [ ] **对外主图**：`instinct_poc_real.png` 已生成、中文显示正常。

## 2. 定位与对外话术（诚实版）

- **一句话**：用**真实果蝇连接组**（权重冻结、不训练）造一个“本能引擎”——给需要“活的、有结构的、非学习反应”的项目提供信号。
- **三个卖点**：
  1. **真数据**：核心是 MaleCNS 真实连接组子图，不是替身。
  2. **纯本地**：零联网、零 API、零密钥、数据不外传、确定性可复现。
  3. **即插即用**：一行 `fly.react(stimulus)` 拿到“本能反应”信号。
- **适用场景**：游戏 NPC 本能行为、生成艺术/ComfyUI 有机扰动、交互装置、科普 demo。
- **明确不卖**：智能、意识、学习、记忆。（这是边界，也是格调）

## 3. 建议发布渠道（按目标选）

| 目标 | 渠道 | 说明 |
|---|---|---|
| 开源攒口碑 | **GitHub** | 代码 + 文档；`data/` 用 Git LFS 或放 HF 链接 |
| 模型/数据分发 | **HuggingFace**（dataset） | 放 `data/` + 代码，CC-BY 4.0，附 README |
| 作为 Python 包 | **PyPI** | 把 `fly_instinct` 做成包；`data/` 不打包，改运行时下载/引用 |
| 商业化产品 | 自有站点 / 插件商店 | 闭源引擎 + CC-BY 数据署名，卖“产品/服务” |

## 4. 数据体积与分发建议

- 子集 ~25 MB：**适合直接随包分发**（GitHub LFS / HF / zip 均可）。
- 完整版 1.05 GB：**不随包分发**，README 里给官方下载链接，让用户自行下载（见 MODEL.md 第 4 节）。
- 若上 HF：把 25 MB 子集放 dataset，代码放 repo，互相引用。

## 5. 上架收费前的最后一步

- 用 LICENSE.md 选定**代码授权**；数据部分固定 CC-BY 4.0 + 署名。
- （强烈建议）正式收费前做一次**快速合规审查**，核对署名与“不得再限制”表述。
