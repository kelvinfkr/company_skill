#!/usr/bin/env python3
"""Build public role-holder cases and compare documented experience with a candidate CV.

The host agent searches and reads public sources. This script prepares the search plan,
checks the collected records, ranks current cases and compiles a report section.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import json
import math
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


SOURCE_TYPES = {
    "company_page": (1.0, "B"), "appointment": (1.0, "B"),
    "personal_homepage": (0.9, "D"), "public_cv": (0.9, "D"),
    "orcid": (0.8, "D"), "publication": (0.7, "D"),
    "conference_bio": (0.7, "D"), "technical_blog": (0.7, "D"),
    "open_source": (0.7, "D"), "public_professional_profile": (0.6, "D"),
    "job_posting": (1.0, "A"),
}
KINDS = {"education", "employment", "project", "publication", "service", "honor"}
ROLE_SOURCES = {"company_page", "appointment", "personal_homepage", "public_cv",
                "conference_bio", "technical_blog", "public_professional_profile"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def date_bounds(value):
    """Keep year/month precision instead of inventing an event day."""
    parts = str(value).split("-")
    if len(parts) == 1 and len(parts[0]) == 4:
        year = int(parts[0])
        return date(year, 1, 1), date(year, 12, 31)
    if len(parts) == 2 and len(parts[0]) == 4 and len(parts[1]) == 2:
        year, month = map(int, parts)
        return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
    if len(parts) == 3 and len(str(value)) == 10:
        day = date.fromisoformat(value)
        return day, day
    raise ValueError(f"invalid date: {value!r}")


def validate_bundle(bundle, candidate=None):
    """Check references and evidence boundaries without additional dependencies."""
    errors = []
    if not isinstance(bundle, dict):
        return ["bundle must be an object"]

    def need(condition, message):
        if not condition:
            errors.append(message)

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def records(key):
        value = bundle.get(key)
        if not isinstance(value, list) or any(not isinstance(x, dict) for x in value):
            errors.append(f"{key} must be a list of objects")
            return []
        return value

    meta = bundle.get("meta", {})
    if not isinstance(meta, dict):
        return ["meta must be an object"]
    for field in ("company", "role", "geography", "language", "reference_date"):
        need(text(meta.get(field)), f"meta.{field} is required")
    try:
        reference = date.fromisoformat(meta.get("reference_date", ""))
    except (ValueError, TypeError):
        return errors + ["meta.reference_date must be YYYY-MM-DD"]

    def check_date(value, label, full=False):
        if value is None:
            return
        if not isinstance(value, str):
            errors.append(f'{label}: dates must be strings')
            return
        try:
            low, high = date_bounds(value)
            need(not full or low == high, f"{label} must be YYYY-MM-DD")
            need(low <= reference, f"{label} is after the reference date")
        except (ValueError, TypeError):
            errors.append(f"{label}: invalid date")

    policy = bundle.get("policy", {})
    if not isinstance(policy, dict):
        errors.append("policy must be an object")
        policy = {}
    for key, default in (("half_life_days", 730), ("undated_weight", 0.5)):
        value = policy.get(key, default)
        valid = type(value) in (int, float) and math.isfinite(value)
        need(valid and (value > 0 if key == "half_life_days" else 0 <= value <= 1),
             f"policy.{key} is out of range")

    sources = records("sources")
    by_id = {s.get("id"): s for s in sources if text(s.get("id"))}
    capabilities = records("capabilities")
    profiles = records("profiles")
    requirements = records("requirements")
    for name, items in (("sources", sources), ("capabilities", capabilities), ("profiles", profiles)):
        ids = [x.get("id") for x in items]
        need(all(text(x) for x in ids), f"{name}: every record needs an id")
        need(len(set(x for x in ids if isinstance(x, str))) == len(ids), f"{name}: duplicate ids")
    source_ids = {x["id"] for x in sources if text(x.get("id"))}
    capability_ids = {x["id"] for x in capabilities if text(x.get("id"))}

    def original_source(sid):
        origin_id = by_id.get(sid, {}).get('origin_id')
        return by_id.get(origin_id, {}) if text(origin_id) else {}

    def refs(item, label):
        ids = item.get("evidence_ids")
        need(isinstance(ids, list) and bool(ids) and all(isinstance(x, str) for x in ids),
             f"{label}: evidence_ids must be a nonempty list of source ids")
        if isinstance(ids, list):
            need(all(isinstance(x, str) and x in source_ids for x in ids), f"{label}: unknown source")

    for source in sources:
        label = f"source {source.get('id')}"
        need(text(source.get("title")), f"{label}: title is required")
        need(isinstance(source.get("source_type"), str) and source["source_type"] in SOURCE_TYPES,
             f"{label}: unsupported source_type")
        need(text(source.get("origin_id")), f"{label}: origin_id is required")
        origin = by_id.get(source.get('origin_id')) if text(source.get('origin_id')) else None
        need(origin is not None and origin.get('origin_id') == origin.get('id'),
             f'{label}: origin_id must reference an original source in this bundle')
        try:
            url = urlparse(source.get("url", ""))
            need(url.scheme in ("http", "https") and bool(url.hostname), f"{label}: invalid URL")
            host = (url.hostname or "").lower()
            need(not any(host == d or host.endswith("." + d) for d in
                         ("zhipin.com", "bosszhipin.com")), f"{label}: BOSS sources are excluded")
        except (ValueError, TypeError):
            errors.append(f"{label}: invalid URL")
        need(source.get("accessed_date") is not None, f"{label}: accessed_date is required")
        for key in ("accessed_date", "published_date", "updated_date"):
            check_date(source.get(key), f"{label}.{key}", full=True)
        published, updated, accessed = (source.get(k) for k in
                                        ("published_date", "updated_date", "accessed_date"))
        if isinstance(published, str) and isinstance(updated, str):
            need(updated >= published, f"{label}: updated_date precedes published_date")
        for value in (published, updated):
            if isinstance(value, str) and isinstance(accessed, str):
                need(value <= accessed, f"{label}: content date follows accessed_date")

    for capability in capabilities:
        need(text(capability.get("label")), "capabilities: label is required")
    searches = bundle.get('searches', [])
    if not isinstance(searches, list) or any(not isinstance(x, dict) for x in searches):
        errors.append('searches must be a list of objects')
    else:
        for search in searches:
            need(text(search.get('query')) and text(search.get('note')), 'search: query and note are required')
            need(search.get('outcome') in ('found', 'not_found', 'excluded'), 'search: bad outcome')
            need(search.get('searched_date') is not None, 'search: searched_date is required')
            check_date(search.get('searched_date'), 'search.searched_date', full=True)
    for requirement in requirements:
        need(isinstance(requirement.get("capability_id"), str) and
             requirement['capability_id'] in capability_ids, "requirement: unknown capability")
        need(requirement.get("importance") in ("required", "preferred"), "requirement: bad importance")
        refs(requirement, "requirement")
        evidence_ids = requirement.get("evidence_ids")
        need(isinstance(evidence_ids, list) and any(by_id.get(x, {}).get("source_type") == "job_posting"
                 for x in evidence_ids if isinstance(x, str)),
             "requirement: a job posting must support the advertised requirement")

    for profile in profiles:
        label = f"profile {profile.get('id')}"
        need(text(profile.get("name")), f"{label}: name is required")
        if 'person_key' in profile:
            need(text(profile['person_key']), f"{label}: person_key must be a nonempty string")
        need(profile.get("identity_status") in ("resolved", "ambiguous"), f"{label}: bad identity_status")
        identity = {"evidence_ids": profile.get("identity_evidence_ids")}
        refs(identity, f"{label}.identity")
        role = profile.get("role")
        if not isinstance(role, dict):
            errors.append(f"{label}: role must be an object")
            continue
        for key in ("company", "title", "geography", "match_reason"):
            need(text(role.get(key)), f"{label}.role.{key} is required")
        need(role.get("status") in ("current", "former", "unconfirmed"), f"{label}: bad role status")
        need(role.get("match") in ("exact", "related", "excluded"), f"{label}: bad role match")
        if role.get("match") != "excluded":
            need(role.get("company") == meta.get("company"), f"{label}: employer differs from target")
            need(role.get("geography") == meta.get("geography"), f"{label}: geography differs from target")
        refs(role, f"{label}.role")
        role_ids = role.get('evidence_ids')
        if role.get('status') == 'current':
            need(isinstance(role_ids, list) and any(
                 isinstance(original_source(x).get('source_type'), str)
                 and original_source(x)['source_type'] in ROLE_SOURCES
                 for x in role_ids if isinstance(x, str)), f'{label}: current role needs a direct role statement')
        check_date(role.get("as_of"), f"{label}.role.as_of", full=True)
        check_date(profile.get("joined_date"), f"{label}.joined_date")
        experiences = profile.get("experiences")
        if not isinstance(experiences, list) or any(not isinstance(e, dict) for e in experiences):
            errors.append(f"{label}: experiences must be a list of objects")
            continue
        for exp in experiences:
            need(isinstance(exp.get('kind'), str) and exp['kind'] in KINDS,
                 f"{label}: bad experience kind")
            need(text(exp.get("summary")), f"{label}: experience summary is required")
            ids = exp.get("capability_ids", [])
            need(isinstance(ids, list) and all(isinstance(x, str) and x in capability_ids for x in ids),
                 f"{label}: unknown experience capability")
            refs(exp, f"{label}.experience")
            for key in ("start_date", "end_date"):
                check_date(exp.get(key), f"{label}.{key}")
            if exp.get("start_date") and exp.get("end_date"):
                try:
                    need(date_bounds(exp["start_date"])[0] <= date_bounds(exp["end_date"])[1],
                         f"{label}: experience ends before it starts")
                except (ValueError, TypeError):
                    pass

    if candidate is not None:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("experiences"), list):
            errors.append("candidate.experiences must be a list")
        else:
            for exp in candidate["experiences"]:
                if not isinstance(exp, dict):
                    errors.append("candidate experiences must be objects")
                    continue
                need(text(exp.get("summary")) and text(exp.get("resume_reference")),
                     "candidate experience needs summary and resume_reference")
                ids = exp.get("capability_ids")
                need(isinstance(ids, list) and bool(ids) and
                     all(isinstance(x, str) and x in capability_ids for x in ids),
                     "candidate: unknown capability")
            next_steps = candidate.get('next_steps', [])
            if not isinstance(next_steps, list) or any(not isinstance(x, dict) for x in next_steps):
                errors.append('candidate.next_steps must be a list of objects')
            else:
                for step in next_steps:
                    need(text(step.get('action')), 'candidate next step needs an action')
                    need(isinstance(step.get('capability_id'), str) and
                         step['capability_id'] in capability_ids, 'candidate next step: unknown capability')
                    refs(step, 'candidate next step')
    return errors


def source_date(source):
    return source.get("updated_date") or source.get("published_date")


def experience_phase(experience, joined_date):
    if not joined_date:
        return "unknown"
    join_low, join_high = date_bounds(joined_date)
    end = experience.get("end_date")
    start = experience.get("start_date")
    if end and date_bounds(end)[1] < join_low:
        return "pre_entry"
    if start and date_bounds(start)[0] >= join_high:
        return "post_entry"
    return "unknown"


def rank_profile(profile, sources, meta, policy):
    """A documented ordering heuristic, never a hiring or salary probability."""
    reference = date.fromisoformat(meta["reference_date"])
    role = profile["role"]
    evidence = [sources[sources[x]['origin_id']] for x in role["evidence_ids"]
                if sources[sources[x]['origin_id']]['source_type'] in ROLE_SOURCES]
    # Multiple mirrors of one statement contribute once. Additional sources do not
    # increase the score: use the strongest dated evidence for the role claim.
    scored = {}
    for source in evidence:
        content_date = role.get("as_of") or source_date(source)
        age = (reference - date.fromisoformat(content_date)).days if content_date else None
        freshness = (2 ** (-age / policy.get("half_life_days", 730)) if age is not None
                     else policy.get("undated_weight", 0.5))
        quality = SOURCE_TYPES[source["source_type"]][0]
        score = quality * freshness * (1.0 if role["match"] == "exact" else 0.75)
        record = {"score": score, "evidence_id": source["id"], "as_of": content_date,
                  "age_days": age, "source_weight": quality, "freshness_weight": freshness}
        key = source["origin_id"]
        if score > scored.get(key, {}).get("score", -1):
            scored[key] = record
    return max(scored.values(), key=lambda x: (x["score"], x["evidence_id"]))


def compile_profiles(bundle, candidate=None):
    errors = validate_bundle(bundle, candidate)
    if errors:
        raise ValueError("\n".join(errors))
    sources = {s["id"]: s for s in bundle["sources"]}
    current, other = [], []
    seen = set()
    for profile in bundle["profiles"]:
        # Stable person_key groups records already resolved by the researching agent.
        key = profile.get("person_key") or profile["id"]
        if key in seen:
            raise ValueError(f"duplicate person_key: {key}; merge sources before compiling")
        seen.add(key)
        record = dict(profile)
        record["experiences"] = [dict(e, phase=experience_phase(e, profile.get("joined_date")))
                                 for e in profile["experiences"]]
        included = (profile["identity_status"] == "resolved" and profile["role"]["status"] == "current"
                    and profile["role"]["match"] in ("exact", "related"))
        if included:
            record["ranking"] = rank_profile(profile, sources, bundle["meta"], bundle.get("policy", {}))
            current.append(record)
        else:
            other.append(record)
    current.sort(key=lambda p: (-p["ranking"]["score"], p["id"]))
    candidate_experiences = (candidate or {}).get("experiences", [])
    comparisons = []
    for capability in bundle["capabilities"]:
        cid = capability["id"]
        matches = [{"profile_id": p["id"], "summary": e["summary"], "evidence_ids": e["evidence_ids"]}
                   for p in current for e in p["experiences"]
                   if cid in e.get("capability_ids", []) and e["phase"] == "pre_entry"]
        personal = [e for e in candidate_experiences if cid in e["capability_ids"]]
        requirements = [r for r in bundle["requirements"] if r["capability_id"] == cid]
        comparisons.append({"capability_id": cid, "label": capability["label"],
                            "case_count": len({m["profile_id"] for m in matches}),
                            "pre_entry_examples": matches, "requirements": requirements,
                            "candidate_status": ("documented" if personal else "not_documented")
                            if candidate is not None else "not_supplied",
                            "candidate_examples": personal})
    section = {"bundle": bundle, "candidate": candidate, "current_cases": current,
               "other_cases": other, "comparison": comparisons,
               "sample_count": len(current), "policy": {"half_life_days": 730, "undated_weight": 0.5,
                                                          **bundle.get("policy", {})}}
    return {"meta": dict(bundle["meta"]), "role_profiles": section}


def validate_section(section, meta=None):
    try:
        if not isinstance(section, dict):
            return ['role_profiles must be an object']
        if meta is not None:
            for key in ('company', 'language', 'reference_date'):
                if meta.get(key) != section['bundle']['meta'].get(key):
                    return [f'role_profiles: report meta.{key} differs from profile scope']
        expected = compile_profiles(section["bundle"], section.get("candidate"))["role_profiles"]
        return [] if expected == section else ["role_profiles: derived section differs from its evidence bundle"]
    except (ValueError, KeyError, TypeError) as exc:
        return [f"role_profiles: {exc}"]


def search_plan(meta):
    company, role = meta["company"], meta["role"]
    base = f'"{company}" "{role}" "{meta["geography"]}"'
    passes = [
        ("people", [f"{base} team people", f"{base} 团队 任职", f"{base} appointed joined"]),
        ("cv", [f"{base} CV biography", f"{base} 简历 个人主页", f"{base} site:github.io"]),
        ("work", [f"{base} publications technical report", f"{base} 项目 开源 技术博客"]),
        ("recent", [f"{base} {meta['reference_date'][:4]}", f"{base} joined moved left 离职"]),
        ("requirements", [f"{base} careers salary requirements", f"{base} 招聘 职责 薪资"]),
    ]
    return {"meta": meta, "passes": [{"name": name, "queries": queries} for name, queries in passes],
            "instructions": "Fetch primary pages. Log current-role evidence, content dates, conflicts and missing fields."}


def write_audit(out, bundle):
    sources = {s["id"]: s for s in bundle["sources"]}
    claims = []
    for p in bundle["profiles"]:
        claims.append((f"Identity record: {p['name']} ({p['identity_status']})", p['identity_evidence_ids']))
        claims.append((f"{p['name']}: {p['role']['title']} ({p['role']['status']})", p["role"]["evidence_ids"]))
        claims.extend((f"{p['name']}: {e['summary']}", e["evidence_ids"]) for e in p["experiences"])
    for r in bundle["requirements"]:
        claims.append((f"{r['capability_id']}: {r['importance']}", r["evidence_ids"]))
    ledger = []
    for index, (claim, ids) in enumerate(claims, 1):
        for sid in dict.fromkeys(ids):
            s = sources[sid]
            ledger.append({"id": f"RP{index}-{sid}", "claim": claim, "source": s["url"],
                           "published_date": source_date(s), "observed_date": s["accessed_date"],
                           "claim_type": "observed_fact", "source_tier": SOURCE_TYPES[s["source_type"]][1],
                           "confidence": "medium", "company": bundle["meta"]["company"]})
    (out / "evidence.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in ledger),
                                        encoding="utf-8")
    with (out / "source_manifest.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["pass", "source", "url", "date", "source_type", "tier", "status"])
        writer.writeheader()
        for s in sources.values():
            writer.writerow({"pass": "role_profiles", "source": s["title"], "url": s["url"],
                             "date": source_date(s) or s["accessed_date"], "source_type": s["source_type"],
                             "tier": SOURCE_TYPES[s["source_type"]][1], "status": "used"})
        for search in bundle.get('searches', []):
            if search['outcome'] != 'found':
                writer.writerow({'pass': 'role_profiles', 'source': search['query'] + ': ' + search['note'],
                                 'url': '', 'date': search['searched_date'], 'source_type': 'search', 'tier': '',
                                 'status': 'searched, not found' if search['outcome'] == 'not_found' else 'excluded'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Prepare the evidence template and search queries")
    for key in ("company", "role", "geography"):
        init.add_argument("--" + key, required=True)
    init.add_argument("--language", default="en")
    init.add_argument("--date", default=date.today().isoformat())
    init.add_argument("--out", type=Path, required=True)
    for command in ("check", "build"):
        sub = commands.add_parser(command)
        sub.add_argument("input", type=Path)
        sub.add_argument("--candidate", type=Path)
        if command == "build":
            sub.add_argument("--out", type=Path, required=True)
            sub.add_argument("--report", type=Path, help="Attach to an existing company report")
    args = parser.parse_args()
    try:
        if args.command == "init":
            meta = {"company": args.company, "role": args.role, "geography": args.geography,
                    "language": args.language, "reference_date": date.fromisoformat(args.date).isoformat()}
            args.out.mkdir(parents=True, exist_ok=True)
            for name in ("profiles.json", "search_plan.json"):
                if (args.out / name).exists():
                    raise ValueError(f"{args.out / name} already exists")
            write_json(args.out / "profiles.json", {"meta": meta, "sources": [], "capabilities": [],
                                                   "requirements": [], "profiles": [], "searches": []})
            write_json(args.out / "search_plan.json", search_plan(meta))
            print(f"Prepared {args.out}; search and fill profiles.json before building.")
        else:
            bundle = read_json(args.input)
            candidate = read_json(args.candidate) if args.candidate else None
            report = compile_profiles(bundle, candidate)
            if args.command == "build":
                destination = read_json(args.report) if args.report else None
                if destination is not None:
                    for field in ("company", "language", "reference_date"):
                        if destination.get("meta", {}).get(field) != bundle["meta"][field]:
                            raise ValueError(f"report meta.{field} differs from the profile target")
                    destination["role_profiles"] = report["role_profiles"]
                args.out.mkdir(parents=True, exist_ok=True)
                write_json(args.out / "report.json", report)
                write_audit(args.out, bundle)
                if destination is not None:
                    write_json(args.report, destination)
            print(f"Checked {len(bundle['profiles'])} cases; {report['role_profiles']['sample_count']} current matches.")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
