import base64
import pickle
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
import streamlit_authenticator as stauth

# -----------------------------------------------------------USER AUTH-----------------------------------------
names = ["Samudrala Neha", " Perapa Tanuja","Basham Namrata"]
usernames = ["Sneha", "Ptanuja","Bnamrata"]

file_path = Path(__file__).parent / "hasher_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,"movie recommendation","abcdef",cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login","main")

if authentication_status == False:
      st.error("Username/Password is Incorrect")

if authentication_status == None:
      st.warning("Please enter your username and password")

if authentication_status: 

    #------------------------------------Function to fetch movie poster using TMDb API---------------------------------------------
    def fetch_poster(movie_title, tmdb_api_key):
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": tmdb_api_key,
            "query": movie_title,
        }
        data = requests.get(url, params=params)
        data = data.json()
        if "results" in data and len(data["results"]) > 0:
            poster_path = data["results"][0]["poster_path"]
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        return None
    
    
    #------------------------------------LOG-OUT BUTTON-------------------------------------------
    authenticator.logout("Logout","sidebar")


    #------------------------Function to fetch user ratings from TMDB------------------------------
    def fetch_user_ratings(movie_id, tmdb_api_key):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}"
        data = requests.get(url)
        data = data.json()
        if "vote_average" in data:
            user_rating = data["vote_average"]
            return user_rating
        return None

    #-----------------Function to fetch recommended movie trailers using TMDB API------------------------
    def fetch_trailer(movie_id, tmdb_api_key):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
        params = {
            "api_key": tmdb_api_key,
        }
        data = requests.get(url, params=params)
        data = data.json()
        if "results" in data and len(data["results"]) > 0:
            trailers = data["results"]
            return trailers
        return None

    #------------------------Function to fetch movie description and tags from TMDB-----------------------
    def fetch_description_and_keywords(movie_id, tmdb_api_key):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&append_to_response=keywords"
        data = requests.get(url)
        data = data.json()
        description = data.get("overview", "Description not available")
        keywords = data.get("keywords", {"keywords": []})["keywords"]
        tags = ", ".join(keyword["name"] for keyword in keywords)
        return description, tags

    #-----------------------Load dataset, movie list, and similarity matrix-----------------------------
    dataset = pd.read_csv('dataset.csv')  # Load your dataset.csv
    with open('movies_list.pkl', 'rb') as movies_file:
        movies_list = pickle.load(movies_file)
    with open('similarity.pkl', 'rb') as similarity_file:
        similarity_matrix = pickle.load(similarity_file)

    #-----------------------------TMDb API Key--------------------------------------------
    TMDB_API_KEY = '5ae42baea48e44a995d5027981f99e98'

    st.header('NTN- a Movie Recommender')

    #---------------------------Step 1: Enter a movie genre-------------------------------
    genre = st.text_input("Enter a movie genre (e.g., Action, Drama):")

    if not genre:
        st.warning("Please enter a genre to filter the movies.")
    else:
        #---------------Filter movies based on the entered genre------------------------
        filtered_movies = dataset[dataset['genre'].str.contains(genre, case=False, na=False)]

        if filtered_movies.empty:
            st.warning("No movies found for the entered genre.")
        else:
            #---------------Step 2: Choose a movie from the filtered list---------------
            selected_movie = st.selectbox("Select a movie:", filtered_movies['title'])

            #----------------Step 3: Calculate recommendations----------------------------------
            num_recommendations = st.number_input("Number of recommendations:", min_value=1, max_value=10, value=5)

            if st.button('Show Recommendations'):
                if selected_movie in filtered_movies['title'].values:
                    #----------------Get the index of the selected movie-------------------------
                    selected_movie_index = filtered_movies[filtered_movies['title'] == selected_movie].index[0]

                    #----------------Get the similarity scores for the selected movie------------------
                    similarity_scores = similarity_matrix[selected_movie_index]

                    #------------------Sort movies by similarity score-----------------------
                    recommended_movies = movies_list.copy()
                    recommended_movies['similarity'] = similarity_scores

                    #---------------Sort recommended movies by similarity score----------------------------
                    recommended_movies = recommended_movies.sort_values(by='similarity', ascending=False)

                    #---------------Display recommendations, posters, user ratings, movie trailers, description, and tags--------------------
                    st.subheader("Recommended Movies:")
                    for i in range(num_recommendations):
                        movie_title = recommended_movies['title'].iloc[i]
                        similarity = recommended_movies['similarity'].iloc[i]

                        #------------------Fetch movie poster using TMDb API--------------------------------
                        poster_url = fetch_poster(movie_title, TMDB_API_KEY)
                        if poster_url:
                            st.image(poster_url, caption=f"*Movie Title:* {movie_title}")

                        #-------------------------Fetch user ratings from TMDB-------------------------------
                        movie_id = recommended_movies['id'].iloc[i]  # Assuming "id" is available in your dataset
                        user_rating = fetch_user_ratings(movie_id, TMDB_API_KEY)
                        if user_rating is not None:
                            st.write(f"*User Rating:* {user_rating}")

                        #---------------------Fetch movie trailer using TMDB API--------------------------
                        trailers = fetch_trailer(movie_id, TMDB_API_KEY)
                        if trailers:
                            trailer_url = f"https://www.themoviedb.org/video/play?key={trailers[0]['key']}"
                            st.write(f"[Watch Trailer]( {trailer_url} )")
                        else:
                            st.warning(f"Trailer not found for '{movie_title}'")

                        #-----------------------Fetch description and tags from TMDB-----------------------
                        description, tags = fetch_description_and_keywords(movie_id, TMDB_API_KEY)
                        st.write(f"*Description:* {description}")
                        st.write(f"*Tags:* {tags}")

                        st.write(f"*Similarity Score:* {similarity:.2f}%")
                else:
                    st.warning("Selected movie not found. Please try a different movie title.")

# -------------------SIDEBAR------------------
st.sidebar.header("ABOUT OF DATASET ")
st.sidebar.markdown("The Dataset contains the following things  ID: Movie ID number on the website, title: Movie name genre: Movie genre (crime, adventure, etc.), original_language: Original language in which the movie is released, overview: Summary of the movie, popularity: Movie Popularity, release_date: Movie release date, vote_average: Movie vote average, vote_count: Movie vote count")


with open("image1.jpg", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")

st.sidebar.header("TOP 10 MOVIES")
st.sidebar.markdown("Based on Popularity Score we plotted a graph of top-10 movies")

st.sidebar.markdown(
    f"""
    <div style="display:table;margin-top:10%;margin-left:5%,margin-right:5%;">
        <img src="data:image1/jpg;base64, {data}" width="300" height="300">
    </div>
    """,
    unsafe_allow_html=True,
)
with open("image2.jpg", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")

st.sidebar.header("INTRA-LIST DIVERSITY")
st.sidebar.markdown("The intra-list diversity bar plot provides insight into the recommended movies' diversity within a dataset containing 10,000 films. On the X-axis, it showcases the indices of recommended movies, ranging from 0 to 2, ensuring a focused view of the top selections. The Y-axis represents the intra-list diversity scores, which span from 0.0 to 0.8. This plot helps us gauge the degree of diversity among the top movie recommendations. A higher intra-list diversity score indicates a broader selection of movies, offering a range of viewing options. Analyzing this diversity within the top recommendations assists in tailoring movie suggestions to the user's preferences and ensuring a more enriching viewing experience.")


st.sidebar.markdown(
    f"""
    <div style="display:table;margin-top:10%;margin-left:5%,margin-right:5%,margin-bottom:5%;">
        <img src="data:image2/jpg;base64, {data}" width="300" height="300">
    </div>
    """,
    unsafe_allow_html=True,
)
with open("image3.jpg", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")

st.sidebar.header("GENRE DISTRIBUTION VISUALIZATION ")
st.sidebar.markdown("The genre distribution visualization bar plot is a graphical representation of the genres present in a dataset of 10,000 movies. The plot provides an overview of the prevalence of various genres in the dataset and allows us to see the diversity of genre combinations. The visualization serves as a valuable tool for understanding the genre distribution within the dataset, aiding in further analysis and recommendations tailored to user preferences")

st.sidebar.markdown(
    f"""
    <div style="display:table;margin-top:10%;margin-left:5%,margin-right:5%;">
        <img src="data:image3/jpg;base64, {data}" width="300" height="300">
    </div>
    """,
    unsafe_allow_html=True,
)

import streamlit as st
from PIL import Image


#------------------------------- A function to convert an image file to a base64 encoded string
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ---------------------------------Open the background image file------------------------------------
bg_image = Image.open("image.jpg")

# ----------------------------------Create a style block that sets the background image of the page---------------------------
page_bg_img = '''
<style>
.stApp {
  background-image: url("data:image/jpg;base64,%s");
  background-size: cover;
}
</style>
''' % get_base64_of_bin_file("image.jpg")

#------------------------------- Use the st.markdown method to render the HTML code-----------------------------------------
st.markdown(page_bg_img, unsafe_allow_html=True)


# ------------------------------Add text at the bottom right after recommendations with "NTN" highlighted
st.markdown('<p style="text-align: right; font-size: 20px;">Developed By <span style="color: #ff0000;">NTN</span></p>', unsafe_allow_html=True)


