import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK resources
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

# Initialize tools
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_reviews(reviews: pd.Series) -> pd.Series:
    """
    Preprocesses a Series of text reviews by:
    - Lowercasing
    - Removing punctuation
    - Removing stopwords
    - Lemmatizing words

    Parameters:
        reviews (pd.Series): Series of raw text reviews.

    Returns:
        pd.Series: Series of lemmatized and cleaned reviews.
    """
    # Lowercase
    reviews = reviews.str.lower()

    # Remove punctuation
    reviews = reviews.str.replace(r'[^\w\s]', '', regex=True)

    # Remove stopwords
    reviews = reviews.apply(lambda x: ' '.join(
        word for word in x.split() if word not in stop_words
    ))

    # Lemmatize
    reviews = reviews.apply(lambda x: ' '.join(
        lemmatizer.lemmatize(word) for word in x.split()
    ))

    return reviews
