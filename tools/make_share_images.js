// Makes the link-preview image for every article: assets/img/og/<slug>.jpg (1200 x 630).
// Run from the repository root after adding an article:  node tools/make_share_images.js
// Needs Node and Playwright (npm i playwright).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');
const art = { home: 'equipment.webp', strength: 'strength.webp', cardio: 'cardio.webp', nutrition: 'macros.webp', meal: 'meal-planning.webp' };
const group = { home: 'Home training', strength: 'Strength training', cardio: 'Cardio', nutrition: 'Nutrition basics', meal: 'Meal planning' };
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1200, height: 630 } });
  const logo = 'data:image/webp;base64,' + fs.readFileSync(path.join(root, 'assets/img/logo.webp')).toString('base64');
  for (const f of fs.readdirSync(path.join(root, 'content/articles')).filter(f => f.endsWith('.md'))) {
    const head = fs.readFileSync(path.join(root, 'content/articles', f), 'utf8').split('---')[1];
    const meta = Object.fromEntries(head.trim().split('\n').map(l => [l.slice(0, l.indexOf(': ')), l.slice(l.indexOf(': ') + 2)]));
    const bg = 'data:image/webp;base64,' + fs.readFileSync(path.join(root, 'assets/img', art[meta.guide])).toString('base64');
    const [main, sub] = meta.title.split(/:\s(.+)/);
    await pg.setContent(`<html><head><link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700&display=swap" rel="stylesheet"><style>
      body{margin:0;width:1200px;height:630px;background:#0f1113;font-family:Inter,Arial,sans-serif;position:relative;overflow:hidden}
      .art{position:absolute;right:-60px;bottom:0;width:820px;height:273px;background:url(${bg}) right bottom/cover;opacity:.55}
      .fade{position:absolute;inset:0;background:linear-gradient(90deg,#0f1113 38%,rgba(15,17,19,.2))}
      .brand{position:absolute;left:72px;top:64px;display:flex;align-items:center;gap:16px;color:#fff;font-weight:700;letter-spacing:.18em;font-size:22px}
      .brand img{width:52px;height:52px;border-radius:50%}
      .kick{position:absolute;left:72px;top:180px;color:#9cc5ed;font-size:26px;font-weight:500}
      h1{position:absolute;left:72px;top:222px;width:860px;margin:0;color:#fff;font-size:${main.length > 34 ? 58 : 66}px;line-height:1.08;letter-spacing:-.025em;font-weight:700}
      p{position:absolute;left:72px;bottom:64px;width:760px;margin:0;color:#a4abb2;font-size:26px;line-height:1.35;font-weight:500}
    </style></head><body><div class="art"></div><div class="fade"></div>
      <div class="brand"><img src="${logo}">TRENESIS</div><div class="kick">${group[meta.guide]}</div>
      <h1>${esc(main)}</h1>${sub ? `<p>${esc(sub.charAt(0).toUpperCase() + sub.slice(1))}</p>` : ''}</body></html>`, { waitUntil: 'networkidle' });
    await pg.screenshot({ path: path.join(root, 'assets/img/og', meta.slug + '.jpg'), type: 'jpeg', quality: 82 });
    console.log('made', meta.slug);
  }
  await b.close();
})();
