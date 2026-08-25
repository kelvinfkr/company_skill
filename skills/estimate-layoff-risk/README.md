# Estimate Layoff Risk

一个用于评估员工、实习生、合同工或某类岗位在未来 **3 / 6 / 12 个月内非自愿离岗风险**的通用 Skill。

它不会根据情绪、公司口碑或单一新闻直接下结论，而是先重建企业利润结构，再把经营压力逐层传导到业务、流程、岗位和个人：

```text
商业模式 → 利润池 → 现金/利润率压力 → 管理层资源配置
→ 业务单元 → 关键流程 → 岗位族 → 用工机制 → 个人暴露度
```

输出是带证据、假设、反证和置信度的概率区间，不是“会 / 不会被裁”的伪精确判断。

## 适合解决什么问题

- 某公司是否可能进行裁员、关停业务线或缩减某个地点；
- 产品、运营、研发、销售、制造、职能等不同岗位谁更容易受到成本削减影响；
- 实习期结束、合同不续签、试用期退出、绩效淘汰与正式裁员分别有多大风险；
- 一家仍然盈利的公司为什么可能裁员；
- 一个暂时亏损的业务或岗位为什么仍可能被保留；
- 哪些可观察信号会让风险上升或下降。

## 推荐交互提示词

把下面内容直接交给支持 Skills 与联网研究的智能体：

```text
请使用 estimate-layoff-risk skill，评估我未来 3、6、12 个月的非自愿离岗风险。

公司：<公司名>
法律雇主（如已知）：<主体名>
国家/地区：<工作所在地>
业务/产品：<所在业务线或产品>
岗位：<岗位名称>
用工类型：<正式员工 / 实习生 / 合同工 / 外包 / 试用期>

请先分两轮问我必要问题，每轮不要太长；只追问会显著改变判断的问题。
然后搜索最新公开资料，从商业模式、利润池、现金与利润率压力、管理层资源配置、
业务优先级、流程依赖、岗位可替代性和用工机制逐层分析。

请把公开事实、我的自述、模型假设和你的推断分开；主动寻找反证；
最后给出 3/6/12 个月风险区间、置信度、乐观/基准/不利情景、
关键驱动因素、会让结论变化的信号，以及我可以采取的低风险行动。
不要索取公司机密、同事隐私或受保护的个人信息。
```

最简用法也可以是：

```text
使用 estimate-layoff-risk，评估追觅某产品实习生未来 3/6/12 个月的非自愿离岗风险。先采访我，再搜索公开证据并生成报告。
```

## Skill 如何与候选人交互

1. **先定义结果**：区分大规模裁员、业务关闭、岗位冗余、绩效退出、合同不续签、实习结束和内部转岗。
2. **两轮核心访谈**：了解法律雇主、业务归属、工作地点、岗位族、用工类型、预算、路线图、工作量、招聘、汇报线和客户承诺的变化。
3. **自适应追问**：根据岗位性质和用工机制选择分支，通常总共 12–25 个问题。
4. **公开信息研究**：分八轮检索实体、偿债能力、利润结构、重组目标、产品生命周期、用工变化、管理层配置历史和反证。
5. **建立因果图**：将利润池映射到关键流程、团队、岗位族和个人暴露。
6. **区间估计**：分别估计公司行动、业务受影响、岗位缩减和个人被选择的条件概率，并检查重复计算。
7. **生成可审计报告**：展示结论、证据、假设、敏感性、情景和后续观察指标。

## 高水平分析框架

核心不是简单看收入增减，而是选对经济分母：

- 软件 / 平台：ARR、留存、毛利、获客效率、云成本与现金生成；
- 硬件 / 制造：单品贡献利润、渠道库存、产能利用率、售后成本与现金周转；
- 项目 / 服务：订单、积压、利用率、项目毛利与回款；
- 初创公司：现金 runway、融资概率、里程碑和下一轮资本需求；
- 高杠杆 / PE 持有：债务、契约、利息覆盖、协同承诺和退出时间表；
- 受监管行业：合规、安全、牌照与最低人员配置；
- 长周期研发：技术里程碑、期权价值、失败成本与管理层继续出资概率。

岗位层面的概念模型是：

```text
裁撤净收益
= 可避免的完全成本现值
−（损失的贡献利润 + 执行风险 + 重招成本 + 知识损失 + 战略期权价值）的现值
```

Skill 不会虚构个人产出金额，而是使用范围、场景与敏感性分析。

## 目录结构

```text
estimate-layoff-risk/
├── README.md                    # 本说明
├── SKILL.md                     # 智能体工作流与硬性边界
├── agents/openai.yaml           # 展示元数据
├── assets/                      # 问题库、报告规范、图标与字体说明
├── references/                  # 访谈、利润池、岗位、领导配置与研究方法
├── schemas/                     # case / evidence / model / report JSON Schema
├── scripts/                     # 初始化、问卷、搜索计划、估计、渲染与校验
└── examples/fictional_robotics_intern/
    └── ...                      # 完全虚构、可复现的产品实习生案例
```

## 本地运行

要求：Python 3.10+。结构化分析只使用标准库；生成与校验 PDF 需要额外依赖：

```bash
python -m pip install python-docx jsonschema
```

若要生成中文 PDF，请安装 LibreOffice，并确保系统存在 `Noto Sans CJK SC`。也可以把相应字体文件放到：

```text
assets/fonts/NotoSansCJKsc-Regular.otf
```

初始化案例：

```bash
python scripts/init_case.py \
  --company "Company" \
  --role "Product Intern" \
  --country "China" \
  --employment-type intern \
  --out runs/company-role-YYYY-MM-DD
```

生成问题与搜索计划：

```bash
python scripts/questionnaire.py runs/company-role-YYYY-MM-DD/case.json \
  -o runs/company-role-YYYY-MM-DD/questionnaire.json

python scripts/search_plan.py runs/company-role-YYYY-MM-DD/case.json \
  -o runs/company-role-YYYY-MM-DD/search_plan.json
```

运行区间估计、生成并校验报告：

```bash
python scripts/estimate_risk.py runs/company-role-YYYY-MM-DD/model.json \
  -o runs/company-role-YYYY-MM-DD/risk_results.json

python scripts/render_report.py runs/company-role-YYYY-MM-DD/report.json \
  -o runs/company-role-YYYY-MM-DD/report.pdf

python scripts/validate_bundle.py runs/company-role-YYYY-MM-DD
```

仓库内的虚构案例可以直接重建 PDF：

```bash
python scripts/render_report.py \
  examples/fictional_robotics_intern/report.json \
  -o examples/fictional_robotics_intern/report.pdf
```

## 报告产物

标准案例目录包含：

- `case.json`：范围、岗位、地点、用工类型和时间窗；
- `candidate_answers.json`：候选人自述、日期、来源与信心；
- `public_evidence.jsonl`：逐条公开证据；
- `source_manifest.csv`：搜索过和使用过的来源；
- `profit_pools.json`：利润池与战略期权；
- `dependency_graph.json`：利润池到岗位的依赖链；
- `model.json`：概率层、先验、假设与敏感性；
- `risk_results.json`：模型计算结果；
- `report.json` / `report.pdf`：结构化报告与最终阅读版。

## 证据与隐私边界

- 仅使用公开、合法可访问的信息和候选人自愿提供的事实；
- 不索取内部文档、账号、聊天记录、同事隐私或未公开经营数据；
- 不询问或使用种族、性别、健康、宗教、政治观点、工会身份、家庭状况等受保护或高度敏感特征；
- 不推断私人个体的绩效、薪酬、健康、关系或法律状态；
- 管理层分析只基于可观察的资源配置行为和治理激励，不做人格诊断；
- 法律后果需要单独查询工作所在地的最新法规；本 Skill 不构成法律意见；
- 概率区间是决策支持，不是保证。

## 方法文件导航

- [`references/interview_protocol.md`](references/interview_protocol.md)：自适应访谈顺序与回答溯源；
- [`references/profit_pool_model.md`](references/profit_pool_model.md)：利润池到人力配置的核心模型；
- [`references/role_playbooks.md`](references/role_playbooks.md)：不同岗位族与用工类型分支；
- [`references/leadership_regimes.md`](references/leadership_regimes.md)：基于行为的领导配置机制；
- [`references/research_and_evidence.md`](references/research_and_evidence.md)：八轮搜索、证据等级与反证；
- [`references/modeling_and_calibration.md`](references/modeling_and_calibration.md)：竞争风险、区间估计与校准；
- [`references/privacy_and_boundaries.md`](references/privacy_and_boundaries.md)：隐私与候选人控制；
- [`references/report_contract.md`](references/report_contract.md)：报告结构规范。

## License

本目录沿用仓库根目录的许可证。
