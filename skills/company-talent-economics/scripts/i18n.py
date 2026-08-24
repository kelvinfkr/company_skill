#!/usr/bin/env python3
"""Language resolution, locale packs, jurisdiction registry and locale-aware formatting.

Two separate things are called "language" in this skill and they must not be confused:

  prose language  - the language the agent writes the analysis in. Any language works.
  chrome locale   - the shipped locales/*.json pack used for section titles, table headers,
                    claim-type labels and number formatting. Only shipped tags have one.

resolve() returns both. If a language has no pack, the chrome falls back down a chain
(zh-HK -> zh-TW -> en) while the prose language stays exactly what the user asked for.

Standard library only.

CLI:
  python i18n.py detect "小米集团"          # what language/jurisdiction does this name imply?
  python i18n.py locales                    # list shipped chrome locales
  python i18n.py jurisdictions [code]       # show the jurisdiction registry
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
LOCALES = SKILL / "locales"
DEFAULT_LOCALE = "en"

# --------------------------------------------------------------------------- tags

# Requested tag -> shipped chrome pack. Anything not listed falls back on the
# primary subtag, then on English.
CHROME_ALIASES = {
    "zh": "zh-CN", "zh-hans": "zh-CN", "zh-cn": "zh-CN", "zh-sg": "zh-CN", "cmn": "zh-CN",
    "zh-hant": "zh-TW", "zh-tw": "zh-TW", "zh-hk": "zh-TW", "zh-mo": "zh-TW", "yue": "zh-TW",
    "pt-br": "pt", "pt-pt": "pt", "es-419": "es", "es-mx": "es", "es-ar": "es",
    "en-us": "en", "en-gb": "en", "fr-ca": "fr", "de-at": "de", "de-ch": "de",
}


def normalize_tag(tag: str) -> str:
    """Normalise a BCP-47-ish tag: 'ZH_hans' -> 'zh-Hans'."""
    if not tag:
        return ""
    parts = re.split(r"[-_]", tag.strip())
    out = [parts[0].lower()]
    for p in parts[1:]:
        out.append(p.upper() if len(p) == 2 else p.title())
    return "-".join(out)


@lru_cache(maxsize=1)
def available_locales() -> tuple:
    return tuple(sorted(p.stem for p in LOCALES.glob("*.json")))


def chrome_tag_for(language: str) -> str:
    """Pick the shipped chrome pack that best serves this prose language."""
    tag = normalize_tag(language)
    if not tag:
        return DEFAULT_LOCALE
    shipped = available_locales()
    if tag in shipped:
        return tag
    low = tag.lower()
    if low in CHROME_ALIASES and CHROME_ALIASES[low] in shipped:
        return CHROME_ALIASES[low]
    primary = low.split("-")[0]
    if primary in shipped:
        return primary
    if primary in CHROME_ALIASES and CHROME_ALIASES[primary] in shipped:
        return CHROME_ALIASES[primary]
    return DEFAULT_LOCALE


@lru_cache(maxsize=32)
def _load_pack(tag: str) -> dict:
    p = LOCALES / f"{tag}.json"
    if not p.exists():
        raise FileNotFoundError(f"locale pack not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def load_locale(language: str | None = None) -> dict:
    """Return a chrome pack, annotated with the prose language that was requested."""
    requested = normalize_tag(language or "") or DEFAULT_LOCALE
    chrome = chrome_tag_for(requested)
    pack = json.loads(json.dumps(_load_pack(chrome)))  # cheap deep copy
    pack["_requested"] = requested
    pack["_chrome"] = chrome
    pack["_chrome_is_fallback"] = chrome_tag_for(requested) != requested
    return pack


def resolve(language: str | None = None, company: str | None = None, env: bool = True) -> dict:
    """Decide the prose language. Precedence: explicit > CTE_LANG env > company-name script.

    Returns {"language", "chrome", "chrome_is_fallback", "confidence", "signal",
             "jurisdiction_hint"}.
    """
    if language:
        tag = normalize_tag(language)
        return {"language": tag, "chrome": chrome_tag_for(tag),
                "chrome_is_fallback": chrome_tag_for(tag) != tag,
                "confidence": "explicit", "signal": "set by --language",
                "jurisdiction_hint": detect_language(company or "")["jurisdiction_hint"]}
    if env and os.environ.get("CTE_LANG"):
        tag = normalize_tag(os.environ["CTE_LANG"])
        return {"language": tag, "chrome": chrome_tag_for(tag),
                "chrome_is_fallback": chrome_tag_for(tag) != tag,
                "confidence": "explicit", "signal": "set by CTE_LANG",
                "jurisdiction_hint": detect_language(company or "")["jurisdiction_hint"]}
    d = detect_language(company or "")
    d["chrome"] = chrome_tag_for(d["language"])
    d["chrome_is_fallback"] = d["chrome"] != d["language"]
    return d


# --------------------------------------------------------------------- detection

# Characters that exist only in traditional / only in simplified Chinese.
# 台 is deliberately absent: Taiwan writes 台灣 as often as 臺灣, so it separates nothing.
_TRAD = set("團華電國際業開發銀證券產機構資訊網絡體實驗設計製藥輛廠務員總經營銷區處長級職稱聯統劃項當貨幣灣臺龍鳳傳媒報導學習醫療農環東亞歐萬億廣濟儀錢車馬鳥魚積陽壽豐興辦飛鐵鋼鑫衛紡織結算會買賣準認讓進運邊過這對說話語質貿財賬費價樓廈據點連續銷務營銀網絡係則規範標準檢驗證險義齊義")
_SIMP = set("团华电国际业开发银证券产机构资讯网络体实验设计制药辆厂务员总经营销区处长级职称联统划项当货币湾龙凤传媒报导学习医疗农环东亚欧万亿广济仪钱车马鸟鱼积阳寿丰兴办飞铁钢鑫卫纺织结算会买卖准认让进运边过这对说话语质贸财账费价楼厦据点连续则规范标检险义齐")

# Unambiguous Latin-script legal-form markers -> (prose language, jurisdiction hint).
_LEGAL_FORMS = [
    (r"\bkabushiki\s+kaisha\b", "ja", "jp"), (r"\bk\.?\s?k\.?$", "ja", "jp"),
    (r"\bgmbh\s*&?\s*co\.?\s*kg\b", "de", "de"), (r"\bgmbh\b", "de", "de"),
    (r"\bkgaa\b", "de", "de"), (r"\bmbh\b", "de", "de"), (r"\bohg\b", "de", "de"),
    (r"\bag$", "de", "de"), (r"\bse\s*&\s*co\b", "de", "de"), (r"\baktiengesellschaft\b", "de", "de"),
    (r"\bs\.?a\.?s\.?u?$", "fr", "fr"), (r"\bsarl\b", "fr", "fr"),
    (r"\bs\.?a\.?r\.?l\.?\b", "fr", "fr"), (r"\beurl\b", "fr", "fr"),
    (r"\bs\.?p\.?a\.?$", "it", "it"), (r"\bs\.?r\.?l\.?$", "it", "it"),
    (r"\bs\.?a\.?\s*de\s*c\.?v\.?\b", "es", "mx"), (r"\bs\.?\s*de\s*r\.?l\.?\b", "es", "mx"),
    (r"\bs\.?l\.?u?\.?$", "es", "es"), (r"\bsociedad\s+an[oó]nima\b", "es", "es"),
    (r"\bltda\.?$", "pt", "br"), (r"\bsociedade\s+an[oó]nima\b", "pt", "br"),
    (r"\bb\.?v\.?$", "nl", "nl"), (r"\bn\.?v\.?$", "nl", "nl"),
    (r"\baktiebolag\b", "sv", "se"), (r"\bab\s*\(publ\)$", "sv", "se"), (r"\bab$", "sv", "se"),
    (r"\ba/s$", "da", "dk"), (r"\baps$", "da", "dk"),
    (r"\boyj?$", "fi", "fi"), (r"\basa$", "no", "no"),
    (r"\bsp\.?\s*z\s*o\.?o\.?\b", "pl", "pl"), (r"\bsp[oó][lł]ka\b", "pl", "pl"),
    (r"\banonim\s+[sş]irketi\b", "tr", "tr"), (r"\ba\.?[şs]\.?$", "tr", "tr"),
    (r"\bltd\.?\s*[sş]ti\.?$", "tr", "tr"),
    (r"\bsdn\.?\s*bhd\.?\b", "ms", "my"), (r"\bberhad\b", "ms", "my"), (r"\bbhd\.?$", "ms", "my"),
    (r"\btbk\.?$", "id", "id"), (r"^pt\.?\s", "id", "id"), (r"\bpersero\b", "id", "id"),
    (r"\bd\.?o\.?o\.?$", "hr", "other"),
    (r"\bkft\.?$", "hu", "other"), (r"\bzrt\.?$", "hu", "other"), (r"\bnyrt\.?$", "hu", "other"),
    (r"\bs\.?r\.?o\.?$", "cs", "other"),
    (r"\bpte\.?\s*ltd\.?\b", "en", "sg"), (r"\bpty\.?\s*ltd\.?\b", "en", "au"),
    (r"\bplc\.?$", "en", "gb"), (r"\bllp$", "en", "gb"),
    (r"\bl\.?l\.?c\.?$", "en", "us"), (r"\binc\.?$", "en", "us"), (r"\bcorp(oration)?\.?$", "en", "us"),
    (r"\bco\.?,?\s*ltd\.?$", "en", "other"), (r"\blimited$", "en", "other"), (r"\bltd\.?$", "en", "other"),
]

# Legal forms shared by too many languages to be a language signal at all.
# "S.A." alone is French, Spanish, Portuguese, Polish, Swiss and Greek; "A.S." is
# Norwegian, Czech and Turkish. These only justify asking, never guessing.
_AMBIGUOUS_FORMS = r"\b(s\.?\s?a\.?|s/a|a\.?\s?s\.?)$"

_SCRIPT_RANGES = [
    ("hangul", ("가", "힣"), "ko", "kr"),
    ("hangul_jamo", ("ᄀ", "ᇿ"), "ko", "kr"),
    ("hiragana", ("぀", "ゟ"), "ja", "jp"),
    ("katakana", ("゠", "ヿ"), "ja", "jp"),
    ("thai", ("฀", "๿"), "th", "th"),
    ("hebrew", ("֐", "׿"), "he", "il"),
    ("arabic", ("؀", "ۿ"), "ar", None),
    ("devanagari", ("ऀ", "ॿ"), "hi", "in"),
    ("bengali", ("ঀ", "৿"), "bn", "bd"),
    ("tamil", ("஀", "௿"), "ta", "in"),
    ("greek", ("Ͱ", "Ͽ"), "el", "gr"),
    ("cyrillic", ("Ѐ", "ӿ"), "ru", "ru"),
    ("han", ("一", "鿿"), "zh", None),
    ("han_ext", ("㐀", "䶿"), "zh", None),
]


def _counts(text: str) -> dict:
    c = {}
    for ch in text:
        for name, (lo, hi), _lang, _j in _SCRIPT_RANGES:
            if lo <= ch <= hi:
                c[name] = c.get(name, 0) + 1
                break
    return c


def _jurisdiction_from_name(text: str) -> str | None:
    """A country word inside the name pins the jurisdiction: 'أرامكو السعودية' is Saudi, '香港交易所'
    is Hong Kong. Only non-ASCII aliases are matched as substrings - an ASCII alias like 'sec' would
    fire inside 'Secure Corp'."""
    low = text.lower()
    best = None
    for alias, code in jurisdictions()["aliases"].items():
        if alias.isascii() or len(alias) < 2:
            continue
        if alias.lower() in low and (best is None or len(alias) > len(best[0])):
            best = (alias, code)
    return best[1] if best else None


def detect_language(name: str) -> dict:
    """Infer the prose language from a company name.

    The company name is the primary signal on purpose: a user who types a company name in
    Japanese wants a Japanese report. Returns a confidence so the caller can decide whether to ask.

    A country word spelled out in the name overrides the script-level jurisdiction guess, which is
    what makes 'أرامكو السعودية' resolve to Saudi Arabia rather than to "some Arabic-speaking country".
    """
    result = _detect_core(name)
    if not (name and name.strip()):
        return result
    named = _jurisdiction_from_name(unicodedata.normalize("NFKC", name.strip()))
    if not named:
        return result
    result["jurisdiction_hint"] = named
    # A Han name whose characters do not separate the script variants, but whose text names a
    # place, takes the variant from the place: 香港交易及結算所 is written in traditional Chinese.
    variant = {"hk": "zh-TW", "tw": "zh-TW", "cn": "zh-CN", "sg": "zh-CN"}.get(named)
    if variant and result["language"].startswith("zh") and result["confidence"] != "high":
        result["language"] = variant
        result["confidence"] = "high"
        result["signal"] = f"company name names a place mapping to {named}, which fixes the script variant"
    return result


def _detect_core(name: str) -> dict:
    if not name or not name.strip():
        return {"language": DEFAULT_LOCALE, "confidence": "none",
                "signal": "no company name given", "jurisdiction_hint": None}
    text = unicodedata.normalize("NFKC", name.strip())
    c = _counts(text)

    if c.get("hangul") or c.get("hangul_jamo"):
        return {"language": "ko", "confidence": "high", "signal": "Hangul in the company name",
                "jurisdiction_hint": "kr"}
    if c.get("hiragana") or c.get("katakana"):
        return {"language": "ja", "confidence": "high", "signal": "kana in the company name",
                "jurisdiction_hint": "jp"}
    if c.get("han") or c.get("han_ext"):
        if re.search(r"株式会社|合同会社|有限会社|合資会社", text):
            return {"language": "ja", "confidence": "high",
                    "signal": "Japanese legal form in the company name", "jurisdiction_hint": "jp"}
        trad = sum(1 for ch in text if ch in _TRAD)
        simp = sum(1 for ch in text if ch in _SIMP)
        if trad > simp:
            j = "tw" if re.search(r"臺灣|台灣", text) else ("hk" if "香港" in text else "tw")
            return {"language": "zh-TW", "confidence": "high",
                    "signal": "traditional Chinese characters in the company name", "jurisdiction_hint": j}
        if simp > trad:
            return {"language": "zh-CN", "confidence": "high",
                    "signal": "simplified Chinese characters in the company name", "jurisdiction_hint": "cn"}
        return {"language": "zh-CN", "confidence": "medium",
                "signal": "Han characters, script variant not distinguishable from the name alone",
                "jurisdiction_hint": None}
    if c.get("cyrillic"):
        if re.search(r"[іїєґІЇЄҐ]", text):
            return {"language": "uk", "confidence": "high", "signal": "Ukrainian letters in the company name",
                    "jurisdiction_hint": "other"}
        return {"language": "ru", "confidence": "medium", "signal": "Cyrillic script in the company name",
                "jurisdiction_hint": "ru"}
    if c.get("hebrew"):
        return {"language": "he", "confidence": "high", "signal": "Hebrew script in the company name",
                "jurisdiction_hint": "il"}
    if c.get("arabic"):
        return {"language": "ar", "confidence": "high", "signal": "Arabic script in the company name",
                "jurisdiction_hint": None}
    for key, lang, j in (("thai", "th", "th"), ("devanagari", "hi", "in"), ("bengali", "bn", "bd"),
                         ("tamil", "ta", "in"), ("greek", "el", "gr")):
        if c.get(key):
            return {"language": lang, "confidence": "high", "signal": f"{key} script in the company name",
                    "jurisdiction_hint": j}

    flat = re.sub(r"[,]", " ", text.lower())

    flat = re.sub(r"\s+", " ", flat).strip()
    for pattern, lang, j in _LEGAL_FORMS:
        if re.search(pattern, flat):
            return {"language": lang, "confidence": "medium",
                    "signal": f"legal-form marker matching /{pattern}/ in the company name",
                    "jurisdiction_hint": j}
    ambiguous = re.search(_AMBIGUOUS_FORMS, flat)
    if re.search(r"[àâçéèêëîïôùûüœ]", flat):
        return {"language": "fr", "confidence": "low", "signal": "French diacritics in the company name",
                "jurisdiction_hint": "fr"}
    if re.search(r"[äöüß]", flat):
        return {"language": "de", "confidence": "low", "signal": "German diacritics in the company name",
                "jurisdiction_hint": "de"}
    if re.search(r"[ñ¿¡]", flat):
        return {"language": "es", "confidence": "low", "signal": "Spanish orthography in the company name",
                "jurisdiction_hint": "es"}
    if re.search(r"[ãõç]", flat):
        return {"language": "pt", "confidence": "low", "signal": "Portuguese orthography in the company name",
                "jurisdiction_hint": "br"}
    if re.search(r"[ığşöçü]", flat):
        return {"language": "tr", "confidence": "low", "signal": "Turkish orthography in the company name",
                "jurisdiction_hint": "tr"}
    if ambiguous:
        return {"language": DEFAULT_LOCALE, "confidence": "ambiguous",
                "signal": (f"legal form '{ambiguous.group(0).strip()}' is shared by several languages and "
                           "the name carries no other marker; ask the user or pass --language"),
                "jurisdiction_hint": None}
    return {"language": DEFAULT_LOCALE, "confidence": "low",
            "signal": "Latin script with no language-specific marker; defaulted to English",
            "jurisdiction_hint": None}


# ------------------------------------------------------------------ jurisdictions

@lru_cache(maxsize=1)
def jurisdictions() -> dict:
    return json.loads((SKILL / "assets/jurisdictions.json").read_text(encoding="utf-8"))


def jurisdiction(code: str | None) -> dict:
    """Look up a jurisdiction by code, ISO name or alias. Unknown codes fall back to 'other'."""
    reg = jurisdictions()
    if not code:
        return reg["jurisdictions"]["other"] | {"code": "other"}
    k = str(code).strip().lower()
    k = reg["aliases"].get(k, k)
    if k not in reg["jurisdictions"]:
        k = "other"
    return reg["jurisdictions"][k] | {"code": k}


def jurisdiction_codes() -> list:
    return sorted(jurisdictions()["jurisdictions"])


# -------------------------------------------------------------------- formatting

def _sep(loc: dict, key: str, default: str) -> str:
    return loc.get("meta", {}).get(key, default)


def fmt_int(n, loc: dict) -> str:
    """Group digits using the locale's separator. 1234567 -> '1,234,567' / '1.234.567'."""
    if n is None:
        return loc["labels"]["dash"]
    s = f"{round(float(n)):,}"
    return s.replace(",", _sep(loc, "group_sep", ","))


def fmt_float(n, loc: dict, digits: int = 1) -> str:
    if n is None:
        return loc["labels"]["dash"]
    s = f"{float(n):,.{digits}f}"
    grp, dec = _sep(loc, "group_sep", ","), _sep(loc, "decimal_sep", ".")
    return s.replace(",", "\x00").replace(".", dec).replace("\x00", grp)


def fmt_pct(x, loc: dict, digits: int = 0) -> str:
    if x is None:
        return loc["labels"]["dash"]
    return fmt_float(float(x) * 100, loc, digits) + "%"


def fmt_compact(n, loc: dict, digits: int | None = None) -> str:
    """Scale a number the way this language actually says it: 1.2亿 / 120M / 1,2 Mrd."""
    if n is None:
        return loc["labels"]["dash"]
    n = float(n)
    sign = "-" if n < 0 else ""
    a = abs(n)
    for threshold, divisor, suffix in loc.get("scale", []):
        if a >= threshold:
            v = a / divisor
            d = digits if digits is not None else (0 if v >= 100 else 1)
            return sign + fmt_float(v, loc, d) + suffix
    return sign + fmt_int(a, loc)


def fmt_money(n, currency: str | None, loc: dict, compact: bool = True) -> str:
    if n is None:
        return loc["labels"]["dash"]
    body = fmt_compact(n, loc) if compact else fmt_int(n, loc)
    if not currency:
        return body
    space = " " if loc.get("meta", {}).get("currency_space", True) else ""
    if loc.get("meta", {}).get("currency_position", "before") == "before":
        return f"{currency}{space}{body}"
    return f"{body}{space}{currency}"


def fmt_people(n, loc: dict, approx: bool = True) -> str:
    if n is None:
        return loc["labels"]["dash"]
    pre = loc["labels"]["approx"] if approx else ""
    return f"{pre}{fmt_int(n, loc)}{loc['labels']['people_suffix']}"


def t(loc: dict, path: str, default=None):
    """Dotted-path lookup into a locale pack: t(loc, 'sections.executive')."""
    cur = loc
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def claim_type(loc: dict, key: str) -> str:
    """Canonical claim-type key -> display label in this locale."""
    return loc["claim_types"].get(key, key)


def claim_type_values(loc: dict) -> set:
    """Everything a report.json 'type' field may legally hold in this locale:
    the canonical English keys plus this locale's display labels."""
    return set(loc["claim_types"]) | set(loc["claim_types"].values())


def is_rtl(loc: dict) -> bool:
    return loc.get("meta", {}).get("direction", "ltr") == "rtl"


@lru_cache(maxsize=1)
def _installed_fonts() -> str:
    try:
        return subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True,
                              timeout=10).stdout.lower()
    except Exception:
        return ""


def pick_font(candidates, default: str) -> str:
    installed = _installed_fonts()
    if not installed:
        return default
    for c in candidates:
        if c.lower() in installed:
            return c
    return default


def fonts(loc: dict) -> tuple:
    """(sans, serif) actually installed on this machine, with a Latin safety net.

    Latin fallbacks are appended so a missing CJK/Arabic font degrades to a readable
    face instead of tofu boxes; the caller still warns when the script font is absent.
    """
    sans = list(t(loc, "meta.font_sans", [])) + ["Noto Sans", "DejaVu Sans", "Arial"]
    serif = list(t(loc, "meta.font_serif", [])) + ["Noto Serif", "DejaVu Serif", "Times New Roman"]
    return pick_font(sans, sans[0]), pick_font(serif, serif[0])


def font_warning(loc: dict) -> str | None:
    """Warn when no font for this script is installed, before a PDF full of boxes is produced."""
    script = t(loc, "meta.script", "latin")
    if script == "latin":
        return None
    wanted = list(t(loc, "meta.font_sans", []))
    installed = _installed_fonts()
    if not installed:
        return None
    if any(w.lower() in installed for w in wanted):
        return None
    hint = {"hans": "fonts-noto-cjk", "hant": "fonts-noto-cjk", "jpan": "fonts-noto-cjk",
            "kore": "fonts-noto-cjk", "arab": "fonts-noto-core (Noto Sans Arabic)",
            "cyrl": "fonts-noto-core"}.get(script, "fonts-noto-core")
    return (f"no installed font covers script '{script}' for locale {loc.get('_chrome')}; "
            f"install one (apt: {hint}) or the PDF will render boxes")


# --------------------------------------------------------------------------- CLI

def _cli():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "detect":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        print(json.dumps(resolve(company=name, env=False), ensure_ascii=False, indent=1))
    elif cmd == "locales":
        for tag in available_locales():
            p = _load_pack(tag)
            print(f"{tag:<6} {p['meta']['native_name']:<12} {p['meta']['name']:<28} "
                  f"dir={p['meta']['direction']} script={p['meta']['script']}")
        print("\nAny other language still works: prose is written in it, chrome falls back to English.")
    elif cmd == "jurisdictions":
        reg = jurisdictions()
        if len(sys.argv) > 2:
            print(json.dumps(jurisdiction(sys.argv[2]), ensure_ascii=False, indent=1))
            return
        for code in jurisdiction_codes():
            e = reg["jurisdictions"][code]
            print(f"{code:<8} {e['name']:<38} {e['currency'] or '-':<5} "
                  f"threshold={e['threshold_default'] or '-'} langs={','.join(e['languages']) or '-'}")
    else:
        print(__doc__)


if __name__ == "__main__":
    _cli()
