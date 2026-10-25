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
  // A regional language preference is a hint, never a claim of physical location.
  for (const language of navigator.languages || [navigator.language]) {
    try {
      const region = new Intl.Locale(language).region;
      if (region && valid(region)) { suggested = region; break; }
    } catch (_) { /* malformed/unsupported locale */ }
  }
  select.value = valid(saved) ? saved : suggested || 'GLOBAL';
  hint.textContent = valid(saved) ? 'Using your saved country. Change it anytime.' : suggested ? 'Suggested from your browser region. You can change it anytime.' : 'Choose your country; your preference stays on this device.';
  function render() {
    if (!title || !detail || !list) return;
    const code = valid(select.value) ? select.value : 'GLOBAL';
    const market = markets[code];
    const picks = category === 'all' ? ['equipment', 'supplements', 'accessories'].flatMap(c => market[c] || []) : (market[category] || []);
    list.replaceChildren();
    document.querySelectorAll('.inline-picks').forEach(el => el.remove());
    title.textContent = picks.length ? `Examples for ${market.name}` : code === 'GLOBAL' ? 'Choose your country to see local product examples.' : `Product examples for ${market.name} are coming soon.`;
    detail.textContent = picks.length ? category === 'all' ? 'Start with a buying guide. Relevant product examples follow each recommendation.' : 'Product examples appear alongside the advice below. Check current options and delivery on Amazon.' : 'The buying advice is available for everyone. Local product examples are currently available for the USA and Germany.';
    document.querySelectorAll('.affiliate-disclosure').forEach(el => { el.hidden = !picks.length; });
    if (category === 'all') return;
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
      link.target = '_blank'; link.rel = 'sponsored noopener'; link.textContent = code === 'DE' ? 'Details at Amazon.de ↗' : 'Details at Amazon.com ↗';
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
