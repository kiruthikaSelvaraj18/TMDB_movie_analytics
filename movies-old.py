import pandas as pd
df=pd.read_csv("movies.csv")
print (df)

print (df.shape)
print (df.columns)
print (df.dtypes)
df["release_date"]=pd.to_datetime(df["release_date"],format="%Y-%m-%d")
print (df["release_date"])
print (df["release_date"].info)
print (df["release_date"].dtypes)
print (df.dtypes)
print (df.isnull())
print (df.isnull().sum())
print (df.duplicated())
print (df.duplicated().sum())
# View exact full-row duplicates
print("Exact duplicates:")
print(df[df.duplicated(keep=False)])
# Drop duplicates based on the primary key (movie_id), keeping the first occurrence
df = df.drop_duplicates(subset=["movie_id","title","overview"], keep="first").reset_index(drop=True)
# Verify the new shape and confirm no duplicates remain
print("New shape:", df.shape)
print("Remaining duplicates:", df["movie_id"].duplicated().sum())
# List of valid movie IDs
valid_movie_ids = set(df["movie_id"])
print (df.describe())
print (df.columns)
print("New shape:", df.shape)
print("Remaining duplicates:", df["movie_id"].duplicated().sum())

# 1. Fill missing text columns with clean placeholders (if any exist)
print (df["movie_id"].fillna(""))

# 3. Enforce schema data types
print (df["movie_id"]==df["movie_id"].astype("int64"))
print (df["budget"]==df["budget"].astype("int64"))
print (df["revenue"]==df["revenue"].astype("int64"))
print (df["vote_count"]==df["vote_count"].astype("int64"))
print (df["popularity"]==df["popularity"].astype("float64"))
print (df["vote_average"]==df["vote_average"].astype("float64"))

print (df.info)
print (df.shape)
print (df.columns)
print (df.dtypes)


print(df.isnull().sum())

# Step 1: Perform the assignment on its own line (NO print around this)
df["release_date"] = pd.to_datetime(df["release_date"]).dt.strftime("%Y-%m-%d")
print(df["release_date"].unique())

df["release_date"] = pd.to_datetime(df["release_date"])
print (df["release_date"])


# Convert to true date objects
df["release_date"] = pd.to_datetime(df["release_date"]).dt.date
print(df["release_date"])

print (df.dtypes)

df["release_date"] = pd.to_datetime(df["release_date"])
print(df.dtypes)

print (df["release_date"].info)

# Load cleaned parent references
df_movies = pd.read_csv("movies.csv")
df_genres = pd.read_csv("genres.csv")

# Create lookup sets for O(1) fast filtering
valid_movie_ids = set(df_movies["movie_id"])
valid_genre_ids = set(df_genres["genre_id"])
print ()

# 1. Load table
df_mg = pd.read_csv("movie_genres.csv")

# 2. Check & drop exact duplicate pairings
print("Original movie_genres shape:", df_mg.shape)
df_mg = df_mg.drop_duplicates().reset_index(drop=True)

print (df["movie_id"].info)

print (df)

pd.set_option("display.max_columns", None)
print (df.info)

print (df["title"])

from spellchecker import SpellChecker
import re

spell = SpellChecker()

def find_unknown_words(text):
    # Extract clean alphabetical words
    words = re.findall(r"\b[A-Za-z]+\b", str(text))
    # Find words not in standard English dictionary
    misspelled = spell.unknown(words)
    return list(misspelled)

# Sample check on a subset or flag words
df["flagged_words"] = df["title"].apply(find_unknown_words)
sample_flagged = df[df["flagged_words"].map(len) > 0][["title", "flagged_words"]]
print(sample_flagged.head(10))

df['title']=df['title'].replace({"deadpool":"Deadpool","shawshank":"Shawshank","gump":"Gump","django":"Django","ultron":"Ultron","inglurious":"Inglourious","basterds":"Basterds","azkaban":"Azkaban","vol":"Vol","ragnarok":"Ragnarok","nemo":"Nemo"})
# 1. Save a copy of the original titles before making changes
df["original_title"] = df["title"]

# 1. Save original titles first
df["original_title"] = df["title"]

# 2. Apply substring replacement with regex=True
df["title"] = df["title"].replace(
    {"deadpool": "Deadpool", "shawshank": "Shawshank", "gump": "Gump"},
    regex=True
)

# 3. Check for any changed titles
changed = df[df["original_title"] != df["title"]]
print(f"Titles changed: {len(changed)}")
if len(changed) > 0:
    print(changed[["original_title", "title"]])

# 4. Remove the helper column
df = df.drop(columns=["original_title"])

# 1. Save copy of titles before change
df["original_title"] = df["title"]

# 2. Test change
df["title"] = df["title"].replace({"nemo": "NEMO"}, regex=True)

# 3. Check changed titles
changed = df[df["original_title"] != df["title"]]
print(f"Titles changed: {len(changed)}")
if len(changed) > 0:
    print(changed[["original_title", "title"]].head())

# 4. Clean up / revert back if desired
df["title"] = df["original_title"]
df = df.drop(columns=["original_title"])

# 1. Save original copy
df["original_title"] = df["title"]

# 2. Match exact case "Nemo" -> "NEMO"
df["title"] = df["title"].replace({"Nemo": "NEMO"}, regex=True)

# 3. Check and display changed titles
changed = df[df["original_title"] != df["title"]]
print(f"Titles changed: {len(changed)}")
if len(changed) > 0:
    print(changed[["original_title", "title"]])

# 4. Drop the comparison column (do NOT reassign df['title'] = df['original_title'])
df = df.drop(columns=["original_title"])

# Revert "NEMO" back to "Nemo"
df["title"] = df["title"].replace({"NEMO": "Nemo"}, regex=True)

# Verify the reversal
print(df[df["title"].str.contains("Nemo", na=False)][["title"]])

