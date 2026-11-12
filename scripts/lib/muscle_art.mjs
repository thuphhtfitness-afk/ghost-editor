// Shaded "medical illustration" muscle figures, drawn procedurally (own artwork, no licence issues).
// A grey body with every muscle drawn as a lofted fibre bundle (curved striations between two edge lines), soft
// lighting and dark edges; the named groups are tinted orange-red with a glow and the view zooms to them.
//   muscleSvg({ view: "post" | "ant", highlight: ["glute", ...], id, w, h })
// post: erector (alias back), lat, glute_med, glute, hamstring, calf.   ant: core (abs + obliques), pec, quad.
const P = (a) => `${a[0].toFixed(1)},${a[1].toFixed(1)}`;
function smooth(pts, closed = true) {
  const n = pts.length, get = (i) => (closed ? pts[((i % n) + n) % n] : pts[Math.max(0, Math.min(n - 1, i))]);
  let d = `M${P(pts[0])}`;
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const p0 = get(i - 1), p1 = get(i), p2 = get(i + 1), p3 = get(i + 2);
    d += ` C${P([p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6])} ${P([p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6])} ${P(p2)}`;
  }
  return d + (closed ? " Z" : "");
}
function along(poly, s) {
  const L = [0];
  for (let i = 1; i < poly.length; i++) L.push(L[i - 1] + Math.hypot(poly[i][0] - poly[i - 1][0], poly[i][1] - poly[i - 1][1]));
  const t = Math.min(1, Math.max(0, s)) * L[L.length - 1]; let i = 1;
  while (i < L.length - 1 && L[i] < t) i++;
  const u = (t - L[i - 1]) / ((L[i] - L[i - 1]) || 1);
  return [poly[i - 1][0] + (poly[i][0] - poly[i - 1][0]) * u, poly[i - 1][1] + (poly[i][1] - poly[i - 1][1]) * u];
}
function fibres(a, b, n, shift = 0, bulge = 7) {
  let d = "";
  for (let i = 0; i <= n; i++) {
    const s = i / n, p = along(a, s), q = along(b, s + shift), dx = q[0] - p[0], dy = q[1] - p[1], L = Math.hypot(dx, dy) || 1;
    const k = bulge * Math.sin(i * 1.9 + 0.7), c = [(p[0] + q[0]) / 2 - (dy / L) * k, (p[1] + q[1]) / 2 + (dx / L) * k];
    d += `M${P(p)} Q${P(c)} ${P(q)} `;
  }
  return d;
}

// ---- posterior, left half (viewer's left); x = 300 is the spine ------------------------------------------------------
const POST = {
  body: [[300, 52], [205, 60], [142, 92], [128, 168], [150, 258], [186, 338], [168, 418], [140, 500], [132, 590], [142, 690], [150, 790], [160, 862], [168, 938], [176, 972], [254, 972], [258, 938], [262, 862], [268, 800], [280, 700], [292, 610], [300, 580]],
  trap: { o: [[300, 70], [250, 80], [196, 96], [210, 150], [268, 190], [300, 250]], a: [[300, 72], [300, 250]], b: [[196, 96], [210, 150], [268, 190]], n: 12 },
  lat: { o: [[254, 150], [190, 150], [146, 196], [152, 282], [196, 352], [252, 398], [266, 330], [256, 232]], a: [[252, 398], [266, 330], [256, 232], [254, 150]], b: [[196, 352], [152, 282], [146, 196], [190, 150]], n: 16 },
  erector: { o: [[298, 205], [262, 214], [250, 300], [254, 360], [268, 412], [298, 420]], a: [[298, 205], [298, 420]], b: [[262, 214], [250, 300], [254, 360], [268, 412]], n: 11, hotName: "erector" },
  glute_med: { o: [[262, 372], [236, 326], [188, 322], [150, 366], [146, 420], [162, 456], [196, 398], [244, 378]], a: [[262, 372], [236, 326], [188, 322], [150, 366], [146, 420]], b: [[244, 378], [196, 398], [162, 456]], n: 15 },
  glute: { o: [[298, 386], [244, 376], [192, 396], [160, 452], [164, 512], [206, 550], [258, 550], [298, 526]], a: [[298, 526], [298, 386], [244, 376], [192, 396]], b: [[258, 550], [206, 550], [164, 512], [160, 452]], n: 20 },
  bicep: { o: [[236, 556], [200, 562], [168, 640], [160, 740], [168, 796], [208, 782], [214, 690], [232, 606]], a: [[236, 556], [232, 606], [214, 690], [208, 782]], b: [[200, 562], [168, 640], [160, 740], [168, 796]], n: 14, hotName: "hamstring" },
  semi: { o: [[240, 556], [292, 566], [284, 650], [270, 742], [258, 796], [226, 790], [214, 700], [232, 608]], a: [[240, 556], [232, 608], [214, 700], [226, 790]], b: [[292, 566], [284, 650], [270, 742], [258, 796]], n: 14, hotName: "hamstring" },
  calf_l: { o: [[222, 806], [182, 814], [166, 858], [180, 906], [222, 944], [224, 880]], a: [[222, 808], [224, 880], [222, 942]], b: [[182, 814], [166, 858], [180, 906]], n: 12, hotName: "calf" },
  calf_m: { o: [[222, 806], [262, 806], [274, 852], [258, 908], [222, 944], [224, 880]], a: [[222, 808], [224, 880], [222, 942]], b: [[262, 806], [274, 852], [258, 908]], n: 12, hotName: "calf" },
};
// ---- anterior, left half ---------------------------------------------------------------------------------------------
const ANT = {
  body: [[300, 56], [196, 66], [128, 104], [120, 190], [152, 290], [184, 380], [176, 450], [136, 506], [138, 600], [146, 720], [152, 804], [160, 900], [170, 972], [252, 972], [258, 900], [264, 804], [274, 700], [290, 590], [300, 560]],
  pec: { o: [[298, 96], [236, 98], [176, 128], [168, 186], [214, 216], [298, 202]], a: [[298, 98], [298, 202]], b: [[176, 128], [168, 186], [214, 216]], n: 14, shift: 0.18 },
  oblique: { o: [[238, 228], [196, 236], [176, 300], [182, 398], [214, 468], [240, 470]], a: [[238, 228], [240, 470]], b: [[196, 236], [176, 300], [182, 398], [214, 468]], n: 14, shift: 0.22, hotName: "core" },
  abs: [0, 1, 2, 3].map((r) => { const y0 = 224 + r * 61, y1 = y0 + 54, xo = 246 + r * 2; return { o: [[xo, y0 + 6], [292, y0], [293, y1 - 4], [xo + 2, y1]], a: [[xo, y0 + 4], [xo + 2, y1]], b: [[292, y0], [293, y1]], n: 5, hotName: "core", bulge: 3 }; }),
  rf: { o: [[232, 526], [252, 548], [250, 700], [238, 792], [226, 702], [214, 548]], a: [[233, 536], [235, 700], [238, 786]], b: [[251, 552], [250, 700], [240, 784]], n: 13, shift: 0.12, hotName: "quad" },
  vl: { o: [[206, 540], [166, 584], [151, 680], [156, 762], [186, 792], [222, 788], [226, 702], [214, 548]], a: [[214, 548], [226, 702], [222, 788]], b: [[206, 540], [166, 584], [151, 680], [156, 762], [186, 792]], n: 16, shift: -0.1, hotName: "quad" },
  vm: { o: [[252, 604], [280, 588], [286, 644], [274, 742], [258, 794], [238, 792], [246, 700], [250, 644]], a: [[250, 610], [246, 700], [238, 790]], b: [[280, 590], [286, 644], [274, 742], [258, 794]], n: 12, shift: 0.1, hotName: "quad" },
  patella: { o: [[238, 800], [262, 806], [266, 836], [240, 848], [218, 832], [220, 808]], a: [[222, 810], [222, 840]], b: [[262, 808], [262, 838]], n: 4, bulge: 2 },
};
const ALIAS = { back: ["erector"], abs: ["core"], quads: ["quad"], hamstrings: ["hamstring"], glutes: ["glute"] };

export function muscleSvg({ view = "post", highlight = ["glute"], id = "mu", w = 600, h = 1000 } = {}) {
  const D = view === "ant" ? ANT : POST;
  const hot = new Set(highlight.flatMap((n) => [n, ...(ALIAS[n] || [])]));
  const all = Object.entries(D).filter(([k]) => k !== "body").flatMap(([k, v]) => (Array.isArray(v) ? v.map((m, i) => [`${k}${i}`, m, k]) : [[k, v, k]]));
  const isHot = (k, m) => hot.has(k) || (m.hotName && hot.has(m.hotName));
  let defs = "", body = "";
  all.forEach(([k, m], i) => { defs += `<clipPath id="${id}-c${i}"><path d="${smooth(m.o)}"/></clipPath>`; });
  const order = view === "ant" ? ["pec", "oblique", "abs", "vl", "vm", "rf", "patella"] : ["trap", "lat", "erector", "glute_med", "glute", "bicep", "semi", "calf_l", "calf_m"];
  order.forEach((key) => all.forEach(([k, m, base], i) => {
    if (base !== key) return;
    const on = isHot(k, m), cid = `${id}-c${i}`, n = m.n ?? 14, sh = m.shift ?? 0, bg = m.bulge ?? 7;
    body += `<g${on ? ` filter="url(#${id}-glow)"` : ""}><path d="${smooth(m.o)}" fill="url(#${id}-${on ? "hot" : "cold"})" stroke="${on ? "#8A220F" : "#5f5f5f"}" stroke-width="${on ? 3 : 2}" stroke-linejoin="round"/>
      <g clip-path="url(#${cid})" fill="none" stroke-linecap="round">
        <path d="${smooth(m.o)}" stroke="rgba(0,0,0,${on ? 0.4 : 0.3})" stroke-width="16"/>
        <path d="${fibres(m.a, m.b, n, sh, bg)}" stroke="${on ? "rgba(120,20,6,.55)" : "rgba(35,35,35,.34)"}" stroke-width="${on ? 2.4 : 1.9}"/>
        <path d="${fibres(m.a, m.b, n, sh, -bg)}" transform="translate(2,1.5)" stroke="${on ? "rgba(255,214,184,.34)" : "rgba(255,255,255,.26)"}" stroke-width="1.3"/>
        <path d="${smooth(m.o)}" fill="url(#${id}-sheen)" stroke="none"/></g></g>`;
  }));
  const half = `<g id="${id}-half"><path d="${smooth(D.body)}" fill="url(#${id}-skin)" stroke="#4f4f4f" stroke-width="3"/>${body}</g>`;
  // zoom to the highlighted muscles (+ margin), keeping the card's aspect ratio
  const pts = all.filter(([k, m]) => isHot(k, m)).flatMap(([, m]) => m.o);
  let vb = [0, 40, 600, 960];
  if (pts.length) {
    const xs = pts.flatMap((p) => [p[0], 600 - p[0]]), ys = pts.map((p) => p[1]);
    let x0 = Math.min(...xs) - 120, x1 = Math.max(...xs) + 120, y0 = Math.min(...ys) - 110, y1 = Math.max(...ys) + 110;
    const ar = w / h; let bw = x1 - x0, bh = y1 - y0;
    if (bw / bh < ar) { const nw = bh * ar; x0 -= (nw - bw) / 2; bw = nw; } else { const nh = bw / ar; y0 -= (nh - bh) / 2; bh = nh; }
    vb = [x0, y0, bw, bh];
  }
  return `<svg width="${w}" height="${h}" viewBox="${vb.map((v) => v.toFixed(1)).join(" ")}" preserveAspectRatio="xMidYMid slice">
  <defs>${defs}
    <linearGradient id="${id}-skin" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8a8a8a"/><stop offset=".6" stop-color="#c9c9c9"/><stop offset="1" stop-color="#b4b4b4"/></linearGradient>
    <linearGradient id="${id}-cold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d6d6d6"/><stop offset="1" stop-color="#8d8d8d"/></linearGradient>
    <linearGradient id="${id}-hot" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF8C5A"/><stop offset=".55" stop-color="#E4522C"/><stop offset="1" stop-color="#B02C14"/></linearGradient>
    <radialGradient id="${id}-sheen" cx=".32" cy=".28" r=".7"><stop offset="0" stop-color="#fff" stop-opacity=".42"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <filter id="${id}-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur in="SourceAlpha" stdDeviation="7" result="b"/><feFlood flood-color="#FF6A3C" flood-opacity=".75"/><feComposite in2="b" operator="in" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  ${half}<use href="#${id}-half" transform="translate(600,0) scale(-1,1)"/>
</svg>`;
}
