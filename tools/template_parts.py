"""Template-only additions: the 'ideal version' of Trenesis.

Everything here is example content that shows how the finished site would work
once the email tool, payment provider and extra affiliate programs exist.
Imported by build_site.py on the ideal-template branch only.
"""
import html

def esc(s):
    return html.escape(s, quote=True)

BANNER = ('<div class="template-bar"><div class="wrap">Template preview: example content showing the finished site. '
          'Forms, prices and numbers are placeholders.</div></div>')

# Handles every signup form in the template: nothing is sent anywhere yet.
FORM_SCRIPT = ("<script>document.addEventListener('submit',function(e){var f=e.target;if(!f.matches('.signup-form'))return;e.preventDefault();"
               "var s=f.querySelector('.form-status');if(s){s.textContent='Template only: this will work once the email tool is connected.';}});</script>")


def signup(heading, text, button='Send me the guides', note='One useful email a week at most. Unsubscribe anytime.', id_=''):
    return (f'<section class="signup"{f" id={chr(34)}{id_}{chr(34)}" if id_ else ""}><div><h2>{heading}</h2><p>{text}</p></div>'
            '<form class="signup-form" novalidate><label class="sr-only" for="email-' + (id_ or 'x') + '">Email address</label>'
            f'<div class="signup-row"><input id="email-{id_ or "x"}" type="email" name="email" placeholder="you@example.com" autocomplete="email" required>'
            f'<button class="btn" type="submit">{button}</button></div>'
            f'<p class="form-note">{note}</p><p class="form-status" role="status" aria-live="polite"></p></form></section>')


# Example in-article picks (Germany's catalog, as most EU visitors would see it).
PICKS = {
    'supplements-that-work': [
        ('natural elements', 'Creatine Monohydrate', 'Plain creatine monohydrate, 500 g. Nothing added, about 100 days at 5 g a day.', 'https://www.amazon.de/dp/B0863QGX3P?tag=trenesisgym-21'),
        ('Body Attack', '100% Whey Protein, Chocolate', 'A 2 kg whey protein. Compare protein per serving and check the milk ingredients.', 'https://www.amazon.de/dp/B0G1ZFS3RL?tag=trenesisgym-21'),
        ('Sunday Natural', 'Organic Vegan Protein, Natural', 'An unflavoured plant-protein blend without sweeteners, 1 kg.', 'https://www.amazon.de/dp/B0GM1JG3GC?tag=trenesisgym-21'),
    ],
    'how-much-protein': [
        ('Body Attack', '100% Whey Protein, Chocolate', 'If shakes make your protein target easier, a plain whey is all you need.', 'https://www.amazon.de/dp/B0G1ZFS3RL?tag=trenesisgym-21'),
        ('Sunday Natural', 'Organic Vegan Protein, Natural', 'A dairy-free option for plant-based eaters.', 'https://www.amazon.de/dp/B0GM1JG3GC?tag=trenesisgym-21'),
    ],
}


def picks_box(slug):
    rows = ''.join(
        f'<li><div><p class="pick-brand">{esc(b)}</p><h3>{esc(n)}</h3><p>{esc(r)}</p></div>'
        f'<div class="pick-action"><a class="btn btn-quiet" href="{u}" target="_blank" rel="sponsored noopener">Check price</a><span>Affiliate link</span></div></li>'
        for b, n, r, u in PICKS[slug])
    return ('<aside class="picks" aria-labelledby="picks-title"><div class="picks-head"><h2 id="picks-title">Our picks</h2>'
            '<p>Shown for Germany. Picks change with the country you choose on the Gear pages.</p></div>'
            f'<ul>{rows}</ul><p class="picks-note">We earn a small commission if you buy through these links, at no extra cost to you. '
            '<a href="products.html#approach">How we pick gear</a></p></aside>')


def home_signup(guides):
    items = ''.join(f'<li><span>{g["name"]}</span><span>{g["pages"]} pages</span></li>' for g in guides.values())
    return ('<section class="section signup-home" id="guides" aria-labelledby="guides-title"><div class="signup-split">'
            '<div><h2 id="guides-title">Get all four guides free</h2>'
            '<p class="signup-lead">Strength, cardio, nutrition and meal planning as printable PDFs, plus one useful email a week.</p>'
            '<form class="signup-form" novalidate><label class="sr-only" for="email-home">Email address</label>'
            '<div class="signup-row"><input id="email-home" type="email" name="email" placeholder="you@example.com" autocomplete="email" required>'
            '<button class="btn" type="submit">Send me the guides</button></div>'
            '<p class="form-note">Unsubscribe anytime. We never share your email.</p><p class="form-status" role="status" aria-live="polite"></p></form></div>'
            f'<ul class="guide-stack">{items}</ul></div></section>')


def home_program():
    return ('<section class="section" aria-labelledby="program-title"><div class="program-teaser">'
            '<div><h2 id="program-title">Want a plan to follow?</h2>'
            '<p>The Trenesis Beginner Program: 8 weeks, 3 sessions a week, every set and rep written out. For the gym or at home.</p></div>'
            '<div class="program-teaser-cta"><p class="price">€12 <span>example price</span></p>'
            '<a class="btn" href="program.html">See the program</a></div></div></section>')


def program_page():
    week = [('Monday', 'Workout A', 'Squat or leg press, bench or machine press, lat pulldown, lateral raises, leg curl, crunches'),
            ('Wednesday', 'Workout B', 'Hip thrusts, incline dumbbell press, cable row, shoulder press, leg extension, curls and pushdowns'),
            ('Friday', 'Workout A', 'Same as Monday, a little heavier or a rep more on each exercise')]
    rows = ''.join(f'<tr><td>{d}</td><td>{w}</td><td>{e}</td></tr>' for d, w, e in week)
    faq = [
        ('Can I do it at home?', 'Yes. Every workout has a gym version and a home version for dumbbells and a bench.'),
        ('Do I need supplements?', 'No. The nutrition quick-start covers calories and protein from normal food.'),
        ('What if I miss a session?', 'Do the next one in the order. The plan works on consistency over weeks, not perfect weeks.'),
        ('Can I get a refund?', '<mark class="todo">Refund policy to decide, for example 14 days, no questions asked</mark>'),
    ]
    faq_html = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in faq)
    return (
        '<div class="wrap"><section class="program-hero"><div>'
        '<p class="kicker">Paid program</p><h1>The Trenesis Beginner Program</h1>'
        '<p class="lead">8 weeks, 3 sessions a week. A full-body plan that takes you from your first workout to a routine that sticks, with every set and rep written out.</p>'
        '<ul class="ticks"><li>Two alternating full-body workouts, gym and home versions</li><li>Short demo video for every exercise</li>'
        '<li>Progress tracker that tells you when to add weight</li><li>Nutrition quick-start: your calories and protein in 5 minutes</li></ul></div>'
        '<aside class="buy-box"><p class="price">€12 <span>example price</span></p><p>One-off payment. Yours to keep.</p>'
        '<form class="signup-form" novalidate><label class="sr-only" for="email-program">Email address</label>'
        '<input id="email-program" type="email" placeholder="you@example.com" autocomplete="email" required>'
        '<button class="btn" type="submit">Join the waitlist</button><p class="form-note">We’ll email you once, when it launches, with a launch discount.</p>'
        '<p class="form-status" role="status" aria-live="polite"></p></form></aside></section>'
        '<section class="section"><div class="section-head"><h2>A week on the program</h2><p>Weeks 1–4 build technique; weeks 5–8 add weight.</p></div>'
        f'<div class="article-body"><div class="table-wrap"><table><thead><tr><th>Day</th><th>Session</th><th>Exercises</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>'
        '<section class="section split-2"><div><h2>Who it’s for</h2><ul class="ticks"><li>You’re new to lifting or coming back after a break</li>'
        '<li>You can train 3 times a week for about an hour</li><li>You want a plan, not more information</li></ul></div>'
        '<div><h2>Who it’s not for</h2><ul class="crosses"><li>Competitive powerlifters or bodybuilders</li><li>Anyone looking for a 30-day transformation</li>'
        '<li>Injuries that need a physiotherapist first</li></ul></div></section>'
        f'<section class="section"><div class="section-head"><h2>Questions</h2></div><div class="faq">{faq_html}</div></section></div>'
    )


def budget_page():
    tiers = [
        ('Around €50', 'Bodyweight plus', ['Doorway pull-up bar', 'Set of resistance bands', 'One kettlebell (8–16 kg)'],
         'Pull-ups, band rows, push-ups, goblet squats, swings', 'If you mostly train at a gym and want something for home days.'),
        ('Around €150', 'The dumbbell starter', ['Flat bench', 'Two or three pairs of hex dumbbells', 'Doorway pull-up bar'],
         'Presses, rows, lunges, Romanian deadlifts, curls', 'If you’re training only at home and starting out.'),
        ('Around €500', 'The complete corner', ['Adjustable dumbbells (2.5–24 kg)', 'Adjustable bench', 'Pull-up bar or dip station', 'One kettlebell'],
         'Every muscle with progression for a year or more', 'If you’re committed and have about 2 × 2 m of space.'),
    ]
    cards = ''.join(
        f'<article class="tier"><p class="tier-price">{p}</p><h2>{n}</h2><p class="tier-for">{w}</p><h3>What’s in it</h3><ul>{"".join(f"<li>{i}</li>" for i in items)}</ul>'
        f'<h3>What you can train</h3><p>{t}</p><a class="btn btn-quiet" href="equipment.html">See the picks for your country</a></article>'
        for p, n, items, t, w in tiers)
    return ('<div class="wrap"><header class="page-intro"><h1>A home gym on a budget</h1>'
            '<p class="lead">Three setups that cover everything a beginner needs, at around €50, €150 and €500. Each one links to picks from the shops in your country.</p></header>'
            f'<div class="tiers">{cards}</div><p class="small-print">Example kits. The real page lists specific products with today’s prices for your country, '
            'checked every month. Product links are affiliate links.</p></div>')


def partner_page():
    return ('<div class="wrap"><article class="article"><header class="article-head"><h1>Work with Trenesis</h1>'
            '<p class="article-lead">We work with brands whose products we’d recommend anyway. Our readers trust us because we say no to the rest.</p></header>'
            '<div class="article-body"><h2>Our audience</h2><div class="table-wrap"><table><thead><tr><th>Channel</th><th>Followers</th><th>Typical reach</th></tr></thead><tbody>'
            '<tr><td>TikTok</td><td><mark class="todo">number</mark></td><td><mark class="todo">average views</mark></td></tr>'
            '<tr><td>Instagram</td><td><mark class="todo">number</mark></td><td><mark class="todo">average views</mark></td></tr>'
            '<tr><td>YouTube Shorts</td><td><mark class="todo">number</mark></td><td><mark class="todo">average views</mark></td></tr>'
            '<tr><td>Website</td><td>—</td><td><mark class="todo">visitors per month</mark></td></tr>'
            '<tr><td>Email list</td><td><mark class="todo">subscribers</mark></td><td><mark class="todo">open rate</mark></td></tr></tbody></table></div>'
            '<p>Mostly beginners aged <mark class="todo">age range</mark>, in the Netherlands, Germany and the UK.</p>'
            '<h2>What we can do</h2><ul><li>An honest review in our buying guides, if the product meets our criteria</li>'
            '<li>A clearly labelled sponsored video on TikTok, Instagram or YouTube</li><li>A mention in our weekly email</li></ul>'
            '<h2>What we don’t do</h2><ul><li>Sell rankings or “best of” spots</li><li>Repeat health claims we can’t back up</li><li>Hide that content is sponsored</li></ul>'
            '<h2>Get in touch</h2><p>Email <mark class="todo">partnerships email</mark> with your brand, product and what you have in mind. '
            'Download our <mark class="todo">media kit PDF</mark>.</p></div></article></div>')
