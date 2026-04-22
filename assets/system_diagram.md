# VibeFinder 1.0 – System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         VibeFinder 1.0                              │
│                   Music Recommendation System                        │
└─────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐         ┌────────────────────┐
  │  User Input  │         │   Song Catalog      │
  │  (genre,     │         │   data/songs.csv    │
  │   mood,      │         │   (20 songs)        │
  │   energy,    │         └────────┬───────────┘
  │   acoustic)  │                  │  load_songs()
  └──────┬───────┘                  ▼
         │              ┌────────────────────────┐
         │  validate    │  Input Validation       │
         └─────────────►│  (guardrails)           │
                        │  validate_user_prefs()  │
                        └──────────┬─────────────┘
                                   │  ValueError on bad input
                                   │  (logged + surfaced to caller)
                                   ▼
                        ┌────────────────────────┐
                        │  Content-Based Scorer  │
                        │  score_song()           │
                        │  ─────────────────────  │
                        │  genre match    +2.0    │
                        │  mood match     +1.0    │
                        │  energy prox.   0–1.0   │
                        │  acoustic bonus +0.5    │
                        └──────────┬─────────────┘
                                   │
                                   ▼
                        ┌────────────────────────┐
                        │  Confidence Scoring     │
                        │  compute_confidence()   │
                        │  score / MAX_SCORE(4.5) │
                        └──────────┬─────────────┘
                                   │
                                   ▼
                        ┌────────────────────────┐
                        │  Ranked Results        │
                        │  Top-K songs with      │
                        │  score + explanation   │
                        │  + confidence (0–1)    │
                        └──────────┬─────────────┘
                                   │
               ┌───────────────────┴────────────────────┐
               │                                        │
               ▼                                        ▼
  ┌────────────────────────┐            ┌───────────────────────────┐
  │  CLI Output (main.py)  │            │  Evaluation Harness       │
  │  Human-readable list   │            │  (evaluate.py)            │
  │  with confidence %     │            │  8 predefined test cases  │
  │                        │            │  pass/fail + avg conf     │
  └────────────────────────┘            └───────────────────────────┘
               │                                        │
               ▼                                        ▼
  ┌────────────────────────┐            ┌───────────────────────────┐
  │  recommender.log       │            │  pytest test suite        │
  │  (INFO + DEBUG events) │            │  (14 unit tests)          │
  └────────────────────────┘            └───────────────────────────┘
```

## Data Flow Summary

1. **User provides preferences** → validated by guardrails (invalid input raises `ValueError` and is logged)
2. **Song catalog loaded** from CSV → malformed rows are logged and skipped
3. **Each song scored** against the user profile using the weighted content-based algorithm
4. **Confidence computed** by normalising the raw score against the theoretical maximum (4.5)
5. **Top-K results returned** with title, artist, score, explanation, and confidence
6. **Everything logged** to `recommender.log` for observability and debugging

## Key Components

| Component | File | Purpose |
|---|---|---|
| Scorer + Confidence | `src/recommender.py` | Core algorithm + reliability metric |
| Input Guardrails | `src/recommender.py` | Validate and reject bad user input |
| CLI Runner | `src/main.py` | Display recommendations with confidence |
| Evaluation Harness | `src/evaluate.py` | Automated pass/fail test cases |
| Unit Tests | `tests/test_recommender.py` | 14 automated unit tests |
| Song Catalog | `data/songs.csv` | 20 labelled songs |
