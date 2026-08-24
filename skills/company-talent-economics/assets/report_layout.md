# PDF report layout contract

The final human-facing deliverable is a typeset PDF compiled from structured `report.json` data. Markdown is documentation only and must never be used as the final report rendering source.

## Layout principles

- A4 portrait, Chinese-first typography, restrained business-research styling.
- Cover page with company, reference date, scope, threshold, confidence and a short methodology note.
- Running header and page number from page 2 onward.
- Major sections start with a numbered heading and a one-line interpretive subtitle when available.
- Tables have explicit column widths, repeating header rows, compact cell padding and automatic page breaks.
- Observed, derived and inferred values should be visually distinguishable in the evidence/status columns.
- Avoid dense raw-source dumps in the main PDF. Keep the evidence ledger compact; put full source manifests in the audit bundle.
- Do not include Markdown syntax in visible PDF text.

## Required final artifacts

- `report.pdf` - primary deliverable.
- `report.json` - structured report model.
- `evidence.jsonl` - evidence ledger.
- `source_manifest.csv` - source acquisition log.
- Optional `report.docx` only when `--keep-docx` is requested.
