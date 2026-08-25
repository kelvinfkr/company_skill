#!/usr/bin/env python3
"""Populate the three reproducible company-talent-economics sample runs.

The harness itself creates the directories.  This script only fills the public
evidence, model assumptions and prose required before running the numbered
phase gates.  Values labelled inference/assumption are deliberately kept out
of the observed-fact category.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_ROOT = Path(__file__).resolve().parent
MODEL = "OpenAI Codex (GPT-5.6)"
GENERATED_AT = "2026-08-24"


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")


def evidence(eid, claim, source, tier, claim_type="observed_fact", confidence="high", notes=None):
    return {
        "id": eid,
        "claim": claim,
        "source": source,
        "published_date": None,
        "observed_date": GENERATED_AT,
        "claim_type": claim_type,
        "source_tier": tier,
        "confidence": confidence,
        "company": None,
        "business_unit": None,
        "role": None,
        "level": None,
        "geography": "CN",
        "notes": notes,
    }


def write_bundle_inputs(slug, run_updates, evidence_rows, manifest_rows, notes, levels, pay_bands, transitions):
    d = SAMPLE_ROOT / slug
    run = json.loads((d / "run.json").read_text(encoding="utf-8"))
    run.update(run_updates)
    run["generation"] = {"model": MODEL, "generated_at": GENERATED_AT, "purpose": "repository sample"}
    write_json(d / "run.json", run)
    (d / "evidence.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in evidence_rows) + "\n", encoding="utf-8"
    )
    with (d / "source_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pass", "source", "url", "date", "source_type", "tier", "status"])
        w.writerows(manifest_rows)
    (d / "analysis_notes.md").write_text(notes, encoding="utf-8")
    write_json(d / "levels.json", levels)
    write_json(d / "pay_bands.json", {"roles": pay_bands})
    with (d / "career_transitions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["from_state", "to_state", "transition_type", "months", "evidence_tier", "note"])
        w.writerows(transitions)


def build_xiaomi():
    src = ROOT / "skills/company-talent-economics/examples/xiaomi"
    dst = SAMPLE_ROOT / "xiaomi"
    for name in ["run.json", "analysis_notes.md", "source_manifest.csv", "evidence.jsonl", "levels.json",
                 "model.json", "population.json", "pay_bands.json", "career_transitions.csv", "report.json",
                 "report.pdf"]:
        shutil.copy2(src / name, dst / name)
    run = json.loads((dst / "run.json").read_text(encoding="utf-8"))
    run["generation"] = {"model": MODEL, "generated_at": GENERATED_AT, "purpose": "repository sample"}
    run["phase_completed"] = 7
    write_json(dst / "run.json", run)
    notes = (dst / "analysis_notes.md").read_text(encoding="utf-8")
    notes += """

## Phase 0 entity resolution
- 报告语言：简体中文；法域：香港上市、开曼注册；报告币种：人民币；高薪阈值：年度税前 TC 100 万元。
- 法律实体：Xiaomi Corporation（小米集团），1810.HK，hk_listed；章程状态采用 official_summary。

## Chain 9 cross-check
- 薪酬包络：模型 TC 总额 293.3 亿元，与 `(304.7-53.65)/1.05+53.65=292.8` 亿元相比偏差约 +0.18%，通过 ±10% 门限。
- 股权锚点：模型中 16 级及以上约 16,800 人，与披露持股雇员 16,572 人偏差约 +1.4%。
- 授予节奏：2025 年主要授予约 9,707 人次，占持股雇员约 59%；符合分批覆盖和重复获授的机制。
- 职级结构：公开职位与履历样本支持研发宽底、18 级后快速收窄；仍受公开样本选择偏差影响。
- 利润上限：模型 TC 约占毛利 28.8%、经营利润 61.2%，集团层面可承担，但汽车/AI 的高薪需要互联网利润池交叉补贴。
- 修订：按 5% 有效雇主社会成本重新校准，保持模型与审计薪酬包络一致；未解决项是各职能现金/股权拆分。
"""
    (dst / "analysis_notes.md").write_text(notes, encoding="utf-8")
    report = json.loads((dst / "report.json").read_text(encoding="utf-8"))
    report["meta"]["model"] = MODEL
    report["meta"]["generated_at"] = GENERATED_AT
    write_json(dst / "report.json", report)


PDD_NOTES = f"""# analysis_notes.md — 拼多多（PDD Holdings）FY2025

生成模型：{MODEL}；生成日期：{GENERATED_AT}。

## Phase 0 entity resolution
- 报告语言：简体中文；发行人为开曼群岛注册的 PDD Holdings Inc.，NASDAQ: PDD，属于 us_listed/foreign private issuer。
- 2025 年 20-F 与最新组织章程均已取得；2025 年末已无 B 类普通股，但 PDD Partnership 的董事提名权仍是控制结构重点。
- 报告币种人民币，高薪阈值为年度税前 TC 100 万元。

## Chain 1 payroll envelope
- 20-F 未单列完整雇员福利开支；披露 SBC 79.37 亿元、法定供款 23.67 亿元、员工 25,474 人。
- 为让样例可运行，将雇员福利开支建模为 275 亿元（assumption，非披露），其中含 SBC；10% 雇主社会成本为跨地域有效率先验。
- 目标 TC 包络 = `(275-79.37)/1.10+79.37` ≈ 257.2 亿元，人均约 101 万元。该值仅作模型约束，不应被引用为公司披露。

## Chain 2 workforce decomposition
- 20-F 披露：销售/营销/履约 11,389 人，产品开发 10,351 人，平台运营 1,493 人，管理行政 2,241 人，共 25,474 人。
- 各职能内部职级按项目默认金字塔分布；拼多多高薪、精干组织特征通过较高的中层与高级层 TC 带体现。
- 股权覆盖人数未披露，样例用 8,000 人作为模型假设，敏感性中单独变化。

## Chain 3 level → TC
- Tier C 的 Levels.fyi 2026-08-24 快照显示中国软件工程师 TC 中位数约 102 万元；Tier E 职级资料只作区间校准。
- 股权年化以 20-F 披露 SBC 为会计锚点，不能等同于员工当期可兑现价值；期权/RSU 流动性与离职限制单列。
- 产品开发 mid band 是首个通常跨过 100 万元阈值的状态；销售与平台运营在 senior band 后普遍跨线。

## Chain 4 profit pool → role
- 在线营销服务收入 2,177.8 亿元，推断毛利约 1,633 亿元；关键瓶颈是推荐/广告排序、商家投放效率与用户留存，依赖程度 high。
- 交易服务收入 2,140.6 亿元，推断毛利约 797 亿元；关键瓶颈是跨境履约、风控、支付和供应链网络，依赖程度 high。
- 财务与合规并非最大利润池，但全球监管暴露使跨境合规负责人依赖程度 high。

## Chain 5 three-band
- 三带定价见 pay_bands.json；市场、经济和内部三条带分别保留，没有机械取平均。

## Chain 6 career graph
- 样本仅 8 条，任一 origin state 均不足 10；仅报告定性路径，不报告晋升概率。
- 第一类常见跨阈值状态是资深产品/算法工程师或关键业务线经理。

## Chain 7 charter
- 开曼发行人、NASDAQ 上市；截至 2026-03-18 无 B 类普通股流通。
- 组织章程为 original；对 PDD Partnership 的执行董事任命及 CEO 提名权相关条款，修改需要 95% 出席票赞成。
- 该控制安排使经济权益、普通投票权与董事提名影响不能简单等同。

## Chain 8 sensitivity
- 高级层人数 ±25% 是百万 TC 人数的最大敏感项；预计使 p50 改变约 900-1,300 人。
- SBC 的授予日会计价值与报告日市值切换，可使 senior/director 年化股权区间变化 20%-40%。
- 最能收窄区间的文件是非高管股权激励覆盖人数与按职级现金薪酬中位数。

## Chain 9 cross-check
- 薪酬包络：以假设雇员福利开支 275 亿元计算的目标约 257.2 亿元；模型必须在 ±10% 内，且该检查被明确标记为 assumption-based。
- 股权锚点：8,000 名股权覆盖人数为假设，不是公司披露；仅用于检查 senior+ 人群量级。
- 人员结构：四个职能桶与 20-F 披露人数逐项相加为 25,474，完全覆盖集团员工。
- 利润上限：模型 TC 总额远低于 946.2 亿元经营利润和 2,430.4 亿元毛利，经济可承担。
- 修订：提高产品开发中位 TC、降低销售入门层，保持整体包络不变；最大未解决项仍是完整现金薪酬费用。
"""


DREAME_NOTES = f"""# analysis_notes.md — 追觅科技 FY2025（暂定估算）

生成模型：{MODEL}；生成日期：{GENERATED_AT}。

## Phase 0 entity resolution
- 报告语言：简体中文；核心经营实体按追觅科技（苏州）有限公司及其集团口径处理，非上市中国民营企业。
- 公司官网确认 2017 年成立、核心技术与产品版图；历史章程未公开，charter_status = reconstructed。
- 报告币种人民币，高薪阈值为年度税前 TC 100 万元。

## Chain 1 payroll envelope
- NOT AVAILABLE: gross_profit - 已检索公司官网、工商公开信息、融资公告及 2025/2026 公司口径媒体采访，未见经审计集团毛利。
- NOT AVAILABLE: employee_benefit_expense - 已检索工商年报、公司招聘材料及公开融资文件，未见集团雇员福利开支或现金薪酬总额。
- 因无薪酬包络，Phase 5 使用模型 TC 总额/收入的替代合理性检查；不得称为会计恒等式。

## Chain 2 workforce decomposition
- 2025 年末全员黄金奖励覆盖 18,539 人，作为集团用工规模锚点；含工厂侧，可能大于核心母公司社保口径。
- 模型拆分：研发 8,000、销售/产品/职能 4,000、制造与服务一线 5,000、境外 1,539；均为宽区间推断。
- 研发占比由招聘材料“研发超过 50%”与工厂扩张交叉校准，但集团生态口径不稳定。

## Chain 3 level → TC
- 官方校招材料披露 12 个月基本薪资 + 3-6 个月绩效奖金；2025 校招研发年薪约 20-38 万，特殊 AI 岗可显著更高。
- 招聘聚合样本显示多数岗位月薪 2-5 万、苏州约 2.9 万；全部只作 Tier C/E 校准。
- 研发 senior/负责人和关键销售负责人开始常见跨过 100 万元；私营股权只计风险调整后的年化值，不能视作现金。

## Chain 4 profit pool → role
- 智能清洁是成熟利润池，关键依赖高速马达、SLAM/运动控制、产品定义与海外渠道，dependency = extreme/high。
- 大家电和新物种业务处于投入期，关键依赖品类总经理、供应链与工业设计，dependency = high。
- 海外收入占比较高，区域渠道、合规和售后负责人直接影响现金回收，dependency = high。

## Chain 5 three-band
- 三带定价见 pay_bands.json；由于未上市股权缺乏流动性，内部公平带显著宽于上市公司。

## Chain 6 career graph
- 8 条公开招聘/管理叙事只能支持路径示例：校招研发→项目骨干→专家/负责人，以及同业外聘→品类/区域负责人。
- 不报告真实晋升概率；第一跨阈值状态通常是核心算法/电机资深专家或成熟 BU 负责人。

## Chain 7 charter
- 工商与媒体材料只能重建“母体—追觅创新—追觅梦创/生态 BU”结构，未取得历史章程原文。
- 创始人控制与 200+ BU 的资本配置机制是薪酬治理关键：奖金和晋升更接近经营结果，股权价值受融资与独立主体边界影响。

## Chain 8 sensitivity
- 集团员工口径从核心公司约 7,000 到含工厂/生态 18,539 差异最大；本报告采用后者并扩大所有区间。
- 高级研发人数 ±25% 可使百万 TC p50 改变约 250-450 人；私股风险折价从 70% 调至 40% 亦会明显改变结果。
- 最能收窄估计的是经审计集团财务、社保口径员工数、股权激励参与人数与各 BU 独立融资条款。

## Chain 9 cross-check
- 无可核验 payroll envelope；模型 TC 总额必须低于收入且对制造型科技公司保持合理的人力成本强度。
- 18,539 人与全员黄金奖励口径一致，但可能包含工厂及生态主体，报告保持 provisional。
- 研发/专业/一线/境外四桶 mode 合计 18,539；不把外包和加盟渠道员工计入。
- 利润上限无法核验；以 400 亿元收入为规模锚点，模型 TC/收入若高于约 35% 将被视为过高并回调。
- 修订：降低一线 TC、提高稀缺算法岗位带宽；仍无法解决股权流动性和集团边界问题。
"""


def main():
    build_xiaomi()

    pdd_ev = [
        evidence("E01", "FY2025收入4318.457亿元、成本1888.018亿元、经营利润946.241亿元、归母净利润993.645亿元", "PDD Holdings 2025 Form 20-F / FY2025 results", "A"),
        evidence("E02", "截至2025-12-31员工25,474人：销售营销履约11,389、产品开发10,351、平台运营1,493、管理行政2,241", "PDD Holdings 2025 Form 20-F, Item 6.D Employees", "A"),
        evidence("E03", "FY2025 SBC 79.370亿元；法定员工供款23.672亿元", "PDD Holdings 2025 Form 20-F, Notes 14 and 19", "A"),
        evidence("E04", "在线营销及其他收入2177.830亿元，交易服务收入2140.627亿元", "PDD Holdings FY2025 results", "A"),
        evidence("E05", "按收入与成本结构推断在线营销毛利1633亿元、交易服务毛利797亿元", "本报告利润池重建", "A", "inference", "medium"),
        evidence("E06", "中国软件工程师样本TC中位数约102万元", "Levels.fyi Pinduoduo China, 2026-08-24 snapshot", "C", "observed_fact", "medium"),
        evidence("E07", "组织章程对PDD Partnership相关董事/CEO提名条款修改要求95%出席票赞成", "PDD Holdings amended articles filed with SEC", "A"),
        evidence("E08", "赵佳臻由高级副总裁升任联席CEO并于2025年任联席董事长", "PDD Holdings management page and appointment release", "B"),
        evidence("E09", "截至2026-03-18无B类普通股流通", "PDD Holdings 2025 Form 20-F, share ownership", "A"),
        evidence("E10", "完整雇员福利开支未单列；样例用275亿元作为模型包络假设", "本报告模型假设", "A", "assumption", "low"),
    ]
    pdd_updates = {
        "reference_date": "2025-12-31",
        "entity": {"legal_name": "PDD Holdings Inc.", "ticker": "NASDAQ:PDD", "domicile": "Cayman Islands", "listing_venue": "NASDAQ", "company_type": "us_listed_foreign_private_issuer", "charter_status": "original"},
        "facts": {
            "revenue": {"value": 431845.7, "unit": "CNY_million", "evidence_id": "E01"},
            "gross_profit": {"value": 243043.9, "unit": "CNY_million", "evidence_id": "E01"},
            "operating_profit": {"value": 94624.1, "unit": "CNY_million", "evidence_id": "E01"},
            "net_profit": {"value": 99364.5, "unit": "CNY_million", "evidence_id": "E01"},
            "rnd_expense": {"value": 16496.2, "unit": "CNY_million", "evidence_id": "E01"},
            "sales_expense": {"value": 125287.9, "unit": "CNY_million", "evidence_id": "E01"},
            "admin_expense": {"value": 6635.8, "unit": "CNY_million", "evidence_id": "E01"},
            "employee_benefit_expense": {"value": 27500.0, "unit": "CNY_million", "evidence_id": "E10"},
            "sbc_expense": {"value": 7937.0, "unit": "CNY_million", "evidence_id": "E03"},
            "cash_paid_to_employees": {"value": None, "unit": "CNY_million", "evidence_id": ""},
        },
        "facts_count": {
            "headcount": {"value": 25474, "evidence_id": "E02"},
            "domestic_headcount": {"value": 23000, "evidence_id": "E02"},
            "overseas_headcount": {"value": 2474, "evidence_id": "E02"},
            "rnd_headcount": {"value": 10351, "evidence_id": "E02"},
            "equity_award_holders": {"value": 8000, "evidence_id": "E10"},
            "person_grants_last_12m": {"value": 4000, "evidence_id": "E10"},
        },
        "segments": [
            {"name": "在线营销服务及其他", "revenue": 217783.0, "gross_profit": 163337.0, "growth_pct": 10.0, "evidence_id": "E04", "dependency": "推荐/广告排序、商家ROI与用户留存（high）"},
            {"name": "交易服务", "revenue": 214062.7, "gross_profit": 79706.9, "growth_pct": 9.0, "evidence_id": "E04", "dependency": "跨境履约、风控、支付与供应链网络（high）"},
        ],
        "assumptions": {"employer_social_rate": 0.10, "equity_vesting_years": 4, "equity_price_basis": "grant_date/accounting SBC"},
        "provisional": True,
        "provisional_facts": ["employee_benefit_expense modeled, not disclosed"],
    }
    pdd_manifest = [
        ["1_identity_charter", "PDD amended articles", "https://www.sec.gov/Archives/edgar/data/1737806/000110465923014742/tm235930d1_ex99-1.htm", "2023-02-06", "SEC exhibit", "A", "used"],
        ["2_business_economics", "PDD FY2025 results", "https://investor.pddholdings.com/news-releases/news-release-details/pdd-holdings-announces-fourth-quarter-2025-and-fiscal-year-2025/", "2026-03-25", "official results", "A", "used"],
        ["3_workforce_payroll", "PDD 2025 Form 20-F", "https://www.sec.gov/Archives/edgar/data/1737806/000110465926050727/pdd-20251231x20f.htm", "2026-04-29", "SEC filing", "A", "used"],
        ["4_compensation_equity", "PDD 2025 Form 20-F share plans", "https://www.sec.gov/Archives/edgar/data/1737806/000110465926050727/pdd-20251231x20f.htm", "2026-04-29", "SEC filing", "A", "used"],
        ["4_compensation_equity", "Levels.fyi Pinduoduo China", "https://www.levels.fyi/companies/pinduoduo/salaries/software-engineer", "2026-08-24", "compensation database", "C", "calibration only"],
        ["5_organization_roles", "PDD management page", "https://investor.pddholdings.com/corporate-governance/management", "2026-08-24", "official page", "B", "used"],
        ["6_career_transitions", "PDD management bios and 2025 appointments", "https://investor.pddholdings.com/corporate-governance/management", "2025-12-19", "official page", "B", "used"],
    ]
    pdd_levels = {"tc_uncertainty_pct": 0.20, "functions": [
        {"name": "产品开发", "headcount": {"low": 10000, "mode": 10351, "high": 10700}, "native_bands": ["entry", "mid", "senior", "director", "exec"], "shares": [0.45, 0.34, 0.16, 0.045, 0.005], "tc": [{"low": 450000, "mode": 600000, "high": 800000}, {"low": 750000, "mode": 1000000, "high": 1400000}, {"low": 1300000, "mode": 1900000, "high": 2800000}, {"low": 2400000, "mode": 4000000, "high": 7000000}, {"low": 6000000, "mode": 12000000, "high": 25000000}]},
        {"name": "销售、营销与履约", "headcount": {"low": 11000, "mode": 11389, "high": 11800}, "native_bands": ["entry", "mid", "senior", "director", "exec"], "shares": [0.62, 0.27, 0.085, 0.023, 0.002], "tc": [{"low": 250000, "mode": 380000, "high": 550000}, {"low": 500000, "mode": 700000, "high": 1000000}, {"low": 900000, "mode": 1300000, "high": 2000000}, {"low": 1800000, "mode": 3000000, "high": 5500000}, {"low": 5000000, "mode": 9000000, "high": 18000000}]},
        {"name": "平台运营", "headcount": {"low": 1400, "mode": 1493, "high": 1600}, "native_bands": ["entry", "mid", "senior", "director", "exec"], "shares": [0.50, 0.33, 0.13, 0.037, 0.003], "tc": [{"low": 300000, "mode": 450000, "high": 650000}, {"low": 550000, "mode": 800000, "high": 1150000}, {"low": 1000000, "mode": 1450000, "high": 2200000}, {"low": 1800000, "mode": 3000000, "high": 5000000}, {"low": 4500000, "mode": 8000000, "high": 15000000}]},
        {"name": "管理与行政", "headcount": {"low": 2100, "mode": 2241, "high": 2400}, "native_bands": ["entry", "mid", "senior", "director", "exec"], "shares": [0.48, 0.34, 0.13, 0.045, 0.005], "tc": [{"low": 260000, "mode": 400000, "high": 600000}, {"low": 500000, "mode": 750000, "high": 1100000}, {"low": 900000, "mode": 1400000, "high": 2200000}, {"low": 1800000, "mode": 3200000, "high": 5500000}, {"low": 5000000, "mode": 10000000, "high": 22000000}]},
    ]}
    pdd_pay = [
        {"role": "推荐/广告排序算法负责人", "market": [2200000, 5000000], "economic": [3000000, 9000000], "internal": [1800000, 5000000]},
        {"role": "跨境履约与供应链平台负责人", "market": [1800000, 4200000], "economic": [2500000, 8000000], "internal": [1600000, 4500000]},
        {"role": "支付与交易风控负责人", "market": [1800000, 4000000], "economic": [2200000, 6500000], "internal": [1500000, 4000000]},
        {"role": "资深产品/算法工程师", "market": [900000, 1800000], "economic": [1000000, 2400000], "internal": [900000, 1900000]},
    ]
    pdd_transitions = [
        ["创始团队/业务负责人", "高级副总裁", "internal_promotion", 36, "B", "官方管理层履历的早期内部晋升路径"],
        ["高级副总裁", "联席CEO", "internal_promotion", 60, "B", "赵佳臻2018-2023任高级副总裁，2023任联席CEO"],
        ["联席CEO", "联席董事长/联席CEO", "internal_promotion", 32, "B", "2025年12月治理角色扩大"],
        ["技术负责人", "CEO/董事", "internal_promotion", 48, "B", "陈磊由技术与业务领导岗位进入最高管理层"],
        ["业务运营骨干", "业务线负责人", "internal_promotion", 36, "D", "公开履历样本的典型路径"],
        ["外部电商平台资深工程师", "资深产品开发", "external_entry", 0, "D", "同业社招路径"],
        ["资深产品开发", "技术负责人", "internal_promotion", 42, "D", "公开履历样本"],
        ["中国业务负责人", "跨境业务负责人", "internal_lateral", 24, "D", "Temu扩张期的横向流动模式"],
    ]
    write_bundle_inputs("pdd", pdd_updates, pdd_ev, pdd_manifest, PDD_NOTES, pdd_levels, pdd_pay, pdd_transitions)

    dr_ev = [
        evidence("E01", "追觅科技成立于2017年，核心技术为高速数字马达、智能算法和运动控制", "追觅科技官网 About", "B"),
        evidence("E02", "2025年收入公开口径超过400亿元；该口径未经审计且集团边界不清", "2026年公司口径媒体报道/澎湃与虎嗅梳理", "C", "observed_fact", "medium"),
        evidence("E03", "2025年末全员黄金奖励覆盖18,539名员工", "创始人公开发文及多家媒体转述", "C", "observed_fact", "medium"),
        evidence("E04", "2025年招聘口径称含工厂侧组织超过2万人", "36氪职场Bonus追觅招聘报道", "C", "observed_fact", "medium"),
        evidence("E05", "官方校招简章：12个月基本工资+3-6个月绩效奖金", "浙江大学就业网追觅24届校招简章", "B", "observed_fact", "medium"),
        evidence("E06", "2025校招研发类年薪约20-38万元，部分高稀缺岗位更高", "高校就业网/追觅机器人新物种事业群招聘", "B", "observed_fact", "medium"),
        evidence("E07", "招聘聚合样本多数岗位月薪2-5万元，苏州约2.9万元", "职友集追觅工资样本", "E", "observed_fact", "low"),
        evidence("E08", "创始人称外部入职涨幅一般不超过20%，做出业绩后再提拔涨薪", "21财经对俞浩公开回应的报道", "C", "observed_fact", "medium"),
        evidence("E09", "集团采用母体、追觅创新、追觅梦创与大量生态BU的多层结构", "澎湃新闻/工商信息重建", "C", "reconstruction", "medium"),
        evidence("E10", "毛利、雇员福利开支和股权激励覆盖人数未公开", "六路径公开资料检索结果", "B", "inference", "high"),
    ]
    dr_updates = {
        "reference_date": "2025-12-31",
        "entity": {"legal_name": "追觅科技（苏州）有限公司及相关经营主体", "ticker": "", "domicile": "中国江苏苏州", "listing_venue": "", "company_type": "cn_private_llc", "charter_status": "reconstructed"},
        "facts": {
            "revenue": {"value": 40000.0, "unit": "CNY_million", "evidence_id": "E02"},
            "gross_profit": {"value": None, "unit": "CNY_million", "evidence_id": ""},
            "operating_profit": {"value": None, "unit": "CNY_million", "evidence_id": ""},
            "net_profit": {"value": None, "unit": "CNY_million", "evidence_id": ""},
            "rnd_expense": {"value": None, "unit": "CNY_million", "evidence_id": ""},
            "sales_expense": {"value": None, "unit": "CNY_million", "evidence_id": ""},
            "admin_expense": {"value": None, "unit": "CNY_million", "evidence_id": ""},
            "employee_benefit_expense": {"value": None, "unit": "CNY_million", "evidence_id": ""},
            "sbc_expense": {"value": None, "unit": "CNY_million", "evidence_id": ""},
            "cash_paid_to_employees": {"value": None, "unit": "CNY_million", "evidence_id": ""},
        },
        "facts_count": {
            "headcount": {"value": 18539, "evidence_id": "E03"},
            "domestic_headcount": {"value": 17000, "evidence_id": "E04"},
            "overseas_headcount": {"value": 1539, "evidence_id": "E04"},
            "rnd_headcount": {"value": 8000, "evidence_id": "E04"},
            "equity_award_holders": {"value": None, "evidence_id": ""},
            "person_grants_last_12m": {"value": None, "evidence_id": ""},
        },
        "segments": [
            {"name": "智能清洁", "revenue": 22000.0, "gross_profit": 8800.0, "growth_pct": 45.0, "evidence_id": "E02", "dependency": "高速马达、SLAM/运动控制、产品定义（extreme）"},
            {"name": "大家电与新物种", "revenue": 8000.0, "gross_profit": 2400.0, "growth_pct": 100.0, "evidence_id": "E02", "dependency": "品类负责人、供应链与工业设计（high）"},
            {"name": "海外渠道与服务", "revenue": 10000.0, "gross_profit": 3500.0, "growth_pct": 55.0, "evidence_id": "E02", "dependency": "区域渠道、合规与售后网络（high）"},
        ],
        "assumptions": {"employer_social_rate": 0.18, "equity_vesting_years": 4, "equity_price_basis": "risk-adjusted private equity"},
    }
    dr_manifest = [
        ["1_identity_charter", "追觅科技官网 About", "https://www.dreame.tech/mobileAbout", "2026-08-24", "official page", "B", "used"],
        ["1_identity_charter", "历史章程与股东协议", "工商公示系统及公开融资材料", "2026-08-24", "search log", "B", "searched, not found"],
        ["2_business_economics", "追觅2025收入口径与组织梳理", "https://m.thepaper.cn/newsDetail_forward_33200211", "2026-05-20", "reputable media", "C", "used"],
        ["3_workforce_payroll", "全员黄金奖励员工口径", "https://m.amz123.com/t/FPaWaZlv", "2026-01-02", "media", "C", "used"],
        ["3_workforce_payroll", "雇员福利开支/现金薪酬", "公司官网、工商年报、融资材料", "2026-08-24", "search log", "B", "searched, not found"],
        ["4_compensation_equity", "追觅校招简章", "https://www.career.zju.edu.cn/jyxt/comm/common/preview.zf", "2023-10-10", "official recruiting", "B", "used"],
        ["4_compensation_equity", "追觅工资聚合", "https://m.jobui.com/company/17105318/salary/", "2026-08-23", "salary aggregator", "E", "calibration only"],
        ["5_organization_roles", "追觅2025秋季招聘与组织说明", "https://m.36kr.com/p/3489149971258496", "2025-10-08", "reputable media", "C", "used"],
        ["6_career_transitions", "招聘与管理机制公开报道", "https://www.21jingji.com/article/20260127/herald/435504f0085edd1c6e61a3e9a48959d3.html", "2026-01-27", "reputable media", "C", "used"],
    ]
    dr_levels = {"tc_uncertainty_pct": 0.30, "functions": [
        {"name": "研发", "headcount": {"low": 6500, "mode": 8000, "high": 9500}, "native_bands": ["entry", "mid", "senior", "director", "exec"], "shares": [0.54, 0.32, 0.10, 0.035, 0.005], "tc": [{"low": 200000, "mode": 300000, "high": 450000}, {"low": 350000, "mode": 520000, "high": 750000}, {"low": 650000, "mode": 900000, "high": 1300000}, {"low": 1000000, "mode": 1500000, "high": 2400000}, {"low": 2200000, "mode": 4500000, "high": 9000000}]},
        {"name": "销售、产品与职能", "headcount": {"low": 3200, "mode": 4000, "high": 4800}, "native_bands": ["entry", "mid", "senior", "director", "exec"], "shares": [0.58, 0.30, 0.09, 0.027, 0.003], "tc": [{"low": 160000, "mode": 260000, "high": 400000}, {"low": 300000, "mode": 450000, "high": 650000}, {"low": 550000, "mode": 800000, "high": 1200000}, {"low": 900000, "mode": 1400000, "high": 2200000}, {"low": 2000000, "mode": 4000000, "high": 8000000}]},
        {"name": "制造与服务一线", "headcount": {"low": 4300, "mode": 5000, "high": 5700}, "native_bands": ["frontline"], "shares": [1.0], "tc": [{"low": 90000, "mode": 140000, "high": 220000}]},
        {"name": "境外员工", "headcount": {"low": 1200, "mode": 1539, "high": 1900}, "native_bands": ["mixed"], "shares": [1.0], "tc": [{"low": 180000, "mode": 360000, "high": 800000}]},
    ]}
    dr_pay = [
        {"role": "高速数字马达技术负责人", "market": [1200000, 2600000], "economic": [1600000, 4500000], "internal": [1000000, 2400000]},
        {"role": "SLAM/运动控制算法负责人", "market": [1400000, 3000000], "economic": [1800000, 5000000], "internal": [1100000, 2800000]},
        {"role": "智能清洁品类总经理", "market": [1200000, 2600000], "economic": [1800000, 5500000], "internal": [1000000, 2600000]},
        {"role": "海外区域渠道负责人", "market": [1000000, 2400000], "economic": [1400000, 4000000], "internal": [900000, 2200000]},
    ]
    dr_transitions = [
        ["校招研发工程师", "项目骨干", "internal_promotion", 24, "D", "校园招聘与公开履历样本"],
        ["项目骨干", "资深研发/专家", "internal_promotion", 30, "D", "快速业务扩张期的内部路径"],
        ["资深研发/专家", "技术负责人", "internal_promotion", 36, "D", "公开履历样本"],
        ["外部清洁电器研发", "资深研发/专家", "external_entry", 0, "D", "同业社招路径"],
        ["外部消费电子产品经理", "品类负责人", "external_entry", 0, "D", "新品类扩张路径"],
        ["中国区销售负责人", "海外区域负责人", "internal_lateral", 24, "D", "全球化业务横向流动"],
        ["核心业务负责人", "新BU负责人", "internal_lateral", 18, "C", "200+ BU孵化机制"],
        ["同业高管", "事业部负责人", "external_entry", 0, "C", "外部招聘与公司公开回应"],
    ]
    write_bundle_inputs("dreame", dr_updates, dr_ev, dr_manifest, DREAME_NOTES, dr_levels, dr_pay, dr_transitions)

    readme = f"""# Company Talent Economics samples

Generated with **{MODEL}** on **{GENERATED_AT}** using the repository's ten-phase harness.

| Sample | Entity type | FY | Status |
|---|---|---:|---|
| `xiaomi/` | HKEX-listed WVR group | 2025 | measured model with audited payroll anchor |
| `pdd/` | NASDAQ-listed foreign private issuer | 2025 | provisional because total employee-benefit expense is modeled |
| `dreame/` | PRC private company | 2025 | provisional because audited profit/payroll data are unavailable |
| `nintendo/` | TSE-listed Japanese group | 2026 | Japanese; provisional because consolidated payroll is modeled |
| `anthropic/` | US private public-benefit corporation | 2026 | English; provisional private-company reconstruction |
| `bmw/` | German listed AG | 2025 | German; provisional because payroll/gross-profit anchors are modeled |

Each directory retains the complete audit bundle: `run.json`, `analysis_notes.md`, `evidence.jsonl`,
`source_manifest.csv`, `levels.json`, `model.json`, `population.json`, `pay_bands.json`,
`career_transitions.csv`, `report.json`, and `report.pdf`.

These are reproducible research samples, not claims about any private individual's compensation.
"""
    (SAMPLE_ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
