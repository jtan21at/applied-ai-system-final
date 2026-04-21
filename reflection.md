# Reflection: Profile Comparisons

## High-Energy Pop vs. Chill Lofi

The pop/happy profile gravitated toward fast, energetic, major-key songs (Sunrise City, Summer Carnival, Gym Hero). The lofi/chill profile produced the exact opposite: slow, quiet, acoustic tracks (Library Rain, Midnight Coding, Deep Study). What changed was almost everything—energy dropped from ~0.85 to ~0.35, acousticness jumped from near-zero to near-1.0, and tempo fell from 120+ BPM to under 80. This makes sense: these two profiles represent fundamentally different listening contexts (working out vs. studying), and the scoring logic correctly separated them because genre, mood, AND energy all pointed in different directions simultaneously.

## High-Energy Pop vs. Deep Intense Rock

Both profiles target high energy (~0.85–0.92) and an "intense/happy" emotional tone, but the genre boundary separates them completely. The pop profile surfaced Sunrise City and Summer Carnival; the rock profile surfaced Storm Runner and Breakout Anthem. The songs that appeared in both profiles' top-5 were genre-agnostic high-energy tracks like Gym Hero (pop, intense)—it appeared #3 for the pop profile and #3 for the rock profile because it had no genre match for rock but its mood+energy were strong. This shows the genre weight doing its intended job: keeping catalogs separate while still letting great cross-genre energy matches bubble up.

## Chill Lofi vs. Deep Intense Rock

These are the most distinct profiles tested. Every single recommendation differed. The lofi profile rewarded quietness, acousticness, and restraint; the rock profile rewarded rawness and power. The acoustic bonus (+0.5) was decisive for the lofi profile—Library Rain scored 4.50 partly because it is both genre-matching AND highly acoustic. That same song would score only ~0.57 for the rock profile (near-zero energy similarity + no genre/mood match). This contrast demonstrates that when ALL preference dimensions (genre, mood, energy, acoustic) agree, the system confidently separates taste clusters and the results "feel" obviously correct to a human listener.

## Edge Case: Conflicting Preferences (pop + sad + high energy)

Testing `genre=pop, mood=sad, energy=0.9` exposed the filter-bubble effect. No song in the catalog is both pop and sad, so the mood point was never awarded. The system fell back to genre+energy, returning high-energy pop songs regardless of the requested sad mood. A user experiencing this would see recommendations that ignore half of what they asked for, with no indication that the conflict was detected. This is a real limitation: the system silently degrades rather than warning the user.
