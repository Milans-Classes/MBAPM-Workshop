# Workaround for Stlite WebAssembly environment: mock missing pyarrow classes
# that narwhals/plotly tries to access if a partial pyarrow is present.
try:
    import pyarrow as pa
    if not hasattr(pa, 'ChunkedArray'):
        class MockChunkedArray: pass
        pa.ChunkedArray = MockChunkedArray
    if not hasattr(pa, 'Table'):
        class MockTable: pass
        pa.Table = MockTable
except ImportError:
    pass

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------------------------------
# 1. PAGE CONFIG & STYLING
# ----------------------------------------------------
st.set_page_config(
    page_title="Streaming Platforms Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling (Clean layout with subtle shadows and card components)
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        margin-top: 4px;
    }
    /* Title and Subtitle */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 25px;
    }
    /* Divider */
    hr {
        margin-top: 15px;
        margin-bottom: 25px;
        border-color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. DATA LOADING & CACHING
# ----------------------------------------------------
@st.cache_data
def load_data():
    # Use relative path from root, code folder, or stlite virtual FS
    if os.path.exists("cleaned_reelgood.csv"):
        path = "cleaned_reelgood.csv"
    elif os.path.exists("data/cleaned_reelgood.csv"):
        path = "data/cleaned_reelgood.csv"
    else:
        # Fallback for running within 'code/' directory
        path = "../data/cleaned_reelgood.csv"
        
    df = pd.read_csv(path)
    # Ensure proper data types
    df['IMDB'] = df['IMDB'].astype(float)
    df['Released Year'] = df['Released Year'].astype(float)
    df['Seasons'] = df['Seasons'].astype(float)
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.info("Please make sure you have run the data cleaning script: python code/clean_data.py")
    st.stop()

# ----------------------------------------------------
# 3. SIDEBAR / FILTERS
# ----------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/netflix--v1.png", width=60) # General icon
st.sidebar.header("Filter Catalog")

# Multi-select for Platform
platforms = sorted(df_raw['Service'].unique())
selected_platforms = st.sidebar.multiselect(
    "Streaming Platforms",
    options=platforms,
    default=platforms
)

# Multi-select for Content Format
format_map = {'movies': 'Movie', 'tv': 'TV Show'}
formats = list(format_map.keys())
selected_formats = st.sidebar.multiselect(
    "Content Formats",
    options=formats,
    default=formats,
    format_func=lambda x: format_map[x]
)

# Slider for IMDb Rating
min_imdb = float(df_raw['IMDB'].min(skipna=True)) if df_raw['IMDB'].notna().any() else 0.0
max_imdb = float(df_raw['IMDB'].max(skipna=True)) if df_raw['IMDB'].notna().any() else 10.0
selected_imdb = st.sidebar.slider(
    "IMDb Rating Range",
    min_value=0.0,
    max_value=10.0,
    value=(min_imdb, max_imdb),
    step=0.1
)

# Slider for Release Year
min_year = int(df_raw['Released Year'].min(skipna=True)) if df_raw['Released Year'].notna().any() else 1900
max_year = int(df_raw['Released Year'].max(skipna=True)) if df_raw['Released Year'].notna().any() else 2026
selected_years = st.sidebar.slider(
    "Release Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# Multi-select for Genre
genres = sorted(df_raw['Genre'].dropna().unique())
selected_genres = st.sidebar.multiselect(
    "Filter by Genres (Optional)",
    options=genres,
    default=[]
)

# ----------------------------------------------------
# 4. DATA FILTERING LOGIC
# ----------------------------------------------------
# Base filters (Platform, Formats, IMDb, Years)
filtered_df = df_raw[
    (df_raw['Service'].isin(selected_platforms)) &
    (df_raw['Type'].isin(selected_formats)) &
    ((df_raw['IMDB'] >= selected_imdb[0]) & (df_raw['IMDB'] <= selected_imdb[1]) | df_raw['IMDB'].isna()) &
    ((df_raw['Released Year'] >= selected_years[0]) & (df_raw['Released Year'] <= selected_years[1]) | df_raw['Released Year'].isna())
]

# Genre filter (if any selected)
if selected_genres:
    # Get all Titles that have at least one of the selected genres
    matching_titles = filtered_df[filtered_df['Genre'].isin(selected_genres)]['Title'].unique()
    filtered_df = filtered_df[filtered_df['Title'].isin(matching_titles)]

# Create a deduplicated catalog (unique titles per platform) for counting and aggregate statistics
df_titles_unique = filtered_df.drop_duplicates(subset=['Title', 'Type', 'Service'])

# Curated HSL-derived color palette for platforms
color_map = {
    'Netflix': '#E50914',   # Netflix Red
    'Hulu': '#1CE783',      # Hulu Green
    'Disney+': '#006E99'    # Disney+ Blue
}

# ----------------------------------------------------
# 5. DASHBOARD LAYOUT & RENDERING
# ----------------------------------------------------
st.markdown('<div class="main-title">Streaming Marketplaces Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">An interactive analysis of catalogs and ratings on Netflix, Hulu, and Disney+ based on ReelGood data.</div>', unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)

# Metric Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_count = len(df_titles_unique)
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{total_count:,}</div><div class="metric-label">Total Unique Titles</div></div>',
        unsafe_allow_html=True
    )
with col2:
    avg_rating = df_titles_unique['IMDB'].mean()
    avg_str = f"{avg_rating:.2f} ★" if not pd.isna(avg_rating) else "N/A"
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{avg_str}</div><div class="metric-label">Average IMDb Rating</div></div>',
        unsafe_allow_html=True
    )
with col3:
    movies_count = len(df_titles_unique[df_titles_unique['Type'] == 'movies'])
    pct_movies = (movies_count / total_count * 100) if total_count > 0 else 0
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{pct_movies:.1f}%</div><div class="metric-label">Movie catalog share</div></div>',
        unsafe_allow_html=True
    )
with col4:
    tv_count = len(df_titles_unique[df_titles_unique['Type'] == 'tv'])
    pct_tv = (tv_count / total_count * 100) if total_count > 0 else 0
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{pct_tv:.1f}%</div><div class="metric-label">TV Show catalog share</div></div>',
        unsafe_allow_html=True
    )

# ----------------------------------------------------
# CHART ROW 1: PRIMARY CATALOG COMPARISON
# ----------------------------------------------------
st.subheader("📊 Catalog Comparison: Movies vs TV Shows")
if not df_titles_unique.empty:
    # Group by Service and Content Type and compute unique count
    agg_df = df_titles_unique.groupby(['Service', 'Type']).size().reset_index(name='Count')
    agg_df['Type'] = agg_df['Type'].map(format_map)
    
    # Plotly clustered bar chart
    fig_primary = px.bar(
        agg_df,
        x="Service",
        y="Count",
        color="Type",
        barmode="group",
        labels={"Service": "Streaming Platform", "Count": "Number of Titles", "Type": "Format"},
        color_discrete_sequence=['#475569', '#38bdf8'], # Neutral slate for movies, light blue for TV shows
        template="plotly_white",
        text_auto=True
    )
    
    fig_primary.update_layout(
        xaxis_title=None,
        yaxis_title="Title Count",
        font=dict(family="sans-serif", size=12),
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_primary, use_container_width=True)
else:
    st.info("No data available. Try resetting or expanding your sidebar filters.")

# ----------------------------------------------------
# CHART ROW 2: DETAILED INSIGHTS (Ratings & Trends)
# ----------------------------------------------------
col_chart_left, col_chart_right = st.columns(2)

with col_chart_left:
    st.subheader("⭐ IMDb Rating Distribution by Platform")
    df_ratings = df_titles_unique.dropna(subset=['IMDB'])
    if not df_ratings.empty:
        fig_ratings = px.box(
            df_ratings,
            x="Service",
            y="IMDB",
            color="Service",
            color_discrete_map=color_map,
            labels={"Service": "Streaming Platform", "IMDB": "IMDb Rating"},
            points="outliers",
            template="plotly_white"
        )
        fig_ratings.update_layout(
            xaxis_title=None,
            yaxis_title="IMDb Rating",
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_ratings, use_container_width=True)
    else:
        st.info("No IMDb rating data available for the selected filters.")

with col_chart_right:
    st.subheader("📈 Catalog Releases Over Time")
    df_years_plot = df_titles_unique.dropna(subset=['Released Year'])
    if not df_years_plot.empty:
        # Group by release year and service
        trend_df = df_years_plot.groupby(['Released Year', 'Service']).size().reset_index(name='Titles Released')
        
        # Filter for releases after 1995 for visual clarity, unless slider explicitly includes older
        if selected_years[0] <= 1995:
            trend_filtered = trend_df
        else:
            trend_filtered = trend_df[trend_df['Released Year'] >= selected_years[0]]
            
        fig_trends = px.line(
            trend_filtered,
            x="Released Year",
            y="Titles Released",
            color="Service",
            color_discrete_map=color_map,
            labels={"Released Year": "Release Year", "Titles Released": "Count"},
            template="plotly_white",
            line_shape="spline"
        )
        fig_trends.update_layout(
            xaxis_title="Release Year",
            yaxis_title="Number of Releases",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.info("No release year data available for the selected filters.")

# ----------------------------------------------------
# TABULAR VIEW: CATALOG EXPLORER
# ----------------------------------------------------
st.subheader("🔍 Catalog Explorer")
search_term = st.text_input("Search catalog by Title:", placeholder="Type a title name here... (e.g. Breaking Bad)")

explorer_df = df_titles_unique.copy()
if search_term:
    explorer_df = explorer_df[explorer_df['Title'].str.contains(search_term, case=False, na=False)]

# Format columns for user presentation
explorer_display = explorer_df[['Title', 'Service', 'Type', 'IMDB', 'Released Year', 'Seasons']].copy()
explorer_display['Type'] = explorer_display['Type'].map(format_map)
explorer_display.rename(columns={
    'Service': 'Platform',
    'Type': 'Format',
    'IMDB': 'IMDb Rating',
    'Released Year': 'Release Year'
}, inplace=True)

# Sort by IMDb rating by default
explorer_display = explorer_display.sort_values(by="IMDb Rating", ascending=False)

st.dataframe(
    explorer_display,
    column_config={
        "Title": st.column_config.TextColumn("Title", width="medium"),
        "Platform": st.column_config.TextColumn("Platform"),
        "Format": st.column_config.TextColumn("Format"),
        "IMDb Rating": st.column_config.NumberColumn("IMDb Rating", format="%.1f ★"),
        "Release Year": st.column_config.NumberColumn("Release Year", format="%d"),
        "Seasons": st.column_config.NumberColumn("Seasons", format="%d")
    },
    use_container_width=True,
    hide_index=True
)

st.caption("Data source: ReelGood USA streaming catalogues (processed). All rights reserved.")
