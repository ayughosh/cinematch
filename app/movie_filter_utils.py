import os
from app.network_utils import fetch_tmdb_with_retry
from app.genre_mapping import get_genre_names
from app.language_mapping import get_language_name
from app.mood_utils import analyze_sentiment_polarity

api_key = os.getenv("tmdb_api_key")


def get_movies_by_filter(
    genre_ids=None, language=None, year=None, sort_by="vote_average.desc"
):
    """Fetch and annotate movies using TMDB filtering."""
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "sort_by": sort_by,
        "with_genres": ",".join(genre_ids) if genre_ids else None,
        "with_original_language": language,
        "primary_release_year": year,
    }
    # Remove empty params
    params = {k: v for k, v in params.items() if v}

    data = fetch_tmdb_with_retry(url, params=params)
    if not data:
        return []

    movies = data.get("results", [])
    for movie in movies:
        overview = movie.get("overview", "")
        movie["predicted_mood"] = analyze_sentiment_polarity(overview)
        genre_ids = movie.get("genre_ids", [])
        language_code = movie.get("original_language", "")
        movie["genre_names"] = get_genre_names(genre_ids)
        movie["original_language"] = get_language_name(language_code)

    return movies
