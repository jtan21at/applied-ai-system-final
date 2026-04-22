import pytest
from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    compute_confidence,
    validate_user_prefs,
    MAX_SCORE,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


# ── Existing tests ─────────────────────────────────────────────────────────

def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ── Confidence scoring tests ───────────────────────────────────────────────

def test_confidence_perfect_score():
    """A song matching every criterion should yield confidence = 1.0."""
    confidence = compute_confidence(MAX_SCORE)
    assert confidence == pytest.approx(1.0)


def test_confidence_zero_score():
    """A score of 0 should yield confidence = 0.0."""
    assert compute_confidence(0.0) == pytest.approx(0.0)


def test_confidence_clamped_above_one():
    """Confidence must not exceed 1.0 even if score somehow exceeds MAX_SCORE."""
    assert compute_confidence(MAX_SCORE + 99) == pytest.approx(1.0)


def test_confidence_partial_score():
    """A partial score (genre + mood only = 3.0) should produce ~0.67 confidence."""
    confidence = compute_confidence(3.0)
    assert confidence == pytest.approx(3.0 / MAX_SCORE, abs=0.01)


def test_recommend_with_confidence_returns_four_tuple():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend_with_confidence(user, k=2)

    assert len(results) == 2
    song, score, explanation, confidence = results[0]
    assert song.genre == "pop"
    assert 0.0 <= confidence <= 1.0
    assert isinstance(explanation, str)


def test_recommend_with_confidence_sorted_descending():
    user = UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.4,
        likes_acoustic=True,
    )
    rec = make_small_recommender()
    results = rec.recommend_with_confidence(user, k=2)

    scores = [score for _, score, _, _ in results]
    assert scores == sorted(scores, reverse=True)


# ── Guardrail / validation tests ───────────────────────────────────────────

def test_validate_user_prefs_valid():
    """Valid prefs should not raise any exception."""
    validate_user_prefs({"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False})


def test_validate_user_prefs_energy_too_high():
    with pytest.raises(ValueError, match="energy"):
        validate_user_prefs({"genre": "pop", "mood": "happy", "energy": 1.5})


def test_validate_user_prefs_energy_too_low():
    with pytest.raises(ValueError, match="energy"):
        validate_user_prefs({"genre": "pop", "mood": "happy", "energy": -0.1})


def test_validate_user_prefs_empty_genre():
    with pytest.raises(ValueError, match="genre"):
        validate_user_prefs({"genre": "", "mood": "happy", "energy": 0.5})


def test_validate_user_prefs_empty_mood():
    with pytest.raises(ValueError, match="mood"):
        validate_user_prefs({"genre": "pop", "mood": "  ", "energy": 0.5})


def test_validate_user_prefs_non_string_genre():
    with pytest.raises(ValueError, match="genre"):
        validate_user_prefs({"genre": 123, "mood": "happy", "energy": 0.5})

