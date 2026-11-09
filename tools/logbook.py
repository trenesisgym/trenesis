"""The workout logbook page (logbook.html).

Workouts are read from the plan articles' tables at build time, so the logbook
always matches the plans. Everything the visitor logs stays in their browser
(localStorage key trenesis.log.v1); they can export a backup file.

Smart next-weight suggestions exist in the script but are switched off
(SMART = false) because they're meant for the paid 12-Week Program.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# slug -> (menu label, short label)
PLANS = [
    ('full-body-workout-for-beginners', 'Gym · 3 days (full body)'),
    ('upper-lower-workout-plan', 'Gym · 4 days (upper/lower)'),
    ('dumbbell-workout-at-home', 'Home dumbbells · 3 days'),
    ('intermediate-home-workout', 'Home dumbbells · 4 days'),
    ('bodyweight-workout-plan', 'Bodyweight · 3 days'),
    ('bodyweight-workout-plan#4', 'Bodyweight · 4 days'),
]

SETS_RE = re.compile(r'^(\d+)\s*×\s*(.+)$')


def _rows(table_lines):
    out = []
    for line in table_lines[2:]:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        out.append(cells)
    return out


def _tables_after(md, pattern):
    """Yield (label, header cells, rows) for every table that follows a line matching pattern."""
    lines = md.splitlines()
    for i, line in enumerate(lines):
        m = re.match(pattern, line)
        if not m:
            continue
        j = i + 1
        while j < len(lines) and not lines[j].startswith('|'):
            if lines[j].startswith('#'):
                break
            j += 1
        if j >= len(lines) or not lines[j].startswith('|'):
            continue
        k = j
        while k < len(lines) and lines[k].startswith('|'):
            k += 1
        table = lines[j:k]
        header = [c.strip() for c in table[0].strip().strip('|').split('|')]
        yield m.group(1).strip(), header, _rows(table)


def _exercise(name, sets_reps, rest=''):
    m = SETS_RE.match(sets_reps)
    sets, reps = (int(m.group(1)), m.group(2)) if m else (3, sets_reps)
    note = ''
    for tail in (' per arm', ' per leg', ' per side'):
        if tail in reps:
            reps, note = reps.replace(tail, ''), tail.strip()
    timed = bool(re.search(r'\d\s*(s|seconds)\b', reps))
    reps = reps.replace(' seconds', ' s')
    return {'name': name, 'sets': sets, 'reps': reps.strip(), 'note': note, 'rest': rest, 'kind': 'time' if timed else 'weight'}


def weighted_plan(slug):
    md = (ROOT / 'content' / 'articles' / f'{slug}.md').read_text(encoding='utf-8')
    workouts = []
    for label, header, rows in _tables_after(md, r'^## ((?:Workout|Upper|Lower) [AB])\s*$'):
        if not header or header[0] != 'Exercise':
            continue
        exs = []
        for r in rows:
            ex = _exercise(r[0], r[1], r[2] if len(r) > 2 else '')
            # A 4th column ("At home instead", "No bench?") becomes a ready-made swap.
            if len(r) > 3 and r[3] and r[3].lower() not in ('no change needed', '–', '-'):
                ex['alt'] = [x.strip() for x in r[3].split(' or ')]
            exs.append(ex)
        workouts.append({'name': label, 'exercises': exs})
    return workouts


def bodyweight_plans():
    md = (ROOT / 'content' / 'articles' / 'bodyweight-workout-plan.md').read_text(encoding='utf-8')
    full = []
    for _label, header, rows in _tables_after(md, r'^## (The movements and levels)\s*$'):
        for r in rows:
            m = re.match(r'^(\w+) \((.+)\)$', r[0])
            name, reps = (m.group(1), m.group(2)) if m else (r[0], '')
            reps = re.sub(r', per leg on levels 2–3', ' (per leg on levels 2–3)', reps)
            full.append({'name': name, 'sets': 3, 'reps': reps, 'note': '', 'rest': '1–2 min', 'kind': 'level',
                         'levels': [r[1], r[2], r[3]]})
    levels = {e['name']: e['levels'] for e in full}
    split = []
    for label, header, rows in _tables_after(md, r'^\*\*(Upper day|Lower day)\*\*\s*$'):
        exs = []
        for r in rows:
            base = r[0].split(' (')[0].split(',')[0]
            if base in levels:
                exs.append({'name': r[0], 'sets': int(r[1]), 'reps': '', 'note': '', 'rest': r[2], 'kind': 'level', 'levels': levels[base]})
            else:
                m = re.match(r'^(.+?), (.+)$', r[0])
                name, reps = (m.group(1), m.group(2)) if m else (r[0], '')
                note = ''
                for tail in (' per arm', ' per leg', ' per side'):
                    if tail in reps:
                        note = tail.strip()
                        reps = reps.replace(tail, '')
                reps = re.sub(r'\s*\(.*\)', '', reps)
                exs.append({'name': name, 'sets': int(r[1]), 'reps': reps.strip(), 'note': note, 'rest': r[2], 'kind': 'reps'})
        split.append({'name': label.replace(' day', ''), 'exercises': exs})
    return [{'name': 'Full body', 'exercises': full}], split


def plan_data():
    data = []
    bw3, bw4 = bodyweight_plans()
    for slug, label in PLANS:
        if slug == 'bodyweight-workout-plan':
            workouts, href = bw3, 'bodyweight-workout-plan.html'
        elif slug == 'bodyweight-workout-plan#4':
            workouts, href = bw4, 'bodyweight-workout-plan.html#training-4-days-a-week'
        else:
            workouts, href = weighted_plan(slug), f'{slug}.html'
        assert workouts and all(w['exercises'] for w in workouts), f'no workouts parsed for {slug}'
        data.append({'id': slug.replace('#4', '-4'), 'label': label, 'href': href, 'workouts': workouts})
    return data




# Exercise library for swaps, the "add exercise" box and your own plans.
LIBRARY = {
    'Chest': ['Bench press', 'Incline bench press', 'Dumbbell bench press', 'Incline dumbbell press', 'Machine chest press',
              'Cable fly', 'Machine fly', 'Dumbbell fly', 'Push-ups', 'Dips'],
    'Back': ['Lat pulldown', 'Close-grip lat pulldown', 'Pull-ups', 'Chin-ups', 'Assisted pull-ups', 'Seated cable row',
             'Wide-grip cable row', 'Chest-supported row', 'One-arm dumbbell row', 'Barbell row', 'T-bar row', 'Machine row',
             'Straight-arm pulldown', 'Back extension'],
    'Shoulders': ['Shoulder press', 'Machine shoulder press', 'Overhead barbell press', 'Lateral raises', 'Cable lateral raises',
                  'Machine lateral raises', 'Reverse flyes', 'Face pulls'],
    'Biceps': ['Dumbbell curls', 'Barbell curls', 'EZ-bar curls', 'Incline dumbbell curls', 'Hammer curls', 'Preacher curls', 'Cable curls'],
    'Triceps': ['Triceps pushdown', 'Overhead triceps extension', 'Skull crushers', 'Close-grip bench press', 'Cable overhead extension'],
    'Quads': ['Squat', 'Front squat', 'Hack squat', 'Leg press', 'Goblet squat', 'Bulgarian split squat', 'Split squats',
              'Walking lunges', 'Reverse lunges', 'Leg extension'],
    'Hamstrings & glutes': ['Romanian deadlift', 'Deadlift', 'Leg curl', 'Seated leg curl', 'Hip thrusts', 'Glute bridge',
                            'Single-leg Romanian deadlift', 'Hip abduction machine', 'Cable kickback'],
    'Calves': ['Standing calf raise', 'Seated calf raise', 'Leg press calf raise', 'Single-leg calf raises'],
    'Core': ['Crunches', 'Cable crunch', 'Hanging knee raises', 'Leg raises', 'Plank', 'Side plank', 'Dead bug', 'Ab wheel rollout'],
}

# A Push/Pull/Legs starting point for "Create your own plan" (no PPL article exists, so it lives here).
PPL = [
    {'name': 'Push', 'exercises': [
        {'name': 'Bench press', 'sets': 3, 'reps': '6–10'}, {'name': 'Incline dumbbell press', 'sets': 3, 'reps': '8–12'},
        {'name': 'Shoulder press', 'sets': 3, 'reps': '8–12'}, {'name': 'Lateral raises', 'sets': 3, 'reps': '12–20'},
        {'name': 'Triceps pushdown', 'sets': 3, 'reps': '10–15'}, {'name': 'Overhead triceps extension', 'sets': 2, 'reps': '10–15'}]},
    {'name': 'Pull', 'exercises': [
        {'name': 'Lat pulldown', 'sets': 3, 'reps': '8–12'}, {'name': 'Seated cable row', 'sets': 3, 'reps': '8–12'},
        {'name': 'Chest-supported row', 'sets': 2, 'reps': '8–12'}, {'name': 'Face pulls', 'sets': 2, 'reps': '12–20'},
        {'name': 'Incline dumbbell curls', 'sets': 3, 'reps': '10–15'}, {'name': 'Hammer curls', 'sets': 2, 'reps': '10–15'}]},
    {'name': 'Legs', 'exercises': [
        {'name': 'Squat', 'sets': 3, 'reps': '6–10'}, {'name': 'Romanian deadlift', 'sets': 3, 'reps': '8–10'},
        {'name': 'Leg press', 'sets': 3, 'reps': '10–12'}, {'name': 'Leg curl', 'sets': 3, 'reps': '10–15'},
        {'name': 'Leg extension', 'sets': 2, 'reps': '10–15'}, {'name': 'Standing calf raise', 'sets': 3, 'reps': '10–15'}]},
]


def main_html():
    plans = plan_data()
    names = sorted({n for g in LIBRARY.values() for n in g} | {e['name'] for p in plans for w in p['workouts'] for e in w['exercises'] if e['kind'] != 'level'})
    blob = {'plans': plans, 'library': LIBRARY, 'ppl': PPL}
    data = json.dumps(blob, ensure_ascii=False).replace('</', '<\\/')
    datalist = ''.join(f'<option value="{html.escape(n)}"></option>' for n in names)
    return MAIN.replace('{{DATA}}', data).replace('{{DATALIST}}', datalist)


MAIN = (ROOT / 'tools' / 'logbook_page.html').read_text(encoding='utf-8')
