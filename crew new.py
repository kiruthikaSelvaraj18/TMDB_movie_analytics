import pandas as pd

df_movies = pd.read_csv("movies.csv")
df_movies = df_movies.drop_duplicates(subset=["movie_id"], keep="first")
valid_movie_ids = set(df_movies["movie_id"])
df=pd.read_csv("crew.csv")
print (df)

print (df.isnull().sum())

text_columns=["person_name","job","department"]
for col in text_columns:
    df[col]=df[col].astype(str).str.strip()
print (df)

print (df.columns)

df["movie_id"]=df["movie_id"].astype("int64")
print (df["movie_id"])
df["crew_row_id"]=df["crew_row_id"].astype("int64")
print (df["crew_row_id"])
df["person_id"]=df["person_id"].astype("int64")
print (df["person_id"])


print (df.duplicated().sum())
print (df[df.duplicated(keep=False)])
df=df.drop_duplicates().reset_index(drop=True)
print (df)

df = df[df["movie_id"].isin(valid_movie_ids)].reset_index(drop=True)
print(df)
print(df.shape)

df.to_csv("cleaned_crew.csv", index=False)





