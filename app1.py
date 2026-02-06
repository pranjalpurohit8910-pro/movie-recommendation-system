import pickle
import streamlit as st
import requests
import base64

st.set_page_config(page_title="Movie Recommender", layout="wide")

def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .block-container {{
            background-color: rgba(0, 0, 0, 0.55);
            padding: 2rem;
            border-radius: 15px;
        }}
        h1, h2, h3, label, p, span {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg("bg.jpg")


TMDB_API_KEY = "fde7003c7cdaec04006171586107fb1c"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
FALLBACK_POSTER = "https://via.placeholder.com/300x450?text=No+Image"


# -------------------------------
# FETCH POSTER (SAFE + CACHED)
# -------------------------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US"
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        if poster_path:
            return POSTER_BASE_URL + poster_path
        else:
            return FALLBACK_POSTER

    except requests.exceptions.RequestException:
        return FALLBACK_POSTER


# -------------------------------
# RECOMMEND FUNCTION
# -------------------------------
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movie_names, recommended_movie_posters


# -------------------------------
# LOAD DATA
# -------------------------------
movies = pickle.load(open("model/movie_list.pkl", "rb"))
similarity = pickle.load(open("model/similarity.pkl", "rb"))

movie_list = movies["title"].values


# -------------------------------
# UI
# -------------------------------
st.header("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie)

    if names:
        cols = st.columns(5)
        for col, name, poster in zip(cols, names, posters):
            with col:
                st.text(name)
                st.image(poster)
    else:
        st.warning("No recommendations found.")
