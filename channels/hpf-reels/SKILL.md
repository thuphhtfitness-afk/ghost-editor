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

## Content lines and story rules (read FORMATS.md)
HPF publishes three lines: **A. Thẩm định + Chương trình**, **B. Sửa lỗi (POV only)**, **C. Chương trình / combo**.
FORMATS.md has the beat sheet for each. Every reel: the hook is a question / pain / a person with numbers (not just the
exercise name), keep coach–client dialogue, end on a "Kết luận" verdict + a CTA (lưu / comment / follow).

## Status
Builder: `hpf_reel.py spec.json` (same spec as founder-reels/make_reel.py) with the beats `label`, `guide`, `note`, `fault`,
`punch`, `anatomy`, `title` (references/reel-json.md). Done: HPF 1 and HPF 2 (split squat, from DJI 0373 / 0374 / 0375).
