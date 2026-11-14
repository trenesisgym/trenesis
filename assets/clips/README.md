# Exercise clips

Short, silent loops that show an exercise. They appear inside a plan article when someone taps the
exercise name in a plan table (the same panel as the how-to cues).

A clip only shows up when its `.mp4` file exists here. No file, no clip: nothing breaks.
After adding or removing a clip, rebuild (`python3 tools/build_site.py`) and commit the clip files
together with the rebuilt `.html` files.

## File names

Name each file after the exercise slug: the exercise name in lowercase, words joined by hyphens.
It's the same key as in `tools/exercise_cues.py`.

| File | Needed? | What it is |
| --- | --- | --- |
| `leg-press.mp4` | Yes | The clip (H.264). Without it nothing shows. |
| `leg-press.webm` | Optional | A smaller VP9/AV1 version; browsers that can play it use it first. |
| `leg-press.jpg` | Recommended | Poster: one sharp frame from the clip, same size. Shown before the clip loads and, for people who turn on "reduce motion", instead of playing it. |

Table names like "Leg press or squat" are matched per part, so `leg-press.mp4` and `squat.mp4` would
both show for that row.

## Format

- **Length:** 3–5 seconds, one clean rep that loops smoothly (start and end in the same position).
- **Size:** under 500 KB per `.mp4` (keep the `.jpg` under about 60 KB).
- **Dimensions:** 720 × 720 px, **square (1:1)**. The player crops to a square, so keep the movement in
  the middle with some space around it.
- **Codec:** H.264 (MP4), no audio track. Roughly 24–30 fps.
- **Look:** plain background, side or 45° angle, whole body or the working limb in frame. No text,
  music or logos burned in.

Example with ffmpeg (from a longer source video):

```
ffmpeg -ss 2 -t 4 -i source.mov -an -vf "crop='min(iw,ih)':'min(iw,ih)',scale=720:720,fps=30" \
  -c:v libx264 -profile:v main -crf 28 -preset slow -movflags +faststart -pix_fmt yuv420p leg-press.mp4
ffmpeg -i leg-press.mp4 -frames:v 1 -q:v 4 leg-press.jpg
ffmpeg -i leg-press.mp4 -c:v libvpx-vp9 -crf 40 -b:v 0 -an leg-press.webm   # optional
```

If the `.mp4` is over 500 KB, raise `-crf` (for example to 30) and try again.

## How they behave

- Nothing downloads until someone opens the exercise (`preload="none"`, the source is added on open).
- They play muted, looped and inline when the exercise is opened, and pause when it's closed. Nothing
  plays on its own while scrolling.
- With "reduce motion" turned on, the poster shows with a play button instead.
- A play/pause button sits in the corner and works with the keyboard.
