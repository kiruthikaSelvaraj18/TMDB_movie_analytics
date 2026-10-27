import pandas as pd

df_movies = pd.read_csv("movies.csv")
df_movies = df_movies.drop_duplicates(subset=["movie_id"], keep="first")
valid_movie_ids = set(df_movies["movie_id"])


df=pd.read_csv("cast.csv")
print (df)

df["character_name"]=df["character_name"].fillna("Unknown")
print (df)

text_columns = ["actor_name","character_name"]
for col in text_columns:
    df[col] = df[col].astype(str).str.strip()
    print (df)

print (df.isnull().sum())

df["movie_id"]=df["movie_id"].astype("int64")
print (df["movie_id"])
df["cast_row_id"]=df["cast_row_id"].astype("int64")
print (df["cast_row_id"])
df["person_id"]=df["person_id"].astype("int64")
print (df["person_id"])
df["cast_order"]=df["cast_order"].astype("int64")
print (df["cast_order"])

print (df.duplicated().sum())
print(df[df.duplicated(keep=False)])
df = df.drop_duplicates().reset_index(drop=True)
print (df)
print (df.shape)

df = df[df["movie_id"].isin(valid_movie_ids)].reset_index(drop=True)
print(df)
print(df.shape)

df.to_csv("cleaned_cast.csv", index=False)












