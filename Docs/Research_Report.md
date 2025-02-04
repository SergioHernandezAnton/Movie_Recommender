Investigation report 

This report aims to give our team some insight on the usual pipeline, methodologies and issues that are common to projects like ours, that is, developing a movie recommender based on a certain database and implementing it in some kind of web application.

1. What exactly is a recommender?

A recommender is just a system used to improve the experience of users in various fields (online shopping, entertainment…) which consists on using machine learning techniques to learn patterns from data and make relevant suggestions. 

In online shopping, for example, a recommender may analyze what products you usually buy, or when you buy them, to infer what other products may be interesting for you. In entertainment (music, movies…) , it works in a similar way; based on your ratings and other features, the recommender can understand what are your preferences and select personally what to offer. The recommender, hence, improves both the user experience and the quality of the offered service, particularly for companies which have huge catalogs to offer such as Spotify, Netflix or Amazon. 

2. Which type of data is generally used for (movie) recommenders?

Recommenders use, in general, two types of data: user data and item data. For this section I will focus on recommenders for movies, so in this context an item is a movie.

User data refers, initially, to basic, intrinsic characteristics of the users, like age and gender. Item data contains some intrinsic characteristics too, like year of release, genre, director, lead actors, etc. The basis for a recommender, though, is to have some type of relation between the two, which is usually ratings of the movies (whether in form of a score or a simple “like” and “don’t like”); this is the stepping stone from which the first suggestions can be generated. 

Aside from the common problems like missing values, formatting issues, etc. a particular problem that can arise from the data is an imbalance in the ratings. What I mean by this is that since not every user rates every movie, some users may have very few ratings and some others can have a lot of them. Moreover, some users may be more “demanding” and almost never rate everything with the highest grade, while others may tend to rate everything that they like highly. For both of these problems, we will need some type of normalization; a common approach is to make each user have a “rating threshold” which indicates from which point they consider that a movie is good. 

3. How can we generate a recommender from the data that we have?

Given the data explained in the previous section, a first approach to making new suggestions is to recommend movies that are similar to what the user likes. For example, if a User rates Romance movies highly, the recommender will suggest more Romance movies; or if a User does not like movies directed by Quentin Tarantino, the recommender will avoid those. This is a simple approach; we want to find the similarity between the user’s preferences and the item’s attributes. This is known as Content-based Filtering.

While this approach is useful and can generate good recommenders, it is lacking because of its simplicity. Using the same examples as above, only recommending Romance films can get tiring for the user, and maybe they would like a Quentin Tarantino movie but the recommender hides them all. In short, the recommender limits the experience of the user by playing too safe, which can lead to repetitive suggestions and to isolation of items that have a lot of particularities.

To solve these issues, there’s Collaborative Filtering (CF). This approach is called collaborative because it considers not only similarity between items but between users. Content-based considers just one user for the suggestions made to them; CF considers the multiple users’ interactions with items to generate suggestions. For example, a CF algorithm may detect that two users like similar Terror movies, and also that the first user liked a certain movie that the second user has not seen. So, given the similarity between users, that movie will be recommended to the second user.

4. How can we evaluate our recommender?

Now that we have an idea of how to manage the data and how to develop a recommender, let’s see what we should take into account for its evaluation. 

- Accuracy: is the model able to predict all the user’s preferences correctly?
- Quality: while it may seem similar to accuracy, quality refers more to things like relevance (does the user find the recommendations interesting?), novelty (are new items being recommended to the user?) and diversity (are the recommendations too repetitive?)
- Technicalities: this includes things like the scalability of the model (is the model too specific for the dataset or can it be adapted to others?), its stability (what would happen if a lot of fake ratings appeared?) or its coverage (is the whole catalog included in the recommendations or only the most popular ones?)
- Usability: is the presentation of the recommendations adequate? 
- Satisfaction: is the user satisfied with the recommender? This not only includes what is discussed in quality, but also the transparency and trust of the model (does the user trust the recommendations and has an idea of the method used to generate suggestions?)

What type of metrics are used to measure these criteria? The ones that are related to the user experience have to be tested by people, obviously. Regarding those that are objective, I will give a few examples. We can use precision or recall to test the predicting capabilities of the model: for example, consider taking the first K recommendations made to a user. We can measure how many of those are relevant (precision) and how many relevant recommendations are inside of these first K (recall). Another metric that I found interesting to comment on is Hit Rate: it is a metric that considers how many users get a relevant recommendation in their first K suggestions. This allows us to check if the model is struggling with predicting the rankings for certain users. Finally, to measure novelty, which at first glance may seem like a subjective matter, it is common to take the probability of encountering a certain item in a dataset. Those with low probability will be new to most users and therefore can be promoted to improve novelty.

There are other metrics used by specific recommenders, such as particular promotion of certain items or types of items, but that is more than what our work wants to cover.

5. Other technical details

Investigating other projects, I have seen some methodologies that we could consider using for our work:

- MongoDB for easily handling the database
- MLFlow for the models. Recommender models have several parameters, so using it will be essential if we want to develop a good product.
- Airflow for dynamic data. While in principle we are working with static data, we may consider making a better recommender that could adapt to changing ratings.
- Streamlit for the web app.

Bibliography

https://medium.com/@saibhargavkarnati/movie-recommendation-system-using-machine-learning-8f6393d71c83

https://medium.com/@evelyn.eve.9512/collaborative-filtering-in-recommender-system-an-overview-38dfa8462b61

https://www.analyticsvidhya.com/blog/2020/11/create-your-own-movie-movie-recommendation-system/

https://grouplens.org/datasets/movielens/

https://www.evidentlyai.com/ranking-metrics/evaluating-recommender-systems
