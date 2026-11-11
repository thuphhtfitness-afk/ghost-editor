---
name: hpf-reels
description: "Edit HPF (the gym's training channel) workout and form-correction videos: a coach cueing a client through an exercise (split squat, RDL, deadlift ...), filmed handheld in the gym, Vietnamese voice. Use when the user sends a training / exercise tutorial / form-fix recording and asks to edit it, 'like the HPF references', or for HPF captions. Max 90 s per video. Not for the founder's interviews (that is founder-reels)."
---

# hpf-reels

The gym's training channel. One coaching session -> one tutorial reel of at most **90 s** (at least 30 s), built on the
`ghost-editor` engine. This skill has its OWN taste file (`taste.json` here): record the user's corrections with
`GHOST_TASTE=<this dir>/taste.json python3 ~/.claude/skills/ghost-editor/scripts/taste.py add "..."`.

## The look (from the user's two references, a ProLifting RDL fix and a deadlift setup)
- **Story:** the wrong way first (or the client's first attempt), then each cue in order, then the corrected rep.
  Cut setup chatter, repeated cues and counting; keep the cue words and the reps that show them.
- **Cue labels:** small orange rounded boxes (bg #F07A1A, white or black bold Inter, ~34 px), top third, one at a time,
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

## Status
The reference analysis is done; the HPF builder (labels, guides, B&W fault replay, punch-ins) is being added to the
engine. Until it lands, edits use ghost-editor beats (quote/compare cards, broll, zoom) as the closest match.
