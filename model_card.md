# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 suggests up to 5 songs from a 20-song catalog based on a user's preferred genre, mood, energy level, and acoustic preference. It is designed for classroom exploration of how content-based recommendation systems work. It is **not** intended for deployment to real users or for making decisions that affect people in meaningful ways.

---

## 3. How the Model Works

VibeFinder reads each song's attributes and compares them to what the user said they like. It builds a score for every song by awarding points for matching details:

- **Genre match** gives the biggest boost (2 points) because genre is the most fundamental taste boundary.
- **Mood match** gives a medium boost (1 point) because mood overlaps across genres.
- **Energy closeness** contributes up to 1 point—the closer the song's energy is to what the user wants, the more points it earns. A perfect energy match adds 1 full point; a song at the opposite end adds nearly 0.
- **Acoustic bonus** adds 0.5 points if the user likes acoustic sounds and the song is very acoustic (acousticness ≥ 0.6).

After every song is scored, they are sorted from highest to lowest. The top 5 are returned, each accompanied by a plain-language explanation of why it scored the way it did, plus a **confidence score** (raw score ÷ 4.5) that tells the user how strongly the result matched their preferences.

---

## 4. Data

- **Catalog size:** 20 songs (10 original starters + 10 added during design phase).
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, edm, acoustic.
- **Moods represented:** happy, chill, intense, relaxed, moody, focused, euphoric, sad, nostalgic, melancholic.
- **Numerical features:** energy (0–1), tempo_bpm, valence (0–1), danceability (0–1), acousticness (0–1).
- Genre and mood labels were hand-chosen for variety; they do not come from any real listening data. The catalog skews toward English-language Western popular music styles and does not represent global music traditions.

---

## 5. Strengths

- **Transparent:** every recommendation comes with an explanation that any user can read and verify.
- **Reliable:** confidence scoring quantifies how well each recommendation matches the user's preferences, so the system communicates its own certainty.
- **Safe inputs:** the guardrail layer (`validate_user_prefs`) rejects invalid inputs with clear errors rather than silently producing garbage output.
- **Observable:** all events are logged to `recommender.log`, making it straightforward to audit what the system did and why.
- **Fast:** even a naive loop over 20 songs is instantaneous; the design scales to thousands without algorithmic changes.

---

## 6. Limitations and Bias

- **Genre dominance:** the genre weight (2.0) is double the mood weight (1.0), so a song from the right genre but wrong mood will almost always beat a song from the wrong genre but perfectly matching mood and energy. This could frustrate users whose primary preference is mood rather than genre.
- **Small catalog:** with only 20 songs, some genres have just 1–2 entries. An EDM fan or jazz fan will always see the same 1–2 songs at the top regardless of any other preference.
- **No diversity logic:** the system does not prevent recommending multiple songs from the same artist. Neon Echo or LoRoom can appear twice in the same top-5 list.
- **Binary matching:** genre and mood are either an exact match or zero points. There is no concept of "rock is closer to metal than it is to lofi." A rock fan asking for "intense" will get 0 genre points for a metal song if it is labelled differently.
- **Static profile:** the system assumes a single fixed taste and does not learn or adapt.
- **Silent filter-bubble degradation:** if the catalog has no songs matching a requested mood (e.g., `mood=sad` with `genre=pop`), the mood point is never awarded to any song and the user silently receives recommendations that ignore that preference. Confidence scoring partially surfaces this — the conflicting-preference edge case scored 66% confidence vs. 88–100% for well-served profiles — but an explicit warning message would be more helpful.

---

## 7. Evaluation

### Automated Test Results (pytest – 14 unit tests)

All 14 unit tests pass. Tests cover:
- Sorting correctness of recommendations
- Explanation string generation
- Confidence scoring (perfect score, zero score, clamping, partial score)
- `recommend_with_confidence` 4-tuple structure and sort order
- Guardrail validation (energy out of range, empty genre, empty mood, non-string genre)

### Evaluation Harness Results (src/evaluate.py – 8 test cases)

| Test Case | Result | Top Song | Score | Confidence |
|---|---|---|---|---|
| High-Energy Pop | ✅ PASS | Sunrise City (pop) | 3.97 | 88% |
| Chill Lofi Acoustic | ✅ PASS | Library Rain (lofi) | 4.50 | 100% |
| Deep Intense Rock | ✅ PASS | Storm Runner (rock) | 3.99 | 89% |
| Ambient Low Energy | ✅ PASS | Spacewalk Thoughts (ambient) | 4.47 | 99% |
| Jazz Relaxed | ✅ PASS | Coffee Shop Stories (jazz) | 3.97 | 88% |
| Edge Case – Conflicting Prefs | ✅ PASS | Gym Hero (pop) | 2.97 | 66% |
| Guardrail – Invalid Energy | ✅ PASS | ValueError raised | — | — |
| Guardrail – Empty Genre | ✅ PASS | ValueError raised | — | — |

**Summary:** 8/8 tests passed. Average confidence across the 6 recommendation tests: **0.88**. The lowest-confidence result (0.66) corresponded to the known edge case where the catalog cannot serve the requested mood.

### Manual Profile Comparison

| Profile | Top Result | Score | Intuition check |
|---|---|---|---|
| High-Energy Pop (happy) | Sunrise City | 3.97 | ✅ Genre + mood + energy all match |
| Chill Lofi (chill, acoustic) | Library Rain | 4.50 | ✅ Genre + mood + near-perfect energy + acoustic bonus |
| Deep Intense Rock (intense) | Storm Runner | 3.99 | ✅ Genre + mood + near-perfect energy |
| Edge case (pop + sad + high energy) | Gym Hero | 2.97 | ⚠️ No sad pop song → mood ignored, confidence dropped to 66% |

---

## 8. Limitations, Misuse, and Ethics

**What are the limitations or biases?**
The scoring weights encode the designer's assumption that genre is twice as important as mood. This is a value judgment, not a fact, and will frustrate users who care more about mood. The small, Western-centric catalog amplifies bias by limiting the variety of recommendations available to users of underrepresented genres.

**Could this system be misused?**
At this scale, the risk is low. However, if the catalog were expanded and the system were deployed, it could create filter bubbles by repeatedly recommending a narrow slice of music, discouraging listeners from exploring outside their stated preferences. A diversity penalty or serendipity injection could mitigate this.

**What surprised you during testing?**
The edge-case test was most revealing: a user asking for `pop + sad + high energy` silently received recommendations that ignored the `sad` preference because no such songs exist in the catalog. The confidence score dropped (66% vs. 88–100% for well-served profiles), which shows that the reliability layer was working — but a user-facing warning would make this even more transparent.

---

## 9. AI Collaboration Reflection

AI assistance (GitHub Copilot / Claude) was used throughout this project for two categories of work:

**Where AI was helpful:**
- Drafting boilerplate code (CSV parsing loop, pytest fixtures, dataclass definitions) — the AI produced working first drafts that saved time on mechanical typing.
- Suggesting the `compute_confidence = score / MAX_SCORE` normalization approach as a simple, interpretable way to add reliability scoring without adding complexity.

**Where AI was unhelpful or wrong:**
- When asked to suggest scoring weights, the AI proposed equal weights (genre=1.0, mood=1.0) as a "balanced" starting point. This produced poor results in testing — pop and lofi songs tied because the most important signal (genre) had no advantage. The weights had to be redesigned through human analysis of the test outputs.
- The AI initially suggested a `pandas` DataFrame for scoring instead of a plain Python loop. This added a dependency without meaningfully improving readability or performance for a 20-song catalog, so the suggestion was rejected in favor of the simpler approach.

**Takeaway:** AI tools are most valuable for tasks that are well-specified and repetitive. Tasks requiring judgment — choosing weights, deciding what failure modes matter, interpreting test results — still require human reasoning.

---

## 10. Future Work

1. **Add collaborative filtering:** compare the current user's preferences to other users' listening history to surface unexpected but relevant songs.
2. **Introduce a diversity penalty:** if the same artist already appears in the top results, apply a small score reduction to their remaining songs so the list stays varied.
3. **Soft genre similarity:** group genres into a hierarchy (e.g., "indie pop" is closer to "pop" than to "metal") and award partial genre points for near-matches.
4. **Expand the catalog:** 20 songs is far too small to represent any real user's taste. A catalog of 1,000+ songs across more global genres and moods would make the system meaningfully more useful.
5. **User-facing confidence warnings:** when confidence falls below a threshold (e.g., 0.70), surface an explicit message explaining which preference could not be satisfied.
6. **Tempo proximity scoring:** add a scoring rule similar to energy for `tempo_bpm` so users who prefer a specific BPM range are served better.
