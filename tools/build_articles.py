#!/usr/bin/env python3
"""Build the article pages from content/articles/*.md.

Usage (from the repository root):
    pip install markdown
    python3 tools/build_articles.py

Each Markdown file starts with a header between --- lines (slug, title,
description, section, guide, related). The script writes <slug>.html,
articles.html, the article lists on training.html and nutrition.html,
and sitemap.xml. Edit the .md files, never the generated .html files.
"""
import html, math, pathlib, re, sys, datetime
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'content' / 'articles'
BASE = 'https://trenesisgym.github.io/trenesis/'
VERSION = '20261031-relaunch'
UPDATED = datetime.date(2026, 10, 31)

GUIDES = {
    'strength': ('Strength Training Guide', 'pdfs/strength-training.pdf', 'Training'),
    'cardio': ('Cardio Training Guide', 'pdfs/cardio.pdf', 'Training'),
    'nutrition': ('Nutrition Basics Guide', 'pdfs/nutrition-basics.pdf', 'Nutrition'),
    'meal': ('Meal Planning Guide', 'pdfs/meal-planning.pdf', 'Nutrition'),
}
SECTION_PAGE = {'Training': 'training.html', 'Nutrition': 'nutrition.html'}
GUIDE_ORDER = ['strength', 'cardio', 'nutrition', 'meal']
GROUP_LABEL = {'strength': 'Strength training', 'cardio': 'Cardio', 'nutrition': 'Nutrition basics', 'meal': 'Meal planning'}
# Reading order inside each guide.
ORDER = [
    'strength-training-basics', 'how-to-build-a-workout-program', 'best-exercises-for-each-muscle', 'recovery-and-sleep', 'strength-training-mistakes',
    'cardio-for-lifters', 'heart-rate-zones', 'cardio-plans',
    'calories-and-tdee', 'how-much-protein', 'carbs-and-fats', 'supplements-that-work',
    'meal-planning-basics', 'fat-loss-meal-tips', 'weight-gain-meal-tips',
]

def esc(s):
    return html.escape(s, quote=True)

def load():
    arts = {}
    for f in sorted(SRC.glob('*.md')):
        text = f.read_text(encoding='utf-8')
        m = re.match(r'---\n(.*?)\n---\n(.*)', text, re.S)
        if not m:
            sys.exit(f'{f.name}: missing header')
        meta = dict(line.split(': ', 1) for line in m.group(1).splitlines() if line.strip())
        meta['related'] = [r.strip() for r in meta.get('related', '').split(',') if r.strip()]
        meta['body'] = m.group(2)
        meta['words'] = len(re.findall(r'\w+', m.group(2)))
        meta['minutes'] = max(2, math.ceil(meta['words'] / 220))
        arts[meta['slug']] = meta
    missing = [s for s in ORDER if s not in arts] + [s for s in arts if s not in ORDER]
    if missing:
        sys.exit(f'ORDER and content/articles disagree: {missing}')
    for a in arts.values():
        for r in a['related']:
            if r not in arts:
                sys.exit(f"{a['slug']}: unknown related article {r}")
    return arts

def header(current):
    cur = ' aria-current="page"'
    links = ''.join(
        f'<a href="{href}"{cur if name == current else ""}>{name}</a>'
        for name, href in [('Home', 'index.html'), ('Training', 'training.html'), ('Nutrition', 'nutrition.html'), ('Products', 'products.html')])
    return ('<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="nav-wrap">'
            '<a class="brand" href="index.html" aria-label="Trenesis home"><img src="assets/img/logo.webp" alt="" width="40" height="40"><span>TRENESIS</span></a>'
            '<button class="menu-toggle" hidden aria-expanded="false" aria-controls="navigation" aria-label="Open navigation menu">Menu <span aria-hidden="true">☰</span></button>'
            f'<nav id="navigation" aria-label="Main navigation">{links}</nav></div></header>')

FOOTER = ('<footer class="site-footer"><div class="footer-top"><div><a class="brand" href="index.html">TRENESIS</a></div>'
          '<div class="footer-links"><a href="articles.html">Articles</a><a href="about.html">About</a><a href="privacy.html">Privacy</a>'
          '<a href="index.html#guides">Free PDF guides</a>'
          '<a href="https://www.instagram.com/trenesisgym/" target="_blank" rel="noopener noreferrer">Instagram ↗</a>'
          '<a href="https://www.tiktok.com/@trenesis.gym" target="_blank" rel="noopener noreferrer">TikTok ↗</a>'
          '<a href="https://www.youtube.com/@TrenesisGym" target="_blank" rel="noopener noreferrer">YouTube ↗</a></div></div>'
          '<div class="footer-bottom"><span>© <span data-year>2026</span> Trenesis</span><span>Training, nutrition &amp; performance</span></div></footer>')

def head(title, desc, path, og_type='website', extra=''):
    url = BASE + path
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="theme-color" content="#0F1113">'
            f'<link rel="canonical" href="{url}"><meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Trenesis">'
            f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">'
            f'<meta property="og:image" content="{BASE}assets/img/share.jpg"><meta name="twitter:card" content="summary_large_image">'
            '<link rel="icon" href="assets/img/favicon.png"><link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">'
            '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">'
            f'<link rel="stylesheet" href="assets/site.css?v={VERSION}"><link rel="stylesheet" href="assets/refinement.css?v={VERSION}">'
            f'<link rel="stylesheet" href="assets/article.css?v={VERSION}"><script defer src="assets/site.js?v={VERSION}"></script>{extra}</head>')

def render_body(md_text):
    out = markdown.markdown(md_text, extensions=['tables', 'attr_list', 'toc'], output_format='html')
    out = out.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    # Blockquotes are callouts: the first bold line is the label.
    out = re.sub(r'<blockquote>\s*<p><strong>(.*?)</strong>\s*', r'<aside class="callout-note"><p class="callout-label">\1</p><p>', out)
    out = out.replace('</blockquote>', '</aside>')
    # External links open in a new tab.
    out = re.sub(r'<a href="(https?://[^"]+)">', r'<a href="\1" target="_blank" rel="noopener noreferrer">', out)
    return out

def card(a):
    return (f'<a class="article-card" href="{a["slug"]}.html"><span class="article-card-kicker">{GROUP_LABEL[a["guide"]]} · {a["minutes"]} min read</span>'
            f'<span class="article-card-title">{esc(a["title"])}</span><span class="article-card-desc">{esc(a["description"])}</span></a>')

def article_page(a, arts):
    gname, gpdf, section = GUIDES[a['guide']]
    jsonld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article",'
              f'"headline":{json_str(a["title"])},"description":{json_str(a["description"])},'
              f'"dateModified":"{UPDATED.isoformat()}","mainEntityOfPage":"{BASE}{a["slug"]}.html",'
              f'"image":"{BASE}assets/img/share.jpg","author":{{"@type":"Organization","name":"Trenesis"}},'
              '"publisher":{"@type":"Organization","name":"Trenesis"}}</script>')
    related = ''.join(card(arts[r]) for r in a['related'])
    return (head(f'{a["title"]} | Trenesis', a['description'], f'{a["slug"]}.html', 'article', jsonld) + '<body>' + header(section) +
            '<main id="main" tabindex="-1"><article class="article wrap">'
            f'<a class="back" href="{SECTION_PAGE[section]}">← {section}</a>'
            f'<header class="article-head"><p class="eyebrow">{GROUP_LABEL[a["guide"]]}</p><h1>{esc(a["title"])}</h1>'
            f'<p class="article-lead">{esc(a["description"])}</p>'
            f'<p class="article-meta">{a["minutes"]} min read · Updated {UPDATED.strftime("%B %Y")}</p></header>'
            f'<div class="article-body">{render_body(a["body"])}</div>'
            f'<aside class="guide-cta"><div><p class="eyebrow">Free PDF</p><h2>Get the full {gname}</h2>'
            '<p>Every chapter in one printable PDF, free to download.</p></div>'
            f'<a class="button" href="{gpdf}" target="_blank" rel="noopener noreferrer">Download the PDF</a></aside>'
            '<p class="article-disclaimer">This article is for general education and isn\'t medical advice. '
            'If you have an injury or a health condition, check with a doctor or physiotherapist before changing your training or diet.</p>'
            f'<section class="related" aria-labelledby="related-title"><h2 id="related-title">Keep reading</h2><div class="article-grid">{related}</div></section>'
            '</article></main>' + FOOTER + '</body></html>\n')

def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False)

def grouped(arts, guides):
    parts = []
    for g in guides:
        items = [arts[s] for s in ORDER if arts[s]['guide'] == g]
        parts.append(f'<h3 class="article-group">{GROUP_LABEL[g]}</h3><div class="article-grid">{"".join(card(a) for a in items)}</div>')
    return ''.join(parts)

def index_page(arts):
    body = ''.join(
        f'<section class="article-section" aria-labelledby="sec-{s.lower()}"><h2 id="sec-{s.lower()}">{s}</h2>'
        + grouped(arts, [g for g in GUIDE_ORDER if GUIDES[g][2] == s]) + '</section>'
        for s in ['Training', 'Nutrition'])
    desc = 'Every Trenesis article in one place: strength training, cardio, nutrition and meal planning, explained simply and based on evidence.'
    return (head('Articles | Trenesis', desc, 'articles.html') + '<body>' + header('') +
            '<main id="main" tabindex="-1"><div class="article wrap article-index">'
            '<header class="article-head"><p class="eyebrow">Read online</p><h1>Articles</h1>'
            '<p class="article-lead">Everything from our free guides, broken into short articles you can read on your phone between sets.</p></header>'
            f'{body}</div></main>' + FOOTER + '</body></html>\n')

def inject_list(page, arts, guides):
    p = ROOT / page
    s = p.read_text(encoding='utf-8')
    block = ('<!-- articles:start (generated by tools/build_articles.py) -->'
             '<div class="section-header"><h2>Read online</h2><div class="line"></div></div>'
             f'<section class="page-articles">{grouped(arts, guides)}</section><!-- articles:end -->')
    if '<!-- articles:start' in s:
        s = re.sub(r'<!-- articles:start.*?<!-- articles:end -->', block, s, flags=re.S)
    else:
        s = s.replace('<div class="line footer-divider"></div>', block + '\n\n  <div class="line footer-divider"></div>', 1)
    s = s.replace('<link rel="stylesheet" href="assets/refinement.css', f'<link rel="stylesheet" href="assets/article.css?v={VERSION}"><link rel="stylesheet" href="assets/refinement.css', 1) if 'article.css' not in s else s
    p.write_text(s, encoding='utf-8')

def sitemap(arts):
    pages = ['', 'training.html', 'nutrition.html', 'articles.html', 'products.html', 'equipment.html', 'supplements.html',
             'accessories.html', 'about.html'] + [f'{s}.html' for s in ORDER]
    urls = ''.join(f'<url><loc>{BASE}{p}</loc><lastmod>{UPDATED.isoformat()}</lastmod></url>' for p in pages)
    (ROOT / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding='utf-8')

def main():
    arts = load()
    for a in arts.values():
        (ROOT / f'{a["slug"]}.html').write_text(article_page(a, arts), encoding='utf-8')
    (ROOT / 'articles.html').write_text(index_page(arts), encoding='utf-8')
    inject_list('training.html', arts, ['strength', 'cardio'])
    inject_list('nutrition.html', arts, ['nutrition', 'meal'])
    sitemap(arts)
    print(f'built {len(arts)} articles, articles.html, sitemap.xml')

if __name__ == '__main__':
    main()
