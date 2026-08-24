# Language and country coverage

## The rule

**The report is written in the language of the company name the user typed.** Someone who asks about
`ソニーグループ` wants a Japanese report; someone who asks about `Siemens AG` wants a German one. If the
user writes their request in a different language from the company name, **the user's language wins** —
they are the reader.

`scripts/i18n.py` resolves this, in strict precedence order:

1. an explicit `--language <tag>`;
2. the `CTE_LANG` environment variable;
3. the script and legal form of the company name.

`init_run.py` records the result in `run.json -> language` and every later script reads it from there.
Check that field at Phase 0. Changing it later means recompiling and re-rendering.

## Two different things called "language"

| | what it is | coverage |
|---|---|---|
| **prose language** | the language you write the analysis in | any language |
| **chrome locale** | `locales/<tag>.json`: section titles, table headers, claim-type labels, number grouping, fonts, page footer | the 12 shipped packs |

A language with no pack still works: the prose is in that language and the structural labels fall back
(`zh-HK` → `zh-TW` → `en`). The renderer prints a note when it falls back. Shipped packs:

`en` `zh-CN` `zh-TW` `ja` `ko` `es` `fr` `de` `pt` `it` `ru` `ar`

To add one: `python scripts/check_locales.py --new nl` scaffolds `locales/nl.json` from English. Translate
the strings, leave the keys and every `{placeholder}` untouched, then run `python scripts/check_locales.py`.
Nothing else needs to change — no code, no template.

## Detection confidence, and when to ask

`i18n.py detect "<name>"` reports a confidence:

- **high** — a distinct script (Hangul, kana, Cyrillic, Arabic, Devanagari, Thai, Hebrew, Greek, Han).
- **medium** — an unambiguous legal form: `GmbH`, `AG`, `S.p.A.`, `B.V.`, `Oy`, `Sdn Bhd`, `Tbk`, `K.K.`, `Ltda`, `AB`, `A/S`, `Inc`, `PLC`.
- **low** — only diacritics, or plain Latin with nothing to go on.
- **ambiguous** — a legal form shared across languages. `S.A.` is French, Spanish, Portuguese, Polish, Swiss and Greek at once; `A.S.` is Norwegian, Czech and Turkish. The detector refuses to guess.

On **low** or **ambiguous**, do not silently default to English. Use the language the user wrote to you
in; if that is also unclear, ask once, in one line, and proceed.

Simplified and traditional Chinese are separated by character evidence in the name, not by assumption.
`台` is not a signal — Taiwan writes both `台灣` and `臺灣`.

## Country coverage

`assets/jurisdictions.json` holds 49 jurisdictions. Each entry carries the filing venues to scope
`site:` queries to, the local names of the documents worth fetching, the company registry, the
reporting currency, a default high-pay threshold, an employer social-contribution rate, and a note on
what is unusually available — or unusually misleading — in that country.

```bash
python scripts/i18n.py jurisdictions          # list every code
python scripts/i18n.py jurisdictions japan    # one entry in full; aliases resolve
```

`--jurisdiction` accepts codes and aliases (`us`, `usa`, `america`, `sec`, `nasdaq` all reach `us`).
When omitted, it is inferred from the company name's legal form. Unknown values fall back to `other`,
which routes you to find the national registry and securities regulator first.

Adding a country is also data-only: append an entry to `assets/jurisdictions.json` and
`check_locales.py` validates it.

### The two numbers that are priors, not facts

`threshold_default` and `employer_social_rate` are **starting points to be overridden**, and every
override belongs in `analysis_notes.md`.

- `threshold_default` is the round local number that reads as "high earner" in that market — CNY 1,000,000, JPY 20,000,000, USD 250,000, INR 10,000,000 (1 crore). It is not a statistical cut-off, and it is not comparable across countries at market FX. If the user gives a threshold, theirs wins.
- `employer_social_rate` varies enormously and breaks the payroll envelope when applied blindly: roughly 1% in Denmark (funded through income tax) against roughly 32% in Spain. Use the disclosed number whenever the filing gives one.
- In high-inflation economies (`ar`, `tr`, `eg`, `ng`, `ru`), state the threshold with an FX date or express it in USD. A local-currency number without a date is meaningless within a quarter.

## Search runs in two languages

`search_plan.py` emits every pass twice when the local language is not English. Filings are indexed
under their local names (`有価証券報告書`, `Vergütungsbericht`, `사업보고서`, `Formulário de Referência`),
while cross-border analyst coverage and databases are indexed in English. Searching only one side
loses half the evidence.

Search vocabulary lives in `assets/search_terms.json`, one block per language, same keys as `en`.
A language with no block falls back to English terms — the quoted company name still carries the query.

## What does not get localized

- **Canonical claim types.** `report.json` and `evidence.jsonl` store `observed_fact`, `derived_metric`, `assumption`, `inference`, `reconstruction` in English. `render_report.py` prints the local label. This keeps validation language-independent; `validate_bundle.py` accepts either form in `report.json`.
- **File and field names.** `run.json`, `levels.json`, `facts.gross_profit` and the rest stay English so the harness works identically everywhere.
- **The company's own words.** Native titles, level names, segment names and charter terms stay in the original language, with a translation in parentheses on first use. Do not translate `事業部長` into "VP" and then reason about the VP.

## Typography

Fonts are chosen per script from what `fc-list` reports installed, with a Latin fallback so a missing
font degrades to readable text rather than boxes. `render_report.py` warns on stderr when no font
covers the report's script — install `fonts-noto-cjk` (CJK) or `fonts-noto-core` (Arabic, Cyrillic,
Devanagari) rather than shipping a PDF full of tofu.

Arabic and Hebrew render right-to-left: paragraph direction, table column order and the footer all
mirror. Always rasterise a page and look at it before delivering an RTL report.
