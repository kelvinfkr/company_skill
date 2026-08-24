# company-talent-economics（企业人才经济学）

**English: [README.md](README.md)**

一个 agent skill：从公开披露文件出发，重建一家公司的**薪酬分布、高薪人群规模、经济关键岗位、可辩护薪酬区间和晋升路径**，最终交付一份排版好的 PDF 报告，而不是一大段聊天文字。

它支持**任何国家**的公司，并且**跟随你输入的公司名的语言**来写报告：问 `ソニーグループ` 就出日文报告，问 `Siemens AG` 就出德文报告，问 `小米集团` 就出中文报告。

同一个目录可直接在 **Claude Code**、**Codex** 和 **claude.ai** 上运行。

---

## 你最终拿到什么

一个可审计的产出目录，交付物是 `report.pdf`：

| 文件 | 是什么 |
|---|---|
| `report.pdf` | 排版报告：12 个章节、封面、本地化表格，每个数字都带证据状态 |
| `report.json` | PDF 所依据的结构化模型 |
| `analysis_notes.md` | 九条推理链的完整书面推导，含中间数字 |
| `evidence.jsonl` | 声明级证据台账：每个数字的来源、来源等级、声明类型 |
| `source_manifest.csv` | 检索过的每一个来源——包括查了但没查到的 |
| `model.json` / `population.json` | 分桶模型与蒙特卡洛人数估计 |

方法论只跑一条因果链，顺序不可颠倒：

```
商业模式 → 利润池 → 关键流程 → 关键岗位
→ 组织/职级结构 → 市场替代成本 → 薪酬分布 → 晋升与外部进入路径
```

**头衔不等于薪酬。** 同一个名义职级的两个人，如果控制的利润池、客户关系或技术瓶颈不同，其合理薪酬可以差出一倍以上。所以分析从"钱在哪里赚出来"开始，而不是从一张薪酬调研表开始。

---

## 安装

四选一。第一种最短，第二种最通用。

### 1. Claude Code 插件（推荐）

```
/plugin marketplace add kelvinfkr/company_skill
/plugin install company-talent-economics@company-skill
```

### 2. 克隆后一条命令装好（Claude Code + Codex）

```bash
git clone https://github.com/kelvinfkr/company_skill.git
cd company_skill
bash install.sh
```

会把 skill 软链到 `~/.claude/skills/` 和 `~/.codex/skills/`，然后检查依赖。因为是软链，以后 `git pull` 一次，两个宿主同时更新。

```bash
bash install.sh --claude      # 只装 Claude Code
bash install.sh --codex       # 只装 Codex
bash install.sh --project     # 额外装进当前仓库的 ./.claude/skills
bash install.sh --copy        # 用复制代替软链
bash install.sh --check       # 只检查依赖，不安装
bash install.sh --zip         # 生成 dist/company-talent-economics.zip
bash install.sh --uninstall   # 卸载
```

不想先克隆，一行搞定（脚本会先把仓库拉到 `~/.cache`）：

```bash
curl -fsSL https://raw.githubusercontent.com/kelvinfkr/company_skill/main/install.sh | bash
```

### 3. claude.ai（网页版 / 桌面版）

```bash
bash install.sh --zip
```

然后在 **Settings → Capabilities → Skills → Upload skill** 上传 `dist/company-talent-economics.zip`。

### 4. 手动安装

把 `skills/company-talent-economics/` 复制或软链到以下任一位置：

| 宿主 | 路径 |
|---|---|
| Claude Code（全局） | `~/.claude/skills/company-talent-economics/` |
| Claude Code（单个项目） | `<repo>/.claude/skills/company-talent-economics/` |
| Codex | `~/.codex/skills/company-talent-economics/` |

### 依赖

| | 用于 | 安装 |
|---|---|---|
| Python 3.9+ | 全部脚本 | 多数系统自带 |
| `python-docx` | 渲染报告 | `pip install -r skills/company-talent-economics/requirements.txt` |
| LibreOffice | DOCX → PDF | `apt install libreoffice-writer` / `brew install --cask libreoffice` |
| Noto 字体 | 非拉丁字符 | `apt install fonts-noto-cjk fonts-noto-core` |

除渲染器外全部只用标准库。没有 LibreOffice 时，`render_report.py --docx-only` 仍可产出 DOCX。运行 `bash install.sh --check` 会准确告诉你缺什么、缺了影响哪一步。

> 注意：只装了 `libreoffice-core` 而没装 `libreoffice-writer` 时，转换会以 `source file could not be loaded` 失败。`--check` 会专门识别并提示这种情况。

---

## 怎么用

直接问就行，用什么语言都可以：

```
小米集团的员工薪酬分布是怎样的？年薪超过 100 万的有多少人？
西门子有多少人年薪超过 15 万欧元？哪些岗位撑得起这个价？
ソニーで年収2000万円を超える社員は何人くらいいますか？
```

也可以显式调用：

| 宿主 | 调用方式 |
|---|---|
| Claude Code | `/company-talent-economics <公司名>` |
| Codex | `$company-talent-economics <公司名>` |

### 手动驱动整个 harness

```bash
S=~/.claude/skills/company-talent-economics

python $S/scripts/init_run.py "小米集团" --out ./talent-economics/xiaomi --year 2025
python $S/scripts/check_phase.py ./talent-economics/xiaomi --next   # 打印下一阶段该做什么
# ...照做...
python $S/scripts/check_phase.py ./talent-economics/xiaomi          # 过闸；重复到第 10 阶段
```

`init_run.py` 会从公司名推断语言、司法辖区、货币和高薪阈值，并把选择结果打印出来。任何一项都可以覆盖：

```bash
python $S/scripts/init_run.py "Nestlé S.A." --out ./tmp/nestle --year 2024 \
       --jurisdiction ch --language fr --currency CHF --threshold 250000
```

### 十道闸门，不能跳

`check_phase.py` 是整套流程的骨架。每道闸门在工作没真正做完之前会机械地拒绝放行：来源必须登记、每个数字必须挂证据 id、建模薪酬总额必须与披露的薪酬费用在 ±10% 内对上、`report.json` 里不允许残留 `TODO`。**闸门的输出就是你的待办清单。**

| 阶段 | 闸门 |
|---|---|
| 0 | 主体、语言、司法辖区确认 |
| 1 | 六轮检索已登记；核心事实有出处 |
| 2 | 薪酬包络与利润池已推导 |
| 3 | 职级阶梯已映射 |
| 4 | 各职级带的薪酬证据 |
| 5 | 人群模型跑通且对得上 |
| 6 | 关键岗位三区间诊断 |
| 7 | ≥8 条职业转换记录 |
| 8 | 章程、股权与全部文字段落填完 |
| 9 | 交叉校验与敏感性 |
| 10 | PDF 渲染、目视检查、清单勾完 |

---

## 语言与国家

### 规则

报告**跟随公司名的语言**。如果你提问用的语言和公司名的语言不一致，**以你的语言为准**——你才是读者。

优先级：`--language` → `$CTE_LANG` → 公司名的文字体系和法律主体后缀。

```bash
python $S/scripts/i18n.py detect "台積電股份有限公司"
# {"language": "zh-TW", "confidence": "high", "jurisdiction_hint": "tw", ...}
```

识别会给出置信度。像 `S.A.` 这种法语、西班牙语、葡萄牙语、波兰语共用的后缀，会被判为 `ambiguous`——此时不会硬猜英文，而是改用你提问的语言，实在不明确就问你一句。简繁体是靠公司名里的实际用字区分的，不靠假设（`台` 不算证据，台湾两种写法都常用）。

### 任何语言都能用，其中 12 种有完整排版

这里有两个都叫"语言"的东西，必须分开：

- **正文语言**——分析文字用的语言。**任意语言。**
- **骨架语言包**——章节标题、表头、声明类型标签、数字分组、字体和文字方向。**内置 12 种：** `en zh-CN zh-TW ja ko es fr de pt it ru ar`

没有语言包的语言照样能出完整报告，正文就是那种语言，只是结构性标签回退（`zh-HK` → `zh-TW` → `en`），渲染器会明确提示。数字按各语言的真实说法缩放——`1.2 亿`、`120M`、`1,2 Mrd.`、`2 億`；阿拉伯语和希伯来语走 RTL 排版，表格列序和页脚一并镜像。

**新增一种语言**——一个 JSON 文件，不用改代码：

```bash
python $S/scripts/check_locales.py --new nl   # 从英文生成 locales/nl.json 骨架
# 翻译字符串，保持 key 和每个 {placeholder} 不动
python $S/scripts/check_locales.py            # 校验
```

### 49 个司法辖区

`assets/jurisdictions.json` 按国家记录：用于 `site:` 限定检索的披露平台域名、值得抓取的文件的**当地语言名称**、公司登记机关、货币、高薪阈值先验、雇主社保费率，以及该披露制度**特别好用**或**特别容易误导**的地方。

```bash
python $S/scripts/i18n.py jurisdictions            # 列出全部
python $S/scripts/i18n.py jurisdictions japan      # 查看单条；别名可用
```

别名可用，`us`、`usa`、`america`、`sec`、`nasdaq` 都指向同一条。**新增一个国家**同样只是追加一条数据，不用改代码。

检索天然双语并行：披露文件按当地名称被索引（`有価証券報告書`、`Vergütungsbericht`、`사업보고서`、`Formulário de Referência`），而跨境分析师报道按英文被索引。只搜一边会丢掉一半证据。

注册表里有两个字段是**先验，不是事实**，每次覆盖都要写进 notes：

- `threshold_default`——当地语境下读起来像"高薪"的整数（CNY 1,000,000、JPY 20,000,000、USD 250,000、INR 1 crore）。它不是统计分位点，也不能按市场汇率跨国比较。用户给的阈值永远优先。
- `employer_social_rate`——丹麦约 1%（由所得税承担），西班牙约 32%。用错会悄无声息地把薪酬包络算歪，所以只要披露里有实际数字就必须替换。

---

## 它明确拒绝做的事

以下由 harness 强制执行，不是靠自觉：

- **绝不推断任何个人的具体薪酬。** 公开履历只用于聚合的岗位分类和职业转换，仅此而已。
- **只用公开可合法访问的来源。** 绝不绕过登录墙、验证码、robots 限制或访问控制。
- **检索摘要永远不算来源。** 必须抓取并阅读原始文件，否则这个数字不能用。
- **论坛和众包薪资数据是 Tier E**——只能做校准，绝不能单独支撑一个头部结论。
- **绝不编造数字。** 确实查不到的数据要显式声明：`NOT AVAILABLE: <字段> - <搜过什么>`。对非上市主体，流程会**标记为 provisional（临时估计）**继续，封面会写明，报告里任何数字都不得以实测口径呈现。这是对不确定性的诚实标注，不是绕过检查的后门。
- **绝不伪精确。** 人数和占比一律给蒙特卡洛区间。公开履历观察到的转换份额永远不叫"晋升概率"——真实分母未知。

---

## 仓库结构

```
.claude-plugin/            插件与 marketplace 清单
install.sh                 安装器、依赖检查、打包
skills/company-talent-economics/
  SKILL.md                 给 agent 看的指令
  scripts/                 harness（见下表）
  locales/                 12 个骨架语言包
  assets/                  司法辖区注册表、检索词表、先验、模板
  references/              方法论：术语表、推理链、辖区手册、本地化说明
  schemas/                 report / model / evidence 的 JSON schema
  examples/                小米完整案例与可运行样例
```

| 脚本 | 作用 |
|---|---|
| `init_run.py` | 创建 run；解析语言、辖区、货币、阈值 |
| `check_phase.py` | 十道闸门，每次通过或失败都打印下一步 |
| `search_plan.py` | 六轮检索梯队，按披露平台限定、双语并行 |
| `build_model.py` | `levels.json` → `model.json`，薪酬包络校验及 TC/营收替代检查 |
| `estimate_population.py` | 蒙特卡洛估计跨阈值人数 |
| `pay_band_diagnostic.py` | 市场 / 经济 / 内部三区间重叠诊断 |
| `career_graph.py` | 汇总观察到的职业转换 |
| `compile_report.py` | 用 run 的语言填充 `report.json` 的数值段落 |
| `validate_bundle.py` | 交付包完整性、术语、可负担性校验 |
| `render_report.py` | JSON → DOCX → PDF，本地化骨架、按文字体系选字体、RTL |
| `i18n.py` | 语言识别、语言包、辖区注册表、格式化 |
| `check_locales.py` | 校验语言包与注册表；生成新语言骨架 |
| `selftest.py` | 用合成数据跑完十道闸门和全部语言 |

---

## 开发

```bash
python skills/company-talent-economics/scripts/check_locales.py    # 语言包 + 注册表
python skills/company-talent-economics/scripts/selftest.py         # 闸门 0-10，只出 DOCX
python skills/company-talent-economics/scripts/selftest.py --pdf   # 同时转 PDF
```

`selftest.py` 端到端跑三个场景——完整披露的上市公司、必须走 provisional 路径的非上市公司、以及标题里出现字面 `[ ]` 的情况——然后渲染全部语言包。CI 每次 push 跑的就是这些。

---

## 许可证

MIT，见 [LICENSE](LICENSE)。
