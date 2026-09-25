# 发布操作清单（逐步版）

> 定位：**MIT 开源 + open-core 收费**。免费层（GitHub/PyPI）是流量入口和信任状；收费层（Gumroad）卖"下好调好的即用包 + 商业授权 + 持续更新"。
> 本清单按顺序执行，每一步都有具体命令。预计手动操作总耗时约 40 分钟（不含内容创作）。

---

## 第 0 步：准备账号与工具

| 账号 | 网址 | 用途 |
|---|---|---|
| GitHub | https://github.com/signup | 代码主仓库（信任状） |
| PyPI | https://pypi.org/account/register/ | `pip install fly-instinct` 入口 |
| Gumroad | https://gumroad.com | 收费渠道（直链 10%+$0.50，平台代扣销售税） |

本机工具：

```bash
# git 已装（2.55）。上传 PyPI 需要 twine（发布前装一次即可）：
pip install twine build
```

---

## 第 1 步：推 GitHub（免费层主阵地）

```bash
cd fly-instinct

# 1) 初始化并提交（.gitignore 已排除 data/ 大文件和构建产物）
git init
git add .
git commit -m "fly-instinct v0.1.0: instinct engine driven by real MaleCNS connectome"

# 2) 在 github.com 上新建空仓库 fly-instinct（Public，不勾 README），然后：
git branch -M main
git remote add origin https://github.com/roblitz-spec/fly-instinct.git
git push -u origin main
```

推完后做两件事（网页上点）：

1. **仓库描述（About）**：`Instinct Engine — a frozen, non-learning "instinct" signal source driven by the real fruit-fly (MaleCNS) connectome. 基于真实果蝇连接组的"本能"信号源：权重冻结、不学习、纯本地。`
2. **README 顶部加付费入口**（见第 4 步的话术模板）。

> 注意：`data/` 里的 25MB CSV 已被 `.gitignore` 排除，仓库里只有 `data/.gitkeep`。用户 clone 后跑 `python -m fly_instinct fetch-data --out data` 自动下载——这正是我们设计的流程，**不是遗漏**。

---

## 第 2 步：发 PyPI（让 `pip install` 生效）

```bash
cd fly-instinct

# 1) 构建（产出 dist/ 里的 wheel + sdist）
python -m build

# 2) 安装 twine（若未装）并上传
pip install twine
python -m twine upload dist/*
# 按提示输入 PyPI 用户名 + API token
```

API token 获取：登录 PyPI → 头像 → **Account settings → API tokens → Add API token**，权限选 "Entire account" 或针对 `fly-instinct` 项目。

**上传前最后一道检查**：`pyproject.toml` 的作者与 Homepage 已填实（作者 roblitz / Homepage 指向 roblitz-spec 仓库）。注意 PyPI 上传后改元数据需要发新版本（0.1.1+），所以确认无误再传。

**上传后验证**（新 venv 里，模拟真实用户）：

```bash
python -m venv verify && verify\Scripts\activate
pip install "fly-instinct[demo]"
python -m fly_instinct fetch-data --out data
python examples/poc_real.py   # 需要把 examples 从仓库拷一份，或直接在 GitHub 仓库里跑
```

验证 `pip install fly-instinct` 能装上、`fly-instinct-fetch-data` 命令能跑通，即发布成功。

---

## 第 3 步：上架收费渠道（open-core 的"core"）

卖的东西统一叫 **"即用完整包"**，内容：

1. 下好、校验过的 **完整 1.05GB curated 连接组**（`connectome-weights-male-cns-v1.0-minconf-0.5.feather`，含接入脚本，见 MODEL.md）
2. 预调好的刺激/读出层配置（逃避回路、趋糖回路等预设）
3. 商业使用授权书（企业客户可闭源集成、不强制开源其代码）
4. 中英文档 + 一次问题支持

**Gumroad**：

1. 创建 Product → Digital，定价 **$6.9**
2. 描述用 README 英文版要点 + 诚实边界
3. 交付：zip（完整包）自动发下载链接
4. 注意 Gumroad 是 Merchant of Record，销售税它代扣，你不用处理各国税务

---

## 第 4 步：免费仓库 README 顶部加付费入口

在 README.md 的标题下加一行（Gumroad 链接创建后替换）：

```markdown
> 想要**下好、接好、调好**的完整 1.05GB 连接组 + 商业授权？
> → [Gumroad（$6.9）](链接)
```

---

## 第 5 步：内容带流量（真正的增长引擎）

小众题材没有自然流量，靠内容。选题建议（按你写宣传稿的强项排）：

1. **B站/视频号短视频（3–5 分钟）**：《我把果蝇大脑下到了本地，它比随机数更像活的》——主图 + 三方对比是现成素材
2. **公众号/知乎图文**：《果蝇大脑开源了，但那些让它玩游戏的视频都在骗你》——讲"真数据 vs 设计出来的"，立场就是本项目
3. **HuggingFace 模型卡**：搜 "fruit fly" / "connectome" 的人会逛 HF，建个 model card 指回 GitHub
4. **ModelScope（魔搭）**：同上，国内镜像，顺手

每篇内容结尾都带 GitHub 链接，README 顶部带付费入口——漏斗就闭合了。

---

## 第 6 步：合规红线（每次发东西前扫一眼）

- [ ] 署名：MaleCNS v1.0, Janelia FlyEM, https://male-cns.janelia.org, CC-BY-4.0（LICENSE.md 里有现成块）
- [ ] 不夸大：只说"基于真实连接组的本能式反应源"，**不说**"果蝇大脑/有意识/能学习/AGI"
- [ ] 数据不独占：CC-BY 数据别人也能用，你卖的是工程 + 配置 + 授权
- [ ] 代码 MIT：付费包里的代码部分同样保持 MIT，收费点是数据整理 + 商业授权，不是代码本身

---

## 完成标志

- [ ] GitHub 仓库公开可访问，README 带付费入口
- [ ] `pip install fly-instinct` 在全新 venv 里可安装可运行
- [ ] Gumroad 有一个上架产品
- [ ] 至少发了一篇带 GitHub 链接的科普内容
