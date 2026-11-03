"""Reusable page parts: article extras, the plan finder, the start page and the 404 page."""
import html
import re


def esc(s):
    return html.escape(s, quote=True)


AUTHORS = 'Volodymyr and Linus'
PRINTABLE = {'full-body-workout-for-beginners', 'cardio-plans', 'dumbbell-workout-at-home', 'bodyweight-workout-plan', 'short-home-workouts', 'intermediate-home-workout'}


def breadcrumbs(base, hub, hub_page, title):
    """Visible breadcrumb trail plus the matching schema.org BreadcrumbList."""
    nav = (f'<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li>'
           f'<li><a href="{hub_page}">{hub}</a></li></ol></nav>')
    data = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
            f'{{"@type":"ListItem","position":1,"name":"Home","item":"{base}"}},'
            f'{{"@type":"ListItem","position":2,"name":"{hub}","item":"{base}{hub_page}"}},'
            f'{{"@type":"ListItem","position":3,"name":{json_str(title)}}}]}}')
    return nav, f'<script type="application/ld+json">{data}</script>'


def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def takeaways_box(items):
    lis = ''.join(f'<li>{esc(i)}</li>' for i in items)
    return f'<aside class="takeaways" aria-labelledby="takeaways-title"><h2 id="takeaways-title">Key takeaways</h2><ul>{lis}</ul></aside>'


def toc(body_html):
    """Table of contents from the article's h2 headings (Sources left out). Only for articles with 3+ sections."""
    heads = [(i, re.sub(r'<[^>]+>', '', t)) for i, t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body_html) if i != 'sources']
    if len(heads) < 3:
        return ''
    items = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in heads)
    return f'<details class="toc" open><summary>On this page</summary><ol>{items}</ol></details>'


def author_box():
    return ('<aside class="author-box" aria-label="About the authors"><img src="assets/img/logo.webp" alt="" width="48" height="48">'
            f'<div><p class="author-name">Written by {AUTHORS}</p>'
            '<p>One of us trains in Rotterdam, the other in San Francisco. We write evidence-based guides for beginners and link our sources so you can check them. '
            '<a class="text-link" href="about.html#how-we-write">How we write</a></p></div></aside>')


def finder_callout():
    return ('<aside class="nudge" aria-label="Plan finder"><div><p class="nudge-title">Not sure which plan fits you?</p>'
            '<p>Answer 4 quick questions and get the plan, articles and numbers that match your situation.</p></div>'
            '<a class="btn" href="find-your-plan.html">Find your plan</a></aside>')


def calculator_callout():
    return ('<aside class="nudge" aria-label="Calculator"><div><p class="nudge-title">Get your own numbers</p>'
            '<p>Daily calories and protein for your goal, in kg or lb, in 30 seconds.</p></div>'
            '<a class="btn" href="calculator.html">Open the calculator</a></aside>')


def print_button():
    return '<button class="btn btn-quiet print-btn" type="button" onclick="window.print()">Print this plan</button>'


FINDER = r'''
<div class="wrap"><header class="page-intro"><h1>Find your plan</h1>
<p class="lead">Four quick questions, then we point you to the plan, articles and numbers that fit you. No email needed.</p></header>
<form class="finder" id="finder" novalidate>
  <fieldset class="calc-choice"><legend>1. Where will you train?</legend>
    <label><input type="radio" name="place" value="gym" checked> <span><strong>At a gym</strong> Machines, barbells and dumbbells</span></label>
    <label><input type="radio" name="place" value="dumbbells"> <span><strong>At home, with dumbbells</strong> A pair of dumbbells, maybe a bench</span></label>
    <label><input type="radio" name="place" value="none"> <span><strong>At home, no equipment</strong> Just your bodyweight</span></label>
  </fieldset>
  <fieldset class="calc-choice"><legend>2. How experienced are you?</legend>
    <label><input type="radio" name="level" value="new" checked> <span><strong>New, or back after a long break</strong> Less than 6 months of regular training</span></label>
    <label><input type="radio" name="level" value="some"> <span><strong>Some experience</strong> You’ve trained regularly for 6 months or more</span></label>
  </fieldset>
  <fieldset class="calc-choice"><legend>3. How many days a week can you train?</legend>
    <label><input type="radio" name="days" value="3" checked> <span><strong>2–3 days</strong></span></label>
    <label><input type="radio" name="days" value="4"> <span><strong>4 or more days</strong></span></label>
  </fieldset>
  <fieldset class="calc-choice"><legend>4. What’s your main goal?</legend>
    <label><input type="radio" name="goal" value="muscle" checked> <span><strong>Build muscle and strength</strong></span></label>
    <label><input type="radio" name="goal" value="fat"> <span><strong>Lose fat</strong></span></label>
    <label><input type="radio" name="goal" value="fit"> <span><strong>Get fitter and healthier</strong></span></label>
  </fieldset>
  <button class="btn" type="submit">Show my plan</button>
</form>
<section class="finder-result" id="finder-result" aria-live="polite" hidden>
  <p class="kicker">Your plan</p>
  <h2 id="fr-title"></h2>
  <p id="fr-why"></p>
  <a class="btn" id="fr-link" href="#">Open the plan</a>
  <h3>Then read</h3>
  <ol class="finder-next" id="fr-next"></ol>
  <p class="finder-saved">Saved: you’ll find this list under <strong>Your plan</strong> in the corner of every page, with a tick next to everything you’ve read.</p>
</section>
</div>
<script>
(function () {
  'use strict';
  var f = document.getElementById('finder'), box = document.getElementById('finder-result');
  var A = {
    full: ['The free 3-day full-body plan', 'full-body-workout-for-beginners.html'],
    split: ['An upper/lower split, 4 days a week', 'how-to-build-a-workout-program.html'],
    home: ['All home workout plans', 'home-workout-plan.html'],
    bodyweight: ['The bodyweight plan with 3 levels', 'bodyweight-workout-plan.html'],
    dumbbell: ['The 3-day dumbbell plan', 'dumbbell-workout-at-home.html'],
    homeSplit: ['The 4-day intermediate home plan', 'intermediate-home-workout.html'],
    short: ['20-minute workouts for busy weeks', 'short-home-workouts.html'],
    first: ['Your first week at the gym', 'first-week-at-the-gym.html'],
    basics: ['The 5 principles that actually matter', 'strength-training-basics.html'],
    calc: ['Work out your calories and protein', 'calculator.html'],
    protein: ['How much protein you need', 'how-much-protein.html'],
    fatloss: ['Fat loss without starving', 'fat-loss-meal-tips.html'],
    cardio: ['3 cardio plans for beginners and lifters', 'cardio-plans.html'],
    exercises: ['The best exercises for each muscle', 'best-exercises-for-each-muscle.html']
  };
  function v(n) { return f.querySelector('input[name=' + n + ']:checked').value; }
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var place = v('place'), level = v('level'), days = v('days'), goal = v('goal'), plan, why, next = [];
    if (place === 'none') {
      plan = A.bodyweight; why = 'Three days a week with your bodyweight. Every movement has 3 levels, so it keeps getting harder as you get stronger.';
    } else if (place === 'dumbbells' && level === 'some' && days === '4') {
      plan = A.homeSplit; why = 'With some experience and 4 days a week, an upper/lower split with dumbbells, a bench and a pull-up bar gives each muscle more work.';
    } else if (place === 'dumbbells') {
      plan = A.dumbbell; why = 'Two full-body dumbbell workouts, three days a week, with a floor version of every bench exercise.';
    } else if (level === 'some' && days === '4') {
      plan = A.split; why = 'With some experience and 4 days a week, an upper/lower split gives each muscle more work and enough recovery.';
    } else {
      plan = A.full; why = 'Two full-body workouts, three days a week, with every set and rep written out. The best place to start' + (days === '4' ? '; use your 4th day for easy cardio.' : '.');
    }
    if (place === 'gym' && level === 'new') next.push(A.first);
    next.push(A.calc);
    if (goal === 'muscle') next.push(A.protein);
    if (goal === 'fat') next.push(A.fatloss);
    if (goal === 'fit' || days === '4') next.push(A.cardio);
    if (place !== 'gym') next.push(A.short);
    if (level === 'new') next.push(A.basics); else next.push(A.exercises);
    document.getElementById('fr-title').textContent = plan[0];
    document.getElementById('fr-why').textContent = why;
    document.getElementById('fr-link').href = plan[1];
    var ol = document.getElementById('fr-next'); ol.replaceChildren();
    next.slice(0, 4).forEach(function (n) { var li = document.createElement('li'), a = document.createElement('a'); a.href = n[1]; a.textContent = n[0]; a.className = 'text-link'; li.append(a); ol.append(li); });
    box.hidden = false;
    // Save the result so site.js can show "Your plan" on every page.
    var steps = [{ title: plan[0], href: plan[1] }].concat(next.slice(0, 4).map(function (n) { return { title: n[0], href: n[1] }; }));
    try { localStorage.setItem('trenesis.plan.v1', JSON.stringify({ created: Date.now(), steps: steps, done: [] })); } catch (err) {}
    document.dispatchEvent(new CustomEvent('trenesis:plan'));
    box.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  });
})();
</script>
'''

START = '''
<div class="wrap start"><header class="start-head"><img src="assets/img/logo.webp" alt="" width="72" height="72">
<h1>Trenesis</h1><p>Free, no-hype guides to training and nutrition, from Rotterdam and San Francisco.</p></header>
<ul class="start-links">
  <li><a class="btn" href="find-your-plan.html">Find your plan in 4 questions</a></li>
  <li><a class="btn btn-quiet" href="full-body-workout-for-beginners.html">Free 3-day beginner plan</a></li>
  <li><a class="btn btn-quiet" href="calculator.html">Calorie and protein calculator</a></li>
  <li><a class="btn btn-quiet" href="home-workout-plan.html">Home workout plan</a></li>
  <li><a class="btn btn-quiet" href="index.html#guides">Free PDF guides</a></li>
  <li><a class="btn btn-quiet" href="products.html">Gear worth buying</a></li>
</ul>
<p class="start-follow"><a href="https://www.instagram.com/trenesisgym/" target="_blank" rel="noopener noreferrer">Instagram</a>
<a href="https://www.tiktok.com/@trenesis.gym" target="_blank" rel="noopener noreferrer">TikTok</a>
<a href="https://www.youtube.com/@TrenesisGym" target="_blank" rel="noopener noreferrer">YouTube</a></p>
</div>
'''

NOT_FOUND = '''
<div class="wrap"><header class="page-intro"><h1>This page doesn’t exist</h1>
<p class="lead">The link may be old or mistyped. These are the most useful places to go from here.</p></header>
<ul class="start-links lost-links">
  <li><a class="btn" href="find-your-plan.html">Find your plan</a></li>
  <li><a class="btn btn-quiet" href="articles.html">All articles</a></li>
  <li><a class="btn btn-quiet" href="calculator.html">Calorie and protein calculator</a></li>
  <li><a class="btn btn-quiet" href="index.html">Homepage</a></li>
</ul></div>
'''

# Sets <base> so relative links work on the 404 page at any depth, with or without a custom domain.
BASE_SCRIPT = "<script>(function(){var p=location.pathname.indexOf('/trenesis/')===0?'/trenesis/':'/';document.write('<base href=\"'+p+'\">');})();</script>"

CSS = '''
/* ---------- Site upgrades ---------- */
.crumbs ol { list-style: none; display: flex; flex-wrap: wrap; gap: 4px 8px; margin: 0 0 24px; padding: 0; font-size: 14px; color: var(--faint); }
.crumbs li + li::before { content: "/"; margin-right: 8px; color: #4a525a; }
.crumbs a { color: var(--muted); display: inline-block; padding: 6px 0; }
.crumbs a:hover { color: #fff; }
.article-meta a { color: var(--muted); text-decoration: underline; text-decoration-color: #4b6378; text-underline-offset: 3px; }
.takeaways { margin: 0 0 28px; padding: 20px 24px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); }
.takeaways h2 { font-size: 16px; color: var(--ice); margin-bottom: 10px; }
.takeaways ul { margin: 0; padding-left: 20px; display: grid; gap: 8px; }
.takeaways li { color: var(--text); font-size: 16px; line-height: 1.55; }
.takeaways li::marker { color: #739cc5; }
.toc { margin: 0 0 32px; border-left: 2px solid var(--line); padding: 2px 0 2px 18px; }
.toc summary { cursor: pointer; font: 600 15px/1.4 var(--head); color: #fff; padding: 6px 0; }
.toc ol { margin: 8px 0 0; padding-left: 20px; display: grid; gap: 4px; }
.toc a { color: var(--muted); font-size: 15px; display: inline-block; padding: 3px 0; }
.toc a:hover { color: var(--ice); }
.article-body h2 { scroll-margin-top: 20px; }
.author-box { display: flex; gap: 16px; align-items: flex-start; margin-top: 40px; padding: 20px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.author-box img { border-radius: 50%; flex-shrink: 0; }
.author-name { font: 600 16px/1.4 var(--head); color: #fff; }
.author-box p:not(.author-name) { color: var(--muted); font-size: 14px; line-height: 1.6; margin-top: 4px; }
.nudge { display: flex; align-items: center; justify-content: space-between; gap: 24px; margin: 36px 0; padding: 22px 24px; border: 1px solid #3a5470; border-radius: 8px; background: #141b22; }
.nudge-title { font: 700 18px/1.3 var(--head); color: #fff; }
.nudge p:not(.nudge-title) { color: var(--muted); font-size: 15px; margin-top: 4px; }
.nudge .btn { flex-shrink: 0; }
.print-btn { margin: 0 0 28px; }
.hero-actions .btn-note { display: block; font-size: 13px; color: var(--faint); margin-top: 10px; width: 100%; }
.finder { display: grid; gap: 22px; max-width: 640px; }
.finder fieldset { border: 0; margin: 0; padding: 0; }
.finder legend { display: block; font: 600 16px/1.4 var(--head); color: #fff; margin-bottom: 10px; padding: 0; }
.finder .btn { justify-self: start; min-width: 200px; }
.finder-result { margin-top: 40px; max-width: 640px; padding: 28px; border: 1px solid #3a5470; border-radius: 10px; background: var(--panel); scroll-margin-top: 20px; }
.finder-result h2 { font-size: 28px; letter-spacing: -.015em; margin-bottom: 8px; }
.finder-result > p:not(.kicker) { color: var(--muted); margin-bottom: 20px; }
.finder-result h3 { font-size: 16px; color: var(--muted); margin: 28px 0 8px; }
.finder-next { margin: 0; padding-left: 20px; display: grid; gap: 8px; }
.finder-saved { margin-top: 22px; padding-top: 16px; border-top: 1px solid var(--line-soft); color: var(--muted); font-size: 14px; }
.start { max-width: 520px; padding-top: 40px; }
.start-head { text-align: center; }
.start-head img { margin: 0 auto 14px; border-radius: 50%; }
.start-head h1 { font-size: 32px; }
.start-head p { color: var(--muted); margin-top: 8px; }
.start-links { list-style: none; margin: 28px 0 0; padding: 0; display: grid; gap: 12px; }
.start-links .btn { width: 100%; min-height: 54px; font-size: 16px; }
.lost-links { max-width: 420px; }
.start-follow { display: flex; justify-content: center; gap: 24px; margin-top: 28px; font-size: 15px; }
.start-follow a { color: var(--muted); padding: 8px 0; }
.start-follow a:hover { color: #fff; }
@media (max-width: 800px) {
  .nudge { flex-direction: column; align-items: flex-start; gap: 14px; padding: 20px; }
  .nudge .btn, .finder .btn { width: 100%; }
  .takeaways { padding: 18px 20px; }
  .finder-result { padding: 22px; }
}
@media print {
  .site-header, .site-footer, .crumbs, .toc, .nudge, .pdf-box, .related, .author-box, .print-btn, .calc-promo, .skip, .disclaimer { display: none !important; }
  body { background: #fff; color: #000; font-size: 11pt; }
  .article, .wrap { max-width: none; width: auto; padding: 0; }
  h1, h2, h3, .article-body strong, .article-body td:first-child { color: #000 !important; }
  .article-body, .article-body p, .article-body td, .article-lead, .takeaways li { color: #222 !important; }
  .takeaways, .callout-note, .table-wrap { background: none !important; border-color: #999 !important; }
  .article-body th { background: #eee !important; color: #000 !important; }
  .article-body td, .article-body th { border-bottom: 1px solid #ccc !important; }
  .article-body a { color: #000; text-decoration: none; }
  .article-head { border-color: #999; }
  table { page-break-inside: avoid; }
}
'''
