# Hero video (home page)

An optional silent background video behind the home page hero. Without these files the hero looks as it
does today; with them, the video plays quietly behind the headline with a dark overlay so the text stays
readable. After adding or removing files, rebuild (`python3 tools/build_site.py`) and commit the files
together with the rebuilt `index.html`.

| File | Needed? | What it is |
| --- | --- | --- |
| `hero.mp4` | Yes, for video | Landscape clip, **1600 × 900 px** (16:9), H.264, **no audio track**, 6–12 seconds, loops cleanly, **under 2 MB**. |
| `hero-portrait.mp4` | Optional | Portrait version for phones, **720 × 1280 px** (9:16), same rules, **under 1.2 MB**. Without it, phones get `hero.mp4` cropped to fit. |
| `hero.jpg` | Strongly recommended | Poster: one sharp frame, **1600 × 900 px**, **under 150 KB**. Shown at once while the video loads, and instead of the video for people who turn on "reduce motion". It also works on its own (a still background, no video). |

## What to film

- Keep the left half calm and fairly dark: the headline and button sit on top of it. Put the action on the right.
- Slow, steady movement (a set being lifted, plates being loaded). No fast cuts, no text or logos in the picture.
- The picture is cropped to fill the box, so keep the subject away from the edges.

## How it behaves

- Muted, looped, `playsinline`. It is only downloaded after the rest of the page has loaded, so it never slows the first view.
- With "reduce motion" turned on, only the poster shows and the video file is never downloaded.
- It pauses when scrolled out of view, and there is a Pause/Play button in the corner.

Example with ffmpeg:

```
ffmpeg -i source.mov -t 10 -an -vf "scale=1600:900:force_original_aspect_ratio=increase,crop=1600:900,fps=30" \
  -c:v libx264 -crf 27 -preset slow -movflags +faststart -pix_fmt yuv420p hero.mp4
ffmpeg -i hero.mp4 -frames:v 1 -q:v 4 hero.jpg
```
