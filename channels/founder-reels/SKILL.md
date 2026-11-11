---
name: founder-reels
description: "Edit the founder's sit-down interview recordings (Vietnamese, the founder of an HT fitness business talking about hiring, management, fear, failure) into short vertical reels for TikTok/Reels. Use when the user hands over a founder interview or podcast-style recording and asks to break it into reels, write a brief, cut a hook, edit 'like reel 1111 / 2A / 4A', or write a TikTok caption for a founder reel. Not for workout / form-correction videos (that is hpf-reels)."
---

# founder-reels

The founder's channel: one long interview -> a series of reels, each one idea, **30-90 s** (never under 30 s: merge
two short story lines into one reel). Built on the `ghost-editor` engine with `make_reel.py` (spec in its docstring).
This skill has its OWN taste file (`taste.json` here; `make_reel.py` sets `GHOST_TASTE` to it): record the user's
corrections with `GHOST_TASTE=<this dir>/taste.json python3 ~/.claude/skills/ghost-editor/scripts/taste.py add "..."`.
Read `STYLE.md` (house style) and `taste.py list` with that GHOST_TASTE before planning.

## Workflow
1. Base per recording: `prep.sh`, `transcribe.py --lang vi` (re-run quiet stretches on a loudnorm'd copy: an off-camera
   question often comes back empty).
2. Brief first (a doc for the editor): per reel the hook, In/Out table, cards, misheard words. Wait for the OK.
3. One spec per reel -> `python3 make_reel.py spec.json`. Send one pilot reel before a batch.
4. Caption for TikTok when asked: a hook line from the reel, 2-4 short lines of the story, a question to the viewer,
   5-7 Vietnamese hashtags without accents (#khoinghiep #founder ...). No names of people.

## Hard rules from the user (all enforced by make_reel.py unless noted)
- **Privacy:** never show the eyes or nose. `privacy: {top, cx}` crops the RAW recording just under the nose: cheeks,
  chin and beard may show (covering the whole face "looks like a criminal"). Check a sheet of the plate per recording.
- **Privacy line = the LOWEST the face goes in the whole recording**, not the usual position: the founder leans in
  while talking and the glasses / nose drop into frame. Sheet the whole plate (1 frame / 3 s) before rendering and
  check the leaning moments. Measured: office recordings top 680-700, café recordings top 740.
- **Names of people** (`names`): muted and beeped in the plate, `***` in the captions. Street / brand names stay (`proper`).
- **Non-standard words** (vãi, đéo, ngu ... `PROFANITY`): cut out of the takes; the run reports each cut.
- **Captions:** capital letter only at a sentence start and on proper nouns.
- **Hook:** the strongest line, cut to the front, shown as a `quotestack` (Refined Ambition quote style). With a hook cut
  there is NO title / question sticker at the start. Hook -> main: white flash + click (`hookCut`).
- **Comparisons are visualised** (`compare` frame): employee vs manager, then vs now, did-the-work vs didn't, win vs lose.
- **No paraphrase cards** ("Câu hỏi khiến tôi im lặng 5 giây"): cards carry the speaker's own point, never commentary.
- **B-roll:** only footage that IS the line (the client's own clips first). B-roll after B-roll is a straight cut.
  "gương vỡ" gets the glass crack + a quiet glass break (~8 dB under the voice).
- **Music:** warm piano / cello bed (silent-descent, classical-7, miss-you), 14 dB under the voice, the whole reel.
