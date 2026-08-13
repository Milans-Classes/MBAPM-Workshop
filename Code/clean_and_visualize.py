import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for clean, premium aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# Create target directories
os.makedirs('Data/refined data', exist_ok=True)
os.makedirs('Code/images', exist_ok=True)

# Load raw dataset
print("Loading raw data...")
raw_path = 'Data/raw data/Reel Good Data (Title+Service+Genre+Tag List).csv'
df = pd.read_csv(raw_path)

# Filter for major streaming platforms and standardize names
service_map = {
    'netflix': 'Netflix',
    'hulu_plus': 'Hulu',
    'hbo_max': 'HBO Max',
    'hbo': 'HBO Max'
}
filtered_df = df[df['Service'].isin(service_map.keys())].copy()
filtered_df['Service'] = filtered_df['Service'].map(service_map)

# Clean IMDB ratings
filtered_df = filtered_df.dropna(subset=['IMDB'])
filtered_df['IMDB'] = pd.to_numeric(filtered_df['IMDB'])

# Save refined/cleaned dataset
cleaned_path = 'Data/refined data/cleaned_reelgood.csv'
filtered_df.to_csv(cleaned_path, index=False)
print(f"Cleaned dataset saved to {cleaned_path} ({filtered_df.shape[0]} rows)")

# Deduplicate by Title and Service for Title-level metrics (ratings, release year)
# This prevents titles with multiple genres/tags from inflating distributions
df_titles = filtered_df.drop_duplicates(subset=['Title', 'Type', 'Service'])

# 1. Distribution of IMDB Ratings
plt.figure(figsize=(10, 6))
sns.histplot(
    data=df_titles, 
    x='IMDB', 
    hue='Service', 
    kde=True, 
    bins=20, 
    multiple='stack', 
    palette={'Netflix': '#E50914', 'Hulu': '#3DBB3E', 'HBO Max': '#9933FF'}
)
plt.title('Distribution of IMDb Ratings by Streaming Service', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('IMDb Rating', fontsize=12)
plt.ylabel('Count of Unique Titles', fontsize=12)
plt.tight_layout()
plt.savefig('Code/images/imdb_distribution.png', dpi=300)
plt.close()

# 2. Distribution of Release Year (Focusing on 1980 onwards for clarity)
plt.figure(figsize=(10, 6))
df_years = df_titles[df_titles['Released Year'] >= 1980]
sns.histplot(
    data=df_years, 
    x='Released Year', 
    hue='Service', 
    bins=40, 
    multiple='stack', 
    palette={'Netflix': '#E50914', 'Hulu': '#3DBB3E', 'HBO Max': '#9933FF'},
    discrete=True
)
plt.title('Distribution of Titles by Release Year (1980-2020)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Release Year', fontsize=12)
plt.ylabel('Count of Unique Titles', fontsize=12)
plt.tight_layout()
plt.savefig('Code/images/release_year_distribution.png', dpi=300)
plt.close()

# 3. Distribution of Genres (Count of titles in each genre across services)
genre_counts = filtered_df.groupby(['Genre', 'Service']).size().reset_index(name='Count')
top_genres = filtered_df['Genre'].value_counts().index

plt.figure(figsize=(12, 8))
sns.barplot(
    data=genre_counts, 
    y='Genre', 
    x='Count', 
    hue='Service', 
    order=top_genres, 
    palette={'Netflix': '#E50914', 'Hulu': '#3DBB3E', 'HBO Max': '#9933FF'}
)
plt.title('Distribution of Genres across Streaming Services', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Number of Genre Occurrences', fontsize=12)
plt.ylabel('Genre', fontsize=12)
plt.tight_layout()
plt.savefig('Code/images/genre_distribution.png', dpi=300)
plt.close()

print("Visualizations successfully generated and saved to Code/images/")
