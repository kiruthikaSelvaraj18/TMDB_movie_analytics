import pandas as pd
df=pd.read_csv("genres.csv")
print (df)

print (df.shape)
print (df.columns)
print (df.dtypes)
print (df.isnull())
print (df.isnull().sum())
print (df.duplicated())
print (df.duplicated().sum())
print (df.describe())
print (df['genre_id'].unique())
print (df['genre_name'].unique())
##print (df["genre_name"].describe()) - show total count, frequency,most freq value,unique value
##print (df['genre_id'].value_counts()) - counts how many times it appears
##print  (df.isnull().sum()/len(df)) - Calculates the percentage or proportion of missing values by dividing the null count by the total number of rows.

##Proper code from Gemini:

import pandas as pd

# 1. Load the dataset
df_genres = pd.read_csv("genres.csv")
print("Initial Shape:", df_genres.shape) #Returns a tuple (rows, columns) indicating the table's size (around (19, 2) for genres)
print(df_genres)

# 2. Basic structural & health checks
print("\n--- Column Info & Types ---")
print(df_genres.dtypes)

print("\n--- Missing Values ---")
print(df_genres.isnull().sum())

print("\n--- Duplicates ---")
print("Duplicate rows:", df_genres.duplicated().sum())
print("Duplicate genre_ids:", df_genres["genre_id"].duplicated().sum())

# 3. Basic text cleaning (remove accidental leading/trailing spaces)
df_genres["genre_name"] = df_genres["genre_name"].str.strip()

# 4. Enforce schema data types
df_genres["genre_id"] = df_genres["genre_id"].astype("int64")

# 5. Save the valid genre IDs for child table cross-checks later
valid_genre_ids = set(df_genres["genre_id"])
print(f"\nSuccessfully verified {len(valid_genre_ids)} valid genre IDs.")

df_genres["genre_id"].duplicated().sum()

# 3. Basic text cleaning (remove accidental leading/trailing spaces)
df["genre_name"] = df["genre_name"].str.strip()