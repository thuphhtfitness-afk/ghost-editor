#!/usr/bin/env bash
# Windows only: the skill runs `python3` everywhere, but the python.org / winget installer only ships python.exe
# (and "python3" is often the Microsoft Store stub). This puts a python3.exe copy next to the real python.exe.
#   bash scripts/win_python3.sh
set -euo pipefail
. "$(cd "$(dirname "$0")" && pwd)/platform.sh"
is_windows || { echo "not Windows: nothing to do"; exit 0; }
if python3 -c "import sys" >/dev/null 2>&1; then echo "python3 works: $(command -v python3)"; exit 0; fi
real=$(py -3 -c "import sys; print(sys.executable)" 2>/dev/null | tr -d '\r' || true)
[ -n "$real" ] || real=$(python -c "import sys; print(sys.executable)" 2>/dev/null | tr -d '\r' || true)
[ -n "$real" ] || { echo "no Python found: winget install Python.Python.3.12 (then open a new terminal)"; exit 1; }
dir=$(dirname "$(cygpath -u "$real")")
cp "$dir/python.exe" "$dir/python3.exe"
hash -r
python3 -c "import sys; print('python3 ->', sys.executable)"
case ":$PATH:" in *":$dir:"*) ;; *) echo "note: add $dir to PATH (the installer's 'Add python.exe to PATH' box) and open a new terminal";; esac
