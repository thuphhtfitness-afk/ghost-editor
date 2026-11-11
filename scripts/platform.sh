# Cross-platform helpers for the shell scripts: macOS, Linux and Windows (Git Bash, which Claude Code uses there).
#   . "$S/scripts/platform.sh"

is_windows() { case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) return 0;; *) return 1;; esac; }

# The install command for a missing tool on this machine: inst "<macOS>" "<Linux>" "<Windows>"
inst() { if is_windows; then echo "$3"; elif [ "$(uname -s)" = Linux ]; then echo "$2"; else echo "$1"; fi; }

# Python 3.11 for the optional venvs: python3.11 on PATH, then the Windows launcher (py -3.11), then Homebrew's path
find_py311() {
  local p
  p=$(command -v python3.11 2>/dev/null) && [ -n "$p" ] && { echo "$p"; return; }
  if command -v py >/dev/null 2>&1; then
    p=$(py -3.11 -c "import sys; print(sys.executable)" 2>/dev/null | tr -d '\r')
    [ -n "$p" ] && { if is_windows; then cygpath -u "$p"; else echo "$p"; fi; return; }
  fi
  echo /opt/homebrew/bin/python3.11
}

# A Windows venv keeps its programs in Scripts\, not bin/. Link bin -> Scripts (a directory junction, no admin
# rights needed) so every "$V/bin/python" path in the skill works unchanged. No-op elsewhere.
venv_bin_link() {
  is_windows || return 0
  [ -d "$1/Scripts" ] && [ ! -e "$1/bin" ] || return 0
  MSYS2_ARG_CONV_EXCL='*' cmd /c mklink /J "$(cygpath -w "$1/bin")" "$(cygpath -w "$1/Scripts")" >/dev/null
}
