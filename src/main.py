"""
Command line runner for the Music Recommender Simulation.

Run with:
    python -m src.main
"""

from recommender import load_songs, recommend_songs


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
    print("=" * 55)
    print(f"  Profile: {profile_name}")
    print("=" * 55)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  {rank}. {song['title']} by {song['artist']}")
        print(f"     Score : {score:.2f}")
        print(f"     Why   : {explanation}")
    print()


def main() -> None:
    """Load songs and display top-5 recommendations for each user profile."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    for profile_name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(profile_name, recommendations)


if __name__ == "__main__":
    main()
