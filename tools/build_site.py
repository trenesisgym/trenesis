#!/usr/bin/env python3
"""Build every page of the Trenesis website.

Usage, from the repository root:
    pip install markdown
    python3 tools/build_site.py

What it reads:
    content/articles/*.md   the articles (header between --- lines, then Markdown)
    content/pages/*.md      About and Privacy
    content/gear/*.html     the body of the Equipment, Supplements and Accessories pages

What it writes: every .html page in the root, plus sitemap.xml.
Edit the content files or this script, never the generated .html files:
the next build overwrites them. See tools/README.md.
"""
import datetime
import html
import json
import math
import pathlib
import re
import sys

import markdown

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import template_parts as T

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://trenesisgym.github.io/trenesis/'
VERSION = '20261031-redesign'
UPDATED = datetime.date(2026, 10, 31)

GUIDES = {
    'strength': {'name': 'Strength Training Guide', 'pdf': 'pdfs/strength-training.pdf', 'pages': 12, 'hub': 'Training', 'group': 'Strength training'},
    'cardio': {'name': 'Cardio Training Guide', 'pdf': 'pdfs/cardio.pdf', 'pages': 9, 'hub': 'Training', 'group': 'Cardio'},
    'nutrition': {'name': 'Nutrition Basics Guide', 'pdf': 'pdfs/nutrition-basics.pdf', 'pages': 9, 'hub': 'Nutrition', 'group': 'Nutrition basics'},
    'meal': {'name': 'Meal Planning Guide', 'pdf': 'pdfs/meal-planning.pdf', 'pages': 11, 'hub': 'Nutrition', 'group': 'Meal planning'},
}
HUB_PAGE = {'Training': 'training.html', 'Nutrition': 'nutrition.html'}
# Reading order. A new article must be added here.
ORDER = [
    'strength-training-basics', 'how-to-build-a-workout-program', 'best-exercises-for-each-muscle', 'recovery-and-sleep', 'strength-training-mistakes',
    'cardio-for-lifters', 'heart-rate-zones', 'cardio-plans',
    'calories-and-tdee', 'how-much-protein', 'carbs-and-fats', 'supplements-that-work',
    'meal-planning-basics', 'fat-loss-meal-tips', 'weight-gain-meal-tips',
]
SOCIAL = [('Instagram', 'https://www.instagram.com/trenesisgym/'), ('TikTok', 'https://www.tiktok.com/@trenesis.gym'), ('YouTube', 'https://www.youtube.com/@TrenesisGym')]
COUNTRIES = [('GLOBAL', '🌐 Other'), ('US', '🇺🇸 USA'), ('DE', '🇩🇪 Germany'), ('GB', '🇬🇧 UK'), ('FR', '🇫🇷 France'), ('CA', '🇨🇦 Canada'), ('IT', '🇮🇹 Italy'), ('ES', '🇪🇸 Spain')]


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- shared parts

def head(title, desc, path, og_type='website', extra=''):
    url = BASE + ('' if path == 'index.html' else path)
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="theme-color" content="#0f1113">'
        f'<link rel="canonical" href="{url}"><meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Trenesis">'
        f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">'
        f'<meta property="og:image" content="{BASE}assets/img/share.jpg"><meta name="twitter:card" content="summary_large_image">'
        '<link rel="icon" href="assets/img/favicon.png"><link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">'
        f'<link rel="stylesheet" href="assets/styles.css?v={VERSION}">{extra}{T.FORM_SCRIPT}'
        f'<script defer src="assets/site.js?v={VERSION}"></script>'
        "<script>if('serviceWorker' in navigator&&window.isSecureContext){addEventListener('load',()=>{navigator.serviceWorker.register(new URL('sw.js',document.baseURI),{updateViaCache:'none'}).catch(()=>{})},{once:true})}</script>"
        '</head>'
    )


def header(current, country=False):
    items = [('Training', 'training.html'), ('Nutrition', 'nutrition.html'), ('Articles', 'articles.html'), ('Gear', 'products.html'), ('Program', 'program.html'), ('About', 'about.html')]
    here = ' aria-current="page"'
    links = ''.join(f'<a href="{href}"{here if name == current else ""}>{name}</a>' for name, href in items)
    picker = ''
    if country:
        opts = ''.join(f'<option value="{c}">{label}</option>' for c, label in COUNTRIES)
        picker = ('<div class="country-picker"><label class="sr-only" for="country">Country</label>'
                  f'<select disabled id="country" aria-describedby="country-hint">{opts}</select>'
                  '<span id="country-hint" class="sr-only">Select your country. Your choice is remembered on this device.</span></div>')
    return (
        '<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="nav-wrap wrap">'
        '<a class="brand" href="index.html" aria-label="Trenesis home"><img src="assets/img/logo.webp" alt="" width="38" height="38"><span>TRENESIS</span></a>'
        f'<nav id="navigation" aria-label="Main navigation">{links}</nav>{picker}'
        '<button class="menu-toggle" hidden aria-expanded="false" aria-controls="navigation" aria-label="Open navigation menu">Menu</button>'
        '</div></header>' + T.BANNER
    )


def footer():
    social = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener noreferrer">{n}</a></li>' for n, u in SOCIAL)
    return (
        '<footer class="site-footer"><div class="wrap"><div class="footer-grid">'
        '<div class="footer-about"><a class="brand" href="index.html"><img src="assets/img/logo.webp" alt="" width="38" height="38"><span>TRENESIS</span></a>'
        '<p>Free, evidence-based guides to training and nutrition. No hype, just what works.</p></div>'
        '<div class="footer-col"><h2>Learn</h2><ul><li><a href="training.html">Training</a></li><li><a href="nutrition.html">Nutrition</a></li>'
        '<li><a href="articles.html">All articles</a></li><li><a href="home-gym-on-a-budget.html">Home gym on a budget</a></li><li><a href="index.html#guides">Free guides</a></li></ul></div>'
        '<div class="footer-col"><h2>Trenesis</h2><ul><li><a href="about.html">About</a></li><li><a href="products.html">Gear</a></li>'
        '<li><a href="program.html">Beginner program</a></li><li><a href="work-with-us.html">Work with us</a></li><li><a href="privacy.html">Privacy</a></li></ul></div>'
        f'<div class="footer-col"><h2>Follow</h2><ul>{social}</ul></div></div>'
        f'<div class="footer-note"><span>© <span data-year>{UPDATED.year}</span> Trenesis</span>'
        '<span>Some gear links are affiliate links. We earn a small commission at no extra cost to you.</span></div>'
        '</div></footer></body></html>\n'
    )


def page(title, desc, path, current, main, og_type='website', extra='', country=False):
    if country:
        extra += f'<script defer src="assets/catalogs.js?v={VERSION}"></script>'
    return head(title, desc, path, og_type, extra) + header(current, country) + f'<main id="main" tabindex="-1">{main}</main>' + footer()


# ---------------------------------------------------------------- content

def load_articles():
    arts = {}
    for f in sorted((ROOT / 'content' / 'articles').glob('*.md')):
        m = re.match(r'---\n(.*?)\n---\n(.*)', f.read_text(encoding='utf-8'), re.S)
        if not m:
            sys.exit(f'{f.name}: missing header')
        meta = dict(line.split(': ', 1) for line in m.group(1).splitlines() if line.strip())
        meta['related'] = [r.strip() for r in meta.get('related', '').split(',') if r.strip()]
        meta['body'] = m.group(2)
        meta['minutes'] = max(2, math.ceil(len(re.findall(r'\w+', m.group(2))) / 220))
        arts[meta['slug']] = meta
    diff = [s for s in ORDER if s not in arts] + [s for s in arts if s not in ORDER]
    if diff:
        sys.exit(f'ORDER in tools/build_site.py and content/articles disagree: {diff}')
    for a in arts.values():
        bad = [r for r in a['related'] if r not in arts]
        if bad:
            sys.exit(f"{a['slug']}: unknown related article(s) {bad}")
    return arts


def render_md(text):
    out = markdown.markdown(text, extensions=['tables', 'attr_list', 'toc'], output_format='html')
    out = out.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    out = re.sub(r'<blockquote>\s*<p><strong>(.*?)</strong>\s*', r'<aside class="callout-note"><p class="callout-label">\1</p><p>', out)
    out = out.replace('</blockquote>', '</aside>')
    out = re.sub(r'<a href="(https?://[^"]+)">', r'<a href="\1" target="_blank" rel="noopener noreferrer">', out)
    out = re.sub(r'\[\[(.*?)\]\]', r'<mark class="todo">\1</mark>', out)
    return out


def in_guide(arts, guide):
    return [arts[s] for s in ORDER if arts[s]['guide'] == guide]


def reading_list(items, numbered=True):
    rows = ''.join(
        f'<li><a href="{a["slug"]}.html"><h3>{esc(a["title"])}</h3><span class="mins">{a["minutes"]} min</span>'
        f'<p>{esc(a["description"])}</p></a></li>' for a in items)
    return f'<ol class="reading-list{"" if numbered else " unnumbered"}">{rows}</ol>'


def pdf_box(guides, heading, text):
    buttons = ''.join(
        f'<a class="btn{" btn-quiet" if i else ""}" href="{GUIDES[g]["pdf"]}" target="_blank" rel="noopener noreferrer">{GUIDES[g]["name"]} (PDF)</a>'
        for i, g in enumerate(guides))
    return f'<aside class="pdf-box"><div><h2>{heading}</h2><p>{text}</p></div><div class="actions">{buttons}</div></aside>'


# ---------------------------------------------------------------- pages

def build_home(arts):
    ladder = [
        ('Consistency', 'Show up every week, for months', 'strength-training-basics.html#4-consistency'),
        ('Technique', 'Own the movement before adding weight', 'best-exercises-for-each-muscle.html'),
        ('Progressive overload', 'Add reps or weight over time', 'strength-training-basics.html#1-progressive-overload'),
        ('Program design', 'Pick a split you can stick to', 'how-to-build-a-workout-program.html'),
        ('Supplements', 'Protein powder and creatine, that’s it', 'supplements-that-work.html'),
    ]
    ladder_html = ''.join(f'<li><a href="{href}"><span class="term">{t}</span><span class="why">{why}</span></a></li>' for t, why, href in ladder)
    steps = [
        ('Learn the five principles', 'What actually makes you stronger, and what doesn’t matter yet.', 'strength-training-basics.html'),
        ('Pick a program that fits your week', 'Full body, upper/lower or torso/limbs, with sets and reps.', 'how-to-build-a-workout-program.html'),
        ('Set your calories and protein', 'Two numbers that decide whether you build muscle or lose fat.', 'calories-and-tdee.html'),
    ]
    steps_html = ''.join(f'<li><a href="{href}"><h3>{t}</h3><p>{d}</p></a></li>' for t, d, href in steps)

    def topic(name, img, text, guides, href):
        items = [a for g in guides for a in in_guide(arts, g)][:4]
        links = ''.join(f'<li><a href="{a["slug"]}.html"><span>{esc(a["title"].split(":")[0])}</span><span>{a["minutes"]} min</span></a></li>' for a in items)
        total = sum(len(in_guide(arts, g)) for g in guides)
        return (f'<article class="topic"><a class="topic-art" href="{href}" style="background-image:url(assets/img/{img})" aria-hidden="true" tabindex="-1"></a>'
                f'<div class="topic-body"><h3><a href="{href}">{name}</a></h3><p>{text}</p><ul class="topic-links">{links}</ul>'
                f'<a class="text-link" href="{href}">All {total} {name.lower()} articles</a></div></article>')

    guides = ''.join(
        f'<li><div><h3>{g["name"]}</h3><p>{g["pages"]}-page PDF, free</p></div>'
        f'<a class="btn btn-quiet" href="{g["pdf"]}" target="_blank" rel="noopener noreferrer">Download PDF</a></li>' for g in GUIDES.values())
    gear = [('equipment.html', 'equipment.webp', 'Equipment', 'Dumbbells, benches and bars for a home setup.'),
            ('supplements.html', 'supplements.webp', 'Supplements', 'Protein powder and creatine, and what to look for.'),
            ('accessories.html', 'accessories.webp', 'Accessories', 'Shakers, straps and grip trainers.')]
    gear_html = ''.join(f'<a href="{h}"><img src="assets/img/{i}" alt="" loading="lazy" width="1024" height="576"><h3>{t}</h3><p>{d}</p></a>' for h, i, t, d in gear)

    main = (
        '<div class="wrap">'
        '<section class="hero"><div><h1>Focus on what actually works.</h1>'
        '<p class="hero-sub">Free, evidence-based guides to training and nutrition, for people who’d rather lift than wade through fitness hype.</p>'
        '<div class="hero-actions"><a class="btn" href="strength-training-basics.html">Start with the basics</a>'
        '<a class="btn btn-quiet" href="#guides">Get the free guides</a></div></div>'
        f'<div class="ladder-wrap"><p class="ladder-caption">What matters most, in order</p><ol class="ladder">{ladder_html}</ol>'
        '<p class="ladder-note">Most people obsess over the bottom of this list and neglect the top.</p></div></section>'
        '<section class="section" aria-labelledby="new-here"><div class="section-head"><h2 id="new-here">New to the gym? Start here</h2>'
        '<p>Three short reads, in this order, get you from zero to a plan.</p></div>'
        f'<ol class="path">{steps_html}</ol></section>'
        '<section class="section" aria-labelledby="learn"><div class="section-head"><h2 id="learn">Learn the fundamentals</h2></div><div class="topics">'
        + topic('Training', 'strength.webp', 'Strength training and cardio: principles, programs and exercises.', ['strength', 'cardio'], 'training.html')
        + topic('Nutrition', 'macros.webp', 'Calories, protein and meal planning without the extremes.', ['nutrition', 'meal'], 'nutrition.html')
        + '</div></section>'
        + T.home_signup(GUIDES) + T.home_program() +
        '<section class="section" aria-labelledby="gear-title"><div class="section-head"><h2 id="gear-title">Gear that’s worth buying</h2>'
        '<p>Gear doesn’t build a physique, but the right pieces remove friction.</p></div>'
        f'<div class="gear">{gear_html}</div>'
        '<p class="gear-more">Setting up at home? <a class="text-link" href="home-gym-on-a-budget.html">See complete home gyms at €50, €150 and €500</a></p>'
        '<p class="small-print">Product links are affiliate links, matched to the shops in your country.</p></section>'
        '</div>'
    )
    return page('Trenesis | No-nonsense training & nutrition guides',
                'Free, evidence-based guides to strength training, cardio and nutrition, plus honest gear picks. No fluff, just what works.',
                'index.html', '', main)


def build_hub(arts, name):
    if name == 'Training':
        intro = ('<p class="lead">Training isn’t about finding the perfect program. It’s about understanding the fundamentals and applying them consistently over time.</p>'
                 '<p class="lead">Read these in order to train with structure, progress steadily and avoid the mistakes that keep most people stuck.</p>')
        groups = [('strength', 'Strength training', 'Start here if you’re new to lifting.'), ('cardio', 'Cardio', 'How to add cardio without hurting your strength gains.')]
        desc = 'Strength training and cardio fundamentals explained simply: progressive overload, programming, heart-rate zones and free PDF guides.'
        box = T.signup('Get the training guides as PDFs', 'The Strength Training and Cardio guides, printable and free. We’ll send them to your inbox.', id_='hub')
    else:
        intro = ('<p class="lead">Training is only half the equation. Without the right nutrition your body can’t adapt, recover or progress.</p>'
                 '<p class="lead">The answer isn’t perfection or extreme dieting. It’s getting a few numbers right and being consistent.</p>')
        groups = [('nutrition', 'Nutrition basics', 'Calories, protein and the other macros.'), ('meal', 'Meal planning', 'Turning your numbers into actual meals.')]
        desc = 'Calories, protein, macros and simple meal planning explained without the hype, with free PDF guides.'
        box = T.signup('Get the nutrition guides as PDFs', 'The Nutrition Basics and Meal Planning guides, printable and free. We’ll send them to your inbox.', id_='hub')
    sections = ''.join(f'<section class="reading" aria-labelledby="g-{g}"><h2 id="g-{g}">{title}</h2><p>{sub}</p>{reading_list(in_guide(arts, g))}</section>'
                       for g, title, sub in groups)
    main = f'<div class="wrap"><header class="page-intro"><h1>{name}</h1>{intro}</header>{sections}{box}</div>'
    return page(f'{name} | Trenesis', desc, HUB_PAGE[name], name, main)


def build_articles_index(arts):
    parts = ''
    for hub in ['Training', 'Nutrition']:
        parts += f'<section class="reading" aria-labelledby="h-{hub.lower()}"><h2 id="h-{hub.lower()}">{hub}</h2><p></p>'
        parts += reading_list([a for g, info in GUIDES.items() if info['hub'] == hub for a in in_guide(arts, g)], numbered=False) + '</section>'
    parts = parts.replace('<p></p>', '')
    main = ('<div class="wrap"><header class="page-intro"><h1>Articles</h1>'
            '<p class="lead">Everything from our free guides, broken into short reads you can finish between sets.</p></header>'
            f'{parts}</div>')
    return page('Articles | Trenesis', 'Every Trenesis article in one place: strength training, cardio, nutrition and meal planning, explained simply.',
                'articles.html', 'Articles', main)


def article_body_with_picks(a):
    body = render_md(a['body'])
    if a['slug'] in T.PICKS:
        box = T.picks_box(a['slug'])
        body = body.replace('<h2 id="sources">', box + '<h2 id="sources">', 1) if '<h2 id="sources">' in body else body + box
    return f'<div class="article-body">{body}</div>'


def build_article(a, arts):
    g = GUIDES[a['guide']]
    jsonld = ('<script type="application/ld+json">' + json.dumps({
        '@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['description'],
        'dateModified': UPDATED.isoformat(), 'mainEntityOfPage': f'{BASE}{a["slug"]}.html', 'image': f'{BASE}assets/img/share.jpg',
        'author': {'@type': 'Organization', 'name': 'Trenesis'}, 'publisher': {'@type': 'Organization', 'name': 'Trenesis'}}, ensure_ascii=False) + '</script>')
    main = (
        f'<div class="wrap"><article class="article"><a class="back" href="{HUB_PAGE[g["hub"]]}">{g["hub"]}</a>'
        f'<header class="article-head"><p class="kicker">{g["group"]}</p><h1>{esc(a["title"])}</h1>'
        f'<p class="article-lead">{esc(a["description"])}</p>'
        f'<p class="article-meta"><span>{a["minutes"]} min read</span><span>Updated {UPDATED.strftime("%B %Y")}</span></p></header>'
        + article_body_with_picks(a)
        + T.signup(f'Get the full {g["name"]}', f'All chapters in one {g["pages"]}-page PDF, sent to your inbox. Free.', button='Send me the guide', id_='article')
        + '<p class="disclaimer">This article is general education, not medical advice. If you have an injury or a health condition, '
          'check with a doctor or physiotherapist before changing your training or diet.</p>'
        f'<section class="related" aria-labelledby="related-title"><h2 id="related-title">Keep reading</h2>{reading_list([arts[r] for r in a["related"]], numbered=False)}</section>'
        '</article></div>'
    )
    return page(f'{a["title"]} | Trenesis', a['description'], f'{a["slug"]}.html', g['hub'], main, 'article', jsonld)


def build_simple(md_file):
    m = re.match(r'---\n(.*?)\n---\n(.*)', md_file.read_text(encoding='utf-8'), re.S)
    meta = dict(line.split(': ', 1) for line in m.group(1).splitlines() if line.strip())
    main = (f'<div class="wrap"><article class="article"><header class="article-head"><h1>{esc(meta["title"])}</h1></header>'
            f'<div class="article-body">{render_md(m.group(2))}</div></article></div>')
    current = 'About' if meta['slug'] == 'about' else ''
    return meta['slug'], page(f'{meta["title"]} | Trenesis', meta['description'], f'{meta["slug"]}.html', current, main)


def build_gear_overview():
    cards = [('equipment.html', 'equipment.webp', 'Equipment', 'Dumbbells, barbells, benches and bodyweight gear.'),
             ('supplements.html', 'supplements.webp', 'Supplements', 'Protein powder and creatine, the two worth considering.'),
             ('accessories.html', 'accessories.webp', 'Accessories', 'Shakers, lifting straps and grip trainers.')]
    cards_html = ''.join(f'<a href="{h}"><img src="assets/img/{i}" alt="" width="1024" height="576"><h3>{t}</h3><p>{d}</p></a>' for h, i, t, d in cards)
    main = (
        '<div class="wrap"><header class="page-intro"><h1>Gear worth buying</h1>'
        '<p class="lead">Gear doesn’t build a physique, but the right pieces remove friction. Each guide explains what to look for, then shows picks from the shops in your country.</p></header>'
        '<section class="market-status" aria-label="Local recommendations" data-category="all"><p id="market-title">Choose your country to see local picks.</p>'
        '<p id="market-detail" role="status" aria-live="polite"></p><div id="local-picks"></div></section>'
        f'<div class="gear gear-cards">{cards_html}</div>'
        '<section id="approach" class="approach"><h2>How we pick gear</h2>'
        '<p>We start from what you’ll actually use: the exercises in your program, the space you have and your budget. Then we look for options that are available in your country and good value.</p>'
        '<p class="affiliate-disclosure">As an Amazon Associate we earn from qualifying purchases, at no extra cost to you.</p></section></div>'
    )
    return page('Gear worth buying | Trenesis', 'Practical picks for home-gym equipment, supplements and accessories, matched to the shops in your country.',
                'products.html', 'Gear', main, country=True)


def build_gear(name):
    s = (ROOT / 'content' / 'gear' / f'{name}.html').read_text(encoding='utf-8')
    title = re.search(r'<!-- title: (.*?) -->', s).group(1)
    desc = re.search(r'<!-- description: (.*?) -->', s).group(1)
    body = re.sub(r'<!-- (title|description): .*? -->\n', '', s)
    return page(f'{title} | Trenesis', desc, f'{name}.html', 'Gear', body, country=True)


def sitemap():
    pages = ['index.html', 'training.html', 'nutrition.html', 'articles.html', 'products.html', 'equipment.html', 'supplements.html',
             'accessories.html', 'about.html'] + [f'{s}.html' for s in ORDER]
    urls = ''.join(f'<url><loc>{BASE}{"" if p == "index.html" else p}</loc><lastmod>{UPDATED.isoformat()}</lastmod></url>' for p in pages)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'


def main():
    arts = load_articles()
    out = {'index.html': build_home(arts), 'training.html': build_hub(arts, 'Training'), 'nutrition.html': build_hub(arts, 'Nutrition'),
           'articles.html': build_articles_index(arts), 'products.html': build_gear_overview()}
    for name in ['equipment', 'supplements', 'accessories']:
        out[f'{name}.html'] = build_gear(name)
    for a in arts.values():
        out[f'{a["slug"]}.html'] = build_article(a, arts)
    for f in sorted((ROOT / 'content' / 'pages').glob('*.md')):
        slug, html_ = build_simple(f)
        out[f'{slug}.html'] = html_
    out['program.html'] = page('The Trenesis Beginner Program | Trenesis', 'An 8-week, 3-day full-body program for beginners, for the gym or at home.', 'program.html', 'Program', T.program_page())
    out['home-gym-on-a-budget.html'] = page('A home gym on a budget | Trenesis', 'Three home gym setups at around €50, €150 and €500 that cover everything a beginner needs.', 'home-gym-on-a-budget.html', 'Gear', T.budget_page())
    out['work-with-us.html'] = page('Work with us | Trenesis', 'How brands can work with Trenesis, and what we will and won’t do.', 'work-with-us.html', '', T.partner_page())
    for name, text in out.items():
        (ROOT / name).write_text(text, encoding='utf-8')
    (ROOT / 'sitemap.xml').write_text(sitemap(), encoding='utf-8')
    print(f'built {len(out)} pages and sitemap.xml')


if __name__ == '__main__':
    main()
