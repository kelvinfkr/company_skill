#!/usr/bin/env python3
"""Fill analyst-authored prose for the multilingual sample reports."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODEL = "OpenAI Codex (GPT-5.6)"
DATE = "2026-08-24"


def load(slug):
    path = ROOT / slug / "report.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def save(path, report):
    report["meta"]["model"] = MODEL
    report["meta"]["generated_at"] = DATE
    path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")


def uncertainty(report, text):
    for row in report["high_compensation"]["rows"]:
        row["uncertainty"] = text


def nintendo():
    p, r = load("nintendo")
    r["meta"]["entity_type"] = "東証上場の日本株式会社（連結グループ）"
    r["meta"]["scope"] = "任天堂株式会社および連結子会社。職能配分は公開資料からの再構築"
    r["executive"]["diagnosis"] = "任天堂は高いソフトウェア粗利を少数精鋭の開発組織で支える構造で、2,000万円超は主に上位開発者・ディレクターに集中するが、連結人件費が未開示のため人数は暫定レンジである。"
    r["executive"]["metrics"][2]["value"] = "約1,154万 JPY（モデル仮定）"
    uncertainty(r, "連結人件費、職能別等級、海外報酬換算はモデル仮定。会社開示の実測人数ではない")
    r["talent_pnl"] = [
        {"profit_pool": "ゲームソフト・デジタル", "process": "ゲーム企画と制作", "role": "ゲームディレクター／リード開発者", "dependency": "極めて高い", "why": "高粗利IPの品質と発売時期を直接左右する"},
        {"profit_pool": "デジタル継続収益", "process": "オンライン基盤と運用", "role": "ネットワーク／プラットフォーム責任者", "dependency": "高い", "why": "アカウント、ストア、マルチプレイの信頼性が継続収益を支える"},
        {"profit_pool": "ハードウェア", "process": "SoC・量産品質・供給網", "role": "ハードウェア／サプライチェーン責任者", "dependency": "高い", "why": "普及台数と原価が将来のソフトウェア利益を規定する"},
        {"profit_pool": "IP関連", "process": "映像・ライセンス展開", "role": "IP／映像事業責任者", "dependency": "高い", "why": "ゲーム外接点を増やし、長期IP価値を広げる"},
    ]
    r["organization"] = [
        {"native": "entry（再構築）", "track": "IC", "scope": "担当機能", "function": "開発・デザイン", "state": "entry", "confidence": "低"},
        {"native": "mid（再構築）", "track": "IC/M", "scope": "機能・小規模チーム", "function": "全職能", "state": "mid", "confidence": "中"},
        {"native": "senior（再構築）", "track": "IC/M", "scope": "タイトル／重要システム", "function": "開発・ハードウェア", "state": "senior", "confidence": "低"},
        {"native": "director（再構築）", "track": "M", "scope": "部門／複数タイトル", "function": "全職能", "state": "director", "confidence": "低"},
        {"native": "執行役員", "track": "経営", "scope": "全社／事業領域", "function": "グループ", "state": "executive", "confidence": "高"},
    ]
    r["role_pay"] = [
        {"role": "ゲームディレクター", "market": "1,800-3,500万円", "economic": "2,500-6,000万円", "internal": "1,600-3,200万円", "defensible": "2,500-3,200万円", "diagnostic": "重複あり。タイトル成功連動の変動報酬が重要"},
        {"role": "オンライン基盤責任者", "market": "1,800-3,600万円", "economic": "2,400-5,500万円", "internal": "1,600-3,300万円", "defensible": "2,400-3,300万円", "diagnostic": "市場圧力が強い"},
        {"role": "SoC・ハードウェア責任者", "market": "1,700-3,300万円", "economic": "2,200-5,000万円", "internal": "1,500-3,000万円", "defensible": "2,200-3,000万円", "diagnostic": "希少性プレミアムが必要"},
        {"role": "IP・映像事業責任者", "market": "1,600-3,200万円", "economic": "2,200-5,200万円", "internal": "1,500-3,000万円", "defensible": "2,200-3,000万円", "diagnostic": "長期IP価値と連動"},
    ]
    r["career"] = {
        "internal_path": ["開発者 → シニア開発者 → ゲームディレクター", "部門責任者 → 執行役員"],
        "external_path": ["半導体専門家 → SoC責任者", "映像プロデューサー → IP事業責任者"],
        "first_threshold_state": "上位seniorまたはdirector。賞与年度と海外報酬換算に依存する",
        "promotion_tenure": "公開8経路では通常4-7年単位。これは観測経路であり会社全体の率ではない",
        "senior_hire_mix": "ゲーム制作は内部育成中心、半導体・オンライン・映像は外部採用も重要",
    }
    r["governance"] = [
        {"metric": "上場・法形式", "value": "東証7974、日本株式会社", "evidence": "有価証券報告書"},
        {"metric": "平均年間給与", "value": "単体982.5万円（賞与等を含む）", "evidence": "第86期有価証券報告書"},
        {"metric": "報酬設計", "value": "固定報酬と業績連動要素。連結非役員株式報酬は未取得", "evidence": "有価証券報告書・報酬開示"},
        {"metric": "取締役会", "value": "取締役会と執行役員の役割分担", "evidence": "コーポレートガバナンス報告"},
    ]
    r["sensitivity"] = [
        "開発senior比率を±25%変えると2,000万円超p50は概ね150-220人動く。",
        "海外従業員の通貨換算と賞与年度が第2の感応度である。",
        "連結人件費1,000億円はモデル仮定であり、10%変化すれば全TC帯の再校正が必要。",
        "連結人件費、株式報酬参加人数、正式等級別人数が最も価値の高い追加証拠である。",
    ]
    r["evidence"] = [
        {"id": "A01", "source": "2026年3月期 決算短信", "date": "2026-05-08", "status": "開示", "supports": "売上高、粗利益、営業利益、純利益"},
        {"id": "A02", "source": "第86期 有価証券報告書・会社概要", "date": "2026-06", "status": "開示", "supports": "従業員数、単体平均年間給与"},
        {"id": "B01", "source": "採用・役員情報", "date": "2026-08", "status": "校正", "supports": "職種と経路"},
        {"id": "M01", "source": "本レポートの50,000回シミュレーション", "date": DATE, "status": "モデル", "supports": "閾値超人数とTC分布"},
    ]
    r["charter"] = {
        "summary": [
            {"item": "法人・上場", "current": "任天堂株式会社、東証プライム7974", "historical": "京都を本拠とする日本株式会社", "evidence": "定款・有価証券報告書"},
            {"item": "統治", "current": "取締役会と執行役員による監督・執行分離", "historical": "長期IP投資を重視", "evidence": "ガバナンス報告"},
            {"item": "従業員インセンティブ", "current": "固定給・賞与中心。特許・制作貢献の報奨制度", "historical": "利益連動要素を継続", "evidence": "有価証券報告書"},
        ],
        "timeline": [
            {"date": "1889", "event": "創業", "economic": "娯楽IPの長期蓄積", "control": "京都本社", "status": "公式沿革"},
            {"date": "2025-06", "event": "Nintendo Switch 2発売", "economic": "新ハード普及サイクル", "control": "大型投資と供給判断", "status": "公式資料"},
            {"date": "2026-03", "event": "FY2026終了", "economic": "売上2.31兆円", "control": "取締役会・執行役員体制", "status": "原資料"},
        ],
    }
    save(p, r)


def anthropic():
    p, r = load("anthropic")
    r["meta"]["entity_type"] = "Private Delaware public-benefit corporation"
    r["meta"]["scope"] = "Anthropic PBC globally; workforce and function mix reconstructed from public reporting and job postings"
    r["executive"]["diagnosis"] = "Anthropic is an unusually senior, equity-heavy frontier-lab organisation: the model places most employees above $250k TC, but private-equity value, headcount, revenue run-rate, and payroll are all provisional rather than audited."
    r["executive"]["metrics"][2]["value"] = "about $577k (modelled TC, not disclosed payroll)"
    for row in r["business"]["profit_pools"]:
        if row.get("gross_profit") == "TODO":
            row["gross_profit"] = "Not publicly available"
    uncertainty(r, "Headcount, level mix, private-equity value, and threshold crossing are model estimates, not company measurements")
    r["talent_pnl"] = [
        {"profit_pool": "Enterprise API", "process": "Frontier model research", "role": "Frontier research lead", "dependency": "extreme", "why": "Capability and reliability define product value and price"},
        {"profit_pool": "Enterprise API", "process": "Inference efficiency", "role": "Inference systems lead", "dependency": "extreme", "why": "Latency and compute cost directly shape gross economics"},
        {"profit_pool": "Claude Code", "process": "Agentic coding product", "role": "Claude Code product/engineering lead", "dependency": "extreme", "why": "Developer workflow quality drives adoption and retention"},
        {"profit_pool": "Enterprise deployment", "process": "Applied AI and reliability", "role": "Applied AI enterprise lead", "dependency": "high", "why": "Deployment success converts model capability into durable contracts"},
    ]
    r["organization"] = [
        {"native": "entry (reconstructed)", "track": "IC", "scope": "component", "function": "research/engineering", "state": "entry", "confidence": "low"},
        {"native": "mid (reconstructed)", "track": "IC/M", "scope": "system/project", "function": "all", "state": "mid", "confidence": "medium"},
        {"native": "senior", "track": "IC/M", "scope": "critical system/team", "function": "research/product/GTM", "state": "senior", "confidence": "medium"},
        {"native": "staff/director", "track": "IC/M", "scope": "multi-team/platform", "function": "all", "state": "staff/director", "confidence": "medium"},
        {"native": "executive", "track": "leadership", "scope": "company/function", "function": "group", "state": "executive", "confidence": "high"},
    ]
    r["role_pay"] = [
        {"role": "Frontier research lead", "market": "$600k-$1.4m", "economic": "$900k-$3.0m", "internal": "$550k-$1.5m", "defensible": "$900k-$1.4m", "diagnostic": "Overlap; equity risk must remain explicit"},
        {"role": "Inference systems lead", "market": "$500k-$1.2m", "economic": "$800k-$2.4m", "internal": "$500k-$1.3m", "defensible": "$800k-$1.2m", "diagnostic": "Compute economics support a premium"},
        {"role": "Claude Code product lead", "market": "$450k-$1.0m", "economic": "$700k-$2.2m", "internal": "$450k-$1.1m", "defensible": "$700k-$1.0m", "diagnostic": "Product ownership is economically scarce"},
        {"role": "Applied AI enterprise lead", "market": "$400k-$900k", "economic": "$600k-$1.8m", "internal": "$400k-$950k", "defensible": "$600k-$900k", "diagnostic": "Revenue conversion supports variable pay"},
    ]
    r["career"] = {
        "internal_path": ["Research scientist → senior researcher → research lead", "Engineer → staff engineer → platform lead"],
        "external_path": ["Peer-lab researcher → senior researcher", "Enterprise AI leader → applied AI lead"],
        "first_threshold_state": "Upper-mid or senior technical/applied-AI roles; equity valuation is decisive",
        "promotion_tenure": "The eight public paths suggest 2-3 year steps, but they are observed transitions, not promotion probabilities",
        "senior_hire_mix": "Core safety culture favours internal development; rapid product, GTM, and international growth requires external leaders",
    }
    r["governance"] = [
        {"metric": "Legal form", "value": "Delaware public-benefit corporation", "evidence": "Anthropic company materials"},
        {"metric": "Mission governance", "value": "Long-Term Benefit Trust holds Class T governance rights", "evidence": "Anthropic Trust announcement"},
        {"metric": "Latest financing", "value": "$65bn Series H at $965bn post-money", "evidence": "Anthropic, 2026-05-28"},
        {"metric": "Employee equity", "value": "Participation, strike prices, and waterfall are not public", "evidence": "Search log"},
    ]
    r["sensitivity"] = [
        "Changing the private-equity discount from 70% to 50% materially lifts senior and staff TC; nominal valuation is never treated as cash.",
        "A ±25% change in senior technical share moves the $250k p50 count by roughly 250-400 people.",
        "The $65bn figure is an annualised run-rate, not audited revenue; TC/revenue is therefore only a weak affordability check.",
        "Audited payroll, grant participation, strike prices, and a cap-table waterfall would narrow the interval most.",
    ]
    r["evidence"] = [
        {"id": "B01", "source": "Anthropic company, funding, and Trust announcements", "date": "2023-2026", "status": "official", "supports": "PBC mission, governance, financing, valuation"},
        {"id": "C01", "source": "Reuters revenue run-rate report", "date": "2026-08-17", "status": "reported, unaudited", "supports": "commercial scale anchor"},
        {"id": "C02", "source": "Reputable office/headcount reporting", "date": "2026", "status": "reported estimate", "supports": "workforce scale"},
        {"id": "B02", "source": "Anthropic careers and office announcements", "date": "2025-2026", "status": "official calibration", "supports": "roles, geography, hiring mix"},
        {"id": "M01", "source": "This report's 50,000-draw simulation", "date": DATE, "status": "model", "supports": "threshold population and TC distribution"},
    ]
    r["charter"] = {
        "summary": [
            {"item": "Legal form", "current": "Delaware public-benefit corporation", "historical": "Founded in 2021", "evidence": "Official company materials"},
            {"item": "Mission mechanism", "current": "Long-Term Benefit Trust and Class T governance rights", "historical": "Designed to strengthen long-term public-benefit oversight", "evidence": "Official Trust announcement"},
            {"item": "Economic ownership", "current": "Private preferred/common capital structure", "historical": "Multiple financing rounds through Series H", "evidence": "Official funding releases"},
            {"item": "Employee incentives", "current": "Private equity is important but detailed terms are not public", "historical": "Rapid valuation changes create retention and fairness pressure", "evidence": "Careers/funding materials"},
        ],
        "timeline": [
            {"date": "2021", "event": "Anthropic founded", "economic": "Frontier AI research company", "control": "PBC structure", "status": "official summary"},
            {"date": "2023", "event": "Long-Term Benefit Trust announced", "economic": "Mission protection", "control": "Class T governance mechanism", "status": "official summary"},
            {"date": "2026-05", "event": "Series H financing", "economic": "$965bn post-money valuation", "control": "Private preferred capital expands", "status": "official release"},
        ],
    }
    save(p, r)


def bmw():
    p, r = load("bmw")
    r["meta"]["entity_type"] = "Börsennotierte deutsche Aktiengesellschaft mit mitbestimmtem Aufsichtsrat"
    r["meta"]["scope"] = "BMW Group konsolidiert; Funktions- und Levelmix aus öffentlichen Angaben rekonstruiert"
    r["executive"]["diagnosis"] = "BMW hat eine breite tariflich geprägte Basis und eine große technische Führungsschicht: Das Modell verortet rund ein Fünftel über 150.000 EUR TC, doch Rohertrag und Personalaufwand sind für dieses Sample modelliert und das Ergebnis daher vorläufig."
    r["executive"]["metrics"][2]["value"] = "ca. 148.800 EUR (Modellannahme)"
    for row in r["business"]["profit_pools"]:
        if row.get("gross_profit") == "TODO":
            row["gross_profit"] = "Nicht öffentlich; Konzernwert modelliert"
    uncertainty(r, "Funktionsmix, Levelverteilung und modellierter Personalaufwand sind keine von BMW gemessenen Schwellenwerte")
    r["talent_pnl"] = [
        {"profit_pool": "Automotive", "process": "Batterie und E-Antrieb", "role": "Leitung Batterie/E-Antrieb", "dependency": "sehr hoch", "why": "Reichweite, Kosten und Industrialisierung prägen Fahrzeugmarge"},
        {"profit_pool": "Automotive", "process": "E/E- und Softwarearchitektur", "role": "Software-/Architekturleitung", "dependency": "sehr hoch", "why": "NEUE KLASSE bündelt Differenzierung in Elektronik und Software"},
        {"profit_pool": "Automotive", "process": "Industrialisierung", "role": "Werk- und Produktionsleitung", "dependency": "hoch", "why": "Qualität, Anlauf und Auslastung wirken direkt auf EBIT"},
        {"profit_pool": "Financial Services", "process": "Restwert und Kreditrisiko", "role": "Risiko-/Treasury-Leitung", "dependency": "hoch", "why": "Portfolioqualität und Refinanzierung bestimmen Segmentergebnis"},
    ]
    r["organization"] = [
        {"native": "Tarif/Fachkraft (rekonstruiert)", "track": "Fach", "scope": "Arbeitsstation/Funktion", "function": "Produktion/Logistik", "state": "tarif", "confidence": "mittel"},
        {"native": "Professional", "track": "IC/M", "scope": "Modul/Projekt", "function": "alle", "state": "professional", "confidence": "mittel"},
        {"native": "Senior/Lead", "track": "IC/M", "scope": "System/Team", "function": "F&E, Software, Vertrieb", "state": "senior/lead", "confidence": "niedrig"},
        {"native": "Management/Director", "track": "M", "scope": "Bereich/Werk", "function": "alle", "state": "management", "confidence": "niedrig"},
        {"native": "Vorstand", "track": "Organ", "scope": "Konzernressort", "function": "Gruppe", "state": "executive", "confidence": "hoch"},
    ]
    r["role_pay"] = [
        {"role": "Leitung Batterie und E-Antrieb", "market": "180-360 Tsd. EUR", "economic": "240-650 Tsd. EUR", "internal": "170-380 Tsd. EUR", "defensible": "240-360 Tsd. EUR", "diagnostic": "Überlappung; langfristige Technikziele wichtig"},
        {"role": "Leitung E/E- und Softwarearchitektur", "market": "190-400 Tsd. EUR", "economic": "260-750 Tsd. EUR", "internal": "180-420 Tsd. EUR", "defensible": "260-400 Tsd. EUR", "diagnostic": "Starker externer Technologiemarkt"},
        {"role": "Werk- und Industrialisierungsleitung", "market": "170-330 Tsd. EUR", "economic": "220-550 Tsd. EUR", "internal": "160-350 Tsd. EUR", "defensible": "220-330 Tsd. EUR", "diagnostic": "Anlauf- und Qualitätsziele sollten variabel wirken"},
        {"role": "Restwert- und Kreditrisikoleitung", "market": "160-320 Tsd. EUR", "economic": "210-500 Tsd. EUR", "internal": "150-330 Tsd. EUR", "defensible": "210-320 Tsd. EUR", "diagnostic": "Risikoergebnis rechtfertigt Prämie"},
    ]
    r["career"] = {
        "internal_path": ["Ingenieur → Senior-Spezialist → Teamleitung", "Werkleitung → Produktionsressort"],
        "external_path": ["Externer Softwaremanager → Softwarebereichsleitung", "Finanzrisiko-Spezialist → Financial-Services-Leitung"],
        "first_threshold_state": "Senior-Spezialist am oberen Band oder erste größere Führungsverantwortung",
        "promotion_tenure": "Die acht öffentlichen Pfade zeigen meist 3-6 Jahre je Schritt; es sind beobachtete Übergänge, keine Beförderungswahrscheinlichkeiten",
        "senior_hire_mix": "Produktion und klassische Fahrzeugentwicklung überwiegend intern; Software und neue Technologien stärker extern",
    }
    r["governance"] = [
        {"metric": "Rechtsform", "value": "BMW AG, dualistischer Vorstand/Aufsichtsrat", "evidence": "Satzung/Governance-Bericht"},
        {"metric": "Mitbestimmung", "value": "Arbeitnehmervertretung im Aufsichtsrat", "evidence": "Corporate Governance"},
        {"metric": "Organvergütung", "value": "Vergütungsbericht nach §162 AktG", "evidence": "Vergütungsbericht 2025"},
        {"metric": "Belegschaftsaktien", "value": "Programme vorhanden; vollständige Teilnahme nach Level nicht öffentlich", "evidence": "Geschäftsbericht"},
    ]
    r["sensitivity"] = [
        "Ein ±25% höherer Senior-/Lead-Anteil verschiebt den p50-Wert um etwa 4.000-6.000 Personen.",
        "Regionale Mischung und tarifliche Sonderzahlungen sind der zweitgrößte Treiber.",
        "Der Personalaufwand von 23 Mrd. EUR und Rohertrag von 35 Mrd. EUR sind Modellannahmen, keine BMW-Angaben.",
        "Personalaufwand nach Segment, offizielle Levelverteilung und Beteiligungsquote würden die Spanne am stärksten reduzieren.",
    ]
    r["evidence"] = [
        {"id": "A01", "source": "BMW Group Jahresergebnis/Report 2025", "date": "2026-03-12", "status": "offiziell", "supports": "Umsatz, EBIT, EBT, Ergebnis, Beschäftigte, F&E"},
        {"id": "A02", "source": "Vergütungsbericht 2025", "date": "2026-03", "status": "offiziell", "supports": "Organvergütung und Governance"},
        {"id": "B01", "source": "Unternehmens-, Werk- und Karriereprofile", "date": "2026-08", "status": "Kalibrierung", "supports": "Rollen und Karrierepfade"},
        {"id": "M01", "source": "50.000 Ziehungen dieses Modells", "date": DATE, "status": "Modell", "supports": "Schwellenpopulation und TC-Verteilung"},
    ]
    r["charter"] = {
        "summary": [
            {"item": "Rechtsform", "current": "Bayerische Motoren Werke Aktiengesellschaft", "historical": "Deutsche börsennotierte AG", "evidence": "Satzung"},
            {"item": "Leitung", "current": "Vorstand führt, Aufsichtsrat überwacht", "historical": "Dualistisches deutsches Modell", "evidence": "Governance-Bericht"},
            {"item": "Mitbestimmung", "current": "Arbeitnehmervertreter im Aufsichtsrat", "historical": "Gesetzliche Mitbestimmung", "evidence": "Governance-Bericht"},
            {"item": "Vergütung", "current": "Organvergütung mit fixen, variablen und langfristigen Komponenten", "historical": "§162-AktG-Bericht", "evidence": "Vergütungsbericht"},
        ],
        "timeline": [
            {"date": "1916", "event": "Unternehmensgründung", "economic": "Aufbau industrieller Kompetenzen", "control": "Deutsche AG", "status": "offizielle Historie"},
            {"date": "2021-2025", "event": "NEUE-KLASSE-Investitionsphase", "economic": "Batterie, Software und neue Werke", "control": "Kapitalallokation durch Vorstand/Aufsichtsrat", "status": "offizielle Berichte"},
            {"date": "2025-12", "event": "Geschäftsjahr 2025", "economic": "10,2 Mrd. EUR EBT", "control": "Mitbestimmte Governance", "status": "Originalbericht"},
        ],
    }
    save(p, r)


if __name__ == "__main__":
    nintendo()
    anthropic()
    bmw()
