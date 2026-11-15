# Trust line (home page, under the hero)

One short line under the home page hero. It reads from `trust.json` in this folder and shows only the
parts that are filled in, separated by dots. Empty parts are left out, so the page looks complete
either way.

| Field | What to write | Example of the shape (write your own) |
| --- | --- | --- |
| `who` | Who you are, in one sentence, 80 characters or fewer. | `"Written by two lifters who ..."` |
| `followers` | Optional follower count, as you want it to read, 40 characters or fewer. Keep it true and update it now and then. | `"… followers on Instagram"` |
| `sources` | The sources promise. Already filled in. | `"Every claim links to its source"` |

`who` and `followers` are empty on purpose until you write them. To hide the whole line, empty all three.

After editing, rebuild (`python3 tools/build_site.py`) and commit `trust.json` with the rebuilt `index.html`.
