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
  const select = document.querySelector('#country');
  if (!select) return;
  select.disabled = false;
  const markets = window.TRENESIS_MARKETS || {};
  const key = 'trenesis.delivery-country.v1';
  const hint = document.querySelector('#country-hint');
  const title = document.querySelector('#market-title');
  const detail = document.querySelector('#market-detail');
  const list = document.querySelector('#local-picks');
  const category = document.querySelector('[data-category]')?.dataset.category || 'all';
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
  select.value = valid(saved) ? saved : suggested || 'GLOBAL';
  hint.textContent = valid(saved) ? 'Using your saved country. Change it anytime.' : suggested ? (nearest ? 'The closest store we cover to your region. You can change it anytime.' : 'Suggested from your browser region. You can change it anytime.') : 'Choose your country; your preference stays on this device.';
  function render() {
    if (!title || !detail || !list) return;
    const code = valid(select.value) ? select.value : 'GLOBAL';
    const market = markets[code];
    const picks = category === 'all' ? ['equipment', 'supplements', 'accessories'].flatMap(c => market[c] || []) : (market[category] || []);
    list.replaceChildren();
    document.querySelectorAll('.inline-picks').forEach(el => el.remove());
    title.textContent = picks.length ? (category === 'all' ? `Showing picks for ${market.name} inside each guide below.` : `Examples for ${market.name}`) : code === 'GLOBAL' ? 'We don’t have picks for your country yet. Choose the closest country at the top of the page to see examples.' : `Product examples for ${market.name} are coming soon.`;
    detail.hidden = picks.length > 0;
    detail.textContent = picks.length ? '' : 'The buying advice on this page applies wherever you live.';
    document.querySelectorAll('.affiliate-disclosure').forEach(el => { el.hidden = !picks.length; });
    if (category === 'all') return;
    // Quick picks: the first pick for each section, so readers see an answer before the details.
    if (picks.length) {
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
      const body = guide?.querySelector('.advice-body');
      if (!body) continue;
      let examples = sections.get(pick.guideSection);
      if (!examples) {
        examples = document.createElement('section');
        examples.className = 'inline-picks';
        const heading = document.createElement('h3');
        heading.id = `examples-${pick.guideSection}`;
        heading.textContent = 'Options to consider';
        examples.setAttribute('aria-labelledby', heading.id);
        examples.append(heading);
        body.append(examples);
        sections.set(pick.guideSection, examples);
      }
      const article = document.createElement('article');
      article.className = pick.imageStyle === 'catalog-photo' ? 'product catalog-photo' : 'product';
      const media = document.createElement('a');
      media.className = 'product-image-area';
      media.href = pick.url;
      media.target = '_blank';
      media.rel = 'sponsored noopener';
      media.setAttribute('aria-label', `${pick.brand} ${pick.name} on Amazon (affiliate link, opens a new tab)`);
      const image = document.createElement('img');
      image.src = pick.image;
      image.alt = `${pick.brand} ${pick.name}`;
      image.width = 1280; image.height = 720; image.loading = 'lazy';
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
  select.addEventListener('change', () => {
    try {
      localStorage.setItem(key, select.value);
      hint.textContent = 'Country saved on this device. Change it anytime.';
    } catch (_) {
      hint.textContent = 'Selected for this page. Your browser is not allowing preferences to be saved.';
    }
    render();
  });
})();

// Calculator suggestion: a small card in the corner, once per visit, after the reader
// has scrolled halfway or spent 20 seconds on the page. Closing it hides it for 14 days;
// opening the calculator hides it for 30 days. Never shown on the calculator itself.
(() => {
  'use strict';
  const page = location.pathname.split('/').pop() || 'index.html';
  if (['calculator.html', 'privacy.html'].includes(page)) return;
  try { if (localStorage.getItem('trenesis.plan.v1')) return; } catch (_) {}
  const KEY = 'trenesis.calc-promo.v1', DAY = 864e5;
  let store = null;
  try { store = window.localStorage; sessionStorage.getItem(KEY); } catch (_) { return; }
  try {
    const until = Number(store.getItem(KEY) || 0);
    if (until > Date.now() || sessionStorage.getItem(KEY)) return;
  } catch (_) { return; }
  const remember = days => { try { store.setItem(KEY, String(Date.now() + days * DAY)); } catch (_) {} };

  function show() {
    if (document.querySelector('.calc-promo')) return;
    try { sessionStorage.setItem(KEY, '1'); } catch (_) {}
    const box = document.createElement('aside');
    box.className = 'calc-promo';
    box.setAttribute('aria-label', 'Calculator suggestion');
    box.innerHTML =
      '<button class="calc-promo-close" type="button" aria-label="Close">×</button>' +
      '<p class="calc-promo-title">How much should you eat?</p>' +
      '<p class="calc-promo-text">Get your daily calories and protein in 30 seconds, in kg or lb.</p>' +
      '<a class="btn calc-promo-btn" href="calculator.html">Open the calculator</a>';
    const close = () => {
      box.classList.remove('is-in');
      setTimeout(() => box.remove(), 250);
    };
    box.querySelector('.calc-promo-close').addEventListener('click', () => { remember(14); close(); });
    box.querySelector('.calc-promo-btn').addEventListener('click', () => remember(30));
    box.addEventListener('keydown', e => { if (e.key === 'Escape') { remember(14); close(); } });
    document.body.append(box);
    requestAnimationFrame(() => requestAnimationFrame(() => box.classList.add('is-in')));
  }

  let timer = setTimeout(trigger, 20000);
  function onScroll() {
    const doc = document.documentElement;
    const seen = (window.scrollY + window.innerHeight) / doc.scrollHeight;
    if (seen > 0.5) trigger();
  }
  function trigger() {
    clearTimeout(timer);
    window.removeEventListener('scroll', onScroll);
    show();
  }
  window.addEventListener('scroll', onScroll, { passive: true });
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

  function markVisited(plan) {
    if (plan.steps.some(s => file(s.href) === page) && !plan.done.includes(page)) { plan.done.push(page); save(plan); }
  }
  function nextStep(plan) { return plan.steps.find(s => !plan.done.includes(file(s.href))); }

  function render(openNow) {
    const plan = load();
    root?.remove(); root = null;
    document.querySelector('.plan-next')?.remove();
    if (!plan || !Array.isArray(plan.steps) || !plan.steps.length) return;
    if (!Array.isArray(plan.done)) plan.done = [];
    markVisited(plan);
    const done = plan.steps.filter(s => plan.done.includes(file(s.href))).length;
    const upNext = nextStep(plan);

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
    intro.textContent = upNext ? 'Work through these in order. Pages you’ve opened get a tick.' : 'You’ve read everything in your plan. Nice work: now keep training consistently.';
    const ol = document.createElement('ol');
    ol.className = 'plan-steps';
    plan.steps.forEach((s, i) => {
      const li = document.createElement('li');
      const isDone = plan.done.includes(file(s.href));
      li.className = isDone ? 'is-done' : (s === upNext ? 'is-next' : '');
      const a = document.createElement('a');
      a.href = s.href;
      const mark = document.createElement('span');
      mark.className = 'plan-mark';
      mark.setAttribute('aria-hidden', 'true');
      mark.textContent = isDone ? '' : String(i + 1);
      const txt = document.createElement('span');
      txt.className = 'plan-title';
      txt.textContent = s.title;
      a.append(mark, txt);
      if (isDone) { const sr = document.createElement('span'); sr.className = 'sr-only'; sr.textContent = ' (read)'; a.append(sr); }
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
  window.addEventListener('pageshow', e => { if (e.persisted) render(false); });
})();
