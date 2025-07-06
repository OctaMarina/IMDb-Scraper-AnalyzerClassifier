from __future__ import annotations

import streamlit as st
import pandas as pd
import altair as alt
from typing import List, Dict

from imdb import Cinemagoer
from utils.Preprocessor import preprocess_reviews
from utils.FindMovie import search_movies, find_and_get_reviews_link
from utils.Scrapper import extract_imdb_reviews
from utils.SentimentAnalysis import analyze_sentiment

ia = Cinemagoer()

st.set_page_config(
    page_title="IMDb Review Sentiment Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🎬"
)

# Custom CSS to style button and force dropdown direction
st.markdown("""
<style>
/* Make all Streamlit buttons green */
div.stButton > button {
    background-color: #4CAF50 !important;
    color: white !important;
}
/* Force selectbox dropdown to open downward */
div[data-baseweb="select"] > div {
    bottom: auto !important;
    top: 100% !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_movie_candidates(query: str) -> List[Dict]:
    return search_movies(ia, query)

@st.cache_data(show_spinner=False)
def fetch_reviews(movie_title: str) -> List[str]:
    url = find_and_get_reviews_link(ia, movie_title)
    return extract_imdb_reviews(url)

@st.cache_data(show_spinner=False)
def sentiment_pipeline(raw_reviews: List[str]) -> pd.DataFrame:
    processed = preprocess_reviews(pd.Series(raw_reviews))
    return analyze_sentiment(processed, pd.Series(raw_reviews))

def polarity_to_emoji(polarity: float) -> str:
    if polarity > 0.3:
        return "😁"
    elif polarity > 0.05:
        return "🙂"
    elif polarity < -0.3:
        return "😔"
    elif polarity < -0.05:
        return "😐"
    else:
        return "😑"

def polarity_bucket(p: float) -> str:
    if p > 0.05:
        return "Positive"
    if p < -0.05:
        return "Negative"
    return "Neutral"

def get_sentiment_color(polarity: float) -> str:
    if polarity > 0.05:
        return "#4CAF50"
    elif polarity < -0.05:
        return "#F44336"
    else:
        return "#FFC107"

def format_review_for_display(review: str, max_length: int = 300) -> str:
    return review if len(review) <= max_length else review[:max_length] + "..."

def main() -> None:
    st.title("🎬 IMDb Review Sentiment Analyzer")

    with st.container():
        st.markdown("""
        ### How It Works
        1. **Search for a movie** - Type the movie title you want to analyze
        2. **Select the correct movie** - Pick the right entry from the list
        3. **Analyze** - The app will fetch and analyze reviews automatically
        
        **What you’ll learn:** whether viewers had positive or negative opinions
        """ )

    st.divider()

    movie_query = st.text_input(
        "🔍 Search for a movie",
        placeholder="e.g. The Matrix, Inception, Avatar...",
        help="Type the title in English or your preferred language"
    )

    if movie_query:
        with st.spinner("Searching for matching movies..."):
            candidates = get_movie_candidates(movie_query)[:10]

        if not candidates:
            st.error("❌ No movies found. Try a different title!")
            st.stop()

        options: Dict[str, str] = {}
        for m in candidates:
            title = m.get('title', 'Unknown')
            year = m.get('year')
            label = f"{title} ({year})" if year else title
            options[label] = title

        selection_label = st.selectbox(
            "🎯 Select the correct movie:",
            list(options.keys()),
            help="Choose the exact movie you want to analyze"
        )
        selected_movie_title = options[selection_label]

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_button = st.button(
                "📊 Analyze Reviews",
                type="primary",
                use_container_width=True
            )

        if analyze_button:
            progress_container = st.container()

            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("📥 Fetching reviews from IMDb...")
                progress_bar.progress(25)
                raw_reviews = fetch_reviews(selected_movie_title)

                if not raw_reviews:
                    st.error("❌ No reviews found for this movie.")
                    st.stop()

                status_text.text(f"✅ Found {len(raw_reviews)} reviews! Now analyzing...")
                progress_bar.progress(50)

                df = sentiment_pipeline(raw_reviews)
                df['sentiment'] = df['polarity'].apply(polarity_bucket)
                df['emoji'] = df['polarity'].apply(polarity_to_emoji)

                status_text.text("🎯 Generating analysis report...")
                progress_bar.progress(100)

                progress_container.empty()

            st.success(f"✅ Analysis complete for **{selection_label}**!")

            avg_polarity = df['polarity'].mean()
            avg_subjectivity = df['subjectivity'].mean()

            overall_sentiment = polarity_bucket(avg_polarity)
            overall_emoji = polarity_to_emoji(avg_polarity)

            st.header(f"📊 Overall Results {overall_emoji}")

            col1, col2 = st.columns(2)
            with col1:
                st.info(f"""
                ### Overall Sentiment: {overall_sentiment} {overall_emoji}
                - The movie received {'mostly positive' if avg_polarity > 0.05 else 'mostly negative' if avg_polarity < -0.05 else 'mixed'} reviews
                - Average score: **{avg_polarity:.2f}** (scale -1 to +1)
                """ )

            with col2:
                sentiment_counts = df['sentiment'].value_counts()
                total = len(df)

                st.metric(
                    "Positive Reviews",
                    f"{sentiment_counts.get('Positive', 0)} ({sentiment_counts.get('Positive', 0)/total*100:.0f}%)",
                    delta=f"+{sentiment_counts.get('Positive', 0)} reviews"
                )
                st.metric(
                    "Negative Reviews",
                    f"{sentiment_counts.get('Negative', 0)} ({sentiment_counts.get('Negative', 0)/total*100:.0f}%)",
                    delta=f"-{sentiment_counts.get('Negative', 0)} reviews"
                )

            st.divider()

            tab1, tab2, tab3, tab4 = st.tabs(["📈 Simple Stats", "💬 Representative Reviews", "📊 Detailed Charts", "🎓 Explanations"])

            with tab1:
                st.subheader("Easy-to-Understand Statistics")

                col1, col2, col3 = st.columns(3)

                with col1:
                    positive_percent = (df['sentiment'] == 'Positive').sum() / len(df) * 100
                    st.metric(
                        "Approval Rate",
                        f"{positive_percent:.0f}%",
                        help="Percentage of viewers with positive review"
                    )

                with col2:
                    if avg_polarity > 0.3:
                        verdict = "Highly Praised"
                    elif avg_polarity > 0.05:
                        verdict = "Praised"
                    elif avg_polarity < -0.05:
                        verdict = "Not Praised"
                    else:
                        verdict = "Mixed Reviews"

                    st.metric(
                        "Viewer Verdict",
                        verdict,
                        help="Conclusion based on all reviews"
                    )

                with col3:
                    objectivity = (1 - avg_subjectivity) * 100
                    st.metric(
                        "Objectivity",
                        f"{objectivity:.0f}%",
                        help="How objective vs. emotional the reviews are"
                    )

                sentiment_chart_data = df['sentiment'].value_counts().reset_index()
                sentiment_chart_data.columns = ['Sentiment', 'Count']

                st.subheader("Sentiment Distribution")
                chart = alt.Chart(sentiment_chart_data).mark_arc().encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(
                        field="Sentiment",
                        type="nominal",
                        scale=alt.Scale(
                            domain=['Positive', 'Neutral', 'Negative'],
                            range=['#4CAF50', '#FFC107', '#F44336']
                        )
                    ),
                    tooltip=['Sentiment', 'Count']
                ).properties(height=300)

                st.altair_chart(chart, use_container_width=True)

            with tab2:
                st.subheader("🌟 Top Positive Reviews")
                st.caption("Here are the most positive viewer comments:")

                top_positive = df.nlargest(3, 'polarity')
                for _, row in top_positive.iterrows():
                    with st.container():
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            st.markdown(f"*\"{format_review_for_display(row['raw_reviews'])}\"*")
                        with col2:
                            st.markdown(f"**{row['emoji']} {row['polarity']:.2f}**")
                        st.divider()

                st.subheader("⚠️ Top Negative Reviews")
                st.caption("Here are the most critical viewer comments:")

                top_negative = df.nsmallest(3, 'polarity')
                for _, row in top_negative.iterrows():
                    with st.container():
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            st.markdown(f"*\"{format_review_for_display(row['raw_reviews'])}\"*")
                        with col2:
                            st.markdown(f"**{row['emoji']} {row['polarity']:.2f}**")
                        st.divider()

            with tab3:
                st.subheader("Detailed Sentiment Analysis Charts")

                col1, col2 = st.columns(2)

                with col1:
                    st.caption("**Polarity Distribution**")
                    hist_polarity = alt.Chart(df).mark_bar().encode(
                        x=alt.X('polarity:Q', bin=alt.Bin(maxbins=20), title='Polarity (-1 to +1)'),
                        y=alt.Y('count()', title='Number of Reviews'),
                        color=alt.value('#2196F3')
                    ).properties(height=300)
                    st.altair_chart(hist_polarity, use_container_width=True)

                with col2:
                    st.caption("**Subjectivity Distribution**")
                    hist_subjectivity = alt.Chart(df).mark_bar().encode(
                        x=alt.X('subjectivity:Q', bin=alt.Bin(maxbins=20), title='Subjectivity (0 to 1)'),
                        y=alt.Y('count()', title='Number of Reviews'),
                        color=alt.value('#FF9800')
                    ).properties(height=300)
                    st.altair_chart(hist_subjectivity, use_container_width=True)

                st.caption("**Polarity vs Subjectivity**")
                scatter = alt.Chart(df.sample(min(500, len(df)))).mark_circle(size=60, opacity=0.6).encode(
                    x=alt.X('polarity:Q', title='Polarity', scale=alt.Scale(domain=[-1, 1])),
                    y=alt.Y('subjectivity:Q', title='Subjectivity', scale=alt.Scale(domain=[0, 1])),
                    color=alt.Color('sentiment:N', scale=alt.Scale(
                        domain=['Positive', 'Neutral', 'Negative'],
                        range=['#4CAF50', '#FFC107', '#F44336']
                    )),
                    tooltip=['sentiment:N', 'polarity:Q', 'subjectivity:Q']
                ).properties(height=400)
                st.altair_chart(scatter, use_container_width=True)

            with tab4:
                st.subheader("🎓 Explanation of Terms")

                st.info("""
                ### Polarity
                Measures how positive or negative a review is.
                - **Positive values** (+0.1 to +1.0) = Positive review
                - **Negative values** (-0.1 to -1.0) = Negative review
                - **Values around 0** = Neutral review
                """ )

                st.warning("""
                ### Subjectivity
                Measures how much the review is based on personal opinions vs facts.
                - **0.0 - 0.3** = Very objective
                - **0.3 - 0.6** = Balanced
                - **0.6 - 1.0** = Very subjective
                """ )

                st.success("""
                ### Interpreting Results
                1. **Check the overall sentiment** - Positive, negative, or neutral?
                2. **Review distribution** - Are opinions split or aligned?
                3. **Read representative reviews** - Understand WHY viewers felt this way
                4. **Consider subjectivity** - Highly subjective reviews are more emotional
                """ )

    with st.sidebar:
        st.header("ℹ️ About This App")
        st.markdown("""
        This app automatically analyzes IMDb reviews to determine:
        - Whether a movie is generally liked or disliked
        - Key viewer opinions
        - How divided opinions are
        
        **Built with:**
        - AI-driven sentiment analysis
        - Natural language processing
        - Interactive visualizations
        """ )

        st.divider()
        st.caption("Developed with ❤️ using Streamlit")

if __name__ == '__main__':
    main()
