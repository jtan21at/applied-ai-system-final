"""
Command line runner for the Music Recommender Simulation.

Run with:
    PYTHONPATH=src python -m src.main
"""

import logging
import sys

from recommender import load_songs, recommend_songs

# Configure logging: INFO to console, DEBUG to file
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("recommender.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
# Silence debug noise on stdout; file handler keeps full detail
logging.getLogger().handlers[1].setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False,
    },
}


def print_recommendations(profile_name: str, recommendations: list) -> None:
    """Print formatted recommendation results for a named user profile."""
    print("=" * 60)
    print(f"  Profile: {profile_name}")
    print("=" * 60)
    for rank, (song, score, explanation, confidence) in enumerate(recommendations, start=1):
        print(f"  {rank}. {song['title']} by {song['artist']}")
        print(f"     Score      : {score:.2f}  |  Confidence: {confidence:.0%}")
        print(f"     Why        : {explanation}")
    print()


def main() -> None:
    """Load songs and display top-5 recommendations for each user profile."""
    logger.info("VibeFinder starting up")
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    for profile_name, user_prefs in PROFILES.items():
        try:
            recommendations = recommend_songs(user_prefs, songs, k=5)
            print_recommendations(profile_name, recommendations)
        except ValueError as exc:
            logger.error("Invalid profile '%s': %s", profile_name, exc)
            print(f"[ERROR] Skipping '{profile_name}': {exc}\n")

    logger.info("VibeFinder finished")


if __name__ == "__main__":
    main()
