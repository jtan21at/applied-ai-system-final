import csv
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Maximum achievable raw score: genre(2.0) + mood(1.0) + energy(1.0) + acoustic(0.5)
MAX_SCORE = 4.5


@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def compute_confidence(raw_score: float) -> float:
    """Normalize a raw recommendation score to a 0.0–1.0 confidence value."""
    return min(max(raw_score / MAX_SCORE, 0.0), 1.0)


def validate_user_prefs(user_prefs: Dict) -> None:
    """
    Validate user preference dict and raise ValueError for invalid fields.
    Logs a warning for any field that falls outside expected bounds.
    """
    energy = user_prefs.get("energy", 0.5)
    if not isinstance(energy, (int, float)) or not (0.0 <= float(energy) <= 1.0):
        logger.warning("Invalid energy value '%s'; must be a float in [0.0, 1.0]", energy)
        raise ValueError(f"energy must be a float between 0.0 and 1.0, got {energy!r}")

    genre = user_prefs.get("genre", "")
    if not isinstance(genre, str) or not genre.strip():
        logger.warning("Invalid genre value '%s'; must be a non-empty string", genre)
        raise ValueError(f"genre must be a non-empty string, got {genre!r}")

    mood = user_prefs.get("mood", "")
    if not isinstance(mood, str) or not mood.strip():
        logger.warning("Invalid mood value '%s'; must be a non-empty string", mood)
        raise ValueError(f"mood must be a non-empty string, got {mood!r}")


class Recommender:
    """OOP wrapper around the scoring logic for structured recommendation and explanation."""

    def __init__(self, songs: List[Song]):
        """Initialize the recommender with a list of Song objects."""
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Compute a numeric score and list of reasons for a single song against a user profile."""
        score = 0.0
        reasons = []

        if song.genre.lower() == user.favorite_genre.lower():
            score += 2.0
            reasons.append("genre match (+2.0)")

        if song.mood.lower() == user.favorite_mood.lower():
            score += 1.0
            reasons.append("mood match (+1.0)")

        energy_similarity = 1.0 - abs(song.energy - user.target_energy)
        score += energy_similarity
        reasons.append(f"energy similarity (+{energy_similarity:.2f})")

        if user.likes_acoustic and song.acousticness >= 0.6:
            score += 0.5
            reasons.append("acoustic preference (+0.5)")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for the given user profile."""
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def recommend_with_confidence(
        self, user: UserProfile, k: int = 5
    ) -> List[Tuple[Song, float, str, float]]:
        """Return top-k results as (song, score, explanation, confidence) tuples."""
        results = []
        for song in self.songs:
            raw_score, reasons = self._score(user, song)
            explanation = "; ".join(reasons) if reasons else "No matching features found"
            confidence = compute_confidence(raw_score)
            results.append((song, raw_score, explanation, confidence))
        results.sort(key=lambda x: x[1], reverse=True)
        logger.debug(
            "recommend_with_confidence top result: '%s' score=%.2f confidence=%.2f",
            results[0][0].title if results else "N/A",
            results[0][1] if results else 0.0,
            results[0][3] if results else 0.0,
        )
        return results[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        _, reasons = self._score(user, song)
        return "; ".join(reasons) if reasons else "No matching features found"


def load_songs(csv_path: str) -> List[Dict]:
    """
    Load songs from a CSV file and return a list of dicts with numeric fields converted.
    Logs a warning and skips any row that cannot be parsed.
    """
    songs = []
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row["id"] = int(row["id"])
                    row["energy"] = float(row["energy"])
                    row["tempo_bpm"] = float(row["tempo_bpm"])
                    row["valence"] = float(row["valence"])
                    row["danceability"] = float(row["danceability"])
                    row["acousticness"] = float(row["acousticness"])
                    songs.append(row)
                except (KeyError, ValueError) as exc:
                    logger.warning("Skipping malformed song row %s: %s", row.get("id", "?"), exc)
    except FileNotFoundError:
        logger.error("Song catalog not found at path: %s", csv_path)
        raise
    logger.info("Loaded %d songs from '%s'", len(songs), csv_path)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, str]:
    """Score a single song dict against user preferences and return (score, explanation)."""
    score = 0.0
    reasons = []

    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        score += 2.0
        reasons.append("genre match (+2.0)")

    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        score += 1.0
        reasons.append("mood match (+1.0)")

    target_energy = user_prefs.get("energy", 0.5)
    energy_similarity = 1.0 - abs(song["energy"] - target_energy)
    score += energy_similarity
    reasons.append(f"energy similarity (+{energy_similarity:.2f})")

    if user_prefs.get("likes_acoustic", False) and song["acousticness"] >= 0.6:
        score += 0.5
        reasons.append("acoustic preference (+0.5)")

    return score, "; ".join(reasons)


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str, float]]:
    """
    Score all songs, sort by descending score, and return the top-k as
    (song, score, explanation, confidence) tuples.

    Raises ValueError if user_prefs fails validation.
    """
    validate_user_prefs(user_prefs)
    scored = []
    for song in songs:
        raw_score, explanation = score_song(user_prefs, song)
        confidence = compute_confidence(raw_score)
        scored.append((song, raw_score, explanation, confidence))
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:k]
    if top:
        logger.info(
            "Recommendations for genre='%s' mood='%s' energy=%.2f: "
            "top='%s' score=%.2f confidence=%.2f",
            user_prefs.get("genre"),
            user_prefs.get("mood"),
            user_prefs.get("energy", 0.5),
            top[0][0].get("title"),
            top[0][1],
            top[0][3],
        )
    return top
