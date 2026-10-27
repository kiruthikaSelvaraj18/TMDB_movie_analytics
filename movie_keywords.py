import pandas as pd

df_movies = pd.read_csv("movies.csv")
df_movies = df_movies.drop_duplicates(subset=["movie_id"], keep="first")
valid_movie_ids = set(df_movies["movie_id"])
df=pd.read_csv("movie_keywords.csv")
print (df)

print (df.isnull().sum())
print (df.shape)
print (df.columns)

df["keyword_name"]=df["keyword_name"].astype(str).str.strip()
print (df)

df["movie_id"]=df["movie_id"].astype("int64")
print (df["movie_id"])
df["keyword_id"]=df["keyword_id"].astype("int64")
print (df["keyword_id"])

print (df.duplicated().sum())
print (df[df.duplicated(keep=False)])
df=df.drop_duplicates().reset_index(drop=True)
print (df)

df = df[df["movie_id"].isin(valid_movie_ids)].reset_index(drop=True)
print(df)
print(df.shape)

df.to_csv("cleaned_movie_keywords.csv", index=False)

