"""
This code is used to connect to a MongoDB database and access the data stored within it.
1. Construct the MongoDB URI: Constructs the MongoDB URI using the provided username, password, and host. It then creates a MongoClient object to establish a connection to the MongoDB server.
2. Connect to the database: Connects to the specific database named database_name within the MongoDB server.
3. Load movies dataframe: Accesses the "movies" collection in the database, retrieves all documents from the collection, converts them into a list, and then into a pandas DataFrame. It also renames the _id column to movieId. Same for the "ratings" collection.
"""

from pymongo import MongoClient
import pandas as pd
# Read credentials from file
with open("./Database/credentials.txt", "r") as file:
    lines = file.readlines()
    username = lines[0].strip()
    password = lines[1].strip()
    host = lines[2].strip()
    database_name = lines[3].strip()

# Construct the MongoDB URI
uri = f"mongodb+srv://{username}:{password}@{host}"
client = MongoClient(uri)

#Connect to database
db = client[database_name]

#Load movies dataframe
movies = db["movies"]
movies = list(movies.find())
movies = pd.DataFrame(movies)
movies = movies.rename(columns = {'_id':'movieId'})

#Load ratings dataframe
ratings = db["ratings"]
ratings = list(ratings.find())
ratings = pd.DataFrame(ratings)
ratings = ratings.rename(columns = {'_id':'ratingId'})

