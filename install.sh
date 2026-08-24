#!/usr/bin/env bash
# Install company-talent-economics for Claude Code and Codex, check dependencies, or build a zip.
#
#   bash install.sh                # symlink into ~/.claude/skills and ~/.codex/skills
#   bash install.sh --copy         # copy instead of symlink (for machines where symlinks are awkward)
#   bash install.sh --project      # also link into ./.claude/skills of the current repo
#   bash install.sh --claude       # Claude Code only
#   bash install.sh --codex        # Codex only
#   bash install.sh --check        # verify dependencies only, install nothing
#   bash install.sh --zip          # build dist/company-talent-economics.zip for the claude.ai uploader
#   bash install.sh --uninstall    # remove the installed links/copies
#
# Piped straight from the web with no clone present, it fetches the repository first:
#   curl -fsSL https://raw.githubusercontent.com/kelvinfkr/company_skill/main/install.sh | bash
set -euo pipefail

REPO_URL="https://github.com/kelvinfkr/company_skill.git"
NAME="company-talent-economics"
MODE="link"
DO_CLAUDE=1
DO_CODEX=1
PROJECT=0
CHECK_ONLY=0
ZIP_ONLY=0
UNINSTALL=0

for a in "$@"; do
  case "$a" in
    --copy) MODE="copy" ;;
    --project) PROJECT=1 ;;
    --claude) DO_CLAUDE=1; DO_CODEX=0 ;;
    --codex) DO_CODEX=1; DO_CLAUDE=0 ;;
    --check) CHECK_ONLY=1 ;;
    --zip) ZIP_ONLY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "unknown option: $a (try --help)" >&2; exit 2 ;;
  esac
done
# --------------------------------------------------------------- locate the skill
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  ROOT=""
fi

if [ -z "$ROOT" ] || [ ! -d "$ROOT/skills/$NAME" ]; then
  CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/company-talent-economics"
  echo "[..] no local checkout found; fetching $REPO_URL"
  command -v git >/dev/null || { echo "[!!] git is required for the piped install" >&2; exit 1; }
  if [ -d "$CACHE/.git" ]; then
    git -C "$CACHE" pull --ff-only --quiet
  else
    rm -rf "$CACHE"
    git clone --depth 1 --quiet "$REPO_URL" "$CACHE"
  fi
  ROOT="$CACHE"
fi

SRC="$ROOT/skills/$NAME"
[ -f "$SRC/SKILL.md" ] || { echo "[!!] $SRC/SKILL.md not found; is this the right repository?" >&2; exit 1; }

# ------------------------------------------------------------------------ checks
have() { command -v "$1" >/dev/null 2>&1; }

font_installed() {  # font_installed <grep-pattern>
  have fc-list || return 1
  # Captured first on purpose: `fc-list | grep -q` dies of SIGPIPE under `set -o pipefail`
  # and would report every font as missing.
  local families
  families="$(fc-list : family 2>/dev/null || true)"
  printf '%s' "$families" | grep -qiE "$1"
}

check() {
  local ok=1
  local py=python3
  have python3 || py=python
  if have "$py"; then
    echo "[ok] $("$py" -V 2>&1)"
  else
    echo "[!!] python3 not found: everything in scripts/ needs it"; ok=0
  fi

  if "$py" -c "import docx" 2>/dev/null; then
    echo "[ok] python-docx"
  else
    echo "[!!] python-docx missing (only render_report.py needs it):  pip install -r $SRC/requirements.txt"; ok=0
  fi

  if have libreoffice || have soffice || [ -x /Applications/LibreOffice.app/Contents/MacOS/soffice ]; then
    echo "[ok] LibreOffice"
    if have dpkg && dpkg -l 2>/dev/null | grep -q '^ii  libreoffice-core' \
       && ! dpkg -l 2>/dev/null | grep -q '^ii  libreoffice-writer'; then
      echo "[!!] libreoffice-core is installed without libreoffice-writer: DOCX will not convert."
      echo "     apt install libreoffice-writer"; ok=0
    fi
  else
    echo "[!!] LibreOffice missing (DOCX -> PDF step only):"
    echo "     apt install libreoffice-writer  |  brew install --cask libreoffice"
    echo "     render_report.py --docx-only still works without it"; ok=0
  fi

  if font_installed "CJK|Source Han|PingFang|YaHei|SimHei|WenQuanYi|Noto (Sans|Serif) (SC|TC|JP|KR)"; then
    echo "[ok] CJK font (Chinese, Japanese, Korean reports)"
  else
    echo "[--] no CJK font: Chinese/Japanese/Korean PDFs render boxes.  apt install fonts-noto-cjk"
  fi
  if font_installed "Noto Sans Arabic|Noto Naskh|Amiri|Scheherazade"; then
    echo "[ok] Arabic font"
  else
    echo "[--] no Arabic font: Arabic PDFs render boxes.  apt install fonts-noto-core"
  fi
  if font_installed "Noto Sans|DejaVu Sans|Liberation Sans|Arial|Helvetica"; then
    echo "[ok] Latin/Cyrillic font"
  else
    echo "[--] no general Noto/DejaVu font found.  apt install fonts-noto-core fonts-dejavu"
  fi

  echo
  if [ $ok -eq 1 ]; then
    echo "All required dependencies present."
  else
    echo "Some dependencies are missing. Lines marked [--] only affect the scripts named next to them."
  fi
  return 0
}

# ---------------------------------------------------------------------- installs
install_to() {
  local dst="$1"
  mkdir -p "$(dirname "$dst")"
  if [ -e "$dst" ] || [ -L "$dst" ]; then rm -rf "$dst"; fi
  if [ "$MODE" = "copy" ]; then cp -R "$SRC" "$dst"; else ln -s "$SRC" "$dst"; fi
  echo "[installed] $dst ($MODE)"
}

remove_from() {
  local dst="$1"
  if [ -e "$dst" ] || [ -L "$dst" ]; then rm -rf "$dst"; echo "[removed] $dst"; fi
}

build_zip() {
  local out="$ROOT/dist/$NAME.zip"
  mkdir -p "$ROOT/dist"
  rm -f "$out"
  command -v zip >/dev/null || { echo "[!!] zip not found (apt install zip)" >&2; exit 1; }
  ( cd "$ROOT/skills" && zip -qr "$out" "$NAME" -x '*/__pycache__/*' '*.pyc' '*/.DS_Store' )
  echo "[built] $out"
  echo "        Upload it at claude.ai -> Settings -> Capabilities -> Skills -> Upload skill."
}

# -------------------------------------------------------------------------- main
if [ $ZIP_ONLY -eq 1 ]; then build_zip; exit 0; fi

if [ $UNINSTALL -eq 1 ]; then
  if [ $DO_CLAUDE -eq 1 ]; then remove_from "$HOME/.claude/skills/$NAME"; fi
  if [ $DO_CODEX -eq 1 ]; then remove_from "$HOME/.codex/skills/$NAME"; fi
  if [ $PROJECT -eq 1 ]; then remove_from "$(pwd)/.claude/skills/$NAME"; fi
  echo "Uninstalled. The checkout at $ROOT is untouched."
  exit 0
fi

if [ $CHECK_ONLY -eq 1 ]; then check; exit 0; fi

if [ $DO_CLAUDE -eq 1 ]; then install_to "$HOME/.claude/skills/$NAME"; fi
if [ $DO_CODEX -eq 1 ]; then install_to "$HOME/.codex/skills/$NAME"; fi
if [ $PROJECT -eq 1 ]; then install_to "$(pwd)/.claude/skills/$NAME"; fi

echo
check
echo
echo "Claude Code:  /$NAME <company>        Codex:  \$$NAME <company>"
echo "Either host also triggers it automatically from a question about what people at a company earn."
echo "The report language follows the language of the company name you type."
