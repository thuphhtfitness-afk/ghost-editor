// high-heels figures (calf in a heel, seated hip flexor, pelvis tilt, lordosis, shoe icon); needs prims.js
// ---- lower leg + foot in a high heel, lateral view; tight calf glows ----
function calfHeel(ox, oy, s) {
  X.save(); X.translate(ox, oy); X.scale(s, s);
  skin([[-40, -10], [40, -10], [96, 90], [92, 200], [52, 300], [56, 345], [20, 372], [-120, 430], [-210, 446], [-214, 430], [-40, 330], [-30, 200], [-46, 60]]);
  bone([[-30, -20], [6, -20], [8, 312], [-10, 330], [-26, 312]]);                        // tibia
  bone([[14, 10], [26, 12], [24, 300], [14, 300]]);                                        // fibula
  muscle([[20, 0], [80, 60], [96, 140], [74, 230], [40, 270], [22, 200], [14, 70]], [20, 0], [80, 60], [30, 268], [44, 262], { n: 46, bow: 14, hot: true }); // gastrocnemius
  muscle([[22, 150], [60, 170], [64, 260], [42, 300], [24, 280]], [22, 150], [60, 170], [30, 296], [42, 300], { n: 20, bow: 6, c0: "#c44a42" });             // soleus
  band([[30, 262], [48, 262], [44, 340], [30, 342]], [30, 262], [48, 262], [30, 342], [44, 340], { n: 12 });                                                    // Achilles
  bone([[16, 330], [52, 330], [60, 362], [30, 378], [10, 360]]);                           // calcaneus (raised)
  bone([[-14, 322], [16, 330], [12, 362], [-30, 356]]);                                    // talus
  bone([[-30, 352], [12, 360], [-150, 432], [-176, 430], [-160, 414]]);                    // metatarsals (steep)
  bone([[-176, 428], [-214, 436], [-212, 446], [-176, 444]]);                              // toes
  // the shoe
  X.fillStyle = "#1f1f24"; X.beginPath(); X.moveTo(64, 352); X.lineTo(74, 360); X.lineTo(66, 470); X.lineTo(56, 470); X.lineTo(52, 372); X.closePath(); X.fill();  // stiletto
  X.strokeStyle = "#1f1f24"; X.lineWidth = 12; X.lineCap = "round"; X.beginPath(); X.moveTo(60, 372); X.quadraticCurveTo(-40, 402, -200, 454); X.stroke();          // sole
  X.lineWidth = 6; X.beginPath(); X.moveTo(-160, 424); X.quadraticCurveTo(-200, 418, -222, 444); X.stroke();
  X.strokeStyle = "rgba(160,160,160,.9)"; X.lineWidth = 5; X.beginPath(); X.moveTo(-260, 472); X.lineTo(140, 472); X.stroke();
  X.restore();
}
// ---- seated: lumbar spine, pelvis, femur forward; iliopsoas glows ----
function vertebra(x, y, a, w = 46, h = 30) {
  X.save(); X.translate(x, y); X.rotate(a);
  bone([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2 + 2, h / 2], [-w / 2 - 2, h / 2]]);
  bone([[w / 2 - 2, -h / 4], [w / 2 + 30, -h / 2], [w / 2 + 34, h / 4], [w / 2, h / 4]]); // spinous process (back = +x)
  X.restore();
}
function spine(x0, y0, curve, n = 5, step = 38, lean = 0) {    // returns the points of the vertebral bodies
  const pts = [];
  for (let i = 0; i < n; i++) {
    const u = i / (n - 1), x = x0 - curve * Math.sin(Math.PI * u) + lean * u, y = y0 + i * step;
    pts.push([x, y]);
  }
  pts.forEach((p, i) => vertebra(p[0], p[1], (i === 0 ? 0 : Math.atan2(p[0] - pts[i - 1][0], step)) * -1));
  return pts;
}
function pelvis(x, y, a, s = 1) {          // side view: ilium wing, sacrum, ischium; a = tilt (forward = negative)
  X.save(); X.translate(x, y); X.rotate(a); X.scale(s, s);
  bone([[-70, -40], [-20, -76], [50, -70], [86, -30], [70, 10], [40, 30], [10, 90], [-20, 100], [-34, 60], [-60, 20]]);   // ilium + ischium
  bone([[40, -60], [80, -50], [92, 10], [70, 60], [50, 40]]);                                                          // sacrum
  X.fillStyle = "#cdb48b"; X.beginPath(); X.arc(-6, 40, 16, 0, 7); X.fill();                                          // acetabulum
  X.restore();
}
function seatedHip(ox, oy, s) {
  X.save(); X.translate(ox, oy); X.scale(s, s);
  skin([[60, -40], [130, -40], [150, 140], [150, 250], [100, 300], [-260, 300], [-280, 236], [-40, 200], [-10, 100], [20, -40]]);
  const sp = spine(80, -10, 6, 5, 38);
  pelvis(70, 210, 0.05);
  bone([[60, 240], [40, 262], [-250, 262], [-262, 240], [-250, 222], [30, 222]]);                       // femur, forward (seated)
  muscle([[40, 0], [62, 20], [58, 150], [30, 200], [-30, 232], [-60, 240], [-50, 220], [10, 180], [34, 120]],
         [40, 0], [62, 20], [-60, 240], [-50, 222], { n: 40, bow: 10, hot: true });                        // iliopsoas
  X.fillStyle = "#c8a77d"; X.fillRect(-300, 300, 470, 18);                                                // chair seat
  X.restore();
}
// ---- pelvis + lumbar spine: neutral vs anterior tilt ----
function pelvisTilt(ox, oy, s, tilt, col) {
  X.save(); X.translate(ox, oy); X.scale(s, s);
  spine(20, -150, tilt ? 34 : 12, 5, 36);
  pelvis(10, 70, tilt ? -0.38 : 0);
  X.save(); X.translate(10, 70); X.rotate(tilt ? -0.38 : 0);
  X.strokeStyle = col; X.lineWidth = 6; X.setLineDash([12, 8]); X.beginPath(); X.moveTo(-76, -40); X.lineTo(-30, 110); X.stroke(); X.setLineDash([]);
  X.restore();
  if (tilt) { arrow(-120, -10, -150, 60, C.red, 7); }
  X.restore();
}
// ---- torso side view: lumbar lordosis with glowing erector spinae ----
function lordosis(ox, oy, s) {
  X.save(); X.translate(ox, oy); X.scale(s, s);
  skin([[-70, -210], [60, -210], [40, -40], [70, 120], [150, 220], [150, 290], [40, 310], [-110, 290], [-150, 120], [-110, -40]]);
  spine(20, -170, 46, 7, 44);                                              // lumbar bowed forward (lordosis)
  const back = u => [74 - 46 * Math.sin(Math.PI * u), -170 + 6 * 44 * u];   // line just behind the spinous processes
  const L = [], Rr = [];
  for (let i = 0; i <= 8; i++) { const u = i / 8, p = back(u); L.push([p[0] - 6, p[1]]); Rr.push([p[0] + 30 - 6 * Math.sin(Math.PI * u), p[1]]); }
  muscle([...L, ...Rr.reverse()], L[0], Rr[Rr.length - 1], L[L.length - 1], Rr[0], { n: 34, bow: 0, hot: true });   // erector spinae
  pelvis(40, 200, -0.38, 0.9);
  X.restore();
}
// ---- the chain: heel -> tilted pelvis -> sore back ----
function shoeIcon(x, y, s) {
  X.save(); X.translate(x, y); X.scale(s, s);
  const p = shape([[-118, 84], [-112, 62], [-60, 44], [-10, 22], [24, -14], [56, -40], [80, -36], [82, -6], [74, 14], [70, 96], [58, 96], [54, 28], [20, 46], [-50, 80]]);
  const g = X.createLinearGradient(-120, -40, 80, 96); g.addColorStop(0, "#d23a46"); g.addColorStop(1, "#7e1622");
  X.save(); X.shadowColor = "rgba(0,0,0,.35)"; X.shadowBlur = 10; X.shadowOffsetY = 4; X.fillStyle = g; X.fill(p); X.restore();
  X.strokeStyle = "#5a0f18"; X.lineWidth = 2; X.stroke(p);
  X.strokeStyle = "rgba(255,255,255,.45)"; X.lineWidth = 3; X.beginPath(); X.moveTo(-100, 64); X.quadraticCurveTo(-20, 30, 40, -24); X.stroke();
  X.restore();
}

