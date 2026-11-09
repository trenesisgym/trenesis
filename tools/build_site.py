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
import calculator
import logbook
import parts

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://trenesisgym.github.io/trenesis/'
VERSION = '20261109-program'
UPDATED = datetime.date(2026, 10, 31)


def article_updated(slug):
    """Date the article's source last changed: today if it has uncommitted edits, else its last commit, else UPDATED."""
    import subprocess
    src = f'content/articles/{slug}.md'
    try:
        dirty = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', src], cwd=ROOT).returncode != 0
        if dirty:
            return datetime.date.today()
        out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', src], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return max(datetime.date.fromisoformat(out), UPDATED) if out else UPDATED
    except Exception:
        return UPDATED

GUIDES = {
    'strength': {'name': 'Strength Training Guide', 'pdf': 'pdfs/strength-training.pdf', 'pages': 12, 'hub': 'Training', 'group': 'Strength training', 'covers': 'The principles behind the plans: progression, sets and reps, splits, recovery and common mistakes'},
    'home': {'name': 'Strength Training Guide', 'pdf': 'pdfs/strength-training.pdf', 'pages': 12, 'hub': 'Training', 'group': 'Home training', 'covers': 'The principles behind the plans: progression, sets and reps, splits, recovery and common mistakes'},
    'cardio': {'name': 'Cardio Training Guide', 'pdf': 'pdfs/cardio.pdf', 'pages': 9, 'hub': 'Training', 'group': 'Cardio', 'covers': 'Types of cardio, heart rate zones, weekly cardio plans and common mistakes'},
    'nutrition': {'name': 'Nutrition Basics Guide', 'pdf': 'pdfs/nutrition-basics.pdf', 'pages': 9, 'hub': 'Nutrition', 'group': 'Nutrition basics', 'covers': 'Calories, protein, carbs and fats, and the supplements worth considering'},
    'meal': {'name': 'Meal Planning Guide', 'pdf': 'pdfs/meal-planning.pdf', 'pages': 11, 'hub': 'Nutrition', 'group': 'Meal planning', 'covers': 'Planning meals around your goal, example days for fat loss and muscle gain, and meal prep'},
}
LOGGABLE = {slug.split('#')[0] for slug, _ in logbook.PLANS}
HUB_PAGE = {'Training': 'training.html', 'Nutrition': 'nutrition.html'}
# Reading order. A new article must be added here.
ORDER = [
    'first-week-at-the-gym', 'strength-training-basics', 'full-body-workout-for-beginners', 'upper-lower-workout-plan', 'how-to-build-a-workout-program',
    'best-exercises-for-each-muscle', 'recovery-and-sleep', 'strength-training-mistakes',
    'home-workout-plan', 'bodyweight-workout-plan', 'dumbbell-workout-at-home', 'short-home-workouts', 'intermediate-home-workout',
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
        f'<link rel="stylesheet" href="assets/styles.css?v={VERSION}">{extra}'
        f'<script defer src="assets/site.js?v={VERSION}"></script><link rel="stylesheet" href="assets/revision.css?v={VERSION}">'
        "<script>if('serviceWorker' in navigator&&window.isSecureContext){addEventListener('load',()=>{navigator.serviceWorker.register(new URL('sw.js',document.baseURI),{updateViaCache:'none'}).catch(()=>{})},{once:true})}</script>"
        '</head>'
    )


def header(current):
    here = ' aria-current="page"'
    def link(name, href):
        return f'<a href="{href}"{here if name == current else ""}>{name}</a>'
    # Tools live in one menu so the main navigation stays short.
    tools = [('Find your plan', 'find-your-plan.html', '4 questions, a plan that fits you'),
             ('Calorie calculator', 'calculator.html', 'Your calories and protein'),
             ('Workout logbook', 'logbook.html', 'Log your sets, beat last time')]
    in_tools = current in [t[0] for t in tools]
    sub = ''.join(f'<a href="{h}"{here if n == current else ""}>{n}<span>{d}</span></a>' for n, h, d in tools)
    menu = (f'<div class="nav-menu{" is-current" if in_tools else ""}">'
            '<button class="nav-menu-btn" type="button" aria-expanded="false" aria-controls="tools-menu">Tools</button>'
            f'<span class="nav-menu-label" aria-hidden="true">Tools</span><div class="nav-sub" id="tools-menu">{sub}</div></div>')
    links = (link('Home', 'index.html') + link('Training', 'training.html') + link('Nutrition', 'nutrition.html') + menu
             + link('Gear', 'products.html') + link('FAQ', 'faq.html') + link('About', 'about.html'))
    return (
        '<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="nav-wrap wrap">'
        '<a class="brand" href="index.html" aria-label="Trenesis home"><img src="assets/img/logo.webp" alt="" width="38" height="38"><span>TRENESIS</span></a>'
        f'<nav id="navigation" aria-label="Main navigation">{links}</nav>'
        + country_picker()
        + '<button class="menu-toggle" hidden aria-expanded="false" aria-controls="navigation" aria-label="Open navigation menu">Menu</button>'
        '</div></header>'
    )


def footer():
    social = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener noreferrer">{n}</a></li>' for n, u in SOCIAL)
    return (
        '<footer class="site-footer"><div class="wrap"><div class="footer-grid">'
        '<div class="footer-about"><a class="brand" href="index.html"><img src="assets/img/logo.webp" alt="" width="38" height="38"><span>TRENESIS</span></a>'
        '<p>Free, evidence-based guides to training and nutrition. No hype, just what works.</p></div>'
        '<div class="footer-col"><h2>Learn</h2><ul><li><a href="training.html">Training</a></li><li><a href="nutrition.html">Nutrition</a></li>'
        '<li><a href="index.html#guides">Free PDF guides</a></li><li><a href="calculator.html">Calorie calculator</a></li><li><a href="logbook.html">Workout logbook</a></li></ul></div>'
        '<div class="footer-col"><h2>Trenesis</h2><ul><li><a href="program.html">12-Week Program</a></li><li><a href="about.html">About</a></li><li><a href="faq.html">Questions &amp; answers</a></li><li><a href="products.html">Gear</a></li>'
        '<li><a href="products.html#approach">How we pick gear</a></li><li><a href="privacy.html">Privacy</a></li></ul></div>'
        f'<div class="footer-col"><h2>Follow</h2><ul>{social}</ul></div></div>'
        f'<div class="footer-note"><span>© <span data-year>{UPDATED.year}</span> Trenesis</span>'
        '<span>Some gear links are affiliate links. We earn a small commission at no extra cost to you.</span></div>'
        '</div></footer></body></html>\n'
    )


def country_picker():
    opts = ''.join(f'<option value="{c}">{label}</option>' for c, label in COUNTRIES)
    return ('<div class="country-picker site-country"><label class="sr-only" for="country">Country</label>'
            f'<select disabled id="country" aria-describedby="country-hint">{opts}</select>'
            '<span id="country-hint" class="sr-only">Select your country. Your choice applies across the website.</span></div>')


def page(title, desc, path, current, main, og_type='website', extra='', country=False):
    extra += f'<script defer src="assets/catalogs.js?v={VERSION}"></script>'
    return head(title, desc, path, og_type, extra) + header(current) + f'<main id="main" tabindex="-1">{main}</main>' + footer()


def build_hand(name, current, extra=''):
    """Pages Linus designed by hand: content/hand/<name>.html holds the <main> content plus title/description comments."""
    s = (ROOT / 'content' / 'hand' / f'{name}.html').read_text(encoding='utf-8')
    title = html.unescape(re.search(r'<!-- title: (.*?) -->', s).group(1))
    desc = html.unescape(re.search(r'<!-- description: (.*?) -->', s).group(1))
    body = re.sub(r'<!-- (title|description): .*? -->\n', '', s).rstrip('\n')
    return page(title, desc, f'{name}.html', current, body, extra=extra)


def faq_schema():
    """FAQPage structured data built from the questions in content/hand/faq.html."""
    s = (ROOT / 'content' / 'hand' / 'faq.html').read_text(encoding='utf-8')
    qa = []
    for q, a in re.findall(r'<details><summary>(.*?)</summary><div>(.*?)</div></details>', s, re.S):
        text = lambda x: html.unescape(re.sub(r'<[^>]+>', '', x)).strip()
        qa.append({'@type': 'Question', 'name': text(q), 'acceptedAnswer': {'@type': 'Answer', 'text': text(a)}})
    data = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': qa}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'


# ---------------------------------------------------------------- content

def load_articles():
    arts = {}
    for f in sorted((ROOT / 'content' / 'articles').glob('*.md')):
        m = re.match(r'---\n(.*?)\n---\n(.*)', f.read_text(encoding='utf-8'), re.S)
        if not m:
            sys.exit(f'{f.name}: missing header')
        meta = dict(line.split(': ', 1) for line in m.group(1).splitlines() if line.strip())
        meta['related'] = [r.strip() for r in meta.get('related', '').split(',') if r.strip()]
        meta['takeaways'] = [t.strip() for t in meta.get('takeaways', '').split(' | ') if t.strip()]
        meta['body'] = m.group(2)
        reading_text = re.sub(r'<div data-article-picks.*?</div>', '', m.group(2), flags=re.S)
        meta['minutes'] = max(2, math.ceil(len(re.findall(r'\w+', reading_text)) / 220))
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

def build_article(a, arts):
    g = GUIDES[a['guide']]
    hub_page = HUB_PAGE[g['hub']]
    jsonld = ('<script type="application/ld+json">' + json.dumps({
        '@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['description'],
        'dateModified': article_updated(a['slug']).isoformat(), 'mainEntityOfPage': f'{BASE}{a["slug"]}.html', 'image': f'{BASE}assets/img/share.jpg',
        'author': [{'@type': 'Person', 'name': 'Volodymyr'}, {'@type': 'Person', 'name': 'Linus'}],
        'publisher': {'@type': 'Organization', 'name': 'Trenesis'}}, ensure_ascii=False) + '</script>')
    crumbs, crumbs_ld = parts.breadcrumbs(BASE, g['hub'], hub_page, a['title'])
    body = article_body_html(a)
    if a['slug'] in parts.PRINTABLE:
        nudge = parts.program_callout()  # plan pages: the next step after a free plan is the 12-week program
    else:
        nudge = parts.finder_callout() if g['hub'] == 'Training' else parts.calculator_callout()
    main = (
        f'<div class="wrap"><article class="article">{crumbs}'
        f'<header class="article-head"><p class="kicker">{g["group"]}</p><h1>{esc(a["title"])}</h1>'
        f'<p class="article-lead">{esc(a["description"])}</p>'
        f'<p class="article-meta"><span>By <a href="about.html">{parts.AUTHORS}</a></span><span>{a["minutes"]} min read</span>'
        f'<span>Updated {article_updated(a["slug"]).strftime("%B %Y")}</span></p></header>'
        + (parts.takeaways_box(a['takeaways']) if a['takeaways'] else '')
        + (('<div class="plan-actions">' + parts.print_button() + (f'<a class="btn btn-quiet" href="logbook.html?plan={a["slug"]}">Log this workout</a>' if a['slug'] in LOGGABLE else '') + '</div>') if a['slug'] in parts.PRINTABLE else '')
        + parts.toc(body)
        + f'<div class="article-body">{body}</div>'
        + nudge
        + pdf_box([a['guide']], f'Free PDF: {g["name"]}', f'{g["covers"]}, in one {g["pages"]}-page PDF to download and print.')
        + parts.author_box()
        + '<p class="disclaimer">This article is general education, not medical advice. If you have an injury or a health condition, '
          'check with a doctor or physiotherapist before changing your training or diet.</p>'
        f'<section class="related" aria-labelledby="related-title"><h2 id="related-title">Keep reading</h2>{reading_list([arts[r] for r in a["related"]], numbered=False)}</section>'
        '</article></div>'
    )
    out = page(f'{a["title"]} | Trenesis', a['description'], f'{a["slug"]}.html', g['hub'], main, 'article', jsonld + crumbs_ld, country='data-article-picks' in body)
    if (ROOT / 'assets' / 'img' / 'og' / f'{a["slug"]}.jpg').exists():  # made by tools/make_share_images.js
        out = out.replace(f'{BASE}assets/img/share.jpg', f'{BASE}assets/img/og/{a["slug"]}.jpg')
    return out


def article_body_html(a):
    body = render_md(a['body']).replace('<div data-article-picks', '<div hidden data-article-picks')
    if 'data-article-picks' in body:
        controls = ('<div class="sr-only" data-category="all"><p id="market-title"></p>'
                    '<p id="market-detail" role="status" aria-live="polite"></p><div id="local-picks"></div></div>'
                    '<p class="affiliate-disclosure article-affiliate-note" hidden>Affiliate links: we earn a commission at no extra cost to you.</p>')
        body = re.sub(r'(<div hidden data-article-picks.*?</div>)', lambda m: m[1] + controls, body, count=1, flags=re.S)
    return body


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
    pages = ['index.html', 'training.html', 'nutrition.html', 'program.html', 'products.html', 'equipment.html', 'supplements.html',
             'accessories.html', 'about.html', 'faq.html', 'calculator.html', 'logbook.html', 'find-your-plan.html'] + [f'{s}.html' for s in ORDER]
    urls = ''.join(f'<url><loc>{BASE}{"" if p == "index.html" else p}</loc><lastmod>{UPDATED.isoformat()}</lastmod></url>' for p in pages)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'


def main():
    arts = load_articles()
    # Homepage, Training and Nutrition are hand-designed (content/hand). articles.html now redirects to the homepage.
    out = {'index.html': build_hand('index', 'Home'), 'training.html': build_hand('training', 'Training'),
           'nutrition.html': build_hand('nutrition', 'Nutrition'), 'program.html': build_hand('program', 'Program'),
           'articles.html': (ROOT / 'content' / 'hand' / 'articles-redirect.html').read_text(encoding='utf-8'),
           'products.html': build_gear_overview()}
    for name in ['equipment', 'supplements', 'accessories']:
        out[f'{name}.html'] = build_gear(name)
    for a in arts.values():
        out[f'{a["slug"]}.html'] = build_article(a, arts)
    for f in sorted((ROOT / 'content' / 'pages').glob('*.md')):
        slug, html_ = build_simple(f)
        out[f'{slug}.html'] = html_
    out['calculator.html'] = page('Calorie and protein calculator | Trenesis',
        'Work out your daily calories and protein for fat loss, maintenance or muscle gain, in kilograms or pounds.',
        'calculator.html', 'Calorie calculator', calculator.MAIN)
    out['faq.html'] = build_hand('faq', 'FAQ', extra=faq_schema())
    out['logbook.html'] = page('Free workout logbook | Trenesis',
        'Log every set of your Trenesis plan on your phone, see what you lifted last time and keep your history. Free, no account, saved on your device.',
        'logbook.html', 'Workout logbook', logbook.main_html())
    out['find-your-plan.html'] = page('Find your plan | Trenesis', 'Answer 4 quick questions and get the training plan, articles and calorie targets that fit you.',
        'find-your-plan.html', 'Find your plan', parts.FINDER)
    out['start.html'] = page('Start here | Trenesis', 'Trenesis: free beginner plans, a calorie and protein calculator and no-hype guides.',
        'start.html', '', parts.START, extra='<meta name="robots" content="noindex">')
    lost = page('Page not found | Trenesis', 'This page doesn’t exist.', '404.html', '', parts.NOT_FOUND, extra='<meta name="robots" content="noindex">')
    out['404.html'] = lost.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + parts.BASE_SCRIPT, 1)
    for name, text in out.items():
        (ROOT / name).write_text(text, encoding='utf-8')
    (ROOT / 'sitemap.xml').write_text(sitemap(), encoding='utf-8')
    print(f'built {len(out)} pages and sitemap.xml')


if __name__ == '__main__':
    main()
