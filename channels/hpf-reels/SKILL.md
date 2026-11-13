---
name: hpf-reels
description: "Edit HPF (the gym's training channel) workout and form-correction videos: a coach cueing a client through an exercise (split squat, RDL, deadlift ...), filmed handheld in the gym, Vietnamese voice. Use when the user sends a training / exercise tutorial / form-fix recording and asks to edit it, 'like the HPF references', or for HPF captions. Up to 2 minutes per video. Not for the founder's interviews (that is founder-reels)."
---

# hpf-reels

The gym's training channel. One coaching session -> one tutorial reel of 30 s to **2 minutes** (use the extra time for every useful cue rather than ending abruptly), built on the
`ghost-editor` engine. This skill has its OWN taste file (`taste.json` here): record the user's corrections with
`GHOST_TASTE=<this dir>/taste.json python3 ~/.claude/skills/ghost-editor/scripts/taste.py add "..."`.

## The look (from the user's two references, a ProLifting RDL fix and a deadlift setup)
- **Story:** the wrong way first (or the client's first attempt), then each cue in order, then the corrected rep.
  Cut setup chatter, repeated cues and counting; keep the cue words and the reps that show them.
- **Cue labels:** small orange rounded boxes (bg #F07A1A, white or black bold Montserrat, ~42 px), near the middle of the frame, one at a time,
  with ❌ for the fault ("Trọng tâm dồn vào gót chân ❌") and ✅ for the fix ("Mông được kéo căng ✅"); numbered steps for a
  setup ("1. Tạo khoảng cách", "2. Đứng rộng chân", "5. Hinge").
- **Drawn guides on the body, on the cue word:** white dashed lines (hip line, shin line, bar path), white dashed
  arrows for a direction (hips back), red arrows pointing at a foot / the head, red circles around a foot.
- **The fault replays in black and white** with a big red ❌ badge; the fix is in colour (optionally a green ✅).
- **Punch-ins** on the body part being cued (feet, knee, hip) cut from the same shot; whip / flash cuts between moves.
- **Muscle callout:** when the coach names the target muscle (mông, đùi sau ...) a small red anatomy illustration
  pops at the top centre with its name. Use a licensed or self-drawn illustration only.
- **Captions:** small white words at the bottom centre, one or two at a time, no box (the labels carry the meaning).
- Gym branding / address corner tag optional (ask the user for the text).
- Music: upbeat light bed under the voice (not the founder's piano); cue sounds: soft pop on a label, click on a cut.

## The anatomy look (third reference, a hip-extension edit)
- **Hook title:** big Montserrat 900 uppercase at the top, yellow (#FFD21E) for the exercise ("SPLIT SQUAT"), white or
  red under it for the promise / the fault ("TẬP TRUNG MÔNG", "LỖI HAY GẶP"). Red = wrong, green (#35E06B) = correct.
- **Anatomy scene** (`anatomy` beat) whenever a muscle is named or felt ("thấy mông hơn không"): black stage, red floor
  glow, the self-drawn posterior figure (scripts/lib/anatomy.mjs) with the named group glowing (glute, glute_med,
  hamstring, calf), a yellow title ("CƠ MÔNG"), yellow labels ("Kéo căng") and red arrows ON the muscle. 2-4 s.
  The reference's 3D renders are licensed artwork: never copy them; the user may send licensed images later.
- **All text in Montserrat.** Cue labels sit near the middle of the frame (y ~600), or as a `note` AT the body point
  (glowing dot or red ring + a leader line to the words): "Ngón út chạm sàn" on the toe, "Trọng tâm" on the front foot.
- Measure body points on a gridded frame of the base before placing guides / notes (handheld footage moves).

## Show every cue, never just say it (the user's rule; fourth reference, a bent-over-row fix)
- **Every coaching cue gets a picture.** A viewer cannot imagine "dồn trọng tâm vào chân trước" from words: draw it,
  highlight it or show it in the anatomy of the movement. Pick, in this order:
  1. **Anatomy IN the movement** (`anatomy` with `view: "splitsquat"`, `pose: bottom|top`): the exercise's own pose with
     the working muscle group glowing (glute, quad, hamstring, core, back, back_quad) and a mark for the cue:
     `weight` (yellow arrow onto the front foot), `kneeDown` (back knee straight down), `lean` (torso line vs vertical),
     `drive` (green arrow up), `leanBackBad` (red arrow, the fault). Titles: yellow = cue, red = fault, green = correct.
     Other exercises need their own pose drawing in scripts/lib/anatomy.mjs before editing them.
  2. **On-body highlight** (`glow`): a pulsing red (muscle) / yellow (point) / green zone with a dashed rim, placed on the
     body part in the footage (shoulders for "hạ vai", hips for "hông song song", the front foot for "đạp cả bàn chân").
  3. **Drawn guides / notes** (`guide`, `note`): arrows along a leg, a ring on the toe with its words.
  4. A close-up from another take (B-roll) when the detail is small (the heel turn).
- From the reference: red translucent glow painted on the muscle in the footage ("LƯNG DƯỚI"), a small yellow-framed
  anatomy inset, full-screen glowing anatomy for "gồng lên cực kỳ nhiều", yellow lines along the spine / between the
  shoulder blades, an angle marker ("30-45°"), red titles for a fault ("Dốc quá cao"), green for fine ("Không vấn đề gì!").
- **No text on text.** One zone each: titles at the top, cue labels near the middle, notes beside their point, captions
  at the bottom. `hpf_reel.py` (text_layout) moves a note under a label, a label under a title, keeps notes above the
  captions and hides labels during an anatomy scene. Look at a snapshot sheet before rendering anyway.

## Colours and the anatomy card (the user's latest rules; they override anything above)
- **Text colours: red, black and white only. No orange, no yellow, no green text.** Titles and cue labels are white
  Montserrat on a wine-red box (#7A1424); notes are white on a dark box (wine-red for a fault). Icons (red X, check)
  and on-body glows may keep their colours; anatomy marks are white (red for the fault).
- **The anatomy is a small card in a free corner** (`anatomy` default mode, `corner: tl|tr|bl|br`, pick the empty
  side of the frame), with the footage behind it softly blurred and dimmed so the card pops. Its title and labels are
  white on wine red inside the card. `mode: "full"` (the black full-screen stage) only when the user asks for it.

## Anatomy art and quiet voices (the user's latest rules)
- **Anatomy images must look like a real muscle illustration** (grey body, the named muscle in orange-red with visible
  fibres), never the stick-figure / skeleton look. `scripts/lib/muscle_art.mjs` draws them (posterior: glute, glute_med,
  hamstring, calf, erector/back, lat; `view: "ant"`: core, quad, pec); it zooms to the highlighted muscle. The movement
  views (`view: "splitsquat"` / `"hinge"`) are only for a cue about the motion (lean, shin vertical, seesaw). Never use
  stock / newspaper images the user sends as references (copyright); suggest licensed images or keep the drawn art.
- **A quiet voice** (the client asking off-mic): spec `"boost": [[a, b], ...]` lifts each source range to the coach's level
  (auto gain to -16 LUFS, max +20 dB, 80 ms ramps, limiter). Always list the client's questions there.
- Several clips of one lesson: `ghost-editor` base per clip, then `combine.py` (scratch helper) joins them into one base so
  a reel can cut between main footage and close-up clips (the close-up with its own voice is also a main segment).

## Titles, captions, rings and before/after (the user's corrections after HPF 3 / HPF 4)
- **Hook title = the reference card** (`title` beat with `style: "card"`, fields `tag` / `big` / `sub`): a cream card, a small
  wine-red tag line with the question ("Tập mãi không thấy mông?"), a giant heavy red lowercase word ("romanian"), a black
  line under it ("deadlift"). ONE title block at the start, never two stacked titles; no title / label / note may sit on
  another one or on an anatomy scene (text_layout trims them).
- **Captions sit at y 1380** (just below the middle of the lower half), not at the very bottom.
- **A fault replay shows only the faulty rep**: cut the set-up / posing that leads into it. Highlight the muscle that
  takes over (a red `glow` on the thigh) and ring the joint that drifts (a red `guide` circle on the knee).
- **Every time a knee is named, ring the knee** (`guide` circle, red; green for the fix). Measure the knee on a snapshot
  of the BUILT reel (the plate is zoomed per take), never on the raw frame. Do not ring a part that is not in shot.
- **Anatomy B-roll for a mechanism** ("xoay ngoài kém"): `hiprot` beat (hip seen from above: the knee swings out / collapses
  in, the glute fan lights up then dims), black stage like the user's reference. Title words never overflow (auto-fit).
- **Before / after at the end** (`compare2` beat + `stills` in the spec): the frame pauses and splits top / bottom, the
  fault frame in black and white on top (label "Trước khi sửa" / the fault, red X), the fix in colour below (green tick);
  each half carries drawn lines measured on the stills: a dashed plumb line through the ankle, the leg axis (hip-knee-ankle
  or knee-ankle) in red / green and a ring on the knee, so the difference can be seen. Use the coach's own "compare" line
  or the closing line of the lesson for it, 4-6 s. Do this for every reel that has a before and an after.

## Cuts, accents and dark scenes (the user's corrections after HPF 3 / HPF 4)
- **Cut the voice that talks to the camera operator** (words like "tôi", "bác", "Thu ơi", "ngửa máy lên", "gần nữa vào"): it only
  adjusts the scene. Search the kept words for those and drop the whole sentence before building.
- **Never cut a scene before a word is finished.** Take tails are +0.4 s after the last word (whisper word ends come early);
  never end a segment on a word that is cut off in the middle.
- **Local accent:** "mày" in a coaching line means "này": the captions say "này" (done in hpf_reel.py). Fix other accent
  mis-hearings the same way (spec `phrases`).
- **A dark or far shot** (the mirror view): spec `plateFx: [{a, b, raw, crop: [x, y, w, h], eq}]` zooms into the subject from the
  RAW recording (sharp) and brightens it; put such a label high (y 250) so it does not cover the person.
- **The title card stays small** (about 600 px wide, big word <= 150 px) so it never dominates the frame.
- The Reel Fixer page saves its edits to the artifact database (`edits/state`): read them with `ArtifactData` and apply them
  with `patch_apply.py` (do not ask the user to re-send). Each of the user's saved edits is also a rule to learn: record it here.

## Anatomy stays small, sound over a paused comparison, floor symbols (the user's corrections after HPF 4)
- **Anatomy is ALWAYS a small card in one corner** over the blurred, dimmed footage (the split-squat pose card is the model).
  No black full-screen stage and no wide two-panel band: `hiprot` and `anatomy` (`mode: "band"`) now draw the small corner card
  (two muscles = two narrow figures side by side inside one small card).
- **Over the paused before/after comparison the voice is muted** (spec `mute: [[a, b]]` in source seconds; the coach's talk
  there was about something else, e.g. "no need to compare") and replaced by sound: a whoosh as it opens and a soft tick as each
  line is drawn.
- **"Ống đồng vuông góc với mặt đất":** highlight both shins with a yellow `glow` (tall ellipse, `rot` = the shin lean) and
  draw the right-angle symbol on the FLOOR under the feet: a white floor line, a short dashed plumb line up from each foot and a
  small square in the corner (`guide` lines, drawn one after another with `delay`). Measure on a snapshot of the built reel
  (the plate alternates 1.0 / 1.08 zoom per take).
- **A push or pull gets its arrow:** "đẩy mông ra sau" = a red dashed arrow from the hips pointing backwards.

## Endings (the user: "sao vid này cụt thế")
- **Never end a reel mid-flow.** End on the coach's closing line ("Ok, xong", "ngồi dậy", the last cue) and use up the remaining
  cues of the recording (repeated cues can go, new ones stay) up to 2 minutes. Check the last 10 s of the source before cutting.
- Cuts keep +0.4 s after the last word and never split a word.

## Title format (the user's latest, overrides the cream card)
- **Two `title` beats at the middle of the frame (y ~ 770, eye level), white Montserrat 900 uppercase on wine-red boxes (#7A1424):
  line 1 = the exercise name, line 2 = a short question / keyword from the video** ("DUMBBELL CHEST PRESS" / "SET UP THẾ NÀO?",
  "SPLIT SQUAT" / "TẬP TRUNG MÔNG"). Size fits the width (line 1 <= 96, line 2 <= 64). Keep line 2 short and true to the
  lesson; do not invent a tip the coach does not say. It shows over the hook and the first few seconds (no anatomy card in
  that window: text never sits on an anatomy scene).
- **One lesson stays ONE video** (do not split it into parts unless the user asks); the user also does not want shorter
  re-cuts of a lesson that is already a video (same content twice).

## Cuts, quiet client, fast-forward and bridges (the user's corrections on the Bulgarian split squat reels)
- **Always cut on whole sentences; a take ends AFTER the last word's tail.** whisper word ends come early and the take edge is
  capped by the next word: when a sentence is followed by "Ok," include that word too so the sentence is never clipped.
  Order the reel as the story goes (question -> answer -> instruction), never jump back into the middle of a sentence.
- **Keep the whole Q&A** ("đùi sau chân sau hay chân trước?", the client's answers): without those the viewer cannot follow.
- **The client talks quietly and whisper returns nothing for her**: re-transcribe the stretch with +18 dB gain
  (`volume=18dB,alimiter,dynaudnorm`), and REPLACE the base words in that stretch with the boosted ones (merge sorted).
  `AUTO(segs)` in the spec generator lifts every quiet spoken run to -15.5 LUFS (max +16 dB, loud runs untouched).
- **A repeated exercise the coach asks for ("làm cho em 5 cái") is fast-forwarded**: spec `holds` (frozen last frame after a
  take, `{"after": <source s>, "sec": s}`), `speedClips` (`{"name","a","b","factor"}` builds a sped-up clip of the plate) and a `broll`
  beat on `"hold@<source s>+0"` .. `"hold@<source s>+<sec>"` with a label "5 rep · tua nhanh x3".
- **Ending that leads to the next part**: end on the coach's last "rồi" and use `"outro": 2.6` with two title beats at
  `"outro+0.1"` / `"outro+0.25"`: "XEM TIẾP 👉" / "<what the next part fixes>". The outro is a frozen still of the last frame.
- **Cloud stickers over exposed skin were tried and dropped by the user**: do not add them again unless asked (`cloud` beat exists).
- Titles for the three Bulgarian split squat videos: line 1 always `BULGARIAN SPLIT SQUAT`; line 2 per video (the user picks).

## Small fixes without a full re-edit (Reel Fixer)
- Every finished HPF reel can get a **Reel Fixer page** (artifact): `ed/gen.py`-style data (beats with output times, a
  thumbnail per beat, caption lines) + a page where the user edits text, shifts / lengthens / removes a beat, moves a ring
  or glow by clicking the thumbnail, and rewrites wrong captions. It downloads `hpf_<reel>_patch.json`.
- `patch_apply.py <spec.json> <patch.json> [--render]` applies that patch to the spec (plain JSON, no LLM) and re-renders.
  Same rules: caption fixes go into `phrases`. A new reel needs its own data file (re-run the generator on its spec + mp4).
- The page plays a **clean low-res proxy** of the reel (same takes, zoom snaps, voice; no overlays) and redraws every beat
  live in HTML on top, with a draggable timeline and draggable rings. Build it with `fixer/prox.py` (proxy), `fixer/gen.py`
  (data + thumbnails), `fixer/page.html` (replace `__DATA__`), publish with the two proxies as `files`. The overlay look is an
  approximation (anatomy / hiprot / compare2 show a placeholder); the real look needs the re-render.
- CapCut cannot open this engine's output as an editable project (HTML/GSAP scenes, closed project format).

## Status
Builder: `hpf_reel.py spec.json` (same spec as founder-reels/make_reel.py) with the beats `label`, `guide`, `note`, `fault`,
`punch`, `anatomy`, `title` (references/reel-json.md). Done: HPF 1 and HPF 2 (split squat, from DJI 0373 / 0374 / 0375), HPF 3 (split squat, knee opening) and HPF 4 (Romanian deadlift).
