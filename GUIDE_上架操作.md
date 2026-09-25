# 上架操作教程（爱发电 + Gumroad）

> 本文精确到"点哪个按钮、填什么字段"，照做即可。
> 前提：付费 zip 包已打好（见下文"打包"节），主图 `instinct_poc_real.png` 已准备。

---

## 一、打包付费产品 zip

在 `fly-instinct/` 目录下执行：

```bash
mkdir -p package/fly-instinct-full/data
# 1. 数据（1.1GB）
cp data_full/connectome-weights-male-cns-v1.0-minconf-0.5.feather package/fly-instinct-full/data/
cp data_full/body-neurotransmitters-male-cns-v1.0.feather package/fly-instinct-full/data/
cp data_full/body-annotations-male-cns-v1.0-minconf-0.5.feather package/fly-instinct-full/data/

# 2. 代码
cp -r fly_instinct package/fly-instinct-full/
cp pyproject.toml package/fly-instinct-full/
cp -r examples package/fly-instinct-full/

# 3. 授权 & 文档
cp LICENSE.md package/fly-instinct-full/
cp LICENSE_COMMERCIAL.md package/fly-instinct-full/
cp README.md package/fly-instinct-full/

# 4. 快速启动脚本
cp GUIDE_快速启动.md package/fly-instinct-full/QUICKSTART.md  # 见下方模板

# 5. 压缩
cd package
zip -r fly-instinct-full-0.2.0.zip fly-instinct-full/
cd ..
```

产出：`package/fly-instinct-full-0.2.0.zip`（~1.1GB）

### QUICKSTART.md 模板

```markdown
# Fly-Instinct Full Package · 快速启动

## 环境要求
- Python 3.10+
- 内存 ≥ 16 GB（加载完整连接组峰值 ~6 GB）
- 依赖安装：
  ```bash
  pip install numpy scipy pandas pyarrow
  ```

## 一行运行

```python
from fly_instinct import from_full
import numpy as np

fly = from_full(
    "data/connectome-weights-male-cns-v1.0-minconf-0.5.feather",
    nt_feather="data/body-neurotransmitters-male-cns-v1.0.feather",
    ann_feather="data/body-annotations-male-cns-v1.0-minconf-0.5.feather",
)

# 给一段刺激（200 步，后 80 步有输入）
stim = np.zeros(200)
stim[120:] = 1.0
reaction, spikes = fly.react(stim)
print(f"peak={reaction.max():.3f}")
```

## 用预设

```python
from fly_instinct import run_preset
out = run_preset("escape", edges_path="data/...feather", use_real=True)
```

## 数据出处（CC-BY 4.0 署名要求）
> MaleCNS v1.0, Janelia Research Campus (HHMI), https://male-cns.janelia.org/
```

---

## 二、爱发电上架（国内，¥39）

### Step 1：注册 & 进入产品管理

1. 打开 https://afdian.com → 右上角「登录」→ 手机号注册
2. 登录后点右上角头像 → **「创作者中心」**
3. 左侧菜单 → **「产品」** → 点 **「创建产品」**

### Step 2：填写产品信息

| 字段 | 填什么 |
|---|---|
| 产品名称 | `Fly-Instinct 果蝇连接组"本能引擎"完整包` |
| 产品副标题 | 真实果蝇大脑连接组 · 不学习 · 纯本地 · 商业授权 |
| 产品类型 | **数字产品**（不是"支持/赞赏"） |
| 定价 | ¥39（一次性买断） |
| 产品描述 | 直接贴 `SALES_COPY.md` 第一节"中文文案"的"这是什么 + 卖点 + 包含什么"段 |
| 封面图 | 上传 `instinct_poc_real.png`（真实数据三方对比图） |
| 补充图片 | 可再加 `instinct_poc.png` |

### Step 3：设置交付方式

- 交付类型选 **「网盘链接」**（爱发电支持百度网盘/阿里云盘/腾讯微云）
- 把 `fly-instinct-full-0.2.0.zip`（1.1GB）传到你的网盘
- **注意**：网盘文件需设为"链接分享"（非"仅密码"），购买后自动发链接+提取码
- 如果 1.1GB 超网盘免费分享限制：
  - 阿里云盘：个人版 20GB 够用
  - 百度网盘：普通用户限速但能下；或用"转存"方式

### Step 4：发布

- 检查预览页 → 点 **「发布」**
- 发布后得到产品链接：`https://afdian.com/item/xxxxx`
- 把这个链接填回 GitHub README 顶部的付费入口占位

### 收款设置

- 创作者中心 → **「收款账户」** → 绑定银行卡/支付宝
- 爱发电抽成 6%（¥39 → 你收 ¥36.66）

---

## 三、Gumroad 上架（海外，$5.9）

### Step 1：注册

1. 打开 https://gumroad.com → **Sign up**（可用 GitHub 账号一键注册）
2. 完成邮箱验证

### Step 2：创建产品

1. 左侧 **Products** → **New product**
2. 填写：

| 字段 | 填什么 |
|---|---|
| Product name | `Fly-Instinct — Full Connectome Package` |
| Type | **Digital product** |
| Price | $5.90（固定价；也可勾 "Pay what you want" 最低 $5.90） |
| Description | 贴 `SALES_COPY.md` 第二节"English Copy"全文 |
| Cover image | 上传 `instinct_poc_real.png`（1200×630 或更大） |
| Files | 上传 `fly-instinct-full-0.2.0.zip` |

### Step 3：上传文件

- 点 **Files** 区域 → 拖入 zip
- **Gumroad 免费账户文件上限 2GB**——1.1GB 没问题
- 上传耗时取决于上行带宽（1.1GB 约 5-30 分钟）

### Step 4：设置 & 发布

- **Pricing**：$5.90 fixed
- **Visibility**：Public（公开可搜索）
- **URL slug**：`fly-instinct-full`（你的产品链接 = `gumroad.com/l/fly-instinct-full`）
- 点 **Publish**

### 收款设置

- Gumroad 是 **Merchant of Record**（销售税它代扣，你不用处理各国 VAT/GST）
- 左侧 **Payouts** → 绑定 PayPal 或银行（PayPal 最简单）
- Gumroad 抽成 10% + $0.50/单（$5.90 → 你收约 $4.81）
- 首次打款有 7 天等待期（防欺诈）

---

## 四、上架后回填链接

两个产品都发布后：

1. **GitHub README.md** 顶部：
   ```markdown
   > 💎 完整包 → [爱发电 ¥39](https://afdian.com/item/xxx) | [Gumroad $5.9](https://gumroad.com/l/fly-instinct-full)
   ```
2. **PyPI 描述**（`pyproject.toml` 的 `description` 或 `readme`）里也加一行
3. commit + push：
   ```bash
   git add README.md
   git commit -m "docs: add paid product links"
   git push
   ```

---

## 五、上架后第一周动作

1. **知乎/公众号发一篇**（`CONTENT_zhihu.md` 已备好）→ 结尾带 GitHub 链接
2. **GitHub 仓库 About** 加一句英文描述 + Topics: `connectome, neuroscience, game-ai, generative, reservoir-computing`
3. **HuggingFace** 建个 model card（搜 "fly connectome" 的人会逛）→ 指回 GitHub
4. 有人买了 → 按交付方式自动发文件 → 收到 5 星好评截图放 README

---

## 六、常见问题

**Q: 1.1GB 文件在爱发电能自动发吗？**
A: 爱发电数字产品支持"网盘链接"交付（不是直接传文件）。你上传到阿里云盘/百度网盘后，把分享链接填进产品交付设置，购买后自动发给买家。

**Q: Gumroad 能传 1.1GB 吗？**
A: 能。Gumroad 免费账户单文件上限 2GB。上传走 HTTPS 直传，速度取决于你的上行。

**Q: 需要交税吗？**
A: Gumroad 是 MoR（Merchant of Record），海外销售税它代扣代缴，你收的是税后金额。国内爱发电走微信/支付宝，个人创作者小额（年 < 10 万）通常不追税。

**Q: 数据是 CC-BY 的，我收费卖合法吗？**
A: 合法。CC-BY 允许"收费再分发"（只要署名 + 同样 CC-BY 许可）。你卖的不是数据本身（免费可得），是"下好 + 接好 + 商业授权 + 支持"的工程服务。
