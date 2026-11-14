"""How-to cues for exercises in the plan tables.

Tapping an exercise name in a plan article (desktop table or phone card) opens these cues underneath.
Exercises without an entry here simply don't expand (unless there's a video clip for them, see
assets/clips/README.md).

Rules:
- Only use cues that a Trenesis article already says. Don't invent training advice.
- 1-3 short cues per exercise, one sentence each. Note the article each cue comes from in "source",
  so it can be checked and kept in sync when the article changes.
- The key is the exercise slug: lowercase, words joined by hyphens ("leg-press"). It's also the clip
  file name (assets/clips/leg-press.mp4).
- Table names like "Leg press or squat" or "Crunches (machine, cable or bodyweight)" are matched part by
  part, without the text in brackets. ALIASES maps other names to an existing entry.
"""

CUES = {
    'bench-press': {
        'name': 'Bench press',
        'cues': ['Use a spotter or safety arms.'],
        'source': 'best-exercises-for-each-muscle',
    },
    'dumbbell-bench-press': {
        'name': 'Dumbbell bench press',
        'cues': ['Start seated with the dumbbells on your thighs and roll back with them.'],
        'source': 'dumbbell-workout-at-home',
    },
    'close-grip-cable-row': {
        'name': 'Close-grip cable row',
        'cues': ['Pull toward your belly button, not your chest.'],
        'source': 'best-exercises-for-each-muscle',
    },
    'wide-grip-cable-row': {
        'name': 'Wide-grip cable row',
        'cues': ['Pull toward your chest and squeeze your shoulder blades at the end.'],
        'source': 'best-exercises-for-each-muscle',
    },
    't-bar-row': {
        'name': 'T-bar row',
        'cues': ['Pull toward your chest and squeeze your shoulder blades.'],
        'source': 'best-exercises-for-each-muscle',
    },
    'leg-press': {
        'name': 'Leg press',
        'cues': ['Feet lower for more quads, higher for more glutes.'],
        'source': 'best-exercises-for-each-muscle',
    },
    'crunches': {
        'name': 'Crunches',
        'cues': ['Actually round your spine instead of just bending at the hips.'],
        'source': 'best-exercises-for-each-muscle',
    },
    'leg-raises': {
        'name': 'Leg raises',
        'cues': ['Curl your pelvis up rather than only lifting your legs.'],
        'source': 'best-exercises-for-each-muscle',
    },
}

# Other names for the same exercise. The article lists "Crunches (machine, cable or bodyweight)",
# so the cable crunch shares the crunch cue.
ALIASES = {
    'cable-crunch': 'crunches',
}
