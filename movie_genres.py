import pandas as pd

df_movies = pd.read_csv("movies.csv")
df_movies = df_movies.drop_duplicates(subset=["movie_id"], keep="first")
valid_movie_ids = set(df_movies["movie_id"])

df_genres = pd.read_csv("genres.csv")
valid_genre_ids = set(df_genres["genre_id"])

df=pd.read_csv("movie_genres.csv")
print (df)

print (df.info)
print (df.dtypes)
print (df.isnull().sum())

df["movie_id"]=df["movie_id"].astype("int64")
print (df["movie_id"])
df["genre_id"]=df["genre_id"].astype("int64")
print (df["genre_id"])

print (df.duplicated().sum())
print (df[df.duplicated(keep=False)])
df = df.drop_duplicates().reset_index(drop=True)
print (df)
print (df.shape)

df = df[df["movie_id"].isin(valid_movie_ids) & df["genre_id"].isin(valid_genre_ids)].reset_index(drop=True)
print (df)
print("Final cleaned shape:", df.shape)
print(df.head())

df.to_csv("cleaned_movie_genres.csv", index=False)