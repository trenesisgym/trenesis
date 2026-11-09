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
        workouts.append({'name': label, 'exercises': [_exercise(r[0], r[1], r[2] if len(r) > 2 else '') for r in rows]})
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


def main_html():
    data = json.dumps(plan_data(), ensure_ascii=False).replace('</', '<\\/')
    opts = ''.join(f'<option value="{html.escape(p["id"])}">{html.escape(p["label"])}</option>' for p in plan_data())
    return MAIN.replace('{{PLANS}}', data).replace('{{OPTIONS}}', opts)


MAIN = r'''
<div class="wrap log-page">
<header class="page-intro"><h1>Workout logbook</h1>
<p class="lead">Log every set of your Trenesis plan and see what you lifted last time. It works on your phone at the gym and is saved on this device only.</p></header>

<p class="log-preview" id="log-preview" hidden>Preview: smart suggestions from the paid program are on in this browser. <button type="button" class="log-link" id="log-preview-off">Turn off</button></p>
<section class="log-setup" aria-label="Choose your plan and workout">
  <div class="log-field"><label for="log-plan">Your plan</label><select id="log-plan">{{OPTIONS}}</select></div>
  <div class="log-field"><span class="log-label" id="log-wo-label">Workout</span><div class="log-workouts" role="group" aria-labelledby="log-wo-label" id="log-workouts"></div></div>
  <fieldset class="log-units"><legend class="sr-only">Units</legend>
    <label><input type="radio" name="log-units" value="kg" checked> kg</label>
    <label><input type="radio" name="log-units" value="lb"> lb</label>
  </fieldset>
  <div class="log-field"><label for="log-date">Date</label><input type="date" id="log-date" class="log-datein"></div>
  <p class="log-planlink"><a class="text-link" id="log-planlink" href="#">Open the plan</a></p>
</section>

<form id="log-form" class="log-form" novalidate>
  <div id="log-exercises"></div>
  <div class="log-actions">
    <button class="btn" type="submit">Save workout</button>
  </div>
  <p class="log-status" id="log-status" role="status" aria-live="polite"></p>
</form>

<section class="log-history" aria-labelledby="log-history-title">
  <div class="log-history-head"><h2 id="log-history-title">History</h2>
    <div class="log-backup"><button type="button" class="log-link" id="log-export">Download backup</button>
    <label class="log-link log-import">Restore backup<input type="file" id="log-import" accept="application/json,.json" class="sr-only"></label></div></div>
  <p class="log-empty" id="log-empty">No workouts logged yet. Your saved sessions appear here.</p>
  <ol class="log-sessions" id="log-sessions"></ol>
</section>

<aside class="log-note">
  <h2>Your data stays with you</h2>
  <p>The logbook saves to this browser only: nothing is sent to us, and there's no account. Clearing your browser data deletes it, so download a backup now and then. A backup also lets you move your log to another phone or laptop.</p>
</aside>
</div>
<script type="application/json" id="log-plans">{{PLANS}}</script>
<script>
(function () {
  'use strict';
  // Automatic next-weight suggestions are reserved for the 12-Week Program. For testing, open
  // logbook.html?preview=smart once: it stays on for this browser until you press "Turn off".
  var PREVIEW = 'trenesis.log.preview.v1', qs = new URLSearchParams(location.search);
  if (qs.get('preview') === 'smart') { try { localStorage.setItem(PREVIEW, '1'); } catch (e) {} }
  if (qs.get('preview') === 'off') { try { localStorage.removeItem(PREVIEW); } catch (e) {} }
  var SMART = false; try { SMART = localStorage.getItem(PREVIEW) === '1'; } catch (e) {}
  var KEY = 'trenesis.log.v1', DRAFT = 'trenesis.log.draft.v1', PREF = 'trenesis.log.plan.v1', UNITS = 'trenesis.units.v1', LB = 2.20462;
  var PLANS = JSON.parse(document.getElementById('log-plans').textContent);
  var $ = function (id) { return document.getElementById(id); };
  function load(k, d) { try { var v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch (e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function today() { var d = new Date(); d.setMinutes(d.getMinutes() - d.getTimezoneOffset()); return d.toISOString().slice(0, 10); }
  function nice(date) { try { return new Date(date + 'T12:00:00').toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }); } catch (e) { return date; } }
  var log = load(KEY, { sessions: [] }); if (!log || !Array.isArray(log.sessions)) log = { sessions: [] };
  var units = 'kg'; try { units = localStorage.getItem(UNITS) === 'imperial' ? 'lb' : 'kg'; } catch (e) {}
  var planSel = $('log-plan'), state = { plan: null, wo: 0 };

  function planById(id) { for (var i = 0; i < PLANS.length; i++) if (PLANS[i].id === id) return PLANS[i]; return null; }
  function sessionsFor(planId) { return log.sessions.filter(function (s) { return s.plan === planId; }).sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : b.t - a.t; }); }
  function nextWorkout(plan) {
    var last = sessionsFor(plan.id)[0]; if (!last) return 0;
    for (var i = 0; i < plan.workouts.length; i++) if (plan.workouts[i].name === last.workout) return (i + 1) % plan.workouts.length;
    return 0;
  }
  function lastFor(exName) {
    var all = log.sessions.slice().sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : b.t - a.t; });
    for (var i = 0; i < all.length; i++) for (var j = 0; j < all[i].entries.length; j++) {
      var e = all[i].entries[j]; if (e.name === exName && e.sets.some(function (s) { return s.r; })) return { date: all[i].date, sets: e.sets };
    }
    return null;
  }
  function showW(kg) { if (kg == null || kg === '') return ''; var v = units === 'lb' ? kg * LB : kg; return String(Math.round(v * 2) / 2); }
  function toKg(v) { var n = parseFloat(String(v).replace(',', '.')); if (!(n >= 0)) return null; return units === 'lb' ? n / LB : n; }
  function setText(set, kind) {
    if (kind === 'level') return (set.l ? 'L' + set.l + ' × ' : '') + (set.r || '–');
    if (kind === 'time') return (set.r || '–') + ' s';
    if (kind === 'reps') return set.r || '–';
    return (set.w != null ? showW(set.w) + ' ' + units + ' × ' : '') + (set.r || '–');
  }
  function summary(sets, kind) {
    // "60 kg × 12, 11, 10" when every set used the same weight; otherwise set by set.
    var done = sets.filter(function (s) { return s.r || s.w != null; });
    var ws = done.map(function (s) { return s.w; });
    if (kind === 'weight' && done.length > 1 && ws[0] != null && ws.every(function (w) { return w === ws[0]; }))
      return showW(ws[0]) + ' ' + units + ' × ' + done.map(function (s) { return s.r || '–'; }).join(', ');
    return done.map(function (s) { return setText(s, kind); }).join(', ');
  }
  function suggestion(ex, last) {
    // Double progression: every set at the top of the rep range -> add the smallest step; otherwise same weight, one more rep.
    if (!SMART || !last || ex.kind !== 'weight') return '';
    var top = parseInt(String(ex.reps).split(/[–-]/).pop(), 10), w = last.sets[0] && last.sets[0].w;
    if (!top || w == null) return '';
    var done = last.sets.length >= ex.sets && last.sets.every(function (s) { return parseInt(s.r, 10) >= top; });
    var step = units === 'lb' ? 5 / LB : 2.5;
    return done ? 'Next: ' + showW(w + step) + ' ' + units + ' (you hit ' + top + ' on every set)' : 'Next: ' + showW(w) + ' ' + units + ', aim for one more rep';
  }

  function renderWorkouts() {
    var box = $('log-workouts'); box.textContent = '';
    state.plan.workouts.forEach(function (w, i) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'log-wo' + (i === state.wo ? ' is-active' : '');
      b.setAttribute('aria-pressed', i === state.wo ? 'true' : 'false'); b.textContent = w.name;
      if (i === nextWorkout(state.plan) && sessionsFor(state.plan.id).length) { var n = document.createElement('span'); n.className = 'log-next-tag'; n.textContent = 'next'; b.append(' ', n); }
      b.addEventListener('click', function () { saveDraft(); state.wo = i; renderWorkouts(); renderForm(); });
      box.append(b);
    });
    $('log-planlink').href = state.plan.href; $('log-planlink').textContent = 'Open the plan: ' + state.plan.label;
  }

  function inputRow(ex, n, draft) {
    var d = (draft && draft[n]) || {}, id = 'x' + Math.random().toString(36).slice(2, 8), lab = 'Set ' + (n + 1);
    var h = '<div class="log-set"><span class="log-setno" aria-hidden="true">' + (n + 1) + '</span>';
    if (ex.kind === 'weight') h += '<label class="sr-only" for="' + id + 'w">' + lab + ' weight in ' + units + '</label><input class="log-in" id="' + id + 'w" data-f="w" inputmode="decimal" placeholder="' + units + '" value="' + esc(d.w != null ? showW(d.w) : '') + '"><span class="log-x" aria-hidden="true">×</span>';
    if (ex.kind === 'level') {
      h += '<label class="sr-only" for="' + id + 'l">' + lab + ' level</label><select class="log-in log-lvl" id="' + id + 'l" data-f="l"><option value="">Level</option>';
      for (var k = 1; k <= 3; k++) h += '<option value="' + k + '"' + (String(d.l) === String(k) ? ' selected' : '') + '>L' + k + '</option>';
      h += '</select><span class="log-x" aria-hidden="true">×</span>';
    }
    var unit = ex.kind === 'time' ? 's' : 'reps';
    h += '<label class="sr-only" for="' + id + 'r">' + lab + ' ' + (ex.kind === 'time' ? 'seconds' : 'reps') + '</label><input class="log-in" id="' + id + 'r" data-f="r" inputmode="numeric" placeholder="' + unit + '" value="' + esc(d.r || '') + '"></div>';
    return h;
  }

  function renderForm() {
    var wo = state.plan.workouts[state.wo], draft = load(DRAFT, {}), dkey = state.plan.id + '/' + wo.name, dd = draft[dkey] || {};
    var html = '';
    wo.exercises.forEach(function (ex, i) {
      var last = lastFor(ex.name), target = ex.sets + ' × ' + (ex.reps || 'your level') + (ex.note ? ' ' + ex.note : '') + (ex.rest ? ' · rest ' + ex.rest : '');
      html += '<fieldset class="log-ex" data-i="' + i + '"><legend><span class="log-exname">' + esc(ex.name) + '</span><span class="log-target">' + esc(target) + '</span></legend>';
      if (ex.levels) html += '<p class="log-levels">L1 ' + esc(ex.levels[0]) + ' · L2 ' + esc(ex.levels[1]) + ' · L3 ' + esc(ex.levels[2]) + '</p>';
      var first = ex.kind === 'weight' ? 'First time: pick a weight you can lift for the bottom of the rep range.' : ex.kind === 'level' ? 'First time: pick the level where you can just reach the bottom of the rep range.' : 'First time: aim for the bottom of the range with good form.';
      html += '<p class="log-last">' + (last ? 'Last time (' + esc(nice(last.date)) + '): ' + esc(summary(last.sets, ex.kind)) : first) + '</p>';
      var sug = suggestion(ex, last); if (sug) html += '<p class="log-suggest">' + esc(sug) + '</p>';
      for (var n = 0; n < ex.sets; n++) html += inputRow(ex, n, dd[i]);
      html += '</fieldset>';
    });
    $('log-exercises').innerHTML = html;
    $('log-status').textContent = '';
  }

  function readForm() {
    var entries = [];
    $('log-exercises').querySelectorAll('.log-ex').forEach(function (fs) {
      var ex = state.plan.workouts[state.wo].exercises[+fs.dataset.i], sets = [];
      fs.querySelectorAll('.log-set').forEach(function (row) {
        var s = {}, w = row.querySelector('[data-f=w]'), l = row.querySelector('[data-f=l]'), r = row.querySelector('[data-f=r]');
        if (w && w.value.trim() !== '') { var kg = toKg(w.value); if (kg != null) s.w = Math.round(kg * 100) / 100; }
        if (l && l.value) s.l = +l.value;
        if (r && r.value.trim() !== '') s.r = r.value.trim().slice(0, 6);
        sets.push(s);
      });
      entries.push({ name: ex.name, kind: ex.kind, sets: sets });
    });
    return entries;
  }
  function saveDraft() {
    if (!state.plan) return;
    var wo = state.plan.workouts[state.wo], draft = load(DRAFT, {}), out = {};
    readForm().forEach(function (e, i) { out[i] = e.sets; });
    draft[state.plan.id + '/' + wo.name] = out; save(DRAFT, draft);
  }

  function renderHistory() {
    var list = $('log-sessions'), all = log.sessions.slice().sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : b.t - a.t; });
    list.textContent = ''; $('log-empty').hidden = all.length > 0;
    all.slice(0, 30).forEach(function (s) {
      var plan = planById(s.plan), li = document.createElement('li'); li.className = 'log-session';
      var body = s.entries.filter(function (e) { return e.sets.some(function (x) { return x.r || x.w != null; }); })
        .map(function (e) { return '<li><span>' + esc(e.name) + '</span> ' + esc(summary(e.sets, e.kind)) + '</li>'; }).join('');
      li.innerHTML = '<details><summary><span class="log-s-date">' + esc(nice(s.date)) + '</span><span class="log-s-name">' + esc(s.workout) + '</span><span class="log-s-plan">' + esc(plan ? plan.label : '') + '</span></summary><ul>' + body + '</ul><button type="button" class="log-link log-del">Delete this workout</button></details>';
      li.querySelector('.log-del').addEventListener('click', function (ev) {
        var btn = ev.currentTarget;
        if (btn.dataset.confirm !== '1') { btn.dataset.confirm = '1'; btn.textContent = 'Tap again to delete'; return; }
        log.sessions = log.sessions.filter(function (x) { return x.t !== s.t; }); save(KEY, log); renderHistory(); renderWorkouts(); renderForm();
      });
      list.append(li);
    });
  }

  function selectPlan(id, keepWo) {
    state.plan = planById(id) || PLANS[0]; planSel.value = state.plan.id; save(PREF, state.plan.id);
    if (!keepWo) state.wo = nextWorkout(state.plan);
    renderWorkouts(); renderForm();
  }

  $('log-form').addEventListener('input', function () { clearTimeout(saveDraft.t); saveDraft.t = setTimeout(saveDraft, 400); });
  $('log-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var entries = readForm(), any = entries.some(function (x) { return x.sets.some(function (s) { return s.r; }); });
    if (!any) { $('log-status').textContent = 'Enter the reps for at least one set before saving.'; return; }
    var wo = state.plan.workouts[state.wo];
    log.sessions.push({ t: Date.now(), date: $('log-date').value || today(), plan: state.plan.id, workout: wo.name, entries: entries });
    if (!save(KEY, log)) { $('log-status').textContent = 'Couldn’t save: your browser blocks storage (private mode?). Download a backup instead.'; return; }
    var draft = load(DRAFT, {}); delete draft[state.plan.id + '/' + wo.name]; save(DRAFT, draft);
    state.wo = nextWorkout(state.plan); renderWorkouts(); renderForm(); renderHistory();
    $('log-status').textContent = 'Saved. Next time: ' + state.plan.workouts[state.wo].name + '.';
    $('log-status').scrollIntoView({ block: 'nearest' });
  });
  planSel.addEventListener('change', function () { saveDraft(); selectPlan(planSel.value); });
  document.querySelectorAll('input[name=log-units]').forEach(function (r) {
    r.checked = r.value === units;
    r.addEventListener('change', function () { saveDraft(); units = r.value; try { localStorage.setItem(UNITS, units === 'lb' ? 'imperial' : 'metric'); } catch (e) {} renderForm(); renderHistory(); });
  });
  $('log-export').addEventListener('click', function () {
    var blob = new Blob([JSON.stringify({ app: 'trenesis-logbook', version: 1, exported: new Date().toISOString(), sessions: log.sessions }, null, 1)], { type: 'application/json' });
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'trenesis-logbook-' + today() + '.json'; document.body.append(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  });
  $('log-import').addEventListener('change', function (e) {
    var file = e.target.files[0]; if (!file) return;
    var rd = new FileReader();
    rd.onload = function () {
      try {
        var d = JSON.parse(rd.result); if (!d || !Array.isArray(d.sessions)) throw 0;
        var have = {}; log.sessions.forEach(function (s) { have[s.t] = 1; });
        var added = d.sessions.filter(function (s) { return s && s.t && s.date && s.plan && Array.isArray(s.entries) && !have[s.t]; });
        log.sessions = log.sessions.concat(added); save(KEY, log); renderHistory(); renderWorkouts(); renderForm();
        $('log-status').textContent = 'Backup restored: ' + added.length + ' workout' + (added.length === 1 ? '' : 's') + ' added.';
      } catch (x) { $('log-status').textContent = 'That file isn’t a Trenesis logbook backup.'; }
      e.target.value = '';
    };
    rd.readAsText(file);
  });

  if (SMART) { $('log-preview').hidden = false; $('log-preview-off').addEventListener('click', function () { try { localStorage.removeItem(PREVIEW); } catch (e) {} location.href = location.pathname; }); }
  $('log-date').value = today();
  var q = new URLSearchParams(location.search).get('plan'), start = q && planById(q) ? q : null;
  if (!start) { var pref = load(PREF, null); if (pref && planById(pref)) start = pref; }
  if (!start) { var p = load('trenesis.plan.v1', null); if (p && p.steps && p.steps[0]) { var f = String(p.steps[0].href).split('#'); start = f[0].replace('.html', '') + (f[1] ? '-4' : ''); if (!planById(start)) start = null; } }
  selectPlan(start || PLANS[0].id);
  renderHistory();
  addEventListener('pagehide', saveDraft);
})();
</script>
'''
