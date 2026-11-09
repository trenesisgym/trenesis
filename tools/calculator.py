"""The calorie and protein calculator page (calculator.html).

Rules (also explained in calories-and-tdee and how-much-protein):
- maintenance = Mifflin-St Jeor (sex, age, height, weight) x activity factor 1.2 / 1.375 / 1.55 / 1.725,
  shown as a +-5% range; "prefer not to say" uses the midpoint of the female and male formulas
- fat loss = 10-20% below maintenance; muscle gain = 5-10% above
- protein 1.6-2.2 g/kg, fat 0.6-1 g/kg (at least 20% of calories); above BMI 30 both use the weight at BMI 25
Safety: no fat-loss target under 18 or under BMI 18.5; fat-loss targets never go below 1,200 kcal
(1,500 for men); teen estimates carry a warning.
"""

MAIN = r'''
<div class="wrap"><header class="page-intro"><h1>Calorie and protein calculator</h1>
<p class="lead">Two numbers decide most of your results: how much you eat and how much protein you get. Fill in a few details and get a personal starting point, in kilograms or pounds.</p></header>
<div class="calc">
<form id="calc-form" class="calc-form" novalidate>
  <fieldset class="calc-units"><legend>Units</legend>
    <label><input type="radio" name="units" value="metric" checked> kg and cm</label>
    <label><input type="radio" name="units" value="imperial"> lb and ft</label>
  </fieldset>
  <fieldset class="calc-units calc-sex"><legend>Sex <span class="calc-hint">used only for the formula</span></legend>
    <label><input type="radio" name="sex" value="f"> Female</label>
    <label><input type="radio" name="sex" value="m"> Male</label>
    <label><input type="radio" name="sex" value="x" checked> Prefer not to say</label>
  </fieldset>
  <div class="calc-row">
    <div class="calc-field"><label for="age">Age <span>years</span></label>
      <input id="age" name="age" type="number" inputmode="numeric" min="0" step="1" required></div>
    <div class="calc-field"><label for="weight">Bodyweight <span data-unit="w">kg</span></label>
      <input id="weight" name="weight" type="number" inputmode="decimal" step="0.1" min="0" required></div>
  </div>
  <div class="calc-field" data-metric><label for="height-cm">Height <span>cm</span></label>
    <input id="height-cm" name="height-cm" type="number" inputmode="decimal" min="0" required></div>
  <div class="calc-field calc-ftin" data-imperial hidden><span class="calc-label" id="height-imp-label">Height</span>
    <div><label class="sr-only" for="height-ft">Feet</label><input id="height-ft" type="number" inputmode="numeric" min="0" aria-describedby="height-imp-label"><span>ft</span>
    <label class="sr-only" for="height-in">Inches</label><input id="height-in" type="number" inputmode="numeric" min="0" aria-describedby="height-imp-label"><span>in</span></div></div>
  <fieldset class="calc-choice"><legend>How active are you?</legend>
    <label><input type="radio" name="activity" value="1.2"> <span><strong>Mostly sitting</strong> Desk job, little or no exercise</span></label>
    <label><input type="radio" name="activity" value="1.375"> <span><strong>Lightly active</strong> 1–2 workouts a week, or on your feet a lot</span></label>
    <label><input type="radio" name="activity" value="1.55" checked> <span><strong>Moderately active</strong> 3–4 workouts a week</span></label>
    <label><input type="radio" name="activity" value="1.725"> <span><strong>Very active</strong> 5 or more workouts a week, or a physical job</span></label>
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
  <p class="calc-method" id="r-method"></p>
  <p class="calc-how">These are estimates. Eat this way for 2–3 weeks and watch your average weight, then adjust by 100–200 kcal. Read how it works in <a class="text-link" href="calories-and-tdee.html">calories and TDEE</a> and <a class="text-link" href="how-much-protein.html">how much protein you need</a>, then turn the numbers into meals with <a class="text-link" href="meal-planning-basics.html">meal planning made simple</a>.</p>
  </div>
</section>
</div>
<p class="disclaimer">General guidance, not medical advice. If you're pregnant or breastfeeding, have a medical condition or a history of disordered eating, talk to a doctor or dietitian instead of using a calculator. Under 18? The calculator shows maintenance or a small surplus only, because growing bodies need enough food.</p>
</div>
<script>
(function () {
  'use strict';
  var f = document.getElementById('calc-form'), out = document.getElementById('calc-result'), err = document.getElementById('calc-error');
  var KEY = 'trenesis.units.v1', LB = 2.20462;
  function val(name) { var el = f.querySelector('input[name=' + name + ']:checked'); return el ? el.value : ''; }
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
    if (e.target.name === 'units') { setUnits(e.target.value); try { localStorage.setItem(KEY, e.target.value); } catch (x) {} }
    if (!out.hidden) calc();
  });
  f.addEventListener('submit', function (e) { e.preventDefault(); calc(); });
  function r10(x) { return Math.round(x / 10) * 10; }
  function r5(x) { return Math.round(x / 5) * 5; }
  function fmt(x) { return x.toLocaleString('en-US'); }
  function wt(kg) { return val('units') === 'metric' ? '' : ' (' + r5(kg * LB) + ' lb)'; }
  function fail(msg) { err.textContent = msg; out.hidden = true; document.getElementById('calc-empty').hidden = false; }
  function calc() {
    var u = val('units'), w = parseFloat(f.weight.value), kg = u === 'metric' ? w : w / LB, cm, age = parseFloat(f.age.value);
    if (u === 'metric') cm = parseFloat(f['height-cm'].value);
    else cm = ((parseFloat(document.getElementById('height-ft').value) || 0) * 12 + (parseFloat(document.getElementById('height-in').value) || 0)) * 2.54;
    err.textContent = '';
    if (!(age >= 14 && age <= 100)) return fail('Enter your age, between 14 and 100.');
    if (!(kg >= 30 && kg <= 300)) return fail('Enter your bodyweight, between ' + (u === 'metric' ? '30 and 300 kg.' : '66 and 660 lb.'));
    if (!(cm >= 120 && cm <= 230)) return fail('Enter your height, between ' + (u === 'metric' ? '120 and 230 cm.' : '4 ft and 7 ft 6 in.'));
    var sex = val('sex'), act = parseFloat(val('activity')), goal = val('goal'), warn = [], teen = age < 18;
    // Mifflin-St Jeor resting energy, then an activity factor. "Prefer not to say" uses the midpoint of the two formulas.
    var bmr = 10 * kg + 6.25 * cm - 5 * age + ({ m: 5, f: -161, x: -78 })[sex];
    var mid = bmr * act, mLo = mid * 0.95, mHi = mid * 1.05, bmi = kg / Math.pow(cm / 100, 2);
    var floor = sex === 'm' ? 1500 : 1200;
    if (goal === 'lose' && teen) { goal = 'keep'; warn.push('Under 18, we don’t give a fat-loss target: your body still needs energy to grow. We’ve shown maintenance. Staying active and eating mostly whole foods works well; talk to a doctor if you’re worried about your weight.'); }
    else if (goal === 'lose' && bmi < 18.5) { goal = 'keep'; warn.push('For your height and weight, losing weight isn’t recommended. We’ve shown maintenance instead. If you want to change your body, aim to build muscle, and check with a doctor if you’re unsure.'); }
    var tLo, tHi, note;
    if (goal === 'lose') {
      tLo = mid * 0.8; tHi = mid * 0.9; note = 'About 10–20% below maintenance: roughly 0.5% of your bodyweight a week.';
      if (tLo < floor) {
        tLo = floor;
        if (tHi <= floor + 50) { tLo = mLo; tHi = mHi; note = 'Your estimated maintenance range.'; warn.push('Your maintenance is already fairly low, so a bigger cut could cost muscle and energy. Lose weight with the help of a doctor or dietitian.'); }
        else warn.push('We’ve kept the lower end at ' + fmt(floor) + ' kcal. Eating less than that makes it hard to get enough nutrients; talk to a doctor or dietitian first.');
      }
    } else if (goal === 'gain') { tLo = mid * 1.05; tHi = mid * 1.1; note = 'A small surplus of 5–10%: enough to build muscle without much fat.'; }
    else { tLo = mLo; tHi = mHi; note = 'Your estimated maintenance range.'; }
    if (teen) warn.push('Formulas are less accurate for teenagers. Use this as a rough guide and let your energy, growth and hunger lead.');
    // Protein and fat follow muscle, not total weight: above a BMI of 30 we use the weight at a BMI of 25 for your height.
    var ref = bmi >= 30 ? 25 * Math.pow(cm / 100, 2) : kg, tMid = (tLo + tHi) / 2;
    var pLo = ref * 1.6, pHi = ref * 2.2;
    var fLo = Math.max(ref * 0.6, tMid * 0.2 / 9), fHi = Math.max(ref * 1.0, fLo + 10);
    var carbs = Math.max(0, (tMid - ((pLo + pHi) / 2) * 4 - ((fLo + fHi) / 2) * 9) / 4);
    document.getElementById('r-cal').textContent = fmt(r10(tLo)) + '–' + fmt(r10(tHi));
    document.getElementById('r-cal-note').textContent = note;
    document.getElementById('r-protein').textContent = r5(pLo) + '–' + r5(pHi) + ' g';
    document.getElementById('r-fat').textContent = r5(fLo) + '–' + r5(fHi) + ' g';
    document.getElementById('r-carbs').textContent = 'about ' + r5(carbs) + ' g';
    document.getElementById('r-maint').textContent = fmt(r10(mLo)) + '–' + fmt(r10(mHi)) + ' kcal';
    var method = 'Calculated with the Mifflin-St Jeor equation, which uses your sex, age, height and weight, times an activity factor.';
    if (sex === 'x') method += ' Because you chose not to say, we use the midpoint between the female and male formulas.';
    if (ref !== kg) method += ' Protein and fat are based on ' + r5(ref) + ' kg' + wt(ref) + ', a healthy weight for your height, because protein needs follow muscle rather than total weight.';
    document.getElementById('r-method').textContent = method;
    var wEl = document.getElementById('r-warn'); wEl.textContent = warn.join(' '); wEl.hidden = !warn.length;
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
.calc-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; max-width: 460px; }
.calc-hint { color: var(--faint); font: 400 13px/1.4 var(--body); margin-left: 6px; }
.calc-method { margin-top: 16px; font-size: 13px; color: var(--faint); line-height: 1.55; }
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
