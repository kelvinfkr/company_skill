# Public-data source playbook

Search broad-to-narrow, but always end at a fetched primary document. A search snippet is a pointer, not a source.

## Six mandatory passes

Run each pass separately and log it in `source_manifest.csv` even when it finds nothing. `scripts/search_plan.py --jurisdiction <cn|hk|us|private|other>` prints the query ladder per pass.

| Pass | Goal | Stop when |
|---|---|---|
| 1 Identity & charter | legal entity, ticker, domicile, share classes, articles, WVR terms, board | current articles status recorded (original / official_summary / reconstructed) |
| 2 Business economics | revenue, gross profit, operating profit by segment; customer concentration; opex by function | latest annual report fetched and segment gross profit table extracted |
| 3 Workforce & payroll | headcount by geography/function, R&D count, employee benefit expense, cash paid to employees, SBC | all five numbers found or explicitly marked unavailable |
| 4 Compensation & equity | equity plan terms, grant announcements (shares, recipients, vesting), recipient count, director/executive pay, level-pay tables | ≥2 grant announcements in last 18 months + one level table + director pay |
| 5 Organisation & critical roles | native level ladder, BU structure, named leaders of profit pools, recent org changes | every top-3 profit pool has a named owning function |
| 6 Career transitions | executive bios, appointment/promotion announcements, public profile patterns | ≥10 dated transitions or documented that fewer exist |

## Primary-source routing by venue

- HKEX: `hkexnews.hk` (results announcements, annual reports, "grant of awards" announcements, Form 1 for share plans); issuer IR site for PDFs.
- SEC: EDGAR full-text search; 10-K Item 1 "Human Capital", DEF 14A, S-1/F-1, 8-K Item 5.02.
- PRC A-share: `cninfo.com.cn`; annual report sections 员工情况, 董事监事高管薪酬, 股权激励; 招股说明书 for pre-IPO history.
- PRC private: 国家企业信用信息公示系统 (registration changes), 天眼查/企查查 (secondary), financing announcements, court records.
- Any: company careers site, official WeChat/press releases, ESG report (often has turnover and training data).

## Query ladder per pass (replace placeholders)

### Pass 1
- `"{legal_name}" 组织章程 / articles of association`
- `"{company}" prospectus share classes voting rights`
- `"{company}" 不同投票权 / dual class / WVR beneficiaries`

### Pass 2
- `"{company}" {year} 全年業績 / annual results announcement`
- `"{company}" segment gross profit {year}`
- `"{company}" largest customer percentage revenue`

### Pass 3
- `"{company}" 全職僱員 研發人員 {year}`
- `"{company}" 僱員福利開支 / employee benefit expense`
- `"{company}" 以股份為基礎的薪酬 / share-based compensation {year}`

### Pass 4
- `"{company}" 授出奖励 奖励股份 选定参与者` (HKEX share-award grants)
- `"{company}" 限制性股票 激励计划 授予` (A-share)
- `"{company}" 职级 薪资 总包` (level tables; Tier E)
- `"{company}" 董事 薪酬 年报` / DEF 14A

### Pass 5
- `"{company}" 组织架构 调整 任命 负责人`
- `"{company}" 事业部 总经理 / business unit president`
- `"{company}" 职级 体系 P M 序列`

### Pass 6
- `"{company}" 晋升 副总裁 / promoted to vice president`
- `"{company}" 加入 出任 原 {peer_company}` (external entries)
- executive biography pages on IR site

## Fetch discipline

1. When a search result is a filing, fetch the full document and cite the page/section.
2. When a Tier E page quotes a filing, find the filing; keep the Tier E page only as a pointer.
3. Record in the manifest: source, URL, publish date, type, tier, status (`used` / `calibration only` / `searched, not found` / `not retrieved`).
4. Never paste long passages. Record the number, the unit, the period, and your paraphrase.

## Evidence ledger discipline

For every material fact record: exact claim; source; publish and observation dates; tier; company/BU/function/level/geography specificity; claim type (`observed_fact` / `derived_metric` / `assumption` / `inference` / `reconstruction`); confidence; notes.
