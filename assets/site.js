// Quiet placeholder for a product picture that is missing or fails to load.
window.trenesisImgFallback = () => {
  const ph = document.createElement('span');
  ph.className = 'img-fallback'; ph.setAttribute('aria-hidden', 'true');
  ph.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M6 8v8M3 10v4M18 8v8M21 10v4M6 12h12"/></svg>';
  return ph;
};

(() => {
  'use strict';
  const menu = document.querySelector('#navigation');
  const toggle = document.querySelector('.menu-toggle');
  if (menu && toggle) {
    document.documentElement.classList.add('js');
    toggle.hidden = false;
    const setOpen = open => {
      menu.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    };
    setOpen(false);
    toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });
    menu.addEventListener('click', event => { if (event.target.closest('a')) setOpen(false); });
    const desktop = window.matchMedia('(min-width: 801px)');
    desktop.addEventListener('change', () => setOpen(false));
  }
  document.querySelectorAll('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });
  // Restore the guide highlight when arriving from a homepage guide tile.
  function highlightGuide(card) {
    if (!card) return;
    clearTimeout(card._highlightTimeout);
    card.classList.remove('highlight');
    void card.offsetWidth;
    card.classList.add('highlight');
    card._highlightTimeout = setTimeout(() => card.classList.remove('highlight'), 1800);
  }
  function highlightHashGuide() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const card = document.getElementById(id);
    if (card?.matches('.pdf-card')) highlightGuide(card);
  }
  highlightHashGuide();
  window.addEventListener('hashchange', highlightHashGuide);
  document.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link) return;
    if (/\.pdf(?:[?#]|$)/i.test(link.getAttribute('href') || '')) {
      highlightGuide(link.closest('.pdf-card, .guide-row'));
    } else if (link.hash && link.pathname === location.pathname) {
      highlightHashGuide();
    }
  });
  // Every country picker on the page (gear pages: one near the top and one in the footer) stays in sync.
  const selects = [...document.querySelectorAll('select[data-country]')];
  const select = selects[0];
  if (!select) return;
  selects.forEach(s => { s.disabled = false; });
  const setValue = v => selects.forEach(s => { s.value = v; });
  const hints = [...document.querySelectorAll('[data-country-hint]')];
  const hint = { set textContent(t) { hints.forEach(h => { h.textContent = t; }); } };
  const markets = window.TRENESIS_MARKETS || {};
  const key = 'trenesis.review-country.v1';
  const title = document.querySelector('#market-title');
  const detail = document.querySelector('#market-detail');
  const list = document.querySelector('#local-picks');
  const category = document.querySelector('[data-category]')?.dataset.category || 'all';
  const articleSlots = [...document.querySelectorAll('[data-article-picks]')];
  const matchesSlot = (slot, pick) => slot.dataset.pickSection === pick.guideSection ||
    (slot.dataset.pickNames || '').split('|').includes(pick.name);
  const valid = code => Object.hasOwn(markets, code);
  let saved = null;
  try { saved = localStorage.getItem(key); } catch (_) { /* browsing still works without storage */ }
  let suggested = null;
  let nearest = false;
  // Countries without their own catalog get the closest store we cover.
  const NEAREST = { AT: 'DE', CH: 'DE', LU: 'DE', NL: 'DE', PL: 'DE', CZ: 'DE', DK: 'DE', SE: 'DE', NO: 'DE', FI: 'DE', BE: 'FR', IE: 'GB', PT: 'ES', MX: 'US', PR: 'US' };
  // A regional language preference is a hint, never a claim of physical location.
  for (const language of navigator.languages || [navigator.language]) {
    try {
      const region = new Intl.Locale(language).region;
      if (region && valid(region)) { suggested = region; break; }
      if (region && valid(NEAREST[region])) { suggested = NEAREST[region]; nearest = true; break; }
    } catch (_) { /* malformed/unsupported locale */ }
  }
  setValue(valid(saved) ? saved : suggested || 'GLOBAL');
  hint.textContent = valid(saved) ? 'Using your saved country. Change it anytime.' : suggested ? (nearest ? 'The closest store we cover to your region. You can change it anytime.' : 'Suggested from your browser region. You can change it anytime.') : 'Choose your country; your preference stays on this device.';
  // A product's picture is optional: "photo" (our own file in assets/products/, see the README there) wins over
  // "image" (the retailer's picture). With neither, or if it fails to load, the quiet placeholder shows instead.
  function productImage(pick, w, h, alt) {
    const src = pick.photo || pick.image;
    if (!src) return window.trenesisImgFallback();
    const image = document.createElement('img');
    image.src = src; image.alt = alt; image.width = w; image.height = h; image.loading = 'lazy'; image.decoding = 'async';
    return image;
  }
  function render() {
    if (!title || !detail || !list) return;
    const code = valid(select.value) ? select.value : 'GLOBAL';
    const market = markets[code];
    let picks = category === 'all' ? ['equipment', 'supplements', 'accessories'].flatMap(c => market[c] || []) : (market[category] || []);
    if (articleSlots.length) picks = picks.filter(pick => articleSlots.some(slot => matchesSlot(slot, pick)));
    articleSlots.forEach(slot => { slot.hidden = !picks.some(pick => matchesSlot(slot, pick)); });
    list.replaceChildren();
    document.querySelectorAll('.inline-picks').forEach(el => el.remove());
    title.textContent = picks.length ? (category === 'all' ? `Showing picks for ${market.name} inside each guide below.` : `Examples for ${market.name}`) : code === 'GLOBAL' ? 'We don’t have picks for your country yet. Choose the closest country at the top of the page to see examples.' : `Product examples for ${market.name} are coming soon.`;
    detail.hidden = picks.length > 0;
    detail.textContent = picks.length ? '' : 'The buying advice on this page applies wherever you live.';
    document.querySelectorAll('.affiliate-disclosure').forEach(el => { el.hidden = !picks.length; });
    if (articleSlots.length) {
      title.textContent = picks.length ? `Affiliate picks for ${market.name}` : 'Choose your country in the footer for product picks';
      for (const slot of articleSlots) {
        slot.querySelector('.article-product-picks')?.remove();
        const group = document.createElement('div');
        group.className = 'article-product-picks';
        for (const pick of picks.filter(pick => matchesSlot(slot, pick))) {
          const card = document.createElement('a');
          card.className = 'article-product-pick';
          card.href = pick.url;
          card.target = '_blank';
          card.rel = 'sponsored noopener';
          card.setAttribute('aria-label', `${pick.brand} ${pick.name} on Amazon (affiliate link, opens a new tab)`);
          const image = productImage(pick, 72, 72, '');
          const info = document.createElement('span');
          const brand = document.createElement('span');
          brand.className = 'article-product-brand'; brand.textContent = pick.brand;
          const name = document.createElement('strong');
          name.className = 'article-product-name'; name.textContent = pick.name + ' ↗';
          const reason = document.createElement('span');
          reason.className = 'article-product-reason'; reason.textContent = pick.reason;
          info.append(brand, name, reason);
          if (pick.variantNote) {
            const note = document.createElement('span');
            note.className = 'article-product-reason'; note.textContent = pick.variantNote;
            info.append(note);
          }
          card.append(image, info); group.append(card);
        }
        slot.append(group);
      }
      return;
    }
    if (category === 'all' && !articleSlots.length) return;
    // Quick picks: the first pick for each section, so readers see an answer before the details.
    if (picks.length && !articleSlots.length) {
      const firsts = [];
      for (const pick of picks) if (!firsts.some(p => p.guideSection === pick.guideSection)) firsts.push(pick);
      const order = id => { const el = document.getElementById(id); return el ? [...document.querySelectorAll('.advice-row')].indexOf(el) : 99; };
      firsts.sort((x, y) => order(x.guideSection) - order(y.guideSection));
      const wrap = document.createElement('div');
      wrap.className = 'quick-picks';
      const h = document.createElement('h2');
      h.textContent = `Quick picks for ${market.name}`;
      const ul = document.createElement('ul');
      for (const pick of firsts) {
        const section = document.getElementById(pick.guideSection);
        const label = section?.querySelector('h2')?.textContent || pick.group;
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `#${pick.guideSection}`;
        const k = document.createElement('span'); k.className = 'qp-cat'; k.textContent = label;
        const n = document.createElement('span'); n.className = 'qp-name'; n.textContent = `${pick.brand} ${pick.name}`;
        a.append(k, n); li.append(a); ul.append(li);
      }
      const note = document.createElement('p');
      note.className = 'qp-note';
      note.textContent = 'Tap a pick to jump to what to look for and more options.';
      wrap.append(h, ul, note);
      list.append(wrap);
    }
    const sections = new Map();
    for (const pick of picks) {
      const guide = document.getElementById(pick.guideSection);
      const body = articleSlots.length ? articleSlots.find(slot => matchesSlot(slot, pick)) : guide?.querySelector('.advice-body');
      if (!body) continue;
      let examples = sections.get(body);
      if (!examples) {
        examples = document.createElement('section');
        examples.className = 'inline-picks';
        const heading = document.createElement('h3');
        heading.id = `examples-${pick.guideSection}`;
        heading.textContent = 'Options to consider';
        examples.setAttribute('aria-labelledby', heading.id);
        if (!articleSlots.length) examples.append(heading);
        else { examples.removeAttribute('aria-labelledby'); examples.setAttribute('aria-label', 'Optional product picks'); }
        body.append(examples);
        sections.set(body, examples);
      }
      const article = document.createElement('article');
      article.className = pick.imageStyle === 'catalog-photo' ? 'product catalog-photo' : 'product';
      const media = document.createElement('a');
      media.className = 'product-image-area';
      media.href = pick.url;
      media.target = '_blank';
      media.rel = 'sponsored noopener';
      media.setAttribute('aria-label', `${pick.brand} ${pick.name} on Amazon (affiliate link, opens a new tab)`);
      const image = productImage(pick, 640, 640, `${pick.brand} ${pick.name}`);
      media.append(image);
      const info = document.createElement('div'); info.className = 'product-info';
      const brand = document.createElement('p'); brand.className = 'brand-name'; brand.textContent = pick.brand;
      const name = document.createElement('h4'); name.className = 'product-name'; name.textContent = pick.name;
      const reason = document.createElement('p'); reason.className = 'product-desc'; reason.textContent = pick.reason;
      info.append(brand, name, reason);
      if (pick.variantNote) { const note = document.createElement('p'); note.className = 'variant-note'; note.textContent = pick.variantNote; info.append(note); }
      const link = document.createElement('a'); link.className = 'amazon-btn'; link.href = pick.url;
      link.target = '_blank'; link.rel = 'sponsored noopener'; link.textContent = `Details at ${new URL(pick.url).hostname.replace('www.', '')} ↗`;
      const label = document.createElement('span'); label.className = 'affiliate-label'; label.textContent = 'Affiliate link';
      info.append(link, label); article.append(media, info); examples.append(article);
    }
  }
  render();
  addEventListener('storage', event => {
    if (event.key !== key) return;
    setValue(valid(event.newValue) ? event.newValue : suggested || 'GLOBAL');
    hint.textContent = 'Country preference updated across the website.';
    render();
  });
  selects.forEach(el => el.addEventListener('change', () => {
    setValue(el.value);
    try {
      localStorage.setItem(key, select.value);
      hint.textContent = 'Country saved on this device. Change it anytime.';
    } catch (_) {
      hint.textContent = 'Selected for this page. Your browser is not allowing preferences to be saved.';
    }
    render();
  }));
})();


// Reading progress: each article remembers, in this browser only, how far you got and
// whether you finished it. The article text is split into 10 parts; a part counts as seen
// once it has been on screen for a few seconds while you were active. An article only counts
// as read when at least 9 of the 10 parts were seen AND you spent a realistic amount of active
// time on it (about 40% of its reading time, between 20 seconds and 3 minutes). Opening a page,
// scrolling straight to the bottom or leaving the tab open doesn't count.
// Lists of articles across the site show "✓ Read" or "40% read" next to each link.
(() => {
  'use strict';
  const KEY = 'trenesis.reading.v1';
  const page = location.pathname.split('/').pop() || 'index.html';
  const load = () => { try { const d = JSON.parse(localStorage.getItem(KEY) || '{}'); return d && typeof d === 'object' ? d : {}; } catch (_) { return {}; } };
  const save = d => { try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (_) {} };
  const fileOf = href => { try { const u = new URL(href, location.href); return u.origin === location.origin ? (u.pathname.split('/').pop() || 'index.html') : ''; } catch (_) { return ''; } };
  const PARTS = 10, DWELL = 3;
  const seen = e => (Array.isArray(e.s) ? e.s.filter(x => x >= DWELL).length : 0);
  const readLabel = e => e.r ? '✓ Read' : seen(e) >= 2 ? Math.min(90, seen(e) * 100 / PARTS) + '% read' : '';
  const announce = () => document.dispatchEvent(new CustomEvent('trenesis:read'));

  // ---- badges next to article links (lists, cards, plan boxes)
  const LINKS = '.reading-list a, .starter-links a, .quick-start a, a.text-link, .start-links a, .plan-next a';
  function badges() {
    const data = load();
    document.querySelectorAll('.read-badge.in-list').forEach(b => b.remove());
    document.querySelectorAll(LINKS).forEach(a => {
      if (a.closest('.article-body')) return;
      const e = data[fileOf(a.href)];
      if (!e) return;
      const label = readLabel(e);
      if (!label) return;
      const b = document.createElement('span');
      b.className = 'read-badge in-list ' + (e.r ? 'is-read' : 'is-started');
      b.textContent = label;
      const slot = a.querySelector('.mins');
      if (slot) { b.classList.add('in-meta'); slot.append(b); } else a.append(b);
    });
  }

  // ---- tracking on article pages
  const body = document.querySelector('.article .article-body');
  const meta = document.querySelector('.article .article-meta');
  if (body && meta) {
    const words = (body.innerText || body.textContent || '').trim().split(/\s+/).length;
    const needed = Math.max(20, Math.min(180, Math.round(words / 230 * 60 * 0.4)));
    const fresh = () => ({ s: new Array(PARTS).fill(0), at: 0, t: 0, r: 0 });
    const entry = () => { const e = load()[page]; if (!e || !Array.isArray(e.s) || e.s.length !== PARTS) return Object.assign(fresh(), e && e.r ? { r: e.r } : {}); return e; };
    const put = e => { const d = load(); d[page] = e; save(d); };
    let cur = entry();
    let lastActive = Date.now();
    let dirty = false;
    let paused = false; // after "Mark as unread", don't re-mark during this visit

    const bar = document.createElement('div');
    bar.className = 'read-progress';
    bar.setAttribute('aria-hidden', 'true');
    bar.append(document.createElement('span'));
    document.body.append(bar);

    const state = document.createElement('span');
    state.className = 'read-state';
    state.tabIndex = -1;
    const said = document.createElement('span');
    said.className = 'sr-only';
    said.setAttribute('role', 'status');
    meta.append(state, said);
    const calm = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

    function progressNow() {
      const r = body.getBoundingClientRect();
      if (r.height <= 0) return 0;
      return Math.max(0, Math.min(1, (innerHeight - r.top) / r.height));
    }
    function bodyOnScreen() {
      const r = body.getBoundingClientRect();
      return r.top < innerHeight && r.bottom > 0;
    }
    function drawState(fresh) {
      state.textContent = '';
      if (cur.r) {
        const t = document.createElement('span');
        t.className = 'read-badge is-read' + (fresh ? ' is-fresh' : '');
        t.innerHTML = '<span class="read-check" aria-hidden="true">✓</span> Read';
        const undo = document.createElement('button');
        undo.type = 'button';
        undo.className = 'read-undo';
        undo.textContent = 'Mark as unread';
        undo.addEventListener('click', unread);
        state.append(t, undo);
      } else {
        if (seen(cur) >= 2 && cur.at > 0.1 && cur.at < 0.95 && progressNow() < cur.at - 0.1) {
        const go = document.createElement('button');
        go.type = 'button';
        go.className = 'read-continue';
        go.textContent = `Continue where you left off (${Math.round(cur.at * 100)}%) ↓`;
        go.addEventListener('click', () => {
          const r = body.getBoundingClientRect();
          scrollTo({ top: scrollY + r.top + cur.at * r.height - innerHeight * 0.85, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
          go.remove();
        });
        state.append(go);
        }
        if (readLabel(cur)) {
          const progress = document.createElement('span');
          progress.className = 'read-badge is-started';
          progress.textContent = readLabel(cur);
          const reset = document.createElement('button');
          reset.type = 'button';
          reset.className = 'read-undo';
          reset.textContent = 'Mark as unread';
          reset.addEventListener('click', unread);
          state.append(progress, reset);
        }
      }
    }
    function unread() {
      const d = load(); delete d[page]; save(d);
      paused = true;
      cur = fresh();
      const gone = document.querySelectorAll('.read-state .read-badge, .read-done');
      gone.forEach(el => el.classList.add('is-leaving'));
      setTimeout(() => {
        document.querySelector('.read-done')?.remove();
        drawState(); announce();
        said.textContent = 'Marked as unread';
        state.focus({ preventScroll: true });
      }, gone.length && !calm() ? 180 : 0);
    }
    function finish() {
      cur.r = Date.now();
      put(cur);
      drawState(true);
      const note = document.createElement('p');
      note.className = 'read-done is-fresh';
      note.setAttribute('role', 'status');
      note.innerHTML = '<span><span class="read-check" aria-hidden="true">✓</span> Marked as read</span>';
      const undo = document.createElement('button');
      undo.type = 'button';
      undo.className = 'read-undo';
      undo.textContent = 'Undo';
      undo.addEventListener('click', unread);
      note.append(undo);
      body.after(note);
      announce();
    }
    function onScroll(e) {
      const p = progressNow();
      bar.firstChild.style.width = (p * 100).toFixed(1) + '%';
      if (e && !cur.r && !paused) { cur.at = p; dirty = true; } // only real scrolling moves the "left off" point
    }
    ['scroll', 'pointermove', 'pointerdown', 'keydown', 'wheel', 'touchstart'].forEach(ev =>
      addEventListener(ev, () => { lastActive = Date.now(); }, { passive: true }));
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll, { passive: true });

    let ticks = 0;
    setInterval(() => {
      if (cur.r || paused) return;
      const active = document.visibilityState === 'visible' && Date.now() - lastActive < 45000 && bodyOnScreen();
      const previousLabel = readLabel(cur);
      if (active) {
        cur.t = (cur.t || 0) + 1;
        // credit every part of the text that is currently on screen
        const r = body.getBoundingClientRect();
        for (let i = 0; i < PARTS; i++) {
          const mid = r.top + r.height * (i + 0.5) / PARTS;
          if (mid > 0 && mid < innerHeight) cur.s[i] = Math.min(99, cur.s[i] + 1);
        }
        dirty = true;
      }
      if (seen(cur) >= PARTS - 1 && cur.t >= needed) { finish(); return; }
      if (readLabel(cur) !== previousLabel) {
        put(cur);
        dirty = false;
        drawState();
        badges();
      }
      if (dirty && ++ticks % 5 === 0) { put(cur); dirty = false; badges(); }
    }, 1000);
    addEventListener('pagehide', () => { if (!cur.r && !paused && dirty) put(cur); });

    onScroll();
    drawState();
  }

  setTimeout(badges); // after the plan box below has been added
  document.addEventListener('trenesis:read', () => setTimeout(badges));
  document.addEventListener('trenesis:plan', () => setTimeout(badges));
  addEventListener('storage', e => { if (e.key === KEY) badges(); });
  addEventListener('pageshow', e => { if (e.persisted) badges(); });
})();


// "Your plan": the plan finder's result, saved in this browser and shown on every page.
// A button in the corner opens the list (read pages get a tick); on a page that is part of
// the plan, a box at the end points to the next step.
(() => {
  'use strict';
  const KEY = 'trenesis.plan.v1';
  const page = location.pathname.split('/').pop() || 'index.html';
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (_) { return null; } };
  const save = plan => { try { localStorage.setItem(KEY, JSON.stringify(plan)); } catch (_) {} };
  const file = href => href.split('#')[0];
  let root = null;

  // Articles only count once they've really been read (see the reading tracker above).
  // Other plan pages, like the calculator, count once opened.
  const isArticlePage = !!document.querySelector('.article .article-body') && !!document.querySelector('.article .article-meta');
  const readMap = () => { try { return JSON.parse(localStorage.getItem('trenesis.reading.v1') || '{}') || {}; } catch (_) { return {}; } };
  function markVisited(plan) {
    if (isArticlePage) return;
    if (plan.steps.some(s => file(s.href) === page) && !plan.visited.includes(page)) { plan.visited.push(page); save(plan); }
  }
  const isDoneFn = plan => { const read = readMap(); return f => !!(read[f] && read[f].r) || plan.visited.includes(f); };
  function nextStep(plan, isDone) { return plan.steps.find(s => !isDone(file(s.href))); }

  function render(openNow) {
    const plan = load();
    root?.remove(); root = null;
    document.querySelector('.plan-next')?.remove();
    if (!plan || !Array.isArray(plan.steps) || !plan.steps.length) return;
    if (!Array.isArray(plan.visited)) plan.visited = [];
    markVisited(plan);
    const isDone = isDoneFn(plan);
    const done = plan.steps.filter(s => isDone(file(s.href))).length;
    const upNext = nextStep(plan, isDone);

    root = document.createElement('div');
    root.className = 'plan-dock';
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'plan-toggle';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-controls', 'plan-panel');
    toggle.innerHTML = '<span class="plan-toggle-label">Your plan</span><span class="plan-toggle-count"></span>';
    toggle.querySelector('.plan-toggle-count').textContent = `${done} of ${plan.steps.length} read`;

    const panel = document.createElement('section');
    panel.id = 'plan-panel';
    panel.className = 'plan-panel';
    panel.hidden = true;
    panel.setAttribute('aria-label', 'Your plan');
    const head = document.createElement('div');
    head.className = 'plan-head';
    head.innerHTML = '<h2 tabindex="-1">Your plan</h2><button type="button" class="plan-close" aria-label="Close">×</button>';
    const intro = document.createElement('p');
    intro.className = 'plan-intro';
    intro.textContent = upNext ? 'Work through these in order. Articles get a tick once you’ve read them to the end.' : 'You’ve read everything in your plan. Nice work: now keep training consistently.';
    const ol = document.createElement('ol');
    ol.className = 'plan-steps';
    plan.steps.forEach((s, i) => {
      const li = document.createElement('li');
      const stepDone = isDone(file(s.href));
      li.className = stepDone ? 'is-done' : (s === upNext ? 'is-next' : '');
      const a = document.createElement('a');
      a.href = s.href;
      const mark = document.createElement('span');
      mark.className = 'plan-mark';
      mark.setAttribute('aria-hidden', 'true');
      mark.textContent = stepDone ? '' : String(i + 1);
      const txt = document.createElement('span');
      txt.className = 'plan-title';
      txt.textContent = s.title;
      a.append(mark, txt);
      if (stepDone) { const sr = document.createElement('span'); sr.className = 'sr-only'; sr.textContent = ' (read)'; a.append(sr); }
      if (s === upNext) { const tag = document.createElement('span'); tag.className = 'plan-tag'; tag.textContent = 'Next'; a.append(tag); }
      if (file(s.href) === page) a.setAttribute('aria-current', 'page');
      li.append(a); ol.append(li);
    });
    const foot = document.createElement('div');
    foot.className = 'plan-foot';
    foot.innerHTML = '<a href="find-your-plan.html">Retake the quiz</a><button type="button" class="plan-remove">Remove plan</button>';
    panel.append(head, intro, ol, foot);
    root.append(panel, toggle);
    document.body.append(root);

    const setOpen = open => {
      panel.hidden = !open;
      toggle.setAttribute('aria-expanded', String(open));
      root.classList.toggle('is-open', open);
      if (open) panel.querySelector('h2').focus();
    };
    toggle.addEventListener('click', () => setOpen(panel.hidden));
    head.querySelector('.plan-close').addEventListener('click', () => { setOpen(false); toggle.focus(); });
    root.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) { setOpen(false); toggle.focus(); } });
    foot.querySelector('.plan-remove').addEventListener('click', () => {
      try { localStorage.removeItem(KEY); } catch (_) {}
      root.remove(); root = null; document.querySelector('.plan-next')?.remove();
    });
    if (openNow) setOpen(true);

    // On a page that is part of the plan: point to the next unread step at the end of the content.
    const here = plan.steps.findIndex(s => file(s.href) === page);
    if (here !== -1 && upNext) {
      const box = document.createElement('aside');
      box.className = 'plan-next';
      box.setAttribute('aria-label', 'Next in your plan');
      const p = document.createElement('p');
      p.className = 'plan-next-label';
      p.textContent = `Next in your plan · step ${plan.steps.indexOf(upNext) + 1} of ${plan.steps.length}`;
      const a = document.createElement('a');
      a.className = 'btn';
      a.href = upNext.href;
      a.textContent = upNext.title;
      box.append(p, a);
      const anchor = document.querySelector('.article .nudge, .article .pdf-box, .calc, .finder-result');
      if (anchor && anchor.closest('.calc, .finder-result')) anchor.after(box);
      else if (anchor) anchor.before(box);
      else document.querySelector('main')?.append(box);
    }
  }

  render(false);
  document.addEventListener('trenesis:plan', () => render(false));
  document.addEventListener('trenesis:read', () => render(!!root && root.classList.contains('is-open')));
  window.addEventListener('pageshow', e => { if (e.persisted) render(false); });
})();




// Program waitlist forms. Set data-endpoint on the form to the email provider's form URL
// (for example a MailerLite embedded-form action) to switch them on. Until then they only explain.
(() => {
  'use strict';
  document.querySelectorAll('.waitlist-form').forEach(form => {
    const status = form.querySelector('.form-status');
    const input = form.querySelector('input[type="email"]');
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const email = (input.value || '').trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        status.textContent = 'Please enter a valid email address.';
        input.setAttribute('aria-invalid', 'true');
        input.focus();
        return;
      }
      input.removeAttribute('aria-invalid');
      const endpoint = form.dataset.endpoint;
      if (!endpoint) {
        // No email tool connected yet: open the visitor's email app with a ready-made message to us.
        const subject = encodeURIComponent('Waitlist: Trenesis 12-Week Program');
        const body = encodeURIComponent(`Hi Trenesis, please add ${email} to the waitlist for the 12-Week Program.`);
        location.href = `mailto:trenesisgym@gmail.com?subject=${subject}&body=${body}`;
        status.textContent = 'Your email app should open with a message to us. Press Send and you’re on the list.';
        return;
      }
      const btn = form.querySelector('button');
      btn.disabled = true;
      try {
        const body = new FormData();
        body.append('fields[email]', email);
        await fetch(endpoint, { method: 'POST', body, mode: 'no-cors' });
        form.classList.add('is-done');
        status.textContent = 'You’re on the list. Check your inbox to confirm your email.';
        input.value = '';
      } catch (_) {
        status.textContent = 'Something went wrong. Please try again, or email trenesisgym@gmail.com.';
      } finally {
        btn.disabled = false;
      }
    });
  });
})();

// Tools menu in the header: click to open, Escape or a click elsewhere closes it.
(() => {
  'use strict';
  document.querySelectorAll('.nav-menu').forEach(menu => {
    const btn = menu.querySelector('.nav-menu-btn');
    if (!btn) return;
    const set = open => { menu.classList.toggle('is-open', open); btn.setAttribute('aria-expanded', String(open)); };
    btn.addEventListener('click', e => { e.stopPropagation(); set(!menu.classList.contains('is-open')); });
    document.addEventListener('click', e => { if (!menu.contains(e.target)) set(false); });
    menu.addEventListener('keydown', e => { if (e.key === 'Escape') { set(false); btn.focus(); } });
    menu.addEventListener('focusout', e => { if (!menu.contains(e.relatedTarget)) set(false); });
  });
})();


// Article sidebar: highlight the section you're reading.
(() => {
  'use strict';
  const links = [...document.querySelectorAll('.side-toc a')];
  if (!links.length || !('IntersectionObserver' in window)) return;
  const byId = new Map(links.map(a => [decodeURIComponent(a.hash.slice(1)), a]));
  const heads = [...byId.keys()].map(id => document.getElementById(id)).filter(Boolean);
  const set = id => links.forEach(a => a.classList.toggle('is-current', a === byId.get(id)));
  const io = new IntersectionObserver(() => {
    let current = heads[0];
    for (const h of heads) if (h.getBoundingClientRect().top < innerHeight * 0.3) current = h;
    if (current) set(current.id);
  }, { rootMargin: '0px 0px -60% 0px', threshold: [0, 1] });
  heads.forEach(h => io.observe(h));
  addEventListener('scroll', () => { let c = heads[0]; for (const h of heads) if (h.getBoundingClientRect().top < innerHeight * 0.3) c = h; if (c) set(c.id); }, { passive: true });
})();

// Product photos that can't load get a quiet placeholder instead of a broken-image box.
document.addEventListener('error', e => {
  const img = e.target;
  if (!(img instanceof HTMLImageElement) || !img.closest('.article-product-pick, .product-image-area')) return;
  img.replaceWith(window.trenesisImgFallback());
}, true);


// Tables wider than the screen fade out on the right until you've swiped to the end.
(() => {
  'use strict';
  const wraps = [...document.querySelectorAll('.table-wrap')];
  const check = w => { const s = w.scrollWidth > w.clientWidth + 2; w.classList.toggle('scrolls', s); w.classList.toggle('at-end', !s || w.scrollLeft + w.clientWidth >= w.scrollWidth - 4); };
  wraps.forEach(w => { check(w); w.addEventListener('scroll', () => check(w), { passive: true }); });
  addEventListener('resize', () => wraps.forEach(check), { passive: true });
})();

// Plan tables: tap an exercise name to show its how-to cues (and a short clip, if there is one).
(() => {
  'use strict';
  const calm = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  function loadClip(v) {
    if (v.dataset.loaded) return;
    v.querySelectorAll('source[data-src]').forEach(s => { s.src = s.dataset.src; });
    v.dataset.loaded = '1';
    v.load();
  }
  function setPlaying(fig, on) {
    const v = fig.querySelector('video'), b = fig.querySelector('.ex-play');
    if (!v) return;
    if (on) { loadClip(v); const p = v.play(); if (p && p.catch) p.catch(() => fig.classList.remove('is-playing')); }
    else v.pause();
    fig.classList.toggle('is-playing', on);
    const name = (v.getAttribute('aria-label') || '').replace(/^Silent clip: /, '');
    b.setAttribute('aria-label', (on ? 'Pause clip of ' : 'Play clip of ') + name);
  }
  document.addEventListener('click', e => {
    const play = e.target.closest('.ex-play');
    if (play) { const fig = play.closest('.ex-clip'); setPlaying(fig, !fig.classList.contains('is-playing')); return; }
    const t = e.target.closest('.ex-toggle');
    if (!t) return;
    const detail = document.getElementById(t.getAttribute('aria-controls'));
    if (!detail) return;
    const open = t.getAttribute('aria-expanded') !== 'true';
    t.setAttribute('aria-expanded', String(open));
    t.closest('tr').classList.toggle('is-open', open);
    detail.hidden = !open;
    if (open) { detail.classList.remove('is-fresh'); void detail.offsetWidth; detail.classList.add('is-fresh'); }
    // Clips play when you open the exercise (never on their own); with reduced motion you see the poster and a play button.
    detail.querySelectorAll('.ex-clip').forEach(fig => {
      if (!open) setPlaying(fig, false);
      else if (calm()) { loadClip(fig.querySelector('video')); fig.classList.add('is-ready'); }
      else setPlaying(fig, true);
    });
  });
})();

// Home hero video (only present when assets/hero/hero.mp4 exists): fetched after the page has loaded,
// never with reduced motion (the poster stays), paused while off screen, with a pause button.
(() => {
  'use strict';
  const box = document.querySelector('.hero-media'), v = box && box.querySelector('video');
  if (!v || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const btn = box.querySelector('.hero-pause');
  let userPaused = false;
  const start = () => {
    const narrow = matchMedia('(max-width: 700px)').matches;
    v.src = (narrow && v.dataset.srcPortrait) || v.dataset.src;
    v.addEventListener('playing', () => { box.classList.add('is-playing'); btn.hidden = false; }, { once: true });
    v.play().catch(() => {});
    if ('IntersectionObserver' in window) new IntersectionObserver(es => {
      if (userPaused) return;
      if (es[0].isIntersecting) v.play().catch(() => {}); else v.pause();
    }).observe(box);
  };
  btn.addEventListener('click', () => {
    userPaused = !userPaused;
    if (userPaused) v.pause(); else v.play().catch(() => {});
    btn.setAttribute('aria-pressed', String(userPaused));
    btn.textContent = userPaused ? 'Play video' : 'Pause video';
  });
  if (document.readyState === 'complete') setTimeout(start, 300); else addEventListener('load', () => setTimeout(start, 300), { once: true });
})();
