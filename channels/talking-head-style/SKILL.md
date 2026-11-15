---
name: talking-head-style
description: "Edit style for talking-head videos (one person talking to camera or being interviewed): large keyword overlays on the spoken word, tiny word captions, sticker accents and b-roll / screen-recording insets, learned from the user's reference 'in the edit ep.1' video. Use when the user hands over a talking-head / interview / podcast-style recording and wants this look, wants b-roll slots, or wants a rough cut to approve before the final render. Combine with the channel skill's own rules (hpf-reels, founder-reels): their privacy, naming and music rules still apply."
---

# talking-head-style

Learned from the user's reference (171 s, English, a creator talking about editing). Not a template to copy: the rules below
are what makes it look like that.

## The look (reference analysis)
- **One shot, almost no cuts.** The person stays centred; the edit is carried by text and inserts, not by camera moves.
- **Key-word overlays, not subtitles.** 1-3 words pop on the exact spoken word, one at a time, big (about 150-260 px tall in
  a 1280 px frame), sitting on the TORSO / lower-middle of the frame (never on the face), alternating left / centre / right.
  Each stays 0.6-1.5 s. Words are the point of the sentence ("QUESTION", "MY", "easiest", "#1", "MORE", "NOT A PROFESSIONAL"),
  never a paraphrase.
- **Three type voices, mixed inside one video (2-3 fonts max):**
  1. bold CONDENSED uppercase, cream / white, slight shadow ("QUESTION", "MORE", "STICK TO EM");
  2. elegant high-contrast SERIF italic, lower case, cream-yellow ("easiest", "#1", "reveal", "in the");
  3. small clean sans for asides ("on-screen text", "sound effects"), sometimes on a cream marker box with two round handles
     ("edit style", like a selected text box).
  Colours: cream #F6EBC8 / white, a soft gradient or glow on some, a warm gold on the stacked numbers ("2-3 FONTS").
- **Tiny word-by-word captions** at the bottom centre (one or two words, small, white), only as a reading aid.
- **Accents:** sparkle stars (✦) next to a title, a tiny emoji at the end of a word (🥺 🧰), a hand-drawn white arrow pointing at the
  face or object, an object icon as sticker (camera, app logo) that pops with the word, a title card ("in the | ep.1 - the basics")
  at the start.
- **Inserts (b-roll):** screen recordings as a phone-frame inset in the middle (about 75 % of the width, dark rounded frame) over
  the speaker for 1-5 s, lists / UI shown as stacked text cut-ins; the voice never stops. A hard cut in, a hard cut out.
- Sign-off in handwriting at the end.

## How to build it here (engine = ghost-editor + hpf_reel.py / make_reel.py)
- Keyword overlay = a `title` beat, one word / short phrase at the spoken word's time (`words: [{text, at}]` or `text`, `at`, `to`):
  - condensed voice: `font: "Montserrat"`, `weight: 900`, uppercase, `tracking: "-4px"`, size 150-230 (Oswald has no Vietnamese
    diacritics: do not use it for Vietnamese);
  - serif voice: `font: "Playfair Display"`, `italic: true`, `case: "none"`, colour #F6EBC8, size 130-190;
  - small voice: `font: "Inter"`, weight 600, size 54-64, optional `bg` cream box;
  - `y` about 1050-1350 (torso zone; check the face on a snapshot), `x`/`align` to alternate left / centre / right, `anim: "pop"`.
- Tiny captions: `captions.style "mini"`, size 40, `group` 1-2 at y 1560-1620 (the HPF default 1380 is too high for this look).
- Insets: `broll` beat (`mode` full) for a clip, or a phone-frame inset (to build: dark rounded rect + the clip inside) over the speaker.
- Stickers: `emoji` beat or a PNG with alpha; sparkles = small ✦ text next to the title.
- Voice: keep the speaker's audio under every insert; quiet voices are lifted (`boost`), music bed acoustic / soft at -18 dB.

## Flow with the user (saves tokens: ONE render)
1. Transcribe (boosted gain for a quiet voice), transcript export to the user when asked.
2. Plan the cuts, keywords and b-roll SLOTS (time range + what the shot should show).
3. Publish a REVIEW artifact: low-res proxy of the rough cut, keyword overlays drawn live, empty b-roll slots with their
   description and an upload button, an approve button and a comment box per video; edits are stored in the page database.
4. The user edits, uploads the b-roll and approves; read the saved state with ArtifactData (no re-explaining).
5. Render the final video once from the approved state.
Never render the final before the user approved the rough cut when b-roll is still to come.

## Rules that still apply from the channel
- founder-reels: privacy crop, names beeped, profanity cut. hpf-reels: wine-red label boxes for TRAINING cues, Montserrat,
  acoustic music (never lo-fi-02), whole-sentence cuts, quiet client boosted, no cloud stickers.
- Interviews: cut the interviewer's voice (questions become a keyword / label), keep only the speaker.
