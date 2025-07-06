from imdb import Cinemagoer

def search_movies(ia, movie_name):
    """
    Searches for movies on IMDb that match the given text.

    Parameters:
        ia (Cinemagoer): An instance of the IMDb access class.
        movie_name (str): The name or partial name of the movie.

    Returns:
        list: List of matching movie objects.
    """
    results = ia.search_movie(movie_name)

    for i, movie in enumerate(results[:10]):
        print(f"{i+1}. {movie['title']} ({movie.get('year', 'N/A')})")

    return results


def find_and_get_reviews_link(ia, movie_name):
    # Search for the movie
    results = ia.search_movie(movie_name)

    if results:
        # Take the first result
        movie = results[0]
        movie_id = movie.movieID

        # Build the IMDb reviews link
        reviews_link = f"https://www.imdb.com/title/tt{movie_id}/reviews"

        print(f"Movie found: {movie['title']} ({movie.get('year', 'N/A')})")
        print(f"Reviews link: {reviews_link}")

        return reviews_link

    return None