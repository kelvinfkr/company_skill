#!/usr/bin/env python3
"""Verify every locale pack against en.json, and every jurisdiction entry against the registry schema.

Run this after adding a language or a country. It is what CI runs.

  python scripts/check_locales.py            # check everything
  python scripts/check_locales.py --new xx   # scaffold locales/xx.json from en.json, then check
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
LOCALES = SKILL / "locales"
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def walk(node, prefix=""):
    """Yield (dotted_path, value) for every leaf, and (path, list_len) for lists of strings."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("_"):
                continue
            yield from walk(v, f"{prefix}.{k}" if prefix else k)
    else:
        yield prefix, node


def check_pack(tag: str, pack: dict, ref: dict) -> list:
    problems = []
    ref_leaves = dict(walk(ref))
    leaves = dict(walk(pack))

    for path in ref_leaves:
        if path not in leaves:
            problems.append(f"{tag}: missing key {path}")
    for path in leaves:
        if path not in ref_leaves:
            problems.append(f"{tag}: unknown key {path} (not in en.json)")

    for path, ref_val in ref_leaves.items():
        val = leaves.get(path)
        if val is None:
            continue
        # Column counts and (title, note) pairs must match exactly - the renderer indexes them.
        # Font stacks, number scales and forbidden-term lists are legitimately per-language.
        fixed_arity = path.startswith("tables.") or path.startswith("sections.")
        if fixed_arity and isinstance(ref_val, list) and isinstance(val, list) and len(ref_val) != len(val):
            problems.append(f"{tag}: {path} has {len(val)} entries, en.json has {len(ref_val)}")
        if isinstance(ref_val, str) and isinstance(val, str):
            want, got = set(PLACEHOLDER.findall(ref_val)), set(PLACEHOLDER.findall(val))
            if want != got:
                problems.append(f"{tag}: {path} placeholders {sorted(got)} != en.json {sorted(want)}")
            if ref_val.strip() and val == "":
                problems.append(f"{tag}: {path} is empty")

    meta = pack.get("meta", {})
    if meta.get("tag") != tag:
        problems.append(f"{tag}: meta.tag is {meta.get('tag')!r}, must equal the filename")
    if meta.get("direction") not in ("ltr", "rtl"):
        problems.append(f"{tag}: meta.direction must be 'ltr' or 'rtl'")
    if not meta.get("font_sans"):
        problems.append(f"{tag}: meta.font_sans is empty")
    scale = pack.get("scale", [])
    if scale != sorted(scale, key=lambda s: -s[0]):
        problems.append(f"{tag}: scale must be ordered largest threshold first")
    for step in scale:
        if len(step) != 3 or not isinstance(step[2], str):
            problems.append(f"{tag}: bad scale step {step}; expected [threshold, divisor, suffix]")
    for section, value in pack.get("sections", {}).items():
        if not isinstance(value, list) or len(value) != 2:
            problems.append(f"{tag}: sections.{section} must be [title, note]")
    return problems


def check_jurisdictions() -> list:
    problems = []
    reg = json.loads((SKILL / "assets/jurisdictions.json").read_text(encoding="utf-8"))
    jur = reg["jurisdictions"]
    for code, e in jur.items():
        for k in ("name", "languages", "currency", "threshold_default", "employer_social_rate",
                  "filing_venues", "key_documents", "registry", "notes"):
            if k not in e:
                problems.append(f"jurisdiction {code}: missing field {k}")
        rate = e.get("employer_social_rate")
        if not isinstance(rate, (int, float)) or not 0 <= rate <= 1:
            problems.append(f"jurisdiction {code}: employer_social_rate {rate!r} outside 0..1")
        if e.get("currency") and len(e["currency"]) != 3:
            problems.append(f"jurisdiction {code}: currency {e['currency']!r} is not an ISO 4217 code")
        if code not in ("private", "other") and not e.get("filing_venues"):
            problems.append(f"jurisdiction {code}: no filing venues, so search_plan.py cannot scope a site: query")
    for alias, target in reg["aliases"].items():
        if target not in jur:
            problems.append(f"alias {alias!r} points at unknown jurisdiction {target!r}")

    terms = json.loads((SKILL / "assets/search_terms.json").read_text(encoding="utf-8"))["terms"]
    for lang, block in terms.items():
        missing = sorted(set(terms["en"]) - set(block))
        if missing:
            problems.append(f"search_terms {lang}: missing {missing}")
    return problems


def scaffold(tag: str):
    ref = json.loads((LOCALES / "en.json").read_text(encoding="utf-8"))
    ref["meta"]["tag"] = tag
    ref["meta"]["name"] = f"TODO name of {tag}"
    ref["meta"]["native_name"] = f"TODO endonym of {tag}"
    ref["_doc"] = (f"Locale pack for {tag}. Translate every string below; keep the keys and any "
                   f"{{placeholders}} exactly as they are. Structural chrome only.")
    path = LOCALES / f"{tag}.json"
    if path.exists():
        sys.exit(f"{path} already exists")
    path.write_text(json.dumps(ref, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"scaffolded {path} from en.json - translate the strings, keep the keys")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--new", metavar="TAG", help="scaffold a new locale pack from en.json")
    a = ap.parse_args()
    if a.new:
        scaffold(a.new)

    ref = json.loads((LOCALES / "en.json").read_text(encoding="utf-8"))
    problems = []
    tags = sorted(p.stem for p in LOCALES.glob("*.json"))
    for tag in tags:
        if tag == "en":
            continue
        problems += check_pack(tag, json.loads((LOCALES / f"{tag}.json").read_text(encoding="utf-8")), ref)
    problems += check_jurisdictions()

    if problems:
        print("\n".join("[!!] " + p for p in problems))
        sys.exit(1)
    reg = json.loads((SKILL / "assets/jurisdictions.json").read_text(encoding="utf-8"))
    terms = json.loads((SKILL / "assets/search_terms.json").read_text(encoding="utf-8"))["terms"]
    print(f"[ok] {len(tags)} locale packs consistent with en.json ({', '.join(tags)})")
    print(f"[ok] {len(reg['jurisdictions'])} jurisdictions, {len(reg['aliases'])} aliases, "
          f"{len(terms)} search-term languages")


if __name__ == "__main__":
    main()
