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
