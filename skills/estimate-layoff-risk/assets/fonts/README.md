# CJK font

PDF rendering uses **Noto Sans CJK SC**. The 16 MB font binary is intentionally not committed with the Skill source.

Install the font system-wide, or place a legally obtained copy at:

```text
assets/fonts/NotoSansCJKsc-Regular.otf
```

`scripts/render_report.py` passes this directory to LibreOffice through `SAL_PRIVATE_FONTPATH` when it exists. Follow the font publisher's license terms.
