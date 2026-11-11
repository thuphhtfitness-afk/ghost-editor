> **Superseded where they differ by SKILL.md** (the user's later rules: privacy crop, quotestack hook with no title card, beeped names, cut words, sentence-case captions, 30 s minimum, hard-cut B-roll chains, music bed).

# HT interview reels

Vertical reels cut from long sit-down interviews (Vietnamese, one camera, the speaker in profile, an interviewer off
camera). One recording is broken into a short series: each reel is one idea, 20-60 s, no shared segments. Built on the
core pipeline (`build.mjs` + HyperFrames) by `make_reel.py`; this file is the house style the client asked for.
Call: "HT interview", "edit like reel 1111 / 2A".

## Workflow

1. **Base per recording, once:** `prep.sh <raw> <base>`, then `transcribe.py <base>/assets/talk.mp4 --lang vi`. Quiet
   stretches (an off-camera question, a mic far away) come back EMPTY from Whisper: check the take table for gaps and
   re-run those seconds on a loudnorm'd copy before planning. `face_track.py`, or a measured box when the model cannot
   be fetched (static camera: one box for the whole recording, with margin).
2. **Brief first** (a Claude doc for the editor): summary, one table per reel with hook, In/Out, words, cards, then the
   misheard words. The client approves the brief; reels are cut from it.
3. **One spec per reel** (`make_reel.py` docstring), then `python3 make_reel.py spec.json`. Send the export; their notes
   go back into the spec and `taste.py add` in their words.

## House style (from the client's notes)

- **Hook:** the strongest line of the reel, even when it is said later (put that segment first), plus a short on-screen
  question card. If the recording has a quiet or missing question, replace those seconds with the clean question
  recording the client sends ("voice trám"), timed so it never overlaps the answer (slow the first seconds of picture
  up to ~11 % if needed).
- **Captions:** Vietnamese, `highlighter` template, 4 words a group, one yellow keyword, fixed at y 1400 (under the cards,
  above the platform UI). Fix misheard words with `phrases` (tạp vụ, bạn nhân viên, chiến lược, chung chung).
- **Cards** under the chin, dark, small uppercase header + 1-3 lines that land on their words: `quote` for a question or
  a takeaway. **A comparison the speaker walks through ("some do X, others Y, the best Z") is ONE `compare` frame**, columns
  ordered low to high (red / yellow / green), each lighting up when spoken, never three separate cards (client, 2A).
- **B-roll only when the footage really is the line.** A generic staff shot under "nhân viên" was rejected (1111): no
  insert beats a wrong insert. The client's gym clips with close body shots are never used as B-roll.
- **The literal image when the speaker names one:** "gương vỡ" gets the glass crack (`crack_fx.py`, impact away from the
  face) and a glass-break sound on the word "vỡ", kept QUIET: ~8 dB under the voice (`volume=0.22` on the CC0 file).
  The client asked for it louder than the skill's no-SFX-on-words rule, then smaller: this level is the agreed one.
- No meme sounds, no music bed in the export (the client adds platform music at post time). Voice -14 LUFS.
- Off-topic or off-brand stretches are cut from the gym's channel (e.g. bar pick-up stories) and noted in the brief.
- Outdoor café recordings (speaker at the left edge, cups in front): `frame: {"zoom": 1.2, "x": 0.1}` punches the plate.
