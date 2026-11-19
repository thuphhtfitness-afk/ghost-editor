// shared drawing kit for the HPF anatomy sheets (muscle fibres, bands, bones, cards, labels)
const cv = document.getElementById("c"), X = cv.getContext("2d");
const CW = 1060, CH = 640;
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const C = { ink: "#1d3557", red: "#dc2d37", green: "#28a050", cream: "#f6eaaa", grey: "#7a7e84" };

// ---------- primitives ----------
let TENS = 0.18;
function shape(pts, closed = true) {          // smooth closed path through points (Catmull-Rom -> Bezier)
  const p = new Path2D(), n = pts.length;
  p.moveTo(pts[0][0], pts[0][1]);
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    const t = TENS;
    p.bezierCurveTo(p1[0] + (p2[0] - p0[0]) * t, p1[1] + (p2[1] - p0[1]) * t,
                    p2[0] - (p3[0] - p1[0]) * t, p2[1] - (p3[1] - p1[1]) * t, p2[0], p2[1]);
  }
  if (closed) p.closePath();
  return p;
}
const lerp = (a, b, u) => [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u];

// muscle: outline + fibres running from an origin edge to an insertion edge, bowed, clipped to the outline
function muscle(pts, o0, o1, i0, i1, opt = {}) {
  const p = shape(pts), n = opt.n || 60, bow = opt.bow || 0;
  const g = X.createLinearGradient(o0[0], o0[1], i1[0], i1[1]);
  g.addColorStop(0, opt.c0 || "#d9564a"); g.addColorStop(0.55, opt.c1 || "#b8322c"); g.addColorStop(1, opt.c2 || "#8c1d1f");
  const hot = opt.hot && window.HOT !== false;
  if (hot && window.HOT === true) { g.addColorStop(0, "#ff7a5c"); }
  X.save();
  if (hot) { X.shadowColor = window.HOT === true ? "rgba(255,60,40,1)" : "rgba(255,40,40,.95)"; X.shadowBlur = window.HOT === true ? 46 : 34; X.shadowOffsetY = 0; }
  else { X.shadowColor = "rgba(60,0,0,.35)"; X.shadowBlur = 10; X.shadowOffsetY = 4; }
  X.fillStyle = g; X.fill(p); X.restore();
  X.save(); X.clip(p);
  for (let k = 0; k <= n; k++) {
    const u = k / n, a = lerp(o0, o1, u), b = lerp(i0, i1, u);
    const m = lerp(a, b, 0.5), dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy) || 1;
    const bw = bow * (1 - Math.pow(2 * u - 1, 2)) + (rnd() - .5) * 4;
    const cx = m[0] - dy / L * bw, cy = m[1] + dx / L * bw;
    X.beginPath(); X.moveTo(a[0], a[1]); X.quadraticCurveTo(cx, cy, b[0], b[1]);
    X.strokeStyle = k % 2 ? "rgba(255,205,195,.42)" : "rgba(95,10,12,.30)";
    X.lineWidth = k % 2 ? 1.3 : 1.0; X.stroke();
  }
  // rim light + edge shade
  const r = X.createRadialGradient((o0[0] + i1[0]) / 2 - 10, (o0[1] + i1[1]) / 2 - 10, 5, (o0[0] + i1[0]) / 2, (o0[1] + i1[1]) / 2, 160);
  r.addColorStop(0, "rgba(255,230,220,.22)"); r.addColorStop(1, "rgba(60,0,0,.28)");
  X.fillStyle = r; X.fill(p); X.restore();
  X.lineWidth = 2; X.strokeStyle = "rgba(90,15,15,.75)"; X.stroke(p);
  return p;
}
// tendon / ligament: silver-white fibrous band (or red when highlighted)
function band(pts, o0, o1, i0, i1, opt = {}) {
  const p = shape(pts), n = opt.n || 26, hot = opt.hot && window.HOT !== false;
  X.save(); if (hot) { X.shadowColor = "rgba(220,45,55,.85)"; X.shadowBlur = 26; }
  const g = X.createLinearGradient(o0[0], o0[1], i1[0], i1[1]);
  if (hot) { g.addColorStop(0, "#ff7b7b"); g.addColorStop(1, "#d42a33"); }
  else { g.addColorStop(0, "#fbfaf6"); g.addColorStop(1, "#d8d9dc"); }
  X.fillStyle = g; X.fill(p); X.restore();
  X.save(); X.clip(p);
  for (let k = 0; k <= n; k++) {
    const u = k / n, a = lerp(o0, o1, u), b = lerp(i0, i1, u);
    X.beginPath(); X.moveTo(a[0], a[1]); X.lineTo(b[0] + (rnd() - .5) * 2, b[1]);
    X.strokeStyle = hot ? (k % 2 ? "rgba(255,220,220,.6)" : "rgba(120,0,10,.35)") : (k % 2 ? "rgba(255,255,255,.9)" : "rgba(130,135,145,.45)");
    X.lineWidth = 1.1; X.stroke();
  }
  X.restore();
  X.lineWidth = 1.6; X.strokeStyle = hot ? "rgba(140,10,20,.9)" : "rgba(120,124,132,.8)"; X.stroke(p);
  return p;
}
function bone(pts, opt = {}) {
  const T0 = TENS; TENS = 0.1; const p = shape(pts); TENS = T0;
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; pts.forEach(q => { x0 = Math.min(x0, q[0]); y0 = Math.min(y0, q[1]); x1 = Math.max(x1, q[0]); y1 = Math.max(y1, q[1]); });
  const g = X.createLinearGradient(x0, y0, x1, y1);
  g.addColorStop(0, "#fbf4e4"); g.addColorStop(0.6, "#ecdcbd"); g.addColorStop(1, "#cdb48b");
  X.save(); X.shadowColor = "rgba(70,50,20,.35)"; X.shadowBlur = 8; X.shadowOffsetY = 3;
  X.fillStyle = opt.alpha ? `rgba(240,228,205,${opt.alpha})` : g; X.fill(p); X.restore();
  if (!opt.alpha) {                       // light cortical hatching
    X.save(); X.clip(p); X.strokeStyle = "rgba(150,120,80,.18)"; X.lineWidth = 1;
    for (let k = 0; k < 18; k++) { const yy = y0 + (y1 - y0) * k / 18; X.beginPath(); X.moveTo(x0, yy); X.lineTo(x1, yy + (x1 - x0) * .25); X.stroke(); }
    X.restore();
  }
  X.lineWidth = 2; X.strokeStyle = opt.alpha ? "rgba(140,115,80,.6)" : "#9c8460"; X.stroke(p);
  return p;
}
function cartilage(pts) { const p = shape(pts); X.fillStyle = "#cfe3ec"; X.fill(p); X.lineWidth = 1.5; X.strokeStyle = "#7fa2b3"; X.stroke(p); }
function skin(pts) { const p = shape(pts); X.fillStyle = "rgba(240,196,170,.35)"; X.fill(p); X.lineWidth = 2; X.strokeStyle = "rgba(190,130,105,.55)"; X.stroke(p); }
function arrow(x0, y0, x1, y1, col, w = 7) {
  X.strokeStyle = col; X.fillStyle = col; X.lineWidth = w; X.lineCap = "round";
  X.beginPath(); X.moveTo(x0, y0); X.lineTo(x1, y1); X.stroke();
  const a = Math.atan2(y1 - y0, x1 - x0);
  X.beginPath(); X.moveTo(x1 + Math.cos(a) * 6, y1 + Math.sin(a) * 6);
  X.lineTo(x1 - Math.cos(a - .5) * 26, y1 - Math.sin(a - .5) * 26); X.lineTo(x1 - Math.cos(a + .5) * 26, y1 - Math.sin(a + .5) * 26); X.fill();
}
function hand(txt, x, y, col, size = 52, align = "center") { X.font = `700 ${Math.round(size * 0.78)}px Mont`; X.fillStyle = col; X.textAlign = align; X.textBaseline = "middle"; X.fillText(txt, x, y); }
function tick(x, y, ok) {
  X.fillStyle = ok ? C.green : C.red; X.beginPath(); X.arc(x, y, 24, 0, 7); X.fill();
  X.strokeStyle = "#fff"; X.lineWidth = 6; X.lineCap = "round"; X.beginPath();
  if (ok) { X.moveTo(x - 11, y + 1); X.lineTo(x - 3, y + 10); X.lineTo(x + 12, y - 9); }
  else { X.moveTo(x - 9, y - 9); X.lineTo(x + 9, y + 9); X.moveTo(x + 9, y - 9); X.lineTo(x - 9, y + 9); }
  X.stroke();
}
function labelTick(txt, x, y, col, ok, size = 48) { X.font = `700 ${Math.round(size * 0.78)}px Mont`; const w = X.measureText(txt).width; hand(txt, x, y, col, size); tick(x - w / 2 - 34, y + 2, ok); }
function card(ox, oy, kicker) {
  X.save(); X.translate(ox, oy);
  X.save(); X.shadowColor = "rgba(0,0,0,.35)"; X.shadowBlur = 24; X.shadowOffsetY = 12;
  X.fillStyle = "#fcfcfa"; X.beginPath(); X.roundRect(30, 30, 1000, 580, 30); X.fill(); X.restore();
  X.strokeStyle = "#d4d6da"; X.lineWidth = 4; X.beginPath(); X.roundRect(30, 30, 1000, 580, 30); X.stroke();
  X.font = "800 28px Mont"; const w = X.measureText(kicker).width;
  X.fillStyle = C.cream; X.beginPath(); X.roundRect(60, 54, w + 36, 50, 8); X.fill();
  X.font = "800 28px Mont"; X.fillStyle = "#1c1814"; X.textAlign = "left"; X.textBaseline = "middle"; X.fillText(kicker, 78, 80);
  X.font = "19px Cred"; X.fillStyle = C.grey; X.textAlign = "right"; X.fillText("minh hoạ: HPF", 1004, 590);
}
const end = () => X.restore();

