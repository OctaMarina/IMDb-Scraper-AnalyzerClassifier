import pandas as pd
from textblob import TextBlob

def analyze_sentiment(reviews: pd.Series, reviews_raw: pd.Series) -> pd.DataFrame:
    """
    Analyzes the sentiment of each review using TextBlob.

    Parameters:
        reviews (pd.Series): A Series of lemmatized review texts.

    Returns:
        pd.DataFrame: A DataFrame with 'polarity' and 'subjectivity' columns.
    """
    polarity = reviews.apply(lambda x: TextBlob(x).sentiment.polarity)
    subjectivity = reviews.apply(lambda x: TextBlob(x).sentiment.subjectivity)

    return pd.DataFrame({
        'raw_reviews': reviews_raw,
        'reviews' : reviews,
        'polarity': polarity,
        'subjectivity': subjectivity
    })
