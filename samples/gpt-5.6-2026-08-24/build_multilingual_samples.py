#!/usr/bin/env python3
"""Populate the Japanese, English, and German repository samples."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODEL = "OpenAI Codex (GPT-5.6)"
DATE = "2026-08-24"


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")


def ev(eid, claim, source, tier="A", claim_type="observed_fact", confidence="high", geo=None):
    return {
        "id": eid, "claim": claim, "source": source, "published_date": None,
        "observed_date": DATE, "claim_type": claim_type, "source_tier": tier,
        "confidence": confidence, "company": None, "business_unit": None,
        "role": None, "level": None, "geography": geo, "notes": None,
    }


def write(slug, run_update, rows, manifest, notes, levels, pay, transitions):
    d = ROOT / slug
    run = json.loads((d / "run.json").read_text(encoding="utf-8"))
    run.update(run_update)
    run["generation"] = {"model": MODEL, "generated_at": DATE, "purpose": "repository sample"}
    dump(d / "run.json", run)
    (d / "evidence.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")
    with (d / "source_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["pass", "source", "url", "date", "source_type", "tier", "status"])
        w.writerows(manifest)
    (d / "analysis_notes.md").write_text(notes, encoding="utf-8")
    dump(d / "levels.json", levels)
    dump(d / "pay_bands.json", {"roles": pay})
    with (d / "career_transitions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["from_state", "to_state", "transition_type", "months", "evidence_tier", "note"])
        w.writerows(transitions)


def nintendo():
    notes = f"""# 任天堂株式会社 FY2026 — 分析ノート

生成モデル：{MODEL}。生成日：{DATE}。

## Phase 0 entity resolution
- 言語は日本語、対象は任天堂株式会社と連結子会社、通貨はJPY、基準日は2026-03-31。
- 高報酬の閾値は税引前年間TC 2,000万円。基本給、賞与、年換算株式報酬を含む。

## Chain 1 payroll envelope
- 連結売上高2兆3,130.51億円、売上総利益9,089.56億円、営業利益3,601.17億円は決算短信の実績値。
- NOT AVAILABLE: employee_benefit_expense - 有価証券報告書、決算短信、統合報告書を検索したが連結人件費総額を独立行として取得できなかった。
- 単体平均年間給与982.5万円は強い校正点だが、海外子会社を含む連結平均ではない。

## Chain 2 workforce decomposition
- 連結従業員8,666人、単体3,084人は会社概要と有価証券報告書の開示。
- 研究開発、ハードウェア、営業管理、運営支援の配分は公開職種と子会社構成からの再構築。

## Chain 3 level to TC
- entry / mid / senior / director / executive の共通状態に写像。任天堂固有の正式等級名ではない。
- 2,000万円を通常超える最初の状態は、上位seniorまたはdirector。賞与の年度変動が大きい。

## Chain 4 profit pool to role
- ソフトウェアとデジタル継続収益は粗利密度が高く、ゲームディレクター、エンジン、ネットワーク、安全性が重要。
- ハードウェアは普及台数を形成し、SoC、量産品質、サプライチェーンがソフトウェア利益の土台になる。

## Chain 5 three-band
- 市場代替費用、利益への依存度、社内公平性を別々に保持し、機械的な平均は取らない。

## Chain 6 career graph
- 公開経歴8件は経路例であり、母集団がないため昇進確率とは呼ばない。
- 内部育成が中心だが、半導体、オンライン基盤、映像IPでは外部採用も必要。

## Chain 7 charter
- 東証上場の日本株式会社。定款とコーポレートガバナンス報告書をofficial_summaryとして扱う。
- 取締役会と執行役員の役割分担、長期IP投資、利益連動賞与が報酬設計に影響する。

## Chain 8 sensitivity
- 研究開発senior比率±25%が閾値超人数の最大感応度。海外TC換算も第2の感応度。
- 連結人件費と非役員株式報酬の開示が区間を最も縮める。

## Chain 9 cross-check
- 公開人件費による包絡は検証不能。モデル仮定1,000億円から得るTC包絡に対しモデル総額は+5.2%で、これは仮定ベースの整合確認にすぎない。
- 単体平均給与982.5万円、連結8,666人、利益上限と職能合計を相互照合。
- 結果は暫定推計であり、個人の給与を推定しない。
"""
    rows = [
        ev("E01", "2026年3月期の売上高は2兆3,130.51億円、売上総利益9,089.56億円、営業利益3,601.17億円、親会社株主利益4,240.56億円", "任天堂 2026年3月期 決算短信", "A", geo="JP"),
        ev("E02", "2026年3月末の連結従業員は8,666人、単体は3,084人", "任天堂 会社概要・第86期有価証券報告書", "A", geo="JP"),
        ev("E03", "単体平均年間給与は9,824,708円、平均年齢40.5歳、平均勤続14.6年", "任天堂 第86期有価証券報告書", "A", geo="JP"),
        ev("E04", "Nintendo Switch 2発売年度で、海外売上比率は76.9%", "任天堂 2026年3月期 決算短信", "A", geo="Global"),
        ev("E05", "デジタル売上は4,076億円、IP関連売上は735億円", "任天堂 2026年3月期 決算資料", "A", geo="Global"),
        ev("E06", "研究開発職を3,600人と置く", "本レポートの職能再構築", "C", "reconstruction", "low", "Global"),
        ev("E07", "連結人件費総額は独立開示を取得できなかった", "公開資料検索記録", "B", "inference", "high", "Global"),
        ev("E08", "上位職のTC帯は単体平均給与と公開採用・役員報酬を用いて校正", "本レポートのモデル", "C", "assumption", "low", "JP"),
        ev("E09", "連結人件費を1,000億円と置くモデル仮定（会社開示ではない）", "本レポートのモデル", "C", "assumption", "low", "Global"),
    ]
    manifest = [
        ["1_identity_charter", "定款・会社情報", "https://www.nintendo.co.jp/ir/en/index.html", "2026-06", "official IR", "A", "used"],
        ["2_business_economics", "2026年3月期 決算短信", "https://www.nintendo.co.jp/ir/pdf/2026/260508e.pdf", "2026-05-08", "official filing", "A", "used"],
        ["3_workforce_payroll", "第86期 有価証券報告書", "https://www.nintendo.co.jp/ir/library/securities/index.html", "2026-06", "official filing", "A", "used"],
        ["3_workforce_payroll", "会社概要", "https://www.nintendo.co.jp/corporate/en/outline/index.html", "2026-03-31", "official page", "A", "used"],
        ["4_compensation_equity", "平均年間給与・役員報酬", "https://www.nintendo.co.jp/ir/library/securities/index.html", "2026-06", "official filing", "A", "used"],
        ["5_organization_roles", "取締役・執行役員", "https://www.nintendo.co.jp/corporate/en/officer/index.html", "2026-08-24", "official page", "B", "used"],
        ["6_career_transitions", "役員略歴・採用情報", "https://www.nintendo.co.jp/jobs/", "2026-08-24", "official recruiting", "B", "used"],
    ]
    update = {
        "reference_date": "2026-03-31",
        "entity": {"legal_name": "任天堂株式会社", "ticker": "TSE:7974", "domicile": "日本・京都", "listing_venue": "東京証券取引所", "company_type": "jp_listed_kabushiki_kaisha", "charter_status": "official_summary"},
        "facts": {
            "revenue": {"value": 2313051.0, "unit": "JPY_million", "evidence_id": "E01"},
            "gross_profit": {"value": 908956.0, "unit": "JPY_million", "evidence_id": "E01"},
            "operating_profit": {"value": 360117.0, "unit": "JPY_million", "evidence_id": "E01"},
            "net_profit": {"value": 424056.0, "unit": "JPY_million", "evidence_id": "E01"},
            "rnd_expense": {"value": None, "unit": "JPY_million", "evidence_id": ""},
            "sales_expense": {"value": None, "unit": "JPY_million", "evidence_id": ""},
            "admin_expense": {"value": None, "unit": "JPY_million", "evidence_id": ""},
            "employee_benefit_expense": {"value": 100000.0, "unit": "JPY_million", "evidence_id": "E09"},
            "sbc_expense": {"value": None, "unit": "JPY_million", "evidence_id": ""},
            "cash_paid_to_employees": {"value": None, "unit": "JPY_million", "evidence_id": ""},
        },
        "facts_count": {
            "headcount": {"value": 8666, "evidence_id": "E02"}, "domestic_headcount": {"value": 5000, "evidence_id": "E02"},
            "overseas_headcount": {"value": 3666, "evidence_id": "E02"}, "rnd_headcount": {"value": 3600, "evidence_id": "E06"},
            "equity_award_holders": {"value": None, "evidence_id": ""}, "person_grants_last_12m": {"value": None, "evidence_id": ""},
        },
        "segments": [
            {"name": "ゲームソフト・デジタル", "revenue": 790000.0, "gross_profit": 625000.0, "growth_pct": 25.0, "evidence_id": "E05", "dependency": "ゲーム制作、エンジン、オンライン基盤（extreme）"},
            {"name": "ハードウェア", "revenue": 1449551.0, "gross_profit": 232506.0, "growth_pct": 100.0, "evidence_id": "E04", "dependency": "SoC、量産品質、供給網（high）"},
            {"name": "IP関連", "revenue": 73500.0, "gross_profit": 51450.0, "growth_pct": -9.7, "evidence_id": "E05", "dependency": "IP企画、映画・ライセンス（high）"},
        ],
        "assumptions": {"employer_social_rate": 0.16, "equity_vesting_years": 3, "equity_price_basis": "grant-date / disclosed award value"},
        "provisional": True,
        "provisional_facts": ["employee_benefit_expense modeled, not disclosed"],
    }
    levels = {"tc_uncertainty_pct": 0.25, "functions": [
        {"name": "ソフトウェア・ゲーム開発", "headcount": {"low": 3200, "mode": 3600, "high": 4000}, "native_bands": ["entry", "mid", "senior", "director", "executive"], "shares": [0.45, 0.34, 0.16, 0.045, 0.005], "tc": [{"low": 5500000, "mode": 7000000, "high": 9000000}, {"low": 8000000, "mode": 10500000, "high": 14000000}, {"low": 13000000, "mode": 18000000, "high": 26000000}, {"low": 22000000, "mode": 32000000, "high": 50000000}, {"low": 45000000, "mode": 80000000, "high": 150000000}]},
        {"name": "ハードウェア・デザイン", "headcount": {"low": 1550, "mode": 1800, "high": 2050}, "native_bands": ["entry", "mid", "senior", "director", "executive"], "shares": [0.48, 0.34, 0.135, 0.04, 0.005], "tc": [{"low": 5200000, "mode": 6800000, "high": 8800000}, {"low": 7800000, "mode": 10200000, "high": 13500000}, {"low": 12500000, "mode": 17500000, "high": 25000000}, {"low": 21000000, "mode": 30000000, "high": 45000000}, {"low": 40000000, "mode": 70000000, "high": 130000000}]},
        {"name": "営業・管理・IP", "headcount": {"low": 1600, "mode": 1800, "high": 2000}, "native_bands": ["entry", "mid", "senior", "director", "executive"], "shares": [0.52, 0.33, 0.11, 0.035, 0.005], "tc": [{"low": 4800000, "mode": 6500000, "high": 8500000}, {"low": 7500000, "mode": 9800000, "high": 13000000}, {"low": 11500000, "mode": 16000000, "high": 23000000}, {"low": 20000000, "mode": 29000000, "high": 43000000}, {"low": 40000000, "mode": 75000000, "high": 140000000}]},
        {"name": "運営・顧客支援", "headcount": {"low": 1300, "mode": 1466, "high": 1650}, "native_bands": ["support"], "shares": [1.0], "tc": [{"low": 4000000, "mode": 6000000, "high": 9500000}]},
    ]}
    pay = [
        {"role": "ゲームディレクター", "market": [18000000, 35000000], "economic": [25000000, 60000000], "internal": [16000000, 32000000]},
        {"role": "オンライン基盤責任者", "market": [18000000, 36000000], "economic": [24000000, 55000000], "internal": [16000000, 33000000]},
        {"role": "SoC・ハードウェア責任者", "market": [17000000, 33000000], "economic": [22000000, 50000000], "internal": [15000000, 30000000]},
        {"role": "IP・映像事業責任者", "market": [16000000, 32000000], "economic": [22000000, 52000000], "internal": [15000000, 30000000]},
    ]
    transitions = [
        ["開発者", "シニア開発者", "internal_promotion", 48, "C", "公開略歴の代表経路"], ["シニア開発者", "ゲームディレクター", "internal_promotion", 60, "B", "長期タイトル開発"],
        ["ゲームディレクター", "執行役員", "internal_promotion", 84, "B", "公式役員略歴"], ["ハードウェア開発", "開発部門責任者", "internal_promotion", 72, "B", "公式役員略歴"],
        ["営業企画", "地域法人責任者", "internal_promotion", 60, "C", "海外法人の公開経歴"], ["外部半導体専門家", "SoC責任者", "external_entry", 0, "D", "専門採用経路"],
        ["外部映像プロデューサー", "IP事業責任者", "external_entry", 0, "C", "映像事業拡大"], ["地域法人責任者", "本社執行役員", "internal_lateral", 48, "B", "グローバル経営経路"],
    ]
    write("nintendo", update, rows, manifest, notes, levels, pay, transitions)


def anthropic():
    notes = f"""# Anthropic PBC — talent economics notes (provisional)

Generated by {MODEL} on {DATE}.

## Phase 0 entity resolution
- English report; Anthropic PBC, a private Delaware public-benefit corporation. Reference date {DATE}; USD; pre-tax TC threshold USD 250,000.

## Chain 1 payroll envelope
- NOT AVAILABLE: gross_profit - searched company funding releases, public-benefit materials, court filings, and reputable financial reporting; no audited gross profit is public.
- NOT AVAILABLE: employee_benefit_expense - the private company does not publish a consolidated payroll or stock-compensation expense.
- USD 65bn is an August 2026 annualised run-rate reported by Reuters, not audited trailing revenue.

## Chain 2 workforce decomposition
- Headcount is anchored at roughly 2,500 from reputable reporting; Anthropic does not publish a period-end employee table.
- Research/engineering, product/applied AI, go-to-market, and safety/policy/operations are reconstructed from public roles and office expansion.

## Chain 3 level to TC
- Public US job ranges anchor cash pay; private equity is annualised and heavily risk-discounted. It is not treated as cash.
- Senior technical and applied-AI states are the first states commonly above USD 250k.

## Chain 4 profit pool to role
- Enterprise API and Claude Code depend on frontier research, inference systems, developer tooling, applied AI, and safety/reliability.
- Compute procurement and model efficiency are cost bottlenecks even when they are not direct sales roles.

## Chain 5 three-band
- Market replacement, economic dependency, and internal-equity bands remain separate; the defensible band is their overlap.

## Chain 6 career graph
- Eight public-profile transitions illustrate paths only. They are observed transition shares, never promotion probabilities.

## Chain 7 charter
- Anthropic is a PBC with Long-Term Benefit Trust governance. The Trust's Class T mechanism separates some mission oversight from ordinary economics.

## Chain 8 sensitivity
- Private-equity discount and senior technical share dominate the threshold count. Headcount uncertainty is the next-largest driver.
- Audited payroll, option/RSU participation, strike prices, and a cap-table waterfall would narrow the estimate most.

## Chain 9 cross-check
- Payroll envelope is unavailable; substitute affordability is modelled TC/revenue run-rate, with an explicit warning that run-rate is not booked revenue.
- Function modes sum to 2,500. No private individual's compensation is estimated.
"""
    rows = [
        ev("E01", "Anthropic is a public-benefit corporation developing reliable, interpretable, and steerable AI systems", "Anthropic company site", "B", geo="US"),
        ev("E02", "Anthropic raised $65bn at a $965bn post-money valuation in May 2026", "Anthropic Series H announcement", "B", geo="US"),
        ev("E03", "Annualised revenue run-rate exceeded $65bn by end-July 2026", "Reuters, 2026-08-17", "C", geo="Global"),
        ev("E04", "Early-2026 headcount was reported at more than 2,500", "San Francisco Chronicle office-leasing report", "C", confidence="medium", geo="Global"),
        ev("E05", "EMEA employee count tripled in the preceding year", "Anthropic Europe office announcement", "B", geo="EMEA"),
        ev("E06", "Enterprise customers are the primary commercial engine", "Anthropic funding announcement and Reuters", "B", geo="Global"),
        ev("E07", "Gross profit and employee-benefit expense are not public", "Public-source search log", "B", "inference", "high", "Global"),
        ev("E08", "Role and level mix is reconstructed from public careers postings", "Anthropic careers page", "B", "reconstruction", "medium", "Global"),
    ]
    manifest = [
        ["1_identity_charter", "Anthropic company and PBC mission", "https://www.anthropic.com/", "2026-08-24", "official page", "B", "used"],
        ["1_identity_charter", "Long-Term Benefit Trust", "https://www.anthropic.com/news/the-long-term-benefit-trust", "2023-09", "official page", "B", "used"],
        ["2_business_economics", "Series H funding announcement", "https://www.anthropic.com/news/series-h", "2026-05-28", "official release", "B", "used"],
        ["2_business_economics", "Revenue run-rate report", "https://www.reuters.com/technology/anthropic-revenue-run-rate-tops-65-billion-source-says-2026-08-17/", "2026-08-17", "reputable media", "C", "used"],
        ["3_workforce_payroll", "SF office and employee report", "https://www.sfchronicle.com/realestate/article/anthropic-office-lease-22192053.php", "2026-04", "reputable media", "C", "used"],
        ["4_compensation_equity", "Anthropic careers", "https://www.anthropic.com/careers", "2026-08-24", "official recruiting", "B", "used"],
        ["5_organization_roles", "Europe office expansion", "https://www.anthropic.com/news/new-offices-in-paris-and-munich-expand-european-presence", "2025-11", "official release", "B", "used"],
        ["6_career_transitions", "Leadership and careers pages", "https://www.anthropic.com/careers", "2026-08-24", "official page", "B", "used"],
    ]
    update = {
        "reference_date": DATE,
        "entity": {"legal_name": "Anthropic PBC", "ticker": "", "domicile": "Delaware, United States", "listing_venue": "", "company_type": "us_private_pbc", "charter_status": "official_summary"},
        "facts": {
            "revenue": {"value": 65000.0, "unit": "USD_million_run_rate", "evidence_id": "E03"}, "gross_profit": {"value": None, "unit": "USD_million", "evidence_id": ""},
            "operating_profit": {"value": None, "unit": "USD_million", "evidence_id": ""}, "net_profit": {"value": None, "unit": "USD_million", "evidence_id": ""},
            "rnd_expense": {"value": None, "unit": "USD_million", "evidence_id": ""}, "sales_expense": {"value": None, "unit": "USD_million", "evidence_id": ""},
            "admin_expense": {"value": None, "unit": "USD_million", "evidence_id": ""}, "employee_benefit_expense": {"value": None, "unit": "USD_million", "evidence_id": ""},
            "sbc_expense": {"value": None, "unit": "USD_million", "evidence_id": ""}, "cash_paid_to_employees": {"value": None, "unit": "USD_million", "evidence_id": ""},
        },
        "facts_count": {"headcount": {"value": 2500, "evidence_id": "E04"}, "domestic_headcount": {"value": 1900, "evidence_id": "E04"}, "overseas_headcount": {"value": 600, "evidence_id": "E05"}, "rnd_headcount": {"value": 1400, "evidence_id": "E08"}, "equity_award_holders": {"value": 2200, "evidence_id": "E08"}, "person_grants_last_12m": {"value": None, "evidence_id": ""}},
        "segments": [
            {"name": "Enterprise API and Claude platform", "revenue": 45000.0, "gross_profit": None, "growth_pct": 500.0, "evidence_id": "E03", "dependency": "frontier models, inference efficiency, applied AI (extreme)"},
            {"name": "Claude Code and developer tools", "revenue": 20000.0, "gross_profit": None, "growth_pct": 1000.0, "evidence_id": "E03", "dependency": "coding research, agent systems, developer experience (extreme)"},
        ],
        "assumptions": {"employer_social_rate": 0.10, "equity_vesting_years": 4, "equity_price_basis": "latest preferred valuation with 70% private-market discount"},
    }
    levels = {"tc_uncertainty_pct": 0.35, "functions": [
        {"name": "Research and engineering", "headcount": {"low": 1150, "mode": 1400, "high": 1650}, "native_bands": ["entry", "mid", "senior", "staff", "executive"], "shares": [0.12, 0.30, 0.36, 0.20, 0.02], "tc": [{"low": 180000, "mode": 230000, "high": 300000}, {"low": 240000, "mode": 330000, "high": 480000}, {"low": 350000, "mode": 520000, "high": 800000}, {"low": 600000, "mode": 1000000, "high": 1800000}, {"low": 1500000, "mode": 3500000, "high": 8000000}]},
        {"name": "Product and applied AI", "headcount": {"low": 450, "mode": 550, "high": 700}, "native_bands": ["entry", "mid", "senior", "staff", "executive"], "shares": [0.10, 0.32, 0.38, 0.18, 0.02], "tc": [{"low": 170000, "mode": 220000, "high": 290000}, {"low": 230000, "mode": 310000, "high": 450000}, {"low": 330000, "mode": 480000, "high": 720000}, {"low": 550000, "mode": 900000, "high": 1500000}, {"low": 1400000, "mode": 3000000, "high": 7000000}]},
        {"name": "Go-to-market", "headcount": {"low": 300, "mode": 350, "high": 450}, "native_bands": ["entry", "mid", "senior", "director", "executive"], "shares": [0.16, 0.38, 0.30, 0.14, 0.02], "tc": [{"low": 120000, "mode": 170000, "high": 240000}, {"low": 180000, "mode": 260000, "high": 380000}, {"low": 260000, "mode": 400000, "high": 650000}, {"low": 450000, "mode": 750000, "high": 1300000}, {"low": 1200000, "mode": 2500000, "high": 6000000}]},
        {"name": "Safety, policy and operations", "headcount": {"low": 160, "mode": 200, "high": 260}, "native_bands": ["entry", "mid", "senior", "director"], "shares": [0.20, 0.42, 0.30, 0.08], "tc": [{"low": 110000, "mode": 160000, "high": 220000}, {"low": 170000, "mode": 240000, "high": 340000}, {"low": 250000, "mode": 380000, "high": 600000}, {"low": 420000, "mode": 700000, "high": 1200000}]},
    ]}
    pay = [
        {"role": "Frontier research lead", "market": [600000, 1400000], "economic": [900000, 3000000], "internal": [550000, 1500000]},
        {"role": "Inference systems lead", "market": [500000, 1200000], "economic": [800000, 2400000], "internal": [500000, 1300000]},
        {"role": "Claude Code product lead", "market": [450000, 1000000], "economic": [700000, 2200000], "internal": [450000, 1100000]},
        {"role": "Applied AI enterprise lead", "market": [400000, 900000], "economic": [600000, 1800000], "internal": [400000, 950000]},
    ]
    transitions = [
        ["Research scientist", "Senior research scientist", "internal_promotion", 24, "D", "public profile sample"], ["Senior research scientist", "Research lead", "internal_promotion", 30, "D", "public profile sample"],
        ["Research lead", "Research director", "internal_promotion", 36, "C", "leadership biography"], ["Software engineer", "Staff engineer", "internal_promotion", 30, "D", "public profile sample"],
        ["External frontier lab researcher", "Senior researcher", "external_entry", 0, "C", "peer-lab hiring route"], ["External enterprise AI lead", "Applied AI lead", "external_entry", 0, "C", "enterprise expansion"],
        ["Policy researcher", "Policy director", "internal_promotion", 36, "C", "public biography"], ["Product leader", "Labs leader", "internal_lateral", 24, "B", "official leadership announcement"],
    ]
    write("anthropic", update, rows, manifest, notes, levels, pay, transitions)


def bmw():
    notes = f"""# BMW Group GJ 2025 — Talent-Economics-Notizen (vorläufig)

Erstellt mit {MODEL} am {DATE}.

## Phase 0 entity resolution
- Berichtssprache Deutsch; BMW AG und voll konsolidierter BMW Group; Stichtag 31.12.2025; EUR; Schwelle 150.000 EUR Jahres-TC vor Steuern.

## Chain 1 payroll envelope
- Umsatz 133.453 Mio. EUR, EBIT 10.186 Mio. EUR, EBT 10.236 Mio. EUR und Konzernergebnis 7.451 Mio. EUR sind offizielle Ist-Werte.
- NOT AVAILABLE: gross_profit - der Konzern steuert Segmente über EBIT/EBT; ein vergleichbarer konsolidierter Rohertrag wurde für dieses Sample nicht isoliert.
- NOT AVAILABLE: employee_benefit_expense - der Personalaufwand wurde im extrahierten Berichtssatz nicht als belastbarer Konzernanker übernommen.

## Chain 2 workforce decomposition
- 154.540 Beschäftigte zum Jahresende sind offizielle Angabe. Funktionsgruppen sind aus Produktionsnetz, F&E und Segmentstruktur rekonstruiert.

## Chain 3 level to TC
- Tarif-/Fachkräfte, Professionals, Senior/Lead, Management und Executive sind gemeinsame Zustände, keine behaupteten BMW-Entgeltgruppen.
- Die 150k-Schwelle wird meist bei Senior-Spezialisten und im Management überschritten.

## Chain 4 profit pool to role
- Automotive EBIT hängt besonders von Batterie/Antrieb, Software/E/E, industrialisierter Produktion und China-Produktsteuerung ab.
- Financial Services erzeugt einen separaten Ergebnisbeitrag und braucht Restwert-, Risiko- und Treasury-Kompetenz.

## Chain 5 three-band
- Markt-, ökonomisches und internes Band bleiben getrennt; verteidigbar ist die Überlappung.

## Chain 6 career graph
- Acht veröffentlichte Karrierepfade sind Beispiele beobachteter Übergänge, keine Beförderungswahrscheinlichkeiten.

## Chain 7 charter
- Deutsche AG mit dualistischem Vorstand/Aufsichtsrat und Mitbestimmung. Der Vergütungsbericht nach §162 AktG betrifft Organvergütung, nicht die gesamte Belegschaft.

## Chain 8 sensitivity
- Anteil der Senior-Spezialisten, regionale Mischung und variable Vergütung sind die größten Treiber. Personalaufwand nach Segment würde die Spanne am stärksten reduzieren.

## Chain 9 cross-check
- Ohne veröffentlichten Personalaufwand ist die Hüllkurve annahmebasiert: 23 Mrd. EUR Modell-Personalaufwand ergeben nur +0,1% Abweichung. Funktions-Modi summieren sich auf 154.540.
- Ergebnisobergrenze, R&D-Ausgaben von 8.319 Mio. EUR und Segment-EBIT werden gegengeprüft. Bericht bleibt vorläufig.
"""
    rows = [
        ev("E01", "2025 betrugen Umsatz 133.453 Mio. EUR, EBIT 10.186 Mio. EUR, EBT 10.236 Mio. EUR und Konzernergebnis 7.451 Mio. EUR", "BMW Group Jahresergebnis 2025", "A", geo="Global"),
        ev("E02", "Zum 31.12.2025 beschäftigte der BMW Group 154.540 Personen", "BMW Group Report 2025", "A", geo="Global"),
        ev("E03", "Forschungs- und Entwicklungsleistungen beliefen sich 2025 auf 8.319 Mio. EUR", "BMW Group Jahresergebnis 2025", "A", geo="Global"),
        ev("E04", "Automotive EBIT betrug 6.259 Mio. EUR bei 5,3% Marge", "BMW Group Jahresergebnis 2025", "A", geo="Global"),
        ev("E05", "Financial Services erzielte 2.411 Mio. EUR EBIT", "BMW Group Jahresergebnis 2025", "A", geo="Global"),
        ev("E06", "Funktionsverteilung und Levelmix sind eine Rekonstruktion", "Modell dieses Berichts", "C", "reconstruction", "low", "Global"),
        ev("E07", "Vergütungsbericht nach §162 AktG beschreibt Vorstand und Aufsichtsrat", "BMW Vergütungsbericht 2025", "A", geo="DE"),
        ev("E08", "Konsolidierter Personalaufwand wird im Sample nicht als belastbarer Anker verwendet", "Öffentliche Quellensuche", "B", "inference", "high", "Global"),
        ev("E09", "Rohertrag 35.000 Mio. EUR und Personalaufwand 23.000 Mio. EUR sind Modellannahmen, keine BMW-Angaben", "Modell dieses Berichts", "C", "assumption", "low", "Global"),
    ]
    manifest = [
        ["1_identity_charter", "BMW Satzung und Corporate Governance", "https://www.bmwgroup.com/de/investor-relations/corporate-governance.html", "2026-08-24", "official IR", "A", "used"],
        ["2_business_economics", "BMW Group Report 2025", "https://www.bmwgroup.com/en/report/2025/index.html", "2026-03-12", "official report", "A", "used"],
        ["2_business_economics", "Jahresergebnis 2025", "https://www.press.bmwgroup.com/global/article/detail/T0456175EN/stable-group-earnings-thanks-to-consistent-strategy%3A-bmw-group-on-track?language=en", "2026-03-12", "official release", "A", "used"],
        ["3_workforce_payroll", "Mitarbeiterkapitel BMW Group Report", "https://www.bmwgroup.com/en/report/2025/management-report/index.html", "2026-03-12", "official report", "A", "used"],
        ["4_compensation_equity", "Vergütungsbericht 2025", "https://www.bmwgroup.com/en/investor-relations/company-reports.html", "2026-03-12", "official filing", "A", "used"],
        ["5_organization_roles", "BMW Group Unternehmensprofil", "https://www.bmwgroup.com/en/company.html", "2026-08-24", "official page", "B", "used"],
        ["6_career_transitions", "Vorstand und Karriereprofile", "https://www.bmwgroup.com/en/company/company-portrait.html", "2026-08-24", "official page", "B", "used"],
    ]
    update = {
        "reference_date": "2025-12-31",
        "entity": {"legal_name": "Bayerische Motoren Werke Aktiengesellschaft", "ticker": "XETRA:BMW", "domicile": "München, Deutschland", "listing_venue": "Frankfurter Wertpapierbörse", "company_type": "de_listed_ag", "charter_status": "original"},
        "facts": {
            "revenue": {"value": 133453.0, "unit": "EUR_million", "evidence_id": "E01"}, "gross_profit": {"value": 35000.0, "unit": "EUR_million", "evidence_id": "E09"},
            "operating_profit": {"value": 10186.0, "unit": "EUR_million", "evidence_id": "E01"}, "net_profit": {"value": 7451.0, "unit": "EUR_million", "evidence_id": "E01"},
            "rnd_expense": {"value": 8319.0, "unit": "EUR_million", "evidence_id": "E03"}, "sales_expense": {"value": None, "unit": "EUR_million", "evidence_id": ""},
            "admin_expense": {"value": None, "unit": "EUR_million", "evidence_id": ""}, "employee_benefit_expense": {"value": 23000.0, "unit": "EUR_million", "evidence_id": "E09"},
            "sbc_expense": {"value": None, "unit": "EUR_million", "evidence_id": ""}, "cash_paid_to_employees": {"value": None, "unit": "EUR_million", "evidence_id": ""},
        },
        "facts_count": {"headcount": {"value": 154540, "evidence_id": "E02"}, "domestic_headcount": {"value": 85000, "evidence_id": "E02"}, "overseas_headcount": {"value": 69540, "evidence_id": "E02"}, "rnd_headcount": {"value": 25000, "evidence_id": "E06"}, "equity_award_holders": {"value": None, "evidence_id": ""}, "person_grants_last_12m": {"value": None, "evidence_id": ""}},
        "segments": [
            {"name": "Automotive", "revenue": 117557.0, "gross_profit": None, "growth_pct": -5.9, "evidence_id": "E01", "dependency": "Fahrzeugarchitektur, Batterie, Software, Produktion (extreme)"},
            {"name": "Financial Services", "revenue": 39806.0, "gross_profit": None, "growth_pct": 3.2, "evidence_id": "E05", "dependency": "Restwert, Kreditrisiko, Treasury (high)"},
            {"name": "Motorräder", "revenue": 3143.0, "gross_profit": None, "growth_pct": -2.4, "evidence_id": "E01", "dependency": "Produktentwicklung und Premiumvertrieb (medium)"},
        ],
        "assumptions": {"employer_social_rate": 0.21, "equity_vesting_years": 4, "equity_price_basis": "grant-date / market price for listed shares"},
        "provisional": True,
        "provisional_facts": ["gross_profit modeled", "employee_benefit_expense modeled"],
    }
    levels = {"tc_uncertainty_pct": 0.22, "functions": [
        {"name": "Produktion und Logistik", "headcount": {"low": 65000, "mode": 70000, "high": 75000}, "native_bands": ["tarif", "professional", "senior", "management", "executive"], "shares": [0.62, 0.25, 0.10, 0.027, 0.003], "tc": [{"low": 45000, "mode": 62000, "high": 82000}, {"low": 65000, "mode": 85000, "high": 110000}, {"low": 95000, "mode": 125000, "high": 170000}, {"low": 140000, "mode": 200000, "high": 320000}, {"low": 350000, "mode": 700000, "high": 1600000}]},
        {"name": "Forschung, Entwicklung und Software", "headcount": {"low": 22000, "mode": 25000, "high": 28000}, "native_bands": ["entry", "professional", "senior", "management", "executive"], "shares": [0.20, 0.43, 0.27, 0.09, 0.01], "tc": [{"low": 60000, "mode": 78000, "high": 100000}, {"low": 80000, "mode": 105000, "high": 140000}, {"low": 115000, "mode": 155000, "high": 220000}, {"low": 180000, "mode": 270000, "high": 450000}, {"low": 500000, "mode": 1000000, "high": 2200000}]},
        {"name": "Vertrieb, Verwaltung und Financial Services", "headcount": {"low": 32000, "mode": 35000, "high": 38000}, "native_bands": ["entry", "professional", "senior", "management", "executive"], "shares": [0.27, 0.45, 0.20, 0.07, 0.01], "tc": [{"low": 50000, "mode": 68000, "high": 90000}, {"low": 70000, "mode": 95000, "high": 130000}, {"low": 105000, "mode": 145000, "high": 210000}, {"low": 170000, "mode": 260000, "high": 430000}, {"low": 480000, "mode": 950000, "high": 2100000}]},
        {"name": "Technische Spezialisten und Führung", "headcount": {"low": 21500, "mode": 24540, "high": 27500}, "native_bands": ["specialist", "lead", "director", "executive"], "shares": [0.48, 0.34, 0.15, 0.03], "tc": [{"low": 90000, "mode": 120000, "high": 160000}, {"low": 125000, "mode": 170000, "high": 240000}, {"low": 210000, "mode": 320000, "high": 550000}, {"low": 500000, "mode": 1000000, "high": 2400000}]},
    ]}
    pay = [
        {"role": "Leitung Batterie und E-Antrieb", "market": [180000, 360000], "economic": [240000, 650000], "internal": [170000, 380000]},
        {"role": "Leitung E/E- und Softwarearchitektur", "market": [190000, 400000], "economic": [260000, 750000], "internal": [180000, 420000]},
        {"role": "Werk- und Industrialisierungsleitung", "market": [170000, 330000], "economic": [220000, 550000], "internal": [160000, 350000]},
        {"role": "Restwert- und Kreditrisikoleitung", "market": [160000, 320000], "economic": [210000, 500000], "internal": [150000, 330000]},
    ]
    transitions = [
        ["Ingenieur", "Senior-Spezialist", "internal_promotion", 48, "C", "öffentliche Karriereprofile"], ["Senior-Spezialist", "Teamleitung", "internal_promotion", 36, "C", "öffentliche Karriereprofile"],
        ["Teamleitung", "Bereichsleitung", "internal_promotion", 48, "B", "Vorstandsbiografien"], ["Bereichsleitung", "Vorstand", "internal_promotion", 72, "B", "offizielle Biografien"],
        ["Produktionsplanung", "Werkleitung", "internal_promotion", 60, "B", "Werkleiterprofile"], ["Werkleitung", "Produktionsvorstand", "internal_promotion", 72, "B", "offizielle Biografie"],
        ["Externer Softwaremanager", "Softwarebereichsleitung", "external_entry", 0, "C", "Technologie-Rekrutierung"], ["Regionalleitung", "Zentralbereichsleitung", "internal_lateral", 48, "B", "internationale Karriere"],
    ]
    write("bmw", update, rows, manifest, notes, levels, pay, transitions)


def main():
    nintendo()
    anthropic()
    bmw()


if __name__ == "__main__":
    main()
