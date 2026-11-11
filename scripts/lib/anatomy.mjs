// Self-drawn posterior lower-body anatomy (no licensed artwork): pelvis, femurs, tibiae, gluteus maximus / medius,
// hamstrings and calves. A muscle group in `highlight` glows bright red with a yellow halo; the rest stays dim, the
// HPF anatomy-scene look (black stage, red floor glow). Coordinates: viewBox 0 0 600 1000, the figure faces away.
const BONE = "#EADFC4", BONE_EDGE = "#B9AA86";
const mirror = (d) => d.replace(/(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)/g, (_, x, y) => `${600 - parseFloat(x)},${y}`);

// one side (the viewer's left = the body's left leg seen from behind); the other side is mirrored
const SHAPES = {
  bone: [
    // femur shaft, knee condyles, tibia
    { d: "M206,330 C214,450 222,600 236,742 L262,742 C252,600 246,450 238,330 Z" },
    { d: "M222,736 C214,752 216,780 236,786 C250,790 268,784 272,768 C276,752 266,738 252,736 Z" },
    { d: "M236,790 C238,860 240,930 242,990 L262,990 C262,930 262,860 264,790 Z" },
  ],
  pelvis: "M300,170 C250,150 175,160 150,215 C138,245 150,290 182,312 C200,324 222,330 238,346 C252,360 262,384 286,392 L314,392 C338,384 348,360 362,346 C378,330 400,324 418,312 C450,290 462,245 450,215 C425,160 350,150 300,170 Z",
  sacrum: "M276,214 C276,250 282,300 300,340 C318,300 324,250 324,214 C316,204 284,204 276,214 Z",
  glute_med: { d: "M160,222 C176,198 232,194 262,214 C270,236 262,262 244,272 C214,280 178,270 160,250 Z", fiber: ["M176,226 L236,262", "M196,214 L250,252"] },
  glute: { d: "M150,262 C150,232 196,236 236,246 C276,258 300,286 300,330 C300,376 286,414 252,430 C214,446 172,430 156,396 C142,366 146,300 150,262 Z",
    fiber: ["M166,282 L282,360", "M160,320 L270,398", "M174,262 L292,320", "M168,360 L240,420"] },
  hamstring: { d: "M236,410 C256,404 286,410 292,430 C296,520 288,630 276,722 C268,744 250,748 240,734 C226,640 216,540 222,450 Z",
    fiber: ["M262,440 L258,710", "M244,450 L250,690", "M280,452 L272,700"] },
  hamstring_lat: { d: "M198,420 C214,410 232,414 234,440 C236,540 238,640 236,730 C226,748 210,744 206,726 C196,630 188,520 190,458 Z",
    fiber: ["M214,446 L222,712", "M202,470 L210,700"] },
  calf: { d: "M226,800 C214,830 212,880 226,920 C236,944 262,946 274,920 C288,880 286,830 274,800 C262,786 238,786 226,800 Z",
    fiber: ["M250,806 L250,930"] },
};
const GROUPS = { glute: ["glute"], glute_med: ["glute_med"], hamstring: ["hamstring", "hamstring_lat"], calf: ["calf"] };

export function anatomySvg({ highlight = ["glute"], side = "both", id = "anat", w = 600, h = 1000 } = {}) {
  const hot = new Set(highlight.flatMap((g) => GROUPS[g] || [g]));
  const sides = side === "both" ? ["L", "R"] : [side];
  const muscle = (name, s) => {
    const m = SHAPES[name], on = hot.has(name) && sides.includes(s);
    const d = s === "R" ? mirror(m.d) : m.d;
    const fib = (m.fiber || []).map((f) => `<path d="${s === "R" ? mirror(f) : f}" stroke="${on ? "#FF9A84" : "#8E4A3C"}" stroke-width="2.4" opacity=".55" fill="none"/>`).join("");
    return `<g class="${on ? "hot" : "dim"}"${on ? ` filter="url(#${id}-glow)"` : ""}><path d="${d}" fill="${on ? `url(#${id}-hot)` : "#5E2620"}" stroke="${on ? "#FFE15A" : "#3A1712"}" stroke-width="${on ? 5 : 2}" opacity="${on ? 1 : 0.85}"/>${fib}</g>`;
  };
  const bones = ["L", "R"].map((s) => SHAPES.bone.map((b) => `<path d="${s === "R" ? mirror(b.d) : b.d}" fill="${BONE}" stroke="${BONE_EDGE}" stroke-width="2"/>`).join("")).join("");
  const order = ["calf", "hamstring_lat", "hamstring", "glute_med", "glute"];
  return `<svg width="${w}" height="${h}" viewBox="0 0 600 1000">
  <defs>
    <linearGradient id="${id}-hot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF5A3C"/><stop offset="1" stop-color="#C2261A"/></linearGradient>
    <filter id="${id}-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur in="SourceAlpha" stdDeviation="9" result="b"/><feFlood flood-color="#FFD21E" flood-opacity=".95"/><feComposite in2="b" operator="in" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  ${bones}
  <path d="${SHAPES.pelvis}" fill="${BONE}" stroke="${BONE_EDGE}" stroke-width="3"/>
  <path d="${SHAPES.sacrum}" fill="#D9CCAA" stroke="${BONE_EDGE}" stroke-width="2"/>
  ${["L", "R"].map((s) => order.map((n) => muscle(n, s)).join("")).join("")}
</svg>`;
}

// ---- the exercise in motion: a side-view split squat (the client faces right, front leg on the right) -------------
// Joints per pose in a 800x1000 box; muscles are drawn along the limbs; `highlight` names the working groups
// (glute, quad, hamstring, calf, core, back_quad) of the FRONT leg unless prefixed back_. Marks show what the coach
// says: weight onto the front foot, the back knee going down, the torso leaning slightly forward, the drive up.
export const SPLIT_POSES = {
  bottom: { head: [492, 250], neck: [478, 312], sh: [470, 340], hip: [420, 640], fk: [598, 700], fa: [566, 896], ft: [650, 930], fh: [540, 932],
            bk: [336, 884], ba: [178, 892], bt: [126, 930], hand: [486, 640] },
  top:    { head: [470, 150], neck: [462, 212], sh: [458, 240], hip: [430, 540], fk: [560, 700], fa: [566, 896], ft: [650, 930], fh: [540, 932],
            bk: [318, 720], ba: [190, 880], bt: [130, 930], hand: [470, 540] },
};
const P = (a) => `${a[0].toFixed(1)},${a[1].toFixed(1)}`;
const lerp = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
const norm = (a, b) => { const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy) || 1; return [-dy / L, dx / L]; };
// a muscle belly along a->b on one side (s = +1 / -1), thickest in the middle
function belly(a, b, s, thick, t0 = 0.08, t1 = 0.92) {
  const n = norm(a, b), pts = [];
  for (let i = 0; i <= 10; i++) { const t = t0 + (t1 - t0) * (i / 10), p = lerp(a, b, t), k = Math.sin(Math.PI * (i / 10)); pts.push([p[0] + n[0] * s * thick * k, p[1] + n[1] * s * thick * k]); }
  const base = []; for (let i = 10; i >= 0; i--) { const t = t0 + (t1 - t0) * (i / 10), p = lerp(a, b, t); base.push([p[0] + n[0] * s * 6, p[1] + n[1] * s * 6]); }
  return "M" + [...pts, ...base].map(P).join(" L") + " Z";
}
export function splitSquatSvg({ pose = "bottom", highlight = ["glute", "quad"], marks = [], id = "ss", w = 800, h = 1000 } = {}) {
  const J = SPLIT_POSES[pose] || SPLIT_POSES.bottom, hot = new Set(highlight);
  const limb = (a, b, wd) => `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#5C3E36" stroke-width="${wd}" stroke-linecap="round"/>`;
  const bone = (a, b) => `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#EADFC4" stroke-width="9" stroke-linecap="round" opacity=".9"/>`;
  const M = (name, d) => { const on = hot.has(name);
    return `<path d="${d}" fill="${on ? `url(#${id}-hot)` : "#6A2A22"}" stroke="${on ? "#FFE15A" : "#2A120E"}" stroke-width="${on ? 4 : 1.5}"${on ? ` filter="url(#${id}-glow)"` : ""} opacity="${on ? 1 : .9}"/>`; };
  // the leg shapes: silhouette first, then bones, then muscles (front leg in front of the back leg)
  const sil = [limb(J.hip, J.bk, 104), limb(J.bk, J.ba, 66), limb(J.ba, J.bt, 40), limb(J.sh, J.hip, 168), limb(J.hip, J.fk, 120), limb(J.fk, J.fa, 72), limb(J.fh, J.ft, 40), limb(J.sh, J.hand, 46), limb(J.neck, J.head, 56)].join("");
  const bones = [bone(J.hip, J.bk), bone(J.bk, J.ba), bone(J.hip, J.fk), bone(J.fk, J.fa), bone(J.sh, J.hip)].join("");
  const s = Math.sign((J.fk[0] - J.hip[0]) || 1);
  const muscles = [
    M("back_quad", belly(J.hip, J.bk, -1, 48)), M("back_hamstring", belly(J.hip, J.bk, 1, 36)),
    M("core", belly(J.sh, J.hip, -s, 54, 0.3, 0.95)), M("back", belly(J.sh, J.hip, s, 52, 0.05, 0.85)),
    M("glute", `M${P([J.hip[0] - 80, J.hip[1] - 60])} C${P([J.hip[0] - 140, J.hip[1] + 4])} ${P([J.hip[0] - 96, J.hip[1] + 116])} ${P([J.hip[0] - 4, J.hip[1] + 84])} C${P([J.hip[0] + 26, J.hip[1] + 40])} ${P([J.hip[0] + 6, J.hip[1] - 44])} ${P([J.hip[0] - 80, J.hip[1] - 60])} Z`),
    M("hamstring", belly(J.hip, J.fk, s, 48, 0.18, 0.92)), M("quad", belly(J.hip, J.fk, -s, 62, 0.08, 0.95)),
    M("calf", belly(J.fk, J.fa, s, 40, 0.1, 0.7)),
  ].join("");
  const MARK = {
    weight: (m) => { const f = lerp(J.fh, J.ft, 0.35); return `<g><line x1="${f[0]}" y1="${f[1] - 330}" x2="${f[0]}" y2="${f[1] - 40}" stroke="#FFD21E" stroke-width="12" stroke-linecap="round"/><path d="M${f[0] - 30} ${f[1] - 70} L${f[0]} ${f[1] - 20} L${f[0] + 30} ${f[1] - 70} Z" fill="#FFD21E"/><ellipse cx="${f[0]}" cy="${f[1] + 6}" rx="70" ry="14" fill="#FFD21E" opacity=".55"/></g>`; },
    kneeDown: () => `<g><line x1="${J.bk[0]}" y1="${J.bk[1] - 200}" x2="${J.bk[0]}" y2="${J.bk[1] - 40}" stroke="#FFD21E" stroke-width="12" stroke-dasharray="26 14" stroke-linecap="round"/><path d="M${J.bk[0] - 28} ${J.bk[1] - 66} L${J.bk[0]} ${J.bk[1] - 20} L${J.bk[0] + 28} ${J.bk[1] - 66} Z" fill="#FFD21E"/></g>`,
    lean: () => { const top = [J.hip[0] + (J.sh[0] - J.hip[0]) * 1.25, J.hip[1] + (J.sh[1] - J.hip[1]) * 1.25]; return `<line x1="${J.hip[0]}" y1="${J.hip[1]}" x2="${top[0]}" y2="${top[1]}" stroke="#FFD21E" stroke-width="8" stroke-dasharray="22 14"/><line x1="${J.hip[0]}" y1="${J.hip[1]}" x2="${J.hip[0]}" y2="${J.hip[1] - 400}" stroke="#FFFFFF" stroke-width="5" stroke-dasharray="14 12" opacity=".7"/>`; },
    drive: () => `<g><line x1="${J.fa[0] + 120}" y1="${J.fa[1] - 20}" x2="${J.fa[0] + 120}" y2="${J.fa[1] - 330}" stroke="#35E06B" stroke-width="12" stroke-linecap="round"/><path d="M${J.fa[0] + 92} ${J.fa[1] - 296} L${J.fa[0] + 120} ${J.fa[1] - 344} L${J.fa[0] + 148} ${J.fa[1] - 296} Z" fill="#35E06B"/></g>`,
    leanBackBad: () => `<g><path d="M${J.sh[0]} ${J.sh[1]} Q ${J.sh[0] - 160} ${J.sh[1] - 40} ${J.sh[0] - 210} ${J.sh[1] + 70}" stroke="#FF3B2F" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M${J.sh[0] - 236} ${J.sh[1] + 40} L${J.sh[0] - 210} ${J.sh[1] + 90} L${J.sh[0] - 176} ${J.sh[1] + 52} Z" fill="#FF3B2F"/></g>`,
  };
  const markSvg = marks.map((m, k) => `<g id="${id}-m${k}">${(MARK[m.kind || m] || (() => ""))(m)}</g>`).join("");
  return `<svg width="${w}" height="${h}" viewBox="0 0 800 1000">
  <defs>
    <linearGradient id="${id}-hot" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF5A3C"/><stop offset="1" stop-color="#C2261A"/></linearGradient>
    <filter id="${id}-glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur in="SourceAlpha" stdDeviation="9" result="b"/><feFlood flood-color="#FFD21E" flood-opacity=".95"/><feComposite in2="b" operator="in" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <ellipse cx="400" cy="935" rx="360" ry="16" fill="#000" opacity=".5"/>
  ${sil}${bones}${muscles}
  <circle cx="${J.head[0]}" cy="${J.head[1]}" r="62" fill="#5C3E36"/>
  ${markSvg}
</svg>`;
}
