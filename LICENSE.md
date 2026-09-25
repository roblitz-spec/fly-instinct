# LICENSE.md · 许可与署名

本包由**两部分**组成，许可不同，发布时**都要带上**。

---

## A. 连接组数据 —— CC-BY 4.0（不可改、必须署名）

`data/` 下的连接组数据源自 **MaleCNS v1.0（Janelia FlyEM）**，许可为 **CC-BY 4.0**。
CC-BY 4.0 **允许**：商用、修改、分发、做衍生作品。
CC-BY 4.0 **要求**：署名；且**不得**施加比 CC-BY 更严格的限制（例如不能禁止他人再分发数据）。

**发布时必须包含的署名块（可直接复制）：**

> 本软件使用的果蝇连接组数据来自 **MaleCNS v1.0**（成年雄性果蝇中枢神经连接组），
> 由 Janelia Research Campus / Howard Hughes Medical Institute 提供，
> 来源 <https://male-cns.janelia.org/>，许可 **CC-BY 4.0**。
> 本包内的 25 MB 子集取自 <https://huggingface.co/datasets/nosuchstudios/fruit-fly-brain-runtime>（CC-BY 4.0）。

> ⚠️ 如果你把 `data/` 里的 CSV 随包一起分发，这些文件本身仍是 CC-BY 4.0，**不能**用“禁止再分发”之类的条款限制它们。

---

## B. 本包代码 —— 你的衍生作品（可自定授权）

`fly_instinct.py`、`malecns_loader.py`、`poc_*.py` 是**独立编写的衍生代码**，
**你可以自由选择授权方式**：

- **想开源 / 攒口碑 / 招人**：用 **MIT**（最宽松，允许商用、闭源集成）。
- **想闭源卖产品 / 卖服务**：可用**专有许可**（保留所有权利，仅授予使用许可），
  但**数据部分（A）仍须保持 CC-BY 4.0 + 署名**，不能把数据锁死。

### 代码默认授权（MIT，可替换）

```
MIT License

Copyright (c) 2026 <你的名字/团队>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> 把 `<你的名字/团队>` 换成你的署名即可。若选专有许可，删掉上面的 MIT 段、
> 换成你自己的“保留所有权利 + 使用条款”，但**保留 A 部分的数据 CC-BY 署名**。

---

## 商用边界（一句话）

- ✅ 可以：把“引擎 + 接口 + 体验”做成产品/插件/SaaS 并收费（你卖的是你的工程与产品）。
- ✅ 必须：数据保持 CC-BY 4.0 + 署名；不得夸大（见 MODEL.md 诚实边界）。
- ❌ 不能：宣称拥有/独占“果蝇大脑”数据；用更严条款锁死 CC-BY 数据；以“有意识/能学习”等虚假措辞宣传。

> 本文件不构成法律意见。正式上架收费前，建议花小钱做一次快速合规审查，
> 重点核对署名条款与“不得再限制”的表述。
