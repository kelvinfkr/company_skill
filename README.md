# company-talent-economics

**中文文档：[README.zh-CN.md](README.zh-CN.md)**

An agent skill that reconstructs a company's **compensation distribution, high-pay population,
economically critical roles, defensible pay bands and career graph** from public filings — and
delivers a typeset PDF, not a wall of chat text.

It works for companies **in any country**, and it writes the report **in the language of the company
name you type**. Ask about `ソニーグループ` and you get a Japanese report; ask about `Siemens AG` and
you get a German one; ask about `小米集团` and you get a Chinese one.

Runs in **Claude Code**, **Codex**, and **claude.ai** from the same folder.

---

## What you actually get

A directory of auditable artifacts, with `report.pdf` as the deliverable:

| File | What it is |
|---|---|
| `report.pdf` | The typeset report: 12 sections, cover, localized tables, evidence status on every number |
| `report.json` | The structured model the PDF is rendered from |
| `analysis_notes.md` | The nine written-out reasoning chains with intermediate numbers |
| `evidence.jsonl` | Claim-level ledger: every number, its source, its tier, its claim type |
| `source_manifest.csv` | Every source searched — including the ones that turned up nothing |
| `model.json` / `population.json` | Bucket model and the Monte Carlo population estimate |

The method runs one causal chain, in this order:

```
business model → profit pools → critical processes → critical roles
→ org/level structure → market replacement cost → compensation distribution → promotion paths
```

A title is not a salary. Two people at the same nominal level are worth different amounts if they
control different profit pools, customer relationships or technical bottlenecks — so the analysis
starts from where the money is made, not from a salary survey.

---

## Install

Pick one. The first is the shortest; the second is the most portable.

### 1. Claude Code plugin (recommended)

```
/plugin marketplace add kelvinfkr/company_skill
/plugin install company-talent-economics@company-skill
```

### 2. Clone and install (Claude Code + Codex, one command)

```bash
git clone https://github.com/kelvinfkr/company_skill.git
cd company_skill
bash install.sh
```

Symlinks the skill into `~/.claude/skills/` and `~/.codex/skills/`, then checks your dependencies.
Because it is a symlink, `git pull` updates both hosts at once.

```bash
bash install.sh --claude      # Claude Code only
bash install.sh --codex       # Codex only
bash install.sh --project     # also into ./.claude/skills of the current repo
bash install.sh --copy        # copy instead of symlink
bash install.sh --check       # verify dependencies, install nothing
bash install.sh --zip         # build dist/company-talent-economics.zip
bash install.sh --uninstall   # remove the links
```

One-liner, no clone needed (it fetches the repo into `~/.cache` first):

```bash
curl -fsSL https://raw.githubusercontent.com/kelvinfkr/company_skill/main/install.sh | bash
```

### 3. claude.ai (web / desktop)

```bash
bash install.sh --zip
```

Then upload `dist/company-talent-economics.zip` at **Settings → Capabilities → Skills → Upload skill**.

### 4. Manual

Copy or symlink `skills/company-talent-economics/` into any of:

| Host | Path |
|---|---|
| Claude Code, global | `~/.claude/skills/company-talent-economics/` |
| Claude Code, one project | `<repo>/.claude/skills/company-talent-economics/` |
| Codex | `~/.codex/skills/company-talent-economics/` |

### Requirements

| | Needed for | Install |
|---|---|---|
| Python 3.9+ | everything | already on most systems |
| `python-docx` | rendering the report | `pip install -r skills/company-talent-economics/requirements.txt` |
| LibreOffice | DOCX → PDF | `apt install libreoffice-writer` / `brew install --cask libreoffice` |
| Noto fonts | non-Latin scripts | `apt install fonts-noto-cjk fonts-noto-core` |

Everything except the renderer is standard library only. Without LibreOffice,
`render_report.py --docx-only` still produces the DOCX. `bash install.sh --check` tells you exactly
what is missing and what it affects.

---

## Use it

Just ask, in any language:

```
小米集团的员工薪酬分布是怎样的？年薪超过 100 万的有多少人？
How many people at Siemens earn above €150k, and which roles justify it?
ソニーで年収2000万円を超える社員は何人くらいいますか？
```

Or invoke it directly:

| Host | Invocation |
|---|---|
| Claude Code | `/company-talent-economics <company>` |
| Codex | `$company-talent-economics <company>` |

### Driving the harness by hand

```bash
S=~/.claude/skills/company-talent-economics

python $S/scripts/init_run.py "小米集团" --out ./talent-economics/xiaomi --year 2025
python $S/scripts/check_phase.py ./talent-economics/xiaomi --next   # prints the next phase's steps
# ...do them...
python $S/scripts/check_phase.py ./talent-economics/xiaomi          # gate check; repeat to phase 10
```

`init_run.py` infers language, jurisdiction, currency and threshold from the company name and prints
what it chose. Override any of them:

```bash
python $S/scripts/init_run.py "Nestlé S.A." --out ./tmp/nestle --year 2024 \
       --jurisdiction ch --language fr --currency CHF --threshold 250000
```

### Ten gates, no shortcuts

`check_phase.py` is the spine. Each gate mechanically refuses to advance until the work is real:
sources are logged, every figure carries an evidence id, the modelled payroll reconciles with the
disclosed payroll within ±10%, no `TODO` survives into `report.json`. The gate output *is* the
to-do list.

| Phase | Gate |
|---|---|
| 0 | Entity, language, jurisdiction resolved |
| 1 | Six search passes logged; core facts sourced |
| 2 | Payroll envelope and profit pools written out |
| 3 | Level ladder mapped |
| 4 | Compensation evidence per band |
| 5 | Population model runs and reconciles |
| 6 | Three-band pay diagnosis for critical roles |
| 7 | ≥8 career transitions |
| 8 | Charter, equity, and every prose section filled |
| 9 | Cross-checks and sensitivity |
| 10 | PDF rendered, inspected, checklist ticked |

---

## Languages and countries

### The rule

The report follows the **language of the company name**. If you write your request in a different
language from the company name, **your language wins** — you are the reader.

Resolution order: `--language` → `$CTE_LANG` → the script and legal form of the company name.

```bash
python $S/scripts/i18n.py detect "台積電股份有限公司"
# {"language": "zh-TW", "confidence": "high", "jurisdiction_hint": "tw", ...}
```

### Any language works; twelve are fully typeset

Two different things get called "language" here:

- **prose language** — the language the analysis is written in. **Any language.**
- **chrome locale** — section titles, table headers, claim-type labels, number grouping, fonts and
  text direction. **Twelve shipped packs:** `en zh-CN zh-TW ja ko es fr de pt it ru ar`

A language with no pack still produces a full report in that language; the structural labels fall
back (`zh-HK` → `zh-TW` → `en`) and the renderer says so. Numbers are scaled the way each language
actually says them — `1.2 亿`, `120M`, `1,2 Mrd.`, `2 億` — and Arabic and Hebrew render right-to-left,
with mirrored tables and footer.

**Add a language** — one JSON file, no code:

```bash
python $S/scripts/check_locales.py --new nl   # scaffolds locales/nl.json from English
# translate the strings; keep the keys and every {placeholder}
python $S/scripts/check_locales.py            # verifies it
```

### 49 jurisdictions

`assets/jurisdictions.json` carries, per country: filing venues to scope `site:` searches to, the
**local names** of the documents worth fetching, the company registry, currency, a high-pay threshold
prior, an employer social-contribution rate, and a note on what that regime is unusually good at —
or unusually misleading about.

```bash
python $S/scripts/i18n.py jurisdictions            # list all
python $S/scripts/i18n.py jurisdictions japan      # one entry; aliases resolve
```

Aliases work, so `us`, `usa`, `america`, `sec` and `nasdaq` all reach the same entry. **Add a country**
by appending an entry — again, no code change.

Search runs in two languages at once: filings are indexed under their local names
(`有価証券報告書`, `Vergütungsbericht`, `사업보고서`, `Formulário de Referência`), cross-border analyst
coverage under English ones. Searching one side loses half the evidence.

Two registry fields are **priors, not facts**, and every override is recorded in the notes:

- `threshold_default` — the round local number that reads as "high earner" there (CNY 1,000,000,
  JPY 20,000,000, USD 250,000, INR 1 crore). Not a statistical cut-off; not comparable across
  countries at market FX. Your threshold always wins.
- `employer_social_rate` — roughly 1% in Denmark, roughly 32% in Spain. The wrong one silently breaks
  the payroll envelope, so a disclosed figure always replaces it.

---

## What it refuses to do

These are enforced by the harness, not by good intentions:

- **No private individual's pay is ever inferred.** Public profiles support aggregate role taxonomy and career transitions, nothing more.
- **Public sources only.** No login walls, CAPTCHAs, robots restrictions or access controls, ever.
- **A search snippet is never a source.** The primary document gets fetched and read, or the number does not get used.
- **Forum and crowdsourced salary data is Tier E** — calibration only, never alone behind a headline number.
- **No invented numbers.** A figure that genuinely is not public gets declared: `NOT AVAILABLE: <fact> - <what was searched>`. For an unlisted company the run then continues **marked provisional**, the cover says so, and nothing in it may be presented as measured. It is a label for honest uncertainty, not a workaround.
- **No false precision.** Counts and shares come out as Monte Carlo intervals. Observed public-profile transition shares are never called promotion probabilities, because the true denominator is unknown.

---

## Repository layout

```
.claude-plugin/            plugin + marketplace manifests
install.sh                 installer, dependency check, zip builder
skills/company-talent-economics/
  SKILL.md                 the agent-facing instructions
  scripts/                 the harness (see below)
  locales/                 12 chrome locale packs
  assets/                  jurisdiction registry, search terms, priors, templates
  references/              method: glossary, reasoning chains, jurisdiction playbooks, localization
  schemas/                 JSON schemas for report / model / evidence
  examples/                a worked Xiaomi run and runnable fixtures
```

| Script | Does |
|---|---|
| `init_run.py` | Create a run; resolve language, jurisdiction, currency, threshold |
| `check_phase.py` | The ten gates, with the next steps printed on every pass and failure |
| `search_plan.py` | Six-pass query ladder, venue-scoped and bilingual |
| `build_model.py` | `levels.json` → `model.json`, payroll-envelope check with a TC/revenue fallback |
| `estimate_population.py` | Monte Carlo estimate of employees above the threshold |
| `pay_band_diagnostic.py` | Market / economic / internal band overlap |
| `career_graph.py` | Aggregate observed career transitions |
| `compile_report.py` | Fill `report.json`'s numeric sections in the run's language |
| `validate_bundle.py` | Bundle completeness, vocabulary, terminology, affordability |
| `render_report.py` | JSON → DOCX → PDF, localized chrome, per-script fonts, RTL |
| `i18n.py` | Language detection, locale packs, jurisdiction registry, formatting |
| `check_locales.py` | Validate packs and registry; scaffold a new language |
| `selftest.py` | Drive a synthetic run through all ten gates and every locale |

---

## Development

```bash
python skills/company-talent-economics/scripts/check_locales.py    # packs + registry
python skills/company-talent-economics/scripts/selftest.py         # gates 0-10, DOCX only
python skills/company-talent-economics/scripts/selftest.py --pdf   # also convert to PDF
```

`selftest.py` runs three scenarios end to end — a fully disclosed listed company, an unlisted company
that has to take the provisional path, and the literal-`[ ]`-in-prose case — then renders every locale.
CI runs exactly these on every push.

---

## License

MIT. See [LICENSE](LICENSE).
