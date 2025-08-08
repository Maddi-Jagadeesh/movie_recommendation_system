import os
import pickle
import streamlit as st
import requests
import time
import gdown

def download_large_file():
    # Use direct download link format for Google Drive
    url = "https://drive.google.com/uc?id=1RhPvI5aB_ubvQ2v2reFWIfSIj4_bzehK"
    output = "model/similarity.pkl"
    # Create 'model' directory if it doesn't exist
    if not os.path.exists("model"):
        os.makedirs("model")
    if not os.path.exists(output):
        st.info("Downloading large similarity file, please wait...")
        gdown.download(url, output, quiet=False)

# Download the large file if not present
download_large_file()

# Load the similarity matrix
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    api_key = "4aab67d72de9e9160e5e6d226f8c2c0d"  # Replace with your valid TMDb API key
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return ""  # No poster available
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for movie_id {movie_id}: {e}")
        return ""
    finally:
        time.sleep(1)  # To reduce request rate

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # Top 5 recommendations, excluding the selected movie
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

st.title('🎬 Movie Recommender System')

# Load smaller movie_list.pkl normally
movies = pickle.load(open('model/movie_list.pkl', 'rb'))

movie_list = movies['title'].values

selected_movie = st.selectbox("Select or type a movie name:", movie_list)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    if not recommended_movie_names:
        st.write("No recommendations found, please try another movie.")
    else:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            if idx < len(recommended_movie_names):
                col.text(recommended_movie_names[idx])
                if recommended_movie_posters[idx]:
                    col.image(recommended_movie_posters[idx])
                else:
                    col.write("Poster not available")
