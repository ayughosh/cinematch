# app/routes.py
from flask import Blueprint, redirect, render_template, flash, url_for
import psycopg2
import time
from app.genre_mapping import get_genre_names, map_genre_names_to_ids
from app.movie_filter_utils import get_movies_by_filter
from app.mood_utils import map_mood_to_genres, analyze_sentiment_polarity
from flask_login import login_required, current_user
from app.database_utils import get_db_connection

from app.user import User
from app.language_mapping import (
    get_language_name,
    map_language_name_to_code,
    language_lookup,
)
from flask import jsonify
from flask import request, json
from app.network_utils import fetch_tmdb_with_retry
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("tmdb_api_key")
main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/search")
def search():
    query = request.args.get("query")

    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": api_key, "query": query}
    try:
        # response = requests.get(url, params=params)
        # print(response)
        data = fetch_tmdb_with_retry(url, params=params)
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error: {e}")
    # data = response.json()
    movies = data.get("results", []) if data else []
    print(json.dumps(movies[0], indent=2))
    for movie in movies:
        overview = movie.get("overview", "")
        movie["predicted_mood"] = analyze_sentiment_polarity(overview)
        genre_ids = movie.get("genre_ids", [])
        language_codes = movie.get("original_language", "")
        movie["genre_names"] = get_genre_names(genre_ids)
        movie["original_language"] = get_language_name(language_codes)
    return render_template("results.html", movies=movies, query=query)


@main.route("/suggest", methods=["GET"])
def suggest():
    try:
        query = request.args.get("q", "")
    except Exception as e:
        print("Error fetching query:", e)
        print(query)

    if not query:
        print("No query provided")
        # Handle the case where no query is provided
        return jsonify({"suggestions": []})

    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": api_key, "query": query}

    response = requests.get(url, params=params)
    data = response.json()
    suggestions = [movie["title"] for movie in data.get("results", [])][
        :5
    ]  # Top 5 matches

    return jsonify({"suggestions": suggestions})


@main.route("/mood")
def mood_recommendation():
    mood = request.args.get("mood", "").capitalize()
    if mood == "Tired":
        selected_mood = "tired"
    elif mood == "Happy":
        selected_mood = "happy"
    elif mood == "Romantic":
        selected_mood = "romantic"
    elif mood == "Intense":
        selected_mood = "intense"
    elif mood == "Thrilling":
        selected_mood = "thrilling"
    else:
        selected_mood = "sad"
    genre_ids = map_mood_to_genres().get(mood, [])
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": ",".join(genre_ids),
        "sort_by": "vote_average.desc",
    }
    movie_data = fetch_tmdb_with_retry(url, params=params)
    # response = requests.get(url, params=params)
    # data = response.json()
    if movie_data is None:
        flash(
            "⚠️ Could not fetch movie data from TMDB. Please try again shortly.",
            "warning",
        )
        return redirect(url_for("main.home"))

    movies = movie_data.get("results", [])
    # 2. Add analyzed mood sentiment (from overview)
    for movie in movies:
        overview = movie.get("overview", "")
        movie["predicted_mood"] = analyze_sentiment_polarity(overview)
        genre_ids = movie.get("genre_ids", [])
        language_codes = movie.get("original_language", "")
        movie["genre_names"] = get_genre_names(genre_ids)
        movie["original_language"] = get_language_name(language_codes)

    return render_template(
        "results.html", movies=movies, query=mood, selected_mood=selected_mood
    )


@main.route("/couple-form", methods=["POST", "GET"])
def couple_form():
    if request.method == "POST":
        # Get data from form
        mood_a = request.form.get["mood_a"]
        genres_a = request.form.getlist("genres_a")
        mood_b = request.form.get["mood_b"]
        genres_b = request.form.getlist("genres_b")

        return redirect(
            url_for(
                "main.couple_form",
                mood_a=mood_a,
                genres_a=genres_a,
                mood_b=mood_b,
                genres_b=genres_b,
            )
        )
    # If it's GET and has query params → Show results
    mood_a = request.args.get("mood_a")
    genres_a = request.args.getlist("genres_a")
    mood_b = request.args.get("mood_b")
    genres_b = request.args.getlist("genres_b")

    if mood_a and mood_b:
        # User has submitted and redirected → show results only now
        movies = couple_recommendations()
        return render_template("results.html", movies=movies)
    else:
        # Show only form
        return render_template("couple_form.html")


@main.route("/couple", methods=["GET"])
def couple_recommendations():
    # Get moods from both users and normalize
    mood_a = request.args.get("mood_a", "").capitalize()
    mood_b = request.args.get("mood_b", "").capitalize()

    print("Mood A:", mood_a)
    print("Mood B:", mood_b)
    # get selected genres as lists

    genres_a = request.args.getlist("genres_a")
    genres_b = request.args.getlist("genres_b")

    print("Genres A:", genres_a)
    print("Genres B:", genres_b)

    # set mood based genres, map genres to mood of both users and merge them
    mood_genres = set(
        map_mood_to_genres().get(mood_a, []) + map_mood_to_genres().get(mood_b, [])
    )

    # Merge genres for both
    selected_genres = set(genres_a + genres_b)

    final_genres = list(
        mood_genres & selected_genres
        or mood_genres | selected_genres
        or selected_genres
    )

    # Prepare TMDB API request
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": ",".join(final_genres),
        "sort_by": "vote_average.desc",
    }
    try:
        movie_data = fetch_tmdb_with_retry(url, params=params)
        # response = requests.get(url, params=params)
        # data = response.json()
        movies = movie_data.get("results", []) if movie_data else []
    except requests.exceptions.RequestException as e:
        print("URL:", url)
        print("Params:", params)
        print("❌ TMDB request failed:", e)
        movies = []
    for movie in movies:
        overview = movie.get("overview", "")
        movie["predicted_mood"] = analyze_sentiment_polarity(overview)
        genre_ids = movie.get("genre_ids", [])
        language_codes = movie.get("original_language", "")
        movie["genre_names"] = get_genre_names(genre_ids)
        movie["original_language"] = get_language_name(language_codes)
    return render_template(
        "couple_form.html", movies=movies, query=final_genres, couple_mode=True
    )


@main.route("/mark_watched", methods=["POST"])
def mark_watched():
    print("Mark watched called")
    movie_id = request.form.get("movie_id")
    movie_title = request.form.get("movie_title")

    conn=get_db_connection()

    cur = conn.cursor()

    # Check if movie already exists
    cur.execute(
        "SELECT watch_count FROM watched_movies WHERE movie_id = %s", (movie_id,)
    )
    result = cur.fetchone()

    if result:
        # Movie exists, update count
        watch_count = result[0] + 1
        cur.execute(
            "UPDATE watched_movies SET watch_count = %s, last_watched = NOW() WHERE movie_id = %s",
            (watch_count, movie_id),
        )
        if watch_count >= 3:
            flash(
                f"🎥 '{movie_title}' is now a Comfort Film! You've watched it {watch_count} times! 🧸"
            )
        else:
            flash(f"Movie marked as watched! You've watched it {watch_count} time(s).")

    else:
        cur.execute(
            "INSERT INTO watched_movies(movie_id, movie_title, watch_count, last_watched) VALUES (%s, %s, %s, NOW())",
            (movie_id, movie_title, 1),
        )
        flash("Movie marked as watched!", category="success")

    conn.commit()
    cur.close()
    conn.close()

    return redirect(request.referrer)


@main.route("/comfort_films")
@login_required
def comfort_films():
    # Inner helper function only for this route
    def get_comfort_movies_for_user(user_id):
        # Only fetch for the logged-in user
        conn = get_db_connection()
        cur = conn.cursor()

        # 📋 Fetch movies where watch_count >= 3
        cur.execute(
            """SELECT movie_id, movie_title, watch_count FROM watched_movies WHERE user_id = %s AND watch_count >= 3""",
            (user_id,),
        )
        rows = cur.fetchall()
        comfort_movies = []

        for row in rows:
            movie_id = row[0]  # (movie_id,) tuple

            # Fetch movie details from TMDB
            tmdb_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            params = {"api_key": api_key, "language": "en-US"}
            movie_data = fetch_tmdb_with_retry(tmdb_url, params=params)
            if movie_data:
                comfort_movies.append(movie_data)
            else:
                logging.warning(f"⚠️ Failed to fetch movie {movie_id} retries")

        conn.commit()
        cur.close()
        conn.close()
        return comfort_movies

    comfort_movies = get_comfort_movies_for_user(current_user.id)
    # 🎯 Pass these movies to movie_list.html or results.html
    return render_template("results.html", movies=comfort_movies, comfort_mode=True)


@main.route("/filter-form")
def filter_form():
    return render_template("filter.html", language_lookup=language_lookup)


@main.route("/filter")
def filter_movies():
    genre = request.args.get("genre")
    year = request.args.get("year")
    language = request.args.get("language")
    languagecode = map_language_name_to_code(language)

    genre_ids = map_genre_names_to_ids(genre)
    movies = get_movies_by_filter(genre_ids=genre_ids, year=year, language=languagecode)

    return render_template(
        "results.html", movies=movies, query=f"{genre} {year} {language}"
    )
