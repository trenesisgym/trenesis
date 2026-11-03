"""The calorie and protein calculator page (calculator.html).

Uses the same rules as the articles:
- maintenance = bodyweight (kg) x 28-31 / 32-35 / 36-40 by activity
- fat loss = 10-20% below maintenance; muscle gain = +200-300 kcal
- protein 1.6-2.2 g/kg, fat 0.6-1 g/kg, carbs fill the rest
Safety: never shows a fat-loss target when BMI is under 18.5, and flags any
target under 1,200 kcal.
"""

MAIN = r'''
<div class="wrap"><header class="page-intro"><h1>Calorie and protein calculator</h1>
<p class="lead">Two numbers decide most of your results: how much you eat and how much protein you get. Fill in four things and get a starting point, in kilograms or pounds.</p></header>
<div class="calc">
<form id="calc-form" class="calc-form" novalidate>
  <fieldset class="calc-units"><legend>Units</legend>
    <label><input type="radio" name="units" value="metric" checked> kg and cm</label>
    <label><input type="radio" name="units" value="imperial"> lb and ft</label>
  </fieldset>
  <div class="calc-field"><label for="weight">Bodyweight <span data-unit="w">kg</span></label>
    <input id="weight" name="weight" type="number" inputmode="decimal" step="0.1" min="0" required></div>
  <div class="calc-field" data-metric><label for="height-cm">Height <span>cm</span></label>
    <input id="height-cm" name="height-cm" type="number" inputmode="decimal" min="0" required></div>
  <div class="calc-field calc-ftin" data-imperial hidden><span class="calc-label" id="height-imp-label">Height</span>
    <div><label class="sr-only" for="height-ft">Feet</label><input id="height-ft" type="number" inputmode="numeric" min="0" aria-describedby="height-imp-label"><span>ft</span>
    <label class="sr-only" for="height-in">Inches</label><input id="height-in" type="number" inputmode="numeric" min="0" aria-describedby="height-imp-label"><span>in</span></div></div>
  <fieldset class="calc-choice"><legend>How active are you?</legend>
    <label><input type="radio" name="activity" value="low"> <span><strong>Mostly sitting</strong> Little or no exercise</span></label>
    <label><input type="radio" name="activity" value="mid" checked> <span><strong>Moderately active</strong> 3–4 training sessions a week</span></label>
    <label><input type="radio" name="activity" value="high"> <span><strong>Very active</strong> 5 or more sessions a week</span></label>
  </fieldset>
  <fieldset class="calc-choice"><legend>Your goal</legend>
    <label><input type="radio" name="goal" value="lose"> <span><strong>Lose fat</strong> Keep muscle while the scale goes down</span></label>
    <label><input type="radio" name="goal" value="keep"> <span><strong>Maintain</strong> Stay the same weight, get stronger</span></label>
    <label><input type="radio" name="goal" value="gain" checked> <span><strong>Build muscle</strong> A small surplus, minimal fat gain</span></label>
  </fieldset>
  <p class="calc-error" id="calc-error" role="alert"></p>
  <button class="btn" type="submit">Calculate</button>
</form>
<section class="calc-result" aria-live="polite">
  <h2>Your starting point</h2>
  <p class="calc-empty" id="calc-empty">Fill in your details and press Calculate. You’ll get your daily calories, protein, fat and carbs here.</p>
  <div id="calc-result" hidden>
  <p class="calc-big"><span id="r-cal"></span> <span class="calc-unit">kcal a day</span></p>
  <p class="calc-sub" id="r-cal-note"></p>
  <dl class="calc-macros">
    <div><dt>Protein</dt><dd id="r-protein"></dd></div>
    <div><dt>Fat</dt><dd id="r-fat"></dd></div>
    <div><dt>Carbs</dt><dd id="r-carbs"></dd></div>
    <div><dt>Maintenance</dt><dd id="r-maint"></dd></div>
  </dl>
  <p class="calc-warn" id="r-warn" hidden></p>
  <p class="calc-how">These are estimates. Eat this way for 2–3 weeks and watch your average weight, then adjust by 100–200 kcal. Read how it works in <a class="text-link" href="calories-and-tdee.html">calories and TDEE</a> and <a class="text-link" href="how-much-protein.html">how much protein you need</a>, then turn the numbers into meals with <a class="text-link" href="meal-planning-basics.html">meal planning made simple</a>.</p>
  </div>
</section>
</div>
<p class="disclaimer">General guidance for healthy adults, not medical advice. If you're pregnant, under 18, have a medical condition or a history of disordered eating, talk to a doctor or dietitian instead of using a calculator.</p>
</div>
<script>
(function () {
  'use strict';
  var f = document.getElementById('calc-form'), out = document.getElementById('calc-result'), err = document.getElementById('calc-error');
  var KEY = 'trenesis.units.v1', LB = 2.20462;
  function units() { return f.querySelector('input[name=units]:checked').value; }
  function setUnits(u) {
    f.querySelector('input[name=units][value=' + u + ']').checked = true;
    f.querySelector('[data-unit=w]').textContent = u === 'metric' ? 'kg' : 'lb';
    f.querySelector('[data-metric]').hidden = u !== 'metric';
    f.querySelector('[data-imperial]').hidden = u === 'metric';
  }
  var saved = null; try { saved = localStorage.getItem(KEY); } catch (e) {}
  var lang = (navigator.language || '').toLowerCase();
  setUnits(saved === 'metric' || saved === 'imperial' ? saved : (lang === 'en-us' || lang === 'en-lr' || lang === 'my' ? 'imperial' : 'metric'));
  f.addEventListener('change', function (e) {
    if (e.target.name === 'units') { setUnits(e.target.value); try { localStorage.setItem(KEY, e.target.value); } catch (x) {} if (!out.hidden) calc(); }
    else if (!out.hidden) calc();
  });
  f.addEventListener('submit', function (e) { e.preventDefault(); calc(); });
  function r10(x) { return Math.round(x / 10) * 10; }
  function r5(x) { return Math.round(x / 5) * 5; }
  function fmt(x) { return x.toLocaleString('en-US'); }
  function calc() {
    var u = units(), w = parseFloat(f.weight.value), kg = u === 'metric' ? w : w / LB, cm;
    if (u === 'metric') cm = parseFloat(f['height-cm'].value);
    else cm = ((parseFloat(document.getElementById('height-ft').value) || 0) * 12 + (parseFloat(document.getElementById('height-in').value) || 0)) * 2.54;
    err.textContent = '';
    if (!(kg >= 30 && kg <= 250)) { err.textContent = 'Enter your bodyweight, between ' + (u === 'metric' ? '30 and 250 kg.' : '66 and 550 lb.'); out.hidden = true; return; }
    if (!(cm >= 120 && cm <= 230)) { err.textContent = 'Enter your height, between ' + (u === 'metric' ? '120 and 230 cm.' : '4 ft and 7 ft 6 in.'); out.hidden = true; return; }
    var act = f.querySelector('input[name=activity]:checked').value, goal = f.querySelector('input[name=goal]:checked').value;
    var F = { low: [28, 31], mid: [32, 35], high: [36, 40] }[act];
    var mLo = kg * F[0], mHi = kg * F[1], mid = (mLo + mHi) / 2, bmi = kg / Math.pow(cm / 100, 2);
    var tLo, tHi, note, warn = '';
    if (goal === 'lose' && bmi < 18.5) {
      goal = 'keep';
      warn = 'For your height and weight, losing weight isn’t recommended. We’ve shown maintenance instead. If you want to change your body, aim to build muscle, and check with a doctor if you’re unsure.';
    }
    if (goal === 'lose') { tLo = mid * 0.8; tHi = mid * 0.9; note = 'About 10–20% below maintenance: roughly 0.5% of your bodyweight a week.'; }
    else if (goal === 'gain') { tLo = mid + 200; tHi = mid + 300; note = 'A small surplus of 200–300 kcal: enough to build muscle without much fat.'; }
    else { tLo = mLo; tHi = mHi; note = 'Your estimated maintenance range.'; }
    if (tLo < 1200) warn = (warn ? warn + ' ' : '') + 'This target is very low. Eat closer to maintenance, and talk to a doctor or dietitian before eating less than this.';
    var tMid = (tLo + tHi) / 2, pLo = kg * 1.6, pHi = kg * 2.2, fLo = kg * 0.6, fHi = kg * 1.0;
    var carbs = Math.max(0, (tMid - ((pLo + pHi) / 2) * 4 - ((fLo + fHi) / 2) * 9) / 4);
    document.getElementById('r-cal').textContent = fmt(r10(tLo)) + '–' + fmt(r10(tHi));
    document.getElementById('r-cal-note').textContent = note;
    document.getElementById('r-protein').textContent = r5(pLo) + '–' + r5(pHi) + ' g';
    document.getElementById('r-fat').textContent = r5(fLo) + '–' + r5(fHi) + ' g';
    document.getElementById('r-carbs').textContent = 'about ' + r5(carbs) + ' g';
    document.getElementById('r-maint').textContent = fmt(r10(mLo)) + '–' + fmt(r10(mHi)) + ' kcal';
    var wEl = document.getElementById('r-warn'); wEl.textContent = warn; wEl.hidden = !warn;
    out.hidden = false; document.getElementById('calc-empty').hidden = true;
  }
})();
</script>
'''

CSS = '''
/* Calculator */
.calc { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 40px; align-items: start; }
.calc-form { display: grid; gap: 22px; }
.calc-form fieldset { border: 0; margin: 0; padding: 0; }
.calc-form legend, .calc-field label, .calc-label { display: block; font: 600 15px/1.4 var(--head); color: #fff; margin-bottom: 8px; padding: 0; }
.calc-field label span, .calc-label + div span { color: var(--faint); font-weight: 400; }
.calc-form input[type=number] { width: 100%; max-width: 220px; min-height: 48px; padding: 10px 14px; border: 1px solid #3d4650; border-radius: 4px; background: var(--bg); color: var(--text); font: 17px/1.3 var(--body); }
.calc-ftin > div { display: flex; align-items: center; gap: 8px; }
.calc-ftin input[type=number] { max-width: 90px; }
.calc-form input[type=number]:focus-visible { outline: 2px solid var(--ice); outline-offset: 2px; border-color: var(--ice); }
.calc-units { display: flex; flex-wrap: wrap; gap: 8px 20px; }
.calc-units legend { width: 100%; }
.calc-units label { display: inline-flex; align-items: center; gap: 8px; min-height: 40px; cursor: pointer; color: var(--text); }
.calc-choice label { display: flex; gap: 12px; align-items: flex-start; padding: 12px 14px; border: 1px solid var(--line); border-radius: 6px; margin-bottom: 8px; cursor: pointer; }
.calc-choice label:has(input:checked) { border-color: #4f7397; background: var(--panel); }
.calc-choice input, .calc-units input { accent-color: #739cc5; width: 18px; height: 18px; margin: 3px 0 0; flex-shrink: 0; }
.calc-choice span { display: block; color: var(--muted); font-size: 14px; line-height: 1.45; }
.calc-choice strong { display: block; color: #fff; font: 600 15px/1.4 var(--head); }
.calc-error { color: #ffb3a7; font-size: 14px; min-height: 1px; margin: -8px 0 0; }
.calc-form .btn { justify-self: start; min-width: 180px; }
.calc-result { position: sticky; top: 24px; padding: 28px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); }
.calc-result h2 { font-size: 18px; color: var(--muted); font-weight: 600; }
.calc-big { font: 700 44px/1.1 var(--head); color: #fff; letter-spacing: -.02em; margin-top: 10px; }
.calc-unit { font: 500 16px/1 var(--body); color: var(--muted); letter-spacing: 0; }
.calc-sub { color: var(--muted); font-size: 14px; margin-top: 6px; }
.calc-macros { display: grid; grid-template-columns: 1fr 1fr; gap: 1px; margin: 24px 0 0; background: var(--line-soft); border: 1px solid var(--line-soft); border-radius: 8px; overflow: hidden; }
.calc-macros div { background: var(--panel); padding: 14px 16px; }
.calc-macros dt { font-size: 13px; color: var(--faint); }
.calc-macros dd { margin: 2px 0 0; font: 600 18px/1.3 var(--head); color: #fff; }
.calc-warn { margin-top: 18px; padding: 12px 14px; border-left: 3px solid #d9a54a; background: #241f14; color: #f1d9a8; font-size: 14px; border-radius: 4px; }
.calc-empty { color: var(--muted); font-size: 15px; margin-top: 10px; }
.calc-how { margin-top: 20px; font-size: 14px; color: var(--muted); line-height: 1.6; }
@media (max-width: 800px) {
  .calc { grid-template-columns: 1fr; gap: 28px; }
  .calc-result { position: static; padding: 22px; }
  .calc-big { font-size: 36px; }
  .calc-form .btn { width: 100%; }
}
'''
