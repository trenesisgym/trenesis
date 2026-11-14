# Trenesis: notes for Claude

Trenesis (https://trenesisgym.github.io/trenesis/) is a free fitness site for beginners.
Static site on GitHub Pages, repo `trenesisgym/trenesis`. More detail in `tools/README.md`.

## How the site is built

- The `.html` files at the repo root are **generated**. Never edit them by hand; edit the sources:
  - `tools/build_site.py`: page shell, header/footer, menus, article layout. Has `SHOW_PROGRAM` and `VERSION`.
  - `tools/parts.py`: shared pieces (side table of contents, tables, plan finder).
  - `content/articles/*.md`: articles. `content/hand/*.html`: hand-made pages (home, training, nutrition, faq).
  - `tools/logbook.py` + `tools/logbook_page.html`: the workout logbook. `tools/calculator.py`: the calorie calculator.
  - `assets/styles.css`, `assets/revision.css` (loads last, so it wins), `assets/site.js`: styles and scripts.
- Rebuild: `python3 tools/build_site.py` (needs `pip install markdown`).
- Preview: `python3 -m http.server 8000`, then open http://localhost:8000
- After changing CSS or JS, bump `VERSION` in `build_site.py` (e.g. `'2026MMDD-design'`) so browsers don't serve old cached files.
- Commit the sources **and** the rebuilt `.html` files together.

## Rules (non-negotiable)

1. **Everything must be revertible.** `git pull` on `main` first, then work on a new branch, make small commits grouped by fix, push, and open a pull request. **Never push to `main` and never merge.** The owners merge after reviewing.
2. **Privacy:** the only contact address on the site is `trenesisgym@gmail.com`. Never add a personal email, name or phone number.
3. **The paid 12-Week Program stays hidden** (`SHOW_PROGRAM = False`). Don't turn it on, and don't add prices, "Pro", "premium", waitlists or upsells anywhere visible.
4. **The logbook's hidden Pro features and tester-code check** (a SHA-256 hash in `tools/logbook_page.html`) must keep working exactly as they do now. Don't remove, rename or expose them.
5. **Don't change content or safety logic:** training plans, numbers, calculator formulas and safety limits (no fat-loss target under 18 or when underweight, the calorie floor), medical disclaimers, sources, or affiliate disclosures. For design work, change design and layout only; if some text seems confusing, list it for the owners instead of rewriting it.
6. **Keep all existing `localStorage` keys (`trenesis.*`) unchanged** so visitors don't lose their logs, reading progress or settings.
7. **No new frameworks or build tools.** Plain HTML/CSS/JS only, and the site must stay fast.
