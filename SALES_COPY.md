# SALES_COPY.md · 「即用完整包」上架文案

> 用途：Gumroad / 知乎 / 公众号 上架与引流文案。
> 原则：**不夸大**（不吹成“果蝇大脑/有意识/能学习”），把“诚实边界”当**信任状**；
> 把不足转成正面表述（“不学习” → “纯本地、确定性、可复现”）。

---

## 一、中文文案（知乎 / 公众号 直接贴）

### 标题（任选）
- **我把果蝇大脑下到了本地——它比随机数更像“活的”**
- **一个不学习、但像活物一样会反应的本能引擎**
- **真实果蝇连接组，装进你的项目里**

### 一句话
> 用一个**真实果蝇大脑的连接组**（权重冻结、不训练）造一个“本能引擎”：
> 给需要“活的、有结构的、非学习反应”的项目，一个**比随机数更活、比脚本更不可预测**的信号源。

### 这是什么
它是一个**可复用的“本能”信号源**：把输入刺激喂进一个**权重永久冻结、不学习**的递归网络
（核心是**真实果蝇 MaleCNS 连接组**），得到一段“像活物本能反应”的信号——
既不是白噪声（死的、无结构），也不是脚本规则（可预测、一眼看穿）。

### 它不是什么（这是卖点，不是缺点）
- **不是**“上传的果蝇大脑”，**没有意识、不会学习、没有记忆**——它是**静态线路图 + 冻结动力学**。
- 正因如此：**纯本地、零联网、零 API、零密钥、确定性、可复现**——给同样的输入，永远得到同样的输出。
- 网上那些“果蝇玩 Doom / 开车”的 viral 效果，本质是“真实线路图 + 开发者叠上去的简化动力学与动作映射”，
  **行为多为设计出来的**；本包把这条“真数据 + 诚实边界”的路走正。

### 卖点
1. **真数据**：核心是 MaleCNS 真实连接组（完整校对版 ~16.67 万神经元 / ~2560 万条连接），不是替身、不是随机权重。
2. **下好接好调好**：完整 1.05GB 连接组已下载、已校验、已接好，配好预调“本能”预设，**开箱即用**。
3. **纯本地可复现**：零联网、零密钥、数据不外传；给定输入，输出确定。
4. **一行接入**：`reaction, spikes = fly.react(stimulus)`，拿到“本能反应”信号即可。
5. **商业授权**：可闭源集成进你的产品，不强制开源你的代码（见 `LICENSE_COMMERCIAL.md`）。

### 包含什么（「即用完整包」）
- ✅ 下好、校验过的**完整 MaleCNS v1.0 连接组**（`connectome-weights-male-cns-v1.0-minconf-0.5.feather`，1.05GB）
- ✅ 4 个预调“本能”预设：**逃避 / 趋糖 / 惊跳 / 探索**（换预设 = 换一种本能）
- ✅ 完整连接组接入工具（下载/断点续传/校验 + feather→引擎一条龙）
- ✅ 商业使用授权书（可闭源集成）+ 数据 CC-BY 署名合规
- ✅ 中英文档 + 一次问题支持

### 适用场景
- 游戏 NPC 的**本能行为**（威胁→逃、奖励→趋、惊吓→跳、闲逛→探索）
- 生成艺术 / ComfyUI 的**有机扰动**（比噪声有结构，比脚本不可预测）
- 交互装置（“碰它，它像活物一样反应”）
- 科普 demo / 教学（展示“真实连接组 + 非学习动力学”）

### 定价
- **Gumroad：$6.9**（一次性，含完整连接组 + 全部预设 + 商业授权 + 一次支持）

> 定价说明：本项目是 open-core，免费 PyPI 已含完整连接组下载工具、4 个预设和全部代码（MIT 本可闭源商用），付费包真正多出的是"帮你下好的 1.05GB 数据 + 盖章商业授权书 + 一次支持"。定价卡在不破坏行情的最低线（冲动下单不心疼、又不像赠品）。

### 交付
- Gumroad 购买后自动发送下载链接（完整包 zip，含 1.05GB 数据 + 代码 + 商业授权）；
- 商业授权编号随包附带（`LICENSE_COMMERCIAL.md`）。

---

## 二、English Copy（Gumroad 直接贴）

### Title
**Fly-Instinct — a frozen, non-learning “instinct” engine driven by the real fruit-fly brain**

### One-liner
> A reusable “instinct” signal source: feed a stimulus into a **weight-frozen, non-learning**
> recursive network built on the **real fruit-fly (MaleCNS) connectome**, and get a signal that is
> **more alive than random noise, less predictable than a script**.

### What it is
A drop-in “instinct” signal source. A stimulus goes into a frozen reservoir (the real fruit-fly
connectome as the recurrent core) and out comes an instinct-style reaction — structured,
non-trivial, and non-learning.

### What it is NOT (this is the selling point)
- Not “an uploaded fly brain”. **No consciousness, no learning, no memory** — it is a
  **static wiring diagram + frozen dynamics**.
- Which means: **fully local, zero network, zero API keys, deterministic, reproducible**.
- The viral “fly plays Doom” demos are a real wiring diagram **plus developer-added dynamics and
  action mapping** — mostly *designed* behavior. This package does the “real data + honest
  boundaries” path properly.

### Selling points
1. **Real data** — the full curated MaleCNS v1.0 connectome (~166k neurons / ~25.6M synapses), not a stand-in.
2. **Ready to run** — the full 1.05 GB connectome, downloaded, verified, and wired up, with tuned presets.
3. **Local & reproducible** — no network, no keys, deterministic output.
4. **One-line integration** — `reaction, spikes = fly.react(stimulus)`.
5. **Commercial license** — closed-source integration allowed; you don’t have to open-source your code.

### What’s in the “Ready-to-Run Full Package”
- The full **MaleCNS v1.0 connectome** (1.05 GB feather), downloaded & verified
- 4 tuned instinct presets: **Escape / Sugar-seeking / Startle / Explore**
- Full-connectome integration tooling (download / resume / verify / load)
- Commercial license (closed-source OK) + CC-BY data-attribution compliance
- Bilingual docs + one round of support

### Use cases
- Game NPC instinct (threat→flee, reward→seek, surprise→startle, idle→explore)
- Generative art / ComfyUI organic perturbation
- Interactive installations (“touch it, it reacts like a living thing”)
- Science-communication demos

### Price
**$6.9** (one-time: full connectome + all presets + commercial license + one round of support)

> This is an open-core project — the free PyPI package already includes the full-connectome download tool, all presets, and all code (MIT, already usable in closed-source products). The paid package adds the pre-downloaded 1.05 GB data + a signed commercial license + one round of support. Priced at the lowest point that still signals real value rather than a giveaway.

### Data attribution (required, CC-BY 4.0)
> The fruit-fly connectome data is from **MaleCNS v1.0** (Janelia Research Campus / HHMI),
> available at <https://male-cns.janelia.org/>, licensed under **CC-BY 4.0**.

---

## 三、上架前最后核对（合规红线）

- [ ] 署名块已放入（MaleCNS v1.0 / Janelia FlyEM / CC-BY 4.0）
- [ ] 全文无“果蝇大脑 / 有意识 / 能学习 / AGI”字样
- [ ] 统一话术：“基于真实连接组的、权重冻结、非学习的本能式反应信号源”
- [ ] 数据 CC-BY 4.0 保持（不得加“禁止再分发”等更严条款）
- [ ] 商业授权书（LICENSE_COMMERCIAL.md）随包提供
- [ ] 主图用 `instinct_poc_real.png`（真实数据三方对比）
