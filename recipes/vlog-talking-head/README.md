# Vlog talking head (teaching reels)

A plain talking-head reel for teaching content (trainer courses, tips): the speaker big and centred, a hook at the
top, a 1-2-3 list in big lowercase titles, keyword-highlighted captions near the middle, small two-line notes and
hand-drawn white arrows on the user's own B-roll, no sound effects, a quiet bed, the channel outro at the end.
The look comes from a gym vlog reference (big lowercase heavy titles with a small italic subline, white notes, drawn
arrows). Built for footage shot without a mic in a busy room, often landscape (cropped to 9:16 around the speaker).

Call: "talking head like the reference", "edit dạng talking head", "teaching reel", "vlog talking head".

## What the user asked for (their words, keep them)

- Speaker zoomed in, big, around the middle of the frame. Pauses cut so the talk is continuous.
- Captions pushed up near the middle; keywords highlighted (yellow); hook line at the very start with big type and a
  white flash into the main video; the hook line still plays at its place later.
- No Step Deck cards, no sound effects. Listing 1-2-3 in the reference's plain title style.
- Voice firm and full ("mạnh mẽ, đầm", not thin or "watery"): light denoise (~20 dB) so a little room tone stays,
  body + presence EQ, firm compression; a quiet bed is fine as long as it never covers the voice.
- B-roll = the user's own coaching footage on the lines about pushing / motivating / correcting a client.
- The channel outro on every final (library/outro, `finals.py render` adds it).

## Pipeline

```bash
R=$S/recipes/vlog-talking-head
bash $S/scripts/denoise.sh RAW.mov clean/v.wav 20          # the voice
bash $S/scripts/denoise.sh RAW.mov clean/v_full.wav 100    # only to find pauses (silent floor)
python3 $R/track.py RAW.mov 0 <end> v.track.json <x,y of the speaker's face> <min face px>   # or a fixed track file
# whisper large-v3 word json of clean/v.wav (temperature fallback on; beam-only decoding invents "subscribe" lines)
python3 $R/th_prep.py reel.json        # pauses cut -> pieces, caption words (edit s), zoomed plate, voice, B-roll clips
python3 $P/tools/build.py              # a short config calling th_build.build(P, cfg) -> index.html
bash $S/scripts/hf.sh lint $P; bash $S/scripts/hf.sh snapshot $P --at ... --no-end
python3 $S/scripts/finals.py preview $P --out ... --code R01 --style "Talking head" --title "..."   # WAIT for the OK
python3 $S/scripts/finals.py render  $P ...                 # + "<name> (outro).mp4", the file to post
```

reel.json: `project, src, clean, nr_ref, whisper, track, zoom_w (crop width in source px: 450 for a face in a 1080p
landscape shot, 540 for a seated/standing demo, 810 for a 1080x1920 source), face_y (0.30-0.40), broll_src,
broll [[name, src start, dur]], segs [[a, b, "corrected text with compound_words"]]`. A segment listed first and again
later is the hook (cfg `hook.segs` = how many leading segments are the hook). Text is the corrected Vietnamese; the
words are aligned to whisper onsets per segment and mapped through the pause cuts.

cfg for th_build.build: `title, hook {n tokens, segs, lines [[i, j] | {"text", "at", "key"}], sub}, titles
[(from token, hold s | "w<token>", [lines], subline)], broll [(clip, from, to)], notes [(from, to, [l1, l2], (x, y))],
arrows [(from, to, body path, head path)], key {token indices}, punch [(from, to|None, scale)], cap_y (1180),
title_y (150; 1440 when the speaker's head is near the top), cap_stroke (a dark text stroke on bright backgrounds),
bed, bed_vol (0.06)`.

## Rules learned on the first nine reels

- Look at the speaker's position before choosing the crop: a wide class shot needs a fixed crop around the
  demonstration (bench + coach), not face tracking; a tracker can lock onto another face in a group.
- Place notes and arrows on dark, quiet parts of the frame (a black shirt, the floor), never across the caption band;
  route an arrow around the captions.
- Whisper merges and mishears in a noisy room: cross-check two passes (raw + denoised audio), keep only what is clear,
  and list every guessed word for the user to check.
- Unclear tails are dropped, not captioned with guesses.
- jsdelivr may be blocked in a sandbox: set GSAP_JS to a local gsap.min.js (`npm pack gsap@3.14.2`).
