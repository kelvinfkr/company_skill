# company-talent-economics

Agent skill that reconstructs a company's compensation distribution, high-pay population, critical
roles, pay bands and career graph from public data, and typesets a PDF report (JSON → DOCX → PDF).

Works for companies in any country and writes the report in the language of the company name you type.
Runs in **Claude Code**, **Codex** and **claude.ai** from this same folder.

**Full documentation — installation, usage, language and country coverage — is in the repository root:
[README.md](../../README.md) (English) and [README.zh-CN.md](../../README.zh-CN.md) (中文).**

- `SKILL.md` is the agent-facing instruction set.
- `references/localization.md` explains language and jurisdiction resolution, and how to add either.
- `examples/xiaomi/` is a complete worked run (Xiaomi FY2025) showing the expected depth.

Quick smoke test from this folder:

```bash
pip install -r requirements.txt
python scripts/check_locales.py                                    # locale packs + jurisdiction registry
python scripts/selftest.py                                         # all ten gates, every locale
python scripts/render_report.py examples/demo_report.json -o /tmp/demo.pdf
```

Harness, by hand:

```bash
python scripts/init_run.py "小米集团" --out ./talent-economics/xiaomi --year 2025
python scripts/check_phase.py ./talent-economics/xiaomi --next   # follow the printed steps
python scripts/check_phase.py ./talent-economics/xiaomi          # gate check, repeat through phase 10
```
