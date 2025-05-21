genre_lookup = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}


def get_genre_names(genre_ids):
    """Convert list of genre IDs to list of genre names."""
    return [genre_lookup.get(gid, "Unknown") for gid in genre_ids]


def map_genre_names_to_ids(genre_names):
    """
    Convert genre name(s) to TMDB genre ID(s).
    Accepts a string (e.g., 'Comedy') or list of strings.
    """
    if isinstance(genre_names, str):
        genre_names = [genre_names]

    # Invert the genre_lookup dict to get name → ID
    name_to_id = {name.lower(): str(gid) for gid, name in genre_lookup.items()}
    return [
        name_to_id.get(name.lower())
        for name in genre_names
        if name.lower() in name_to_id
    ]
