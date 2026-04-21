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

After every song is scored, they are sorted from highest to lowest. The top 5 are returned, each accompanied by a plain-language explanation of why it scored the way it did.

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
- **Fast:** even a naive loop over 20 songs is instantaneous; the design scales to thousands without algorithmic changes.
- **Intuitive for clear profiles:** when tested with a "high-energy pop / happy" profile, the top two results were the two happiest, most energetic pop songs in the catalog—exactly what a human curator would pick.
- **Acoustic bonus works well** for lofi/ambient profiles—those genres naturally have high acousticness, so the bonus rewards the right songs without needing extra configuration.

---

## 6. Limitations and Bias

- **Genre dominance:** the genre weight (2.0) is double the mood weight (1.0), so a song from the right genre but wrong mood will almost always beat a song from the wrong genre but perfectly matching mood and energy. This could frustrate users whose primary preference is mood rather than genre.
- **Small catalog:** with only 20 songs, some genres have just 1–2 entries. An EDM fan or jazz fan will always see the same 1–2 songs at the top regardless of any other preference.
- **No diversity logic:** the system does not prevent recommending multiple songs from the same artist. Neon Echo or LoRoom can appear twice in the same top-5 list.
- **Binary matching:** genre and mood are either an exact match or zero points. There is no concept of "rock is closer to metal than it is to lofi." A rock fan asking for "intense" will get 0 genre points for a metal song if it is labelled differently.
- **Static profile:** the system assumes a single fixed taste and does not learn or adapt.

---

## 7. Evaluation

Three distinct user profiles were tested:

| Profile | Top Result | Score | Intuition check |
|---|---|---|---|
| High-Energy Pop (happy) | Sunrise City | 3.97 | ✅ Makes sense—genre + mood + energy all match |
| Chill Lofi (chill, acoustic) | Library Rain | 4.50 | ✅ Highest acousticness in the catalog, matching genre+mood |
| Deep Intense Rock (intense) | Storm Runner | 3.99 | ✅ Genre + mood + near-perfect energy for rock |

An adversarial edge case was also tested: `genre=pop, mood=sad, energy=0.9` (conflicting preferences). The system returned pop songs with high energy because genre+energy outweighed the mood mismatch—there are no sad pop songs in the catalog, so the mood point was never awarded to any result. This is a clear filter-bubble effect: the missing mood label meant the user received songs that partially matched rather than no recommendation at all.

A weight-shift experiment (genre weight doubled to 4.0) confirmed that the recommendations became almost entirely genre-driven, with mood and energy barely affecting the ranking order.

---

## 8. Future Work

1. **Add collaborative filtering:** compare the current user's preferences to other users' listening history to surface unexpected but relevant songs.
2. **Introduce a diversity penalty:** if the same artist already appears in the top results, apply a small score reduction to their remaining songs so the list stays varied.
3. **Soft genre similarity:** group genres into a hierarchy (e.g., "indie pop" is closer to "pop" than to "metal") and award partial genre points for near-matches.
4. **Expand the catalog:** 20 songs is far too small to represent any real user's taste. A catalog of 1,000+ songs across more global genres and moods would make the system meaningfully more useful.
5. **Tempo proximity scoring:** add a scoring rule similar to energy for `tempo_bpm` so users who prefer a specific BPM range are served better.

---

## 9. Personal Reflection

Building VibeFinder revealed how much hidden judgment goes into every weight and threshold. Choosing "genre = 2.0" instead of "genre = 1.5" is not a technical decision—it is a value decision about what matters most to a listener. The system felt surprisingly smart when a profile matched the catalog well, and surprisingly dumb when the catalog had gaps. That gap between "feels smart" and "is actually smart" is exactly what makes real-world AI systems risky: users trust the output without seeing the edge cases. Working through the bias analysis made clear that every recommender inevitably encodes the assumptions of whoever built the dataset and designed the weights—a fact worth remembering any time an algorithm decides what music, news, or products you see.
