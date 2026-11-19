// Shared drawing helpers for FlowPilot reels. Include in scene.html with:
//   <canvas id="c" width="1080" height="1920"></canvas><script src="../../engine/lib.js"></script>
// Then define render(t) and call FP.init(render) at the end of your script.
// Everything here is a pure function of t (no Math.random, no Date), so frames can render in parallel.
const W = 1080, H = 1920;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const FONT = 'Inter, "Inter Display", sans-serif';
const C = { bg0: '#05081A', bg1: '#0B1235', cyan: '#3CF2FF', violet: '#8B6CFF', mint: '#3DFFA8', red: '#FF4D6D', amber: '#FFB547', orange: '#FF8A3D', pink: '#FF6FB5', white: '#F4F7FF', grey: '#8D97B8' };
let TL = {};

// ---------- math ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const eOut = k => 1 - Math.pow(1 - k, 3);
const eIn = k => k * k * k;
const eIO = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const eBack = k => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); };
const eElastic = k => k === 0 || k === 1 ? k : Math.pow(2, -10 * k) * Math.sin((k * 10 - .75) * (2 * Math.PI / 3)) + 1;
function mulberry(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function hash(n) { const s = Math.sin(n * 127.1) * 43758.5453; return s - Math.floor(s); }
function noise1(x) { const i = Math.floor(x), f = x - i; const u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; }
function mix(a, b, k) {
  const pa = [1, 3, 5].map(i => parseInt(a.substr(i, 2), 16)), pb = [1, 3, 5].map(i => parseInt(b.substr(i, 2), 16));
  return `rgb(${pa.map((v, i) => Math.round(lerp(v, pb[i], k))).join(',')})`;
}

// ---------- shapes & text ----------
function rr(x, y, w, h, r) { r = Math.min(r, w / 2, h / 2); ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function glowText(txt, x, y, size, color, weight = 800, align = 'center', blur = 30, alpha = 1, spacing = 0) {
  ctx.save(); ctx.globalAlpha *= alpha; ctx.font = `${weight} ${size}px ${FONT}`; ctx.textAlign = align; ctx.textBaseline = 'middle';
  if (spacing) ctx.letterSpacing = spacing + 'px';
  ctx.shadowColor = color; ctx.shadowBlur = blur; ctx.fillStyle = color; ctx.fillText(txt, x, y);
  ctx.shadowBlur = 0; ctx.fillText(txt, x, y); ctx.restore();
}
function gradText(txt, x, y, size, c1 = C.cyan, c2 = C.violet, weight = 900, blur = 40) {
  ctx.save(); ctx.font = `${weight} ${size}px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.letterSpacing = '-3px';
  const w = ctx.measureText(txt).width; const g = ctx.createLinearGradient(x - w / 2, 0, x + w / 2, 0); g.addColorStop(0, c1); g.addColorStop(1, c2);
  ctx.fillStyle = g; ctx.shadowColor = c1; ctx.shadowBlur = blur; ctx.fillText(txt, x, y); ctx.restore();
}
function wrapText(txt, maxW) {
  const words = txt.split(' '), lines = [''];
  for (const w of words) { const t = lines[lines.length - 1] ? lines[lines.length - 1] + ' ' + w : w; if (ctx.measureText(t).width > maxW && lines[lines.length - 1]) lines.push(w); else lines[lines.length - 1] = t; }
  return lines;
}
function icon(kind, x, y, s, col) {
  ctx.save(); ctx.translate(x, y); ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = s * .12; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const h = s / 2;
  if (kind === 'mail') { rr(-h, -h * .7, s, s * .7 * 2, s * .1); ctx.stroke(); ctx.beginPath(); ctx.moveTo(-h, -h * .6); ctx.lineTo(0, h * .15); ctx.lineTo(h, -h * .6); ctx.stroke(); }
  else if (kind === 'bolt') { ctx.beginPath(); ctx.moveTo(h * .2, -h); ctx.lineTo(-h * .55, h * .1); ctx.lineTo(0, h * .1); ctx.lineTo(-h * .2, h); ctx.lineTo(h * .55, -h * .1); ctx.lineTo(0, -h * .1); ctx.closePath(); ctx.fill(); }
  else if (kind === 'check') { ctx.lineWidth = s * .16; ctx.beginPath(); ctx.moveTo(-h * .7, 0); ctx.lineTo(-h * .15, h * .55); ctx.lineTo(h * .75, -h * .55); ctx.stroke(); }
  else if (kind === 'bell') { ctx.beginPath(); ctx.moveTo(-h * .7, h * .45); ctx.quadraticCurveTo(-h * .6, -h * .9, 0, -h * .9); ctx.quadraticCurveTo(h * .6, -h * .9, h * .7, h * .45); ctx.closePath(); ctx.stroke(); ctx.beginPath(); ctx.arc(0, h * .7, h * .18, 0, 7); ctx.fill(); }
  else if (kind === 'phone') { ctx.lineWidth = s * .14; ctx.beginPath(); ctx.moveTo(-h * .6, -h * .75); ctx.quadraticCurveTo(-h * .95, -h * .2, -h * .2, h * .55); ctx.quadraticCurveTo(h * .45, h * 1.05, h * .75, h * .6); ctx.stroke(); }
  else if (kind === 'cal') { rr(-h, -h * .8, s, s * .9, s * .12); ctx.stroke(); ctx.beginPath(); ctx.moveTo(-h, -h * .35); ctx.lineTo(h, -h * .35); ctx.stroke(); }
  else if (kind === 'x') { ctx.lineWidth = s * .16; ctx.beginPath(); ctx.moveTo(-h * .6, -h * .6); ctx.lineTo(h * .6, h * .6); ctx.moveTo(h * .6, -h * .6); ctx.lineTo(-h * .6, h * .6); ctx.stroke(); }
  ctx.restore();
}
function plane(x, y, ang, s, alpha = 1) {
  ctx.save(); ctx.globalAlpha *= alpha; ctx.translate(x, y); ctx.rotate(ang);
  ctx.shadowColor = C.cyan; ctx.shadowBlur = 50;
  const g = ctx.createLinearGradient(-s, 0, s, 0); g.addColorStop(0, C.violet); g.addColorStop(1, '#FFFFFF');
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(s, 0); ctx.lineTo(-s * .8, -s * .7); ctx.lineTo(-s * .35, 0); ctx.lineTo(-s * .8, s * .7); ctx.closePath(); ctx.fill();
  ctx.shadowBlur = 0; ctx.fillStyle = 'rgba(40,30,120,.55)'; ctx.beginPath(); ctx.moveTo(s, 0); ctx.lineTo(-s * .35, 0); ctx.lineTo(-s * .8, s * .7); ctx.closePath(); ctx.fill();
  ctx.restore();
}
function trailPlane(t, dfun, len = 0.6, size = 46, alpha = 1) {
  ctx.save(); ctx.globalAlpha *= alpha; ctx.lineCap = 'round';
  for (let i = 26; i > 0; i--) {
    const a = dfun(t - len * i / 26), b = dfun(t - len * (i - 1) / 26), k = 1 - i / 26;
    ctx.strokeStyle = `rgba(60,242,255,${k * .8})`; ctx.lineWidth = 4 + k * 22; ctx.shadowColor = C.cyan; ctx.shadowBlur = 30;
    ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
  }
  ctx.restore();
  const p = dfun(t), q = dfun(t - 0.02); plane(p.x, p.y, Math.atan2(p.y - q.y, p.x - q.x), size, alpha);
}
// a robot head (the bots' mascot look)
function robot(x, y, s, t, col = C.cyan) {
  ctx.save(); ctx.translate(x, y);
  ctx.strokeStyle = col; ctx.lineWidth = s * .05; ctx.beginPath(); ctx.moveTo(0, -s * .55); ctx.lineTo(0, -s * .75); ctx.stroke();
  ctx.beginPath(); ctx.arc(0, -s * .8, s * .08, 0, 7); ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 20; ctx.fill(); ctx.shadowBlur = 0;
  rr(-s * .55, -s * .55, s * 1.1, s * .95, s * .28); ctx.fillStyle = '#16204A'; ctx.fill(); ctx.stroke();
  const blink = (Math.floor(t * 1.3) % 5 === 0 && (t * 1.3) % 1 < .15) ? .15 : 1;
  ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 25;
  for (const ex of [-.22, .22]) { ctx.beginPath(); ctx.ellipse(ex * s, -s * .1, s * .09, s * .11 * blink, 0, 0, 7); ctx.fill(); }
  ctx.shadowBlur = 0; ctx.beginPath(); ctx.arc(0, s * .1, s * .14, .15 * Math.PI, .85 * Math.PI); ctx.lineWidth = s * .045; ctx.stroke();
  ctx.restore();
}
// confetti burst starting at t0 from (x,y); seeded, pure in t
function confetti(t, t0, x, y, n = 70, seed = 5) {
  const k = t - t0; if (k < 0 || k > 3) return; const r = mulberry(seed);
  const cols = [C.cyan, C.violet, C.mint, C.amber, C.pink];
  for (let i = 0; i < n; i++) {
    const a = r() * Math.PI * 2, v = 500 + r() * 900, rot = r() * 6, c = cols[i % cols.length];
    const px = x + Math.cos(a) * v * k * .6, py = y + Math.sin(a) * v * k * .6 + 900 * k * k;
    ctx.save(); ctx.globalAlpha = 1 - seg(k, 2, 3); ctx.translate(px, py); ctx.rotate(rot + k * 8); ctx.fillStyle = c; ctx.fillRect(-9, -5, 18, 10); ctx.restore();
  }
}

// ---------- backgrounds & post ----------
const STARS = (() => { const r = mulberry(42); return Array.from({ length: 120 }, () => ({ x: r() * W, y: r() * H, r: r() * 2 + .4, s: r() * 6 + 1, p: r() * 6.28 })); })();
function bgNight(t, top = '#05081A', mid = '#0B1235', bot = '#060A20', grid = true) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, top); g.addColorStop(.6, mid); g.addColorStop(1, bot);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  for (const s of STARS) { ctx.fillStyle = `rgba(200,220,255,${.3 + .3 * Math.sin(t * s.s * .3 + s.p)})`; ctx.beginPath(); ctx.arc(s.x, (s.y - t * s.s * 3 + H * 10) % H, s.r, 0, 7); ctx.fill(); }
  if (!grid) return;
  ctx.save(); ctx.strokeStyle = C.violet; ctx.lineWidth = 1.5; const hz = 1380;
  ctx.globalAlpha = .16; for (let i = -12; i <= 12; i++) { ctx.beginPath(); ctx.moveTo(W / 2 + i * 30, hz); ctx.lineTo(W / 2 + i * 260, H); ctx.stroke(); }
  for (let j = 0; j < 14; j++) { const k = ((j + (t * .6) % 1) / 14); const y = hz + Math.pow(k, 2.2) * (H - hz); ctx.globalAlpha = .16 * k; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.restore();
}
let GRAIN;
function post(t, flash = 0, fadeIn = .5) {
  if (!GRAIN) { GRAIN = document.createElement('canvas'); GRAIN.width = GRAIN.height = 256; const g = GRAIN.getContext('2d'), id = g.createImageData(256, 256), r = mulberry(3); for (let i = 0; i < id.data.length; i += 4) { const v = r() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; } g.putImageData(id, 0, 0); }
  ctx.save(); ctx.globalAlpha = .05; ctx.globalCompositeOperation = 'overlay';
  const f = Math.floor(t * 30); ctx.translate(-Math.floor(hash(f) * 256), -Math.floor(hash(f + 9) * 256));
  for (let x = 0; x < W + 256; x += 256) for (let y = 0; y < H + 256; y += 256) ctx.drawImage(GRAIN, x, y);
  ctx.restore();
  const v = ctx.createRadialGradient(W / 2, H / 2, H * .25, W / 2, H / 2, H * .75); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.5)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  if (flash > 0) { ctx.fillStyle = `rgba(255,255,255,${flash})`; ctx.fillRect(0, 0, W, H); }
  const fb = (fadeIn > 0 ? 1 - seg(t, 0, fadeIn) : 0) + seg(t, TL.dur - 1.2, TL.dur);
  if (fb > 0) { ctx.fillStyle = `rgba(0,0,0,${clamp(fb)})`; ctx.fillRect(0, 0, W, H); }
}

// ---------- captions (TL.captions from voice.py) ----------
// opts.y(t) -> y position or null to hide. Labels and colours per speaker from opts.who.
const WHO = { pilot: ['YOUR PILOT', C.cyan], owner: ['THE OWNER', C.amber], customer: ['CUSTOMER', C.pink], narrator: ['', C.white], commentator: ['LIVE COMMENTARY', C.amber] };
function captions(t, opts = {}) {
  if (!TL.captions) return;
  const c = TL.captions.find(c => t >= c.t0 && t < c.t1 + 0.1); if (!c) return;
  const y = opts.y ? opts.y(t) : 1540; if (y == null) return;
  const [label, col] = (opts.who || WHO)[c.who] || ['', C.white];
  const k = eBack(seg(t, c.t0, c.t0 + .16));
  ctx.save(); ctx.font = `800 54px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const w = Math.min(1000, ctx.measureText(c.text).width + 80);
  ctx.translate(W / 2, y); ctx.scale(.85 + .15 * k, .85 + .15 * k); ctx.globalAlpha = clamp(k * 1.5);
  rr(-w / 2, -50, w, 100, 50); ctx.fillStyle = 'rgba(5,8,26,.9)'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = col; ctx.stroke();
  ctx.fillStyle = col === C.white ? C.white : col; ctx.fillText(c.text, 0, 3);
  if (label) { ctx.font = `800 26px ${FONT}`; ctx.letterSpacing = '6px'; ctx.shadowColor = 'rgba(0,0,0,.9)'; ctx.shadowBlur = 12; ctx.fillStyle = col; ctx.fillText(label, 0, -78); }
  ctx.restore();
}

// ---------- the FlowPilot logo ending (starts at t0, needs ~4.5 s) ----------
function logoEnding(t, t0, o = {}) {
  const cta = o.cta || 'Get your free automation plan  →', tag = o.tagline || 'AI automations for local businesses', foot = o.footer || 'You stay in control.';
  const cx = W / 2, cy = o.cy || 640, R = 230;
  bgNight(t, '#05081A', '#0B1235', '#060A20', true);
  const lp = tt => { const k = eIO(seg(tt, t0, t0 + 1.5)); const ang = -Math.PI * .5 - k * Math.PI * 2; const r = R + Math.pow(1 - k, 3) * 700; return { x: cx + Math.cos(ang) * r, y: cy + Math.sin(ang) * r }; };
  const rk = seg(t, t0, t0 + 1.5);
  ctx.save(); ctx.lineCap = 'round'; const g = ctx.createLinearGradient(cx - R, cy - R, cx + R, cy + R); g.addColorStop(0, C.cyan); g.addColorStop(1, C.violet);
  ctx.strokeStyle = g; ctx.lineWidth = 14; ctx.shadowColor = C.cyan; ctx.shadowBlur = 40;
  if (rk > 0) { ctx.beginPath(); ctx.arc(cx, cy, R, -Math.PI * .5, -Math.PI * .5 - Math.max(.001, eIO(rk) * Math.PI * 2 - .35), true); ctx.stroke(); }
  ctx.restore();
  if (t < t0 + 1.5) trailPlane(t, lp, .45, 56);
  else {
    const k = eBack(seg(t, t0 + 1.5, t0 + 2.1)); plane(cx, cy + Math.sin(t * 2) * 8, -Math.PI / 4 * k, 110 * k);
    for (let i = 0; i < 3; i++) { const an = t * 1.4 + i * 2.094; ctx.fillStyle = '#fff'; ctx.shadowColor = C.cyan; ctx.shadowBlur = 20; ctx.beginPath(); ctx.arc(cx + Math.cos(an) * R, cy + Math.sin(an) * R, 8, 0, 7); ctx.fill(); ctx.shadowBlur = 0; }
  }
  const wk = seg(t, t0 + 1.6, t0 + 2.4);
  if (wk > 0) { ctx.save(); ctx.globalAlpha = wk; ctx.font = `900 168px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.letterSpacing = lerp(40, -5, eOut(wk)) + 'px';
    const g2 = ctx.createLinearGradient(200, 0, 880, 0); g2.addColorStop(0, '#FFFFFF'); g2.addColorStop(.5, C.cyan); g2.addColorStop(1, C.violet); ctx.fillStyle = g2; ctx.shadowColor = C.cyan; ctx.shadowBlur = 35; ctx.fillText('FlowPilot', W / 2, cy + 380); ctx.restore(); }
  const tk = seg(t, t0 + 2.2, t0 + 2.8);
  if (tk > 0) { ctx.save(); ctx.globalAlpha = tk; ctx.font = `600 46px ${FONT}`; ctx.textAlign = 'center'; ctx.fillStyle = C.grey; ctx.textBaseline = 'middle'; ctx.fillText(tag, W / 2, cy + 495 + (1 - eOut(tk)) * 30); ctx.restore(); }
  const ck = seg(t, t0 + 2.8, t0 + 3.3);
  if (ck > 0) {
    ctx.save(); const s = eBack(ck) * (1 + .025 * Math.sin(t * 5)); ctx.translate(W / 2, cy + 680); ctx.scale(s, s); ctx.globalAlpha = ck;
    ctx.font = `800 48px ${FONT}`; const w = Math.max(700, ctx.measureText(cta).width + 120), h = 140;
    const g3 = ctx.createLinearGradient(-w / 2, 0, w / 2, 0); g3.addColorStop(0, C.cyan); g3.addColorStop(1, C.violet);
    rr(-w / 2, -h / 2, w, h, 70); ctx.fillStyle = g3; ctx.shadowColor = C.cyan; ctx.shadowBlur = 50 + 20 * Math.sin(t * 5); ctx.fill(); ctx.shadowBlur = 0;
    ctx.save(); ctx.clip(); const sx = ((t - t0 - 3.3) % 2.2) / 1.2 * (w + 300) - w / 2 - 150; const sh = ctx.createLinearGradient(sx - 80, 0, sx + 80, 0); sh.addColorStop(0, 'rgba(255,255,255,0)'); sh.addColorStop(.5, 'rgba(255,255,255,.55)'); sh.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = sh; ctx.fillRect(-w / 2, -h / 2, w, h); ctx.restore();
    ctx.fillStyle = '#06102A'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(cta, 0, 3); ctx.restore();
  }
  const fk = seg(t, t0 + 3.4, t0 + 4);
  if (fk > 0 && foot) { ctx.save(); ctx.globalAlpha = fk * .9; ctx.font = `500 36px ${FONT}`; ctx.textAlign = 'center'; ctx.fillStyle = C.grey; ctx.textBaseline = 'middle'; ctx.fillText(foot, W / 2, cy + 820); ctx.restore(); }
}

// ---------- wiring ----------
const FP = {
  init(render) {
    window.setup = tl => { TL = tl; };
    window.frame = (t, q) => { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.filter = 'none'; render(t); return cv.toDataURL('image/jpeg', q || .9); };
  }
};
