language_lookup = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "ja": "Japanese",
    "ko": "Korean",
    "hi": "Hindi",
    "de": "German",
    "it": "Italian",
    "zh": "Chinese",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "tr": "Turkish",
    "pl": "Polish",
    "sv": "Swedish",
    "no": "Norwegian",
    "da": "Danish",
    "fi": "Finnish",
    "nl": "Dutch",
    "cs": "Czech",
    "el": "Greek",
    "ro": "Romanian",
    "th": "Thai",
    "id": "Indonesian",
    "he": "Hebrew",
    "vi": "Vietnamese",
    "hu": "Hungarian",
    "uk": "Ukrainian",
}


def get_language_name(code):

    return language_lookup.get(code, "Unknown")


def map_language_name_to_code(name):
    """Map full language name to TMDB code."""
    for code, lang in language_lookup.items():
        if lang.lower() == name.lower():
            return code
    return None
