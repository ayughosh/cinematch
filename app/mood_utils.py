def map_mood_to_genres():
    """Returns a dictionary mapping mood keywords to TMDB genre IDs"""
    return {
        "Happy": ["35"],  # Comedy
        "Romantic": ["10749"],  # Romance
        "Thrilling": ["53", "9648"],  # Thriller, Mystery
        "Sad": ["18"],  # Drama
        "Intense": ["878", "28"],  # Sci-Fi, Action
        "Tired": ["35", "16", "10751"],  # Comedy, Animation, Family
    }


def analyze_sentiment_polarity(text):
    """
    Analyzes sentiment polarity using TextBlob and returns a mood with emoji.
    """
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()

    # sentiment = TextBlob(text).sentiment.polarity
    sentiment = analyzer.polarity_scores(text)["compound"]
    if sentiment > 0.3:
        return "😊 Positive"
    elif sentiment < -0.3:
        return "😢 Negative"
    else:
        return "😐 Neutral"
