// Render an episode folder (scene.html + timeline.json from audio.py) to video.
// usage: node render.js <episodeDir> preview 3,9,13.5   -> <episodeDir>/prev/t<sec>.jpg
//        node render.js <episodeDir> full [workers]       -> <episodeDir>/seg<N>.mp4
// scene.html must define window.setup(timeline) and window.frame(t, jpegQuality) -> dataURL.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const DIR = path.resolve(process.argv[2]), mode = process.argv[3], FPS = 30;
const TL = JSON.parse(fs.readFileSync(path.join(DIR, 'timeline.json')));
async function page(browser) {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => { console.error('PAGE ERROR:', e.message); process.exitCode = 1; });
  await p.goto('file://' + path.join(DIR, 'scene.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(tl => setup(tl), TL);
  return p;
}
(async () => {
  const browser = await chromium.launch();
  if (mode === 'preview') {
    const p = await page(browser); fs.mkdirSync(path.join(DIR, 'prev'), { recursive: true });
    for (const t of process.argv[4].split(',').map(Number)) {
      const url = await p.evaluate(([t]) => frame(t, .8), [t]);
      fs.writeFileSync(path.join(DIR, 'prev', `t${t}.jpg`), Buffer.from(url.split(',')[1], 'base64'));
    }
  } else {
    const total = Math.round(TL.dur * FPS), W = +(process.argv[4] || 4), per = Math.ceil(total / W);
    await Promise.all(Array.from({ length: W }, async (_, w) => {
      const p = await page(browser);
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', path.join(DIR, `seg${w}.mp4`)]);
      for (let f = w * per; f < Math.min(total, (w + 1) * per); f++) {
        const url = await p.evaluate(([t]) => frame(t, .93), [f / FPS]);
        if (!ff.stdin.write(Buffer.from(url.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
        if (f % 300 === 0) console.log('worker', w, 'frame', f, '/', total);
      }
      ff.stdin.end(); await new Promise(r => ff.on('close', r));
    }));
  }
  await browser.close();
})();
