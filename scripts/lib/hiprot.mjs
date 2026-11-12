// Hip rotation seen from above (own artwork): the pelvis, the planted-foot leg whose thigh turns about the hip joint, so the
// knee swings out (external rotation) or collapses in (internal rotation). The thigh and the shank are separate groups so
// the page animates them (GSAP rotation about the hip / the ankle). Geometry is exported for the build.
export const HIP = { H: [540, 560], A: [540, 70], K0: [540, 300], thigh: 260 };

// the knee for a rotation theta (degrees, + = outward) and the matching shank rotation / stretch about the ankle
export function kneeFor(theta) {
  const t = (theta * Math.PI) / 180, K = [HIP.H[0] + HIP.thigh * Math.sin(t), HIP.H[1] - HIP.thigh * Math.cos(t)];
  const v = [K[0] - HIP.A[0], K[1] - HIP.A[1]], s0 = [HIP.K0[0] - HIP.A[0], HIP.K0[1] - HIP.A[1]];
  const phi = (Math.atan2(v[0], v[1]) - Math.atan2(s0[0], s0[1])) * (180 / Math.PI);
  return { K, shankRot: -phi, shankScale: Math.hypot(v[0], v[1]) / Math.hypot(s0[0], s0[1]) };
}

export function hipRotSvg({ id = "hr", w = 900, h = 900 } = {}) {
  const { H, A, K0 } = HIP, H2 = [H[0] - 300, H[1]], K2 = [H2[0], K0[1]], A2 = [H2[0], A[1]];
  const bone = (a, b, wd) => `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#E8E0CC" stroke-width="${wd}" stroke-linecap="round"/><line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#A89F88" stroke-width="${wd * 0.28}" stroke-linecap="round" opacity=".6"/>`;
  const joint = (p, r) => `<circle cx="${p[0]}" cy="${p[1]}" r="${r}" fill="#F1EADA" stroke="#8D8573" stroke-width="5"/>`;
  const foot = (p) => `<rect x="${p[0] - 40}" y="${p[1] - 70}" width="80" height="120" rx="34" fill="#CFC6AE" stroke="#8D8573" stroke-width="5"/>`;
  const thighMuscle = (c, hot) => `<path d="M${c[0] - 70} ${c[1] + 130} C${c[0] - 120} ${c[1] + 30} ${c[0] - 70} ${c[1] - 90} ${c[0] - 6} ${c[1] - 10} C${c[0] + 60} ${c[1] - 90} ${c[0] + 120} ${c[1] + 30} ${c[0] + 70} ${c[1] + 130} Z" fill="${hot ? `url(#${id}-hot)` : "#8A8A8A"}" stroke="${hot ? "#7E1D0E" : "#5d5d5d"}" stroke-width="4" opacity="${hot ? 1 : 0.7}"/>`;
  const pelvis = `<path d="M${H2[0] - 70} ${H[1] + 40} C${H2[0] - 90} ${H[1] - 70} ${H2[0] + 60} ${H[1] - 120} ${(H[0] + H2[0]) / 2} ${H[1] - 70} C${H[0] - 60} ${H[1] - 120} ${H[0] + 90} ${H[1] - 70} ${H[0] + 70} ${H[1] + 40} C${H[0] + 40} ${H[1] + 170} ${H2[0] - 40} ${H[1] + 170} ${H2[0] - 70} ${H[1] + 40} Z" fill="url(#${id}-bone)" stroke="#8D8573" stroke-width="5"/>
    <ellipse cx="${(H[0] + H2[0]) / 2}" cy="${H[1] + 70}" rx="84" ry="64" fill="#D7CEB6" stroke="#8D8573" stroke-width="4"/>`;
  // glute med / max fan behind the hip joint (the working side, the right leg)
  const fan = `<g id="${id}-muscle"><path d="M${H[0] - 150} ${H[1] + 150} C${H[0] - 120} ${H[1] + 40} ${H[0] - 60} ${H[1] - 10} ${H[0]} ${H[1] - 6} C${H[0] + 90} ${H[1] - 20} ${H[0] + 130} ${H[1] + 70} ${H[0] + 100} ${H[1] + 160} C${H[0] + 20} ${H[1] + 210} ${H[0] - 80} ${H[1] + 210} ${H[0] - 150} ${H[1] + 150} Z" fill="url(#${id}-hot)" stroke="#7E1D0E" stroke-width="4"/>
     <path d="M${H[0] - 120} ${H[1] + 150} L${H[0] - 6} ${H[1] + 10} M${H[0] - 60} ${H[1] + 190} L${H[0] + 20} ${H[1] + 20} M${H[0]} ${H[1] + 200} L${H[0] + 50} ${H[1] + 20} M${H[0] + 60} ${H[1] + 195} L${H[0] + 80} ${H[1] + 40}" stroke="rgba(120,20,6,.55)" stroke-width="3" fill="none"/></g>`;
  return `<svg width="${w}" height="${h}" viewBox="0 0 1080 900" style="overflow:visible">
  <defs>
    <linearGradient id="${id}-hot" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF8C5A"/><stop offset=".55" stop-color="#E4522C"/><stop offset="1" stop-color="#B02C14"/></linearGradient>
    <radialGradient id="${id}-bone" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#F4EEDD"/><stop offset="1" stop-color="#BDB39A"/></radialGradient>
  </defs>
  <g>${bone(H2, K2, 30)}${bone(K2, A2, 24)}${foot(A2)}${joint(K2, 22)}</g>
  ${pelvis}${joint(H2, 40)}
  <g id="${id}-fan">${fan}</g>
  <g id="${id}-shank">${bone(A, K0, 24)}${foot(A)}<circle cx="${K0[0]}" cy="${K0[1]}" r="24" fill="#F1EADA" stroke="#8D8573" stroke-width="5"/></g>
  <g id="${id}-thigh">${bone(H, K0, 30)}<circle cx="${K0[0]}" cy="${K0[1]}" r="1" fill="none"/></g>
  ${joint(H, 40)}
</svg>`;
}
