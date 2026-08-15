import os
import pandas as pd

def clean_data():
    raw_path = 'data/raw/Reel Good Data (Title+Service+Genre+Tag List).csv'
    processed_dir = 'data'
    processed_path = os.path.join(processed_dir, 'cleaned_reelgood.csv')
    
    print(f"Reading raw data from {raw_path}...")
    # Load dataset with only necessary columns to optimize size and loading speed
    cols_to_use = [
        'Title', 'Type', 'Service', 'Genre', 'IMDB', 
        'ReelGood', 'Released Year', 'Seasons'
    ]
    df = pd.read_csv(raw_path, usecols=cols_to_use, low_memory=False)
    
    # Filter for the requested major streaming platforms
    service_map = {
        'netflix': 'Netflix',
        'hulu_plus': 'Hulu',
        'disney_plus': 'Disney+'
    }
    
    print("Filtering and mapping services...")
    filtered_df = df[df['Service'].isin(service_map.keys())].copy()
    filtered_df['Service'] = filtered_df['Service'].map(service_map)
    
    # Standardize data types
    filtered_df['IMDB'] = pd.to_numeric(filtered_df['IMDB'], errors='coerce')
    filtered_df['ReelGood'] = pd.to_numeric(filtered_df['ReelGood'], errors='coerce')
    filtered_df['Released Year'] = pd.to_numeric(filtered_df['Released Year'], errors='coerce')
    filtered_df['Seasons'] = pd.to_numeric(filtered_df['Seasons'], errors='coerce')
    
    # Save the cleaned and filtered dataset
    os.makedirs(processed_dir, exist_ok=True)
    filtered_df.to_csv(processed_path, index=False)
    print(f"Cleaned dataset successfully saved to {processed_path}")
    print(f"Row count: {filtered_df.shape[0]}")
    
    # Print sample counts for verification
    df_titles = filtered_df.drop_duplicates(subset=['Title', 'Type', 'Service'])
    counts = df_titles.groupby(['Service', 'Type']).size()
    print("\nCatalog counts (deduplicated by Title):")
    print(counts)

if __name__ == '__main__':
    clean_data()
