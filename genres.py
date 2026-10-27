import pandas as pd
df=pd.read_csv("genres.csv")
print (df)

print (df.shape)
print (df.isnull())
print (df.isnull().sum())
print (df.dtypes)
print (df.duplicated())
print (df.duplicated().sum())
df["genre_name"]=df["genre_name"].str.strip()
print (df)
df["genre_id"]=df["genre_id"].astype("int64")
print (df)
print (df.dtypes)
valid_genre_ids=set(df["genre_id"])
print(f"\nSuccessfully verified {len(valid_genre_ids)} valid genre IDs.")

df.to_csv("cleaned_genres.csv", index=False)
                    