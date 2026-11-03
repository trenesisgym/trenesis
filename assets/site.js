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
  const key = 'trenesis.review-country.v1';
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

