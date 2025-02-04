import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import hashlib
from pymongo import MongoClient
import requests

st.set_page_config(
    page_title="Movie Recommender",
    layout="centered",
    page_icon="🎬"
)

MODEL_SERVER_URL = "http://127.0.0.1:5001/invocations"

# Read credentials
with open("/app/Database/credentials.txt", "r") as file:
    lines = file.readlines()
    username = lines[0].strip()
    password = lines[1].strip()
    host = lines[2].strip()
    database_name = lines[3].strip()

@st.cache_resource(show_spinner=False)

def get_database():
    uri = f"mongodb+srv://{username}:{password}@{host}"
    client = MongoClient(uri)
    return client[database_name]

with st.spinner("Connecting to the database..."):
    db = get_database()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
def verify_password(password, hashed):
    return hash_password(password) == hashed

def login_user():
    st.title("Welcome to the Movie Recommender!")

    login_username = st.session_state.get("login_username", "")
    login_password = st.session_state.get("login_password", "")
    user_id = verify_user_in_db(login_username, login_password)
    
    if user_id is not None:
        st.session_state.logged_in = True
        st.session_state.username = login_username
        st.session_state.user_id = user_id
        st.success(f"Welcome back, {login_username}!")
    else:
        st.error("Incorrect username or password.")

def get_next_user_id():
    counter = db["counters"].find_one_and_update(
        {"_id": "user_id"},
        {"$inc": {"seq": 1}},  # Increment the sequence by 1
        return_document=True,  # Return the updated document
        upsert=True  # Ensure the document exists, create if it doesn't
    )
    return counter["seq"]

users_collection = db["users"]

def save_user_to_db(username, password):
    hashed_password = hash_password(password)
    if users_collection.find_one({"username": username}, {"_id": 1}):
        return False  # Username already exists

    user_id = get_next_user_id()  # Get a custom ID
    users_collection.insert_one({
        "_id": user_id,
        "username": username,
        "password": hashed_password
    })
    return True

def verify_user_in_db(username, password):
    user = users_collection.find_one({"username": username}, {"password": 1, "_id": 1})
    if user and verify_password(password, user["password"]):
        return user["_id"]  # Return the custom user ID
    return None

ratings_web_collection = db["ratings_web"]

def save_rating(user_id, movie_id, rating_value):
    # Data types compatible with mongo
    user_id = int(user_id)
    movie_id = int(movie_id)

    existing_rating = ratings_web_collection.find_one({"userId": user_id, "movieId": movie_id}, {"_id": 1})
    if existing_rating:
        ratings_web_collection.update_one( #Update the rating, in case it already exists
            {"_id": existing_rating["_id"]},
            {"$set": {"rating": rating_value}}
        )
        message = "Rating updated successfully!"
    else:
        ratings_web_collection.insert_one({ #New rating
            "movieId": movie_id,
            "userId": user_id,
            "rating": rating_value
        })
        message = "Rating saved successfully!"
    
    st.session_state[f"ratings_key_{user_id}"] = st.session_state.get(f"ratings_key_{user_id}", 0) + 1

    return message

def delete_rating(user_id, movie_id, title):
    """Delete a specific rating by user_id and movieId."""
    result = ratings_web_collection.delete_one({"userId": user_id, "movieId": movie_id})
    if result.deleted_count > 0:
        st.session_state["rating_deleted"] = f"Rating for '{title}' was deleted successfully."
        st.session_state[f"ratings_key_{user_id}"] = st.session_state.get(f"ratings_key_{user_id}", 0) + 1
    else:
        st.session_state["rating_deleted"] = f"Could not delete rating for '{title}'. Please try again."

@st.cache_data
def load_user_ratings(user_id, key):
    user_ratings = ratings_web_collection.find(
        {"userId": user_id},
        {"movieId": 1, "rating": 1}
    )
    user_ratings_df = pd.DataFrame(list(user_ratings))
    if not user_ratings_df.empty:
        movies = load_movies()
        user_ratings_df = user_ratings_df.merge(
            movies[["movieId", "title"]],
            on="movieId",
            how="left"
        )
    return user_ratings_df

def movie_rating_screen():
    st.title("Rate Movies")
    if "user_id" not in st.session_state:
        st.warning("You must log in to rate movies.")
        return

    user_id = st.session_state.user_id

    movies = load_movies()

    search_query = st.text_input("Search for a movie to rate:")
    filtered_movies = movies[movies["title"].str.contains(search_query, case=False, na=False)]

    if filtered_movies.empty:
        st.write("No movies found.")
        return

    filtered_movies["display"] = filtered_movies.apply(
        lambda row: f"{row['title']} ({row['year']})" if "year" in row and pd.notnull(row["year"]) else row["title"], axis=1
    )

    st.write("Select a movie to rate:")
    selected_movie_display = st.selectbox("Movies", filtered_movies["display"].tolist())

    if selected_movie_display:
        selected_movie = filtered_movies.loc[filtered_movies["display"] == selected_movie_display]
        movie_id = int(selected_movie["movieId"].values[0])
        st.write(f"Selected Movie: {selected_movie_display}")
        
        # Slider with the same format as MovieLens
        rating_value = st.slider("Rate this movie:", 0.5, 5.0, step=0.5, format="%.1f")
        
        if st.button("Submit Rating"):
            message = save_rating(user_id, movie_id, rating_value)
            st.success(message)

def display_user_ratings():
    st.title("Your Ratings")

    if "user_id" not in st.session_state:
        st.warning("You must log in to view your ratings.")
        return

    user_id = st.session_state.user_id
    key = st.session_state.get(f"ratings_key_{user_id}", 0)
    user_ratings_df = load_user_ratings(user_id, key=key)
    
    if "rating_deleted" in st.session_state:
        st.info(st.session_state.pop("rating_deleted"))  # Show message and remove it

    if user_ratings_df.empty:
        st.write("You have not rated any movies yet.")
        return

    all_ratings = pd.DataFrame({'rating': [i / 2 for i in range(1, 11)]})  # 0.5 to 5 with step of 0.5

    rating_counts = pd.DataFrame(user_ratings_df, columns=["rating"])["rating"].value_counts().reset_index()
    rating_counts.columns = ["rating", "count"]

    final_counts = all_ratings.merge(rating_counts, on="rating", how="left").fillna(0)
    final_counts["count"] = final_counts["count"].astype(int)

    # Display stars
    user_ratings_df["Rating"] = user_ratings_df["rating"].apply(
        lambda x: "⭐" * int(round(x)) + f" ({x:.1f})" if pd.notnull(x) else "No Rating"
    )

    user_ratings_df = user_ratings_df.rename(columns={"title": "Title"}).reset_index(drop=True)

    # user_ratings_df.insert(0, "No.", range(1, len(user_ratings_df) + 1))

    for _, row in user_ratings_df.iterrows():
        cols = st.columns([7, 3])
        # with cols[0]:
        #     st.write(row["No."])
        with cols[0]:
            st.write(f"{row['Title']} — {row['Rating']}")
        with cols[1]:
            if st.button("Delete", key=f"delete_{row['movieId']}"):
                delete_rating(user_id, row["movieId"], row["Title"])
                st.session_state["rating_deleted"] = f"Rating for '{row['Title']}' deleted."
                st.rerun()  # Force a rerun of the script
    
    chart = (
        alt.Chart(final_counts)
        .mark_bar(color="orange")
        .encode(
            x=alt.X("rating:N", title="Rating"),  
            y=alt.Y("count:Q", title="Amount", axis=alt.Axis(format=".0f")),  
        )
    )

    st.divider()

    st.altair_chart(chart, use_container_width=True)

def recommend_movies(user_id, n_recommendations=10):
    key = st.session_state.get(f"ratings_key_{user_id}", 0)
    user_ratings_df = load_user_ratings(user_id, key=key)
    if len(user_ratings_df) < 10:
        st.warning("You need to rate at least 10 movies to get recommendations.")
        return None

    movie_ids = user_ratings_df['movieId'].tolist()
    ratings = user_ratings_df['rating'].tolist()

    payload = {
        "dataframe_records": [{
            "user_id": user_id,
            "user_interactions": movie_ids,
            "ratings": ratings,
            "n_recommendations": n_recommendations
        }]
    }

    try:
        # Call the MLflow model server
        response = requests.post(MODEL_SERVER_URL, json=payload)
        if response.status_code != 200:
            st.error(f"API call failed with status code {response.status_code}.")
            return None

        response_json = response.json()

        recommended_ids = response_json.get("predictions", [])
        if not isinstance(recommended_ids, list) or not recommended_ids:
            st.error("No predictions found in API response.")
            return None

        movies = load_movies()

        filtered_movies = movies[movies["movieId"].isin(recommended_ids)]
        return filtered_movies[["title", "year"]]

    except requests.RequestException as e:
        st.error(f"An error occurred while calling the API: {e}")
        return None

def recommender_page():
    st.title("Movie Recommender")

    if "user_id" not in st.session_state:
        st.warning("You must log in to get recommendations.")
        return

    user_id = st.session_state.user_id

    if st.button("Recommend Movies"):
        with st.spinner("Getting recommendations..."):
            recommendations = recommend_movies(user_id)  # This function might take a while to execute

        if recommendations is not None and not recommendations.empty:
            st.subheader("Here are 10 movies we recommend:")

            if "year" in recommendations.columns:
                recommendations["Formatted Title"] = recommendations.apply(
                    lambda row: f"{row['title']} ({int(row['year'])})" if pd.notnull(row["year"]) else row["title"], axis=1
                )
            else:
                recommendations["Formatted Title"] = recommendations["title"]

            recommendations = recommendations.rename(columns={"Formatted Title": "Title"}).reset_index(drop=True)

            recommendations.insert(0, "No.", range(1, len(recommendations) + 1))

            for _, row in recommendations.iterrows():
                cols = st.columns([2, 8])
                with cols[0]:
                    st.write(row["No."])
                with cols[1]:
                    st.write(row["Title"])
        else:
            st.write("We couldn't find any recommendations for you.")


@st.cache_data
def load_movies():
    movies_collection = db["movies"]
    movies_cursor = movies_collection.find({}, {"_id": 1, "title": 1, "year": 1})
    movies_list = list(movies_cursor)
    movies_df = pd.DataFrame(movies_list)
    movies_df = movies_df.rename(columns={'_id': 'movieId'})
    return movies_df

def main():
    # st.title("Welcome to the Movie Recommender")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    def log_out():
        """Function to log the user out."""
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.success("You have been logged out.")

    if st.session_state.get("logged_in"):
        st.sidebar.button("Log Out", on_click=log_out)

    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])

        with tab1:
            st.subheader("Log In")

            st.text_input("Username", key="login_username")
            st.text_input(
                "Password",
                type="password",
                key="login_password",
                on_change=login_user,
            )

            # Optional login button for users who prefer clicking
            if st.button("Log In"):
                login_user()

        with tab2:
            st.subheader("Sign Up")
            sign_in_username = st.text_input("Choose a Username")
            sign_in_password = st.text_input("Choose a Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("Sign Up"):
                if sign_in_password != confirm_password:
                    st.error("Passwords do not match!")
                elif not sign_in_username or not sign_in_password:
                    st.error("Please provide a username and password.")
                else:
                    if save_user_to_db(sign_in_username, sign_in_password):
                        st.success("Account created! Please log in.")
                    else:
                        st.error("Username already exists.")

    if st.session_state.get("logged_in"):
        st.sidebar.title("Navigation")
        choice = st.sidebar.radio("Go to:", ["Rate Movies", "View Ratings", "Recommender"])

        if choice == "Rate Movies":
            movie_rating_screen()
        elif choice == "View Ratings":
            display_user_ratings()
        elif choice == "Recommender":
            recommender_page()
    else:
        st.markdown("""
    <div style="background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #800000; font-weight: bold;">
        <span style="font-size: 24px;">🎥</span> <strong>
        Please log in or sign up to access the movie recommender.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
