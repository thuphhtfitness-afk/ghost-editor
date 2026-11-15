# HT Essay (HT Private Fitness)

Video-essay style (red / paper / black pages with grain, big serif keyword + small sans words on the spoken word,
graded coach footage: cine, B&W, red duotone; footage cards; drawn rings, counters, bars, footsteps), interleaved
with the coach talking. Colours always come from the fixed palette `styles/ht-private-fitness.palette.json`
(override with env `PALETTE=<file>`).

Rules for this channel:
- Never show the coach from behind (shirt back). If a line from such a scene is needed, keep the voice and cover it
  with another shot (page, card, or a front/side shot of the coach).
- Reels under 120 s, keep coach talking shots alternating with graphic pages.

Pipeline (Linux, ffmpeg + faster-whisper + Pillow):
1. 1080x1920 proxy of the raw take -> `work/src1080.mp4`, 16 kHz mono wav -> `work/audio16k.wav`
2. transcribe (faster-whisper large-v3, vi, word timestamps, condition_on_previous_text=False) -> `work/words.json`
3. `cuts.py ranges.json audio16k.wav > cuts.json` (pauses trimmed inside the chosen source ranges)
4. write a reel spec (see `reels/r1.py`: shots by source time `s`; captions split into short chunks with `/`, one `*keyword*` per chunk (big heavy serif italic, or heavy sans with `*!word*`))
5. `engine.py reel.json outdir` then `finish.py reel.json outdir final.mp4` (voice clean-up, procedural piano bed, mix)

Type: keywords in Playfair Display Black Italic (900i) or Inter Tight ExtraBold (800); small words Inter Tight Bold (700)
at 56 px. On coach shots captions sit mid-body (y ≈ 1180 of 1920), never on the face.
Fonts (OFL, Google Fonts) are downloaded into `<workdir>/fonts`; the engine reads `fonts/`, `work/src1080.mp4` and
`dl/src.mp4` relative to the folder above `scripts/`.
