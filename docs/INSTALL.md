# Installing ghost-editor

The easy way: paste this into [Claude Code](https://claude.com/claude-code):

> Install the ghost-editor skill: clone https://github.com/kurbaitaev/ghost-editor into ~/.claude/skills/ghost-editor and follow its docs/INSTALL.md.

Your agent does the rest and tells you if it needs anything from you.

---

## For the agent doing the install

Work through these steps in order. Tell the user in plain words what you're installing and why.

1. **Clone** (skip if already there):
   ```bash
   git clone https://github.com/kurbaitaev/ghost-editor ~/.claude/skills/ghost-editor
   ```
2. **Check what's missing:**
   ```bash
   bash ~/.claude/skills/ghost-editor/scripts/doctor.sh
   ```
   Every `MISS` line ends with the command that fixes it. Run those.
   - On a Mac they use Homebrew. If `brew` is missing, ask the user to install it from https://brew.sh first (it needs their password).
   - Install Python packages with `pip install` (or `pip3`). If pip refuses with "externally managed environment", use `pip install --user`, or ask the user whether they prefer a virtualenv.
3. **Download the sound effects, music and animated emoji** (free Mixkit licence and Microsoft's MIT Fluent emoji, ~60 MB):
   ```bash
   python3 ~/.claude/skills/ghost-editor/scripts/library_restore.py
   ```
4. **Run `doctor.sh` again** until it ends with `0 missing`. Lines marked `opt` are optional.
5. **Gemini key (recommended, free tier).** It runs the B-roll check (each shot matches its line and keeps the user's
   people rules), finds the user's own footage by what is in it, copies the look of a reel they show you, and makes AI
   B-roll stills. Without it the presets work and the B-roll check is skipped. Ask the user for one:
   - they get a free key at https://aistudio.google.com/apikey
   - `pip install google-genai pillow`
   - save it with `echo 'GEMINI_API_KEY=<key>' >> ~/.claude/skills/ghost-editor/.env` (the file is gitignored)
   - tell them the frames being checked are sent to Google.
   Then ask whether they have rules for who or what may appear in B-roll (for example no women, no children, no flags or
   religious symbols). If they do, write them into `people-rules.json` in the format of `people-rules.example.json`;
   if not, leave it empty. Never add rules they didn't ask for.
6. **ElevenLabs key (optional).** Only for the vector explainer's narrator. If the user wants it: a key from elevenlabs.io (Profile → API keys),
   saved as `ELEVENLABS_API_KEY=<key>` in the same `.env`. Noise removal (`scripts/denoise.sh`) needs no key; it sets itself up on first use
   (python3.11 + uv, about 1 GB).
7. **Optional extras (ask first; each is one command and sets up its own venv, weights go to `~/.cache`):**
   - `bash scripts/setup_looks.sh`: film-stock looks (generates the LUTs, ~1 GB venv, a minute).
   - `bash scripts/setup_matte.sh`: the clean person cut-out for words behind the speaker (~2.4 GB with the model).
   - `bash scripts/setup_audioqa.sh`: pause detection on noisy recordings and voice super-resolution (~1.9 GB).
   - `bash scripts/setup_captions.sh`: only to add a new font to the caption templates.
   Without them everything else works; `doctor.sh` lists them as `opt`.
8. **Tell the user it's ready**, and that they can now say, for example: "Edit ~/Downloads/my-video.mov into a reel."

Restart Claude Code (or start a new session) so the skill shows up.

---

## On Windows

Untested on a real Windows machine so far (the changes were checked on Linux); please report what breaks.
Run everything from Claude Code, whose shell on Windows is Git Bash, so the `bash scripts/...` commands work as written.

1. Install the tools (PowerShell or Git Bash), then open a **new** terminal so PATH picks them up:
   ```bash
   winget install Git.Git
   winget install Gyan.FFmpeg
   winget install OpenJS.NodeJS.LTS
   winget install Python.Python.3.12
   ```
   Tick "Add python.exe to PATH" if the Python installer asks. `Gyan.FFmpeg` is the full build (libvpx + libass).
2. Make `python3` work (Windows ships only `python.exe`) and switch Python to UTF-8 file reading:
   ```bash
   bash ~/.claude/skills/ghost-editor/scripts/win_python3.sh
   ```
   ```bash
   setx PYTHONUTF8 1
   ```
   Open a new terminal after `setx`.
3. Python packages, including EasyOCR for the caption check (macOS uses its built-in Vision instead):
   ```bash
   pip install openai-whisper numpy opencv-python pillow google-genai easyocr
   ```
   The caption check reads Russian + English by default; set `GHOST_OCR_LANGS` for other captions, e.g. `vi,en`
   for Vietnamese (EasyOCR pairs English with either one Cyrillic or one Latin-script language).
4. Continue from step 3 of the agent steps above (`library_restore.py`, then `doctor.sh` until `0 missing`).

Notes:
- The optional setups (`setup_looks.sh`, `setup_matte.sh`, `setup_audioqa.sh`, `denoise.sh`) need Python 3.11:
  `winget install Python.Python.3.11`. They find it through the `py` launcher and link each venv's `Scripts\` folder
  as `bin\`, so the skill's paths work unchanged.
- Without Developer Mode, Windows cannot make symlinks; the scripts then copy the file instead (uses more disk).
- Whisper runs on the CPU unless you have an NVIDIA GPU with CUDA PyTorch, so transcription is slower.
- WSL2 (Ubuntu) is an alternative: there, follow the Linux path (`apt` instead of `brew`).

## Doing it by hand

You need a Mac with Apple silicon (what it is built and tested on; Linux, Intel Macs and Windows are less tested,
and off macOS the caption check uses EasyOCR, see "On Windows" above) with:
- ffmpeg (with libvpx and libass): `brew install ffmpeg`
- Node 18 or newer: `brew install node`
- Whisper: `pip install openai-whisper`
- Python packages: `pip install numpy opencv-python pillow`
- Recommended: `pip install google-genai` and a Gemini key (see above); optional: `brew install yt-dlp` to pull reference videos from a link

```bash
git clone https://github.com/kurbaitaev/ghost-editor ~/.claude/skills/ghost-editor
cd ~/.claude/skills/ghost-editor
bash scripts/doctor.sh
python3 scripts/library_restore.py
```

**Other agents** (untested; it is built with Claude Code). Codex, or any agent that reads Agent Skills: clone or symlink the folder into that agent's skills directory. Any other agent: tell it "Follow `<path>/ghost-editor/SKILL.md` to edit this recording." Every step is a plain shell command.
