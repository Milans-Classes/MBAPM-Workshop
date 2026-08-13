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
import plotly.express as px
import numpy as np

# Set page config
st.set_page_config(
    page_title="Streaming Marketplace Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a beautiful Tokyo Night Bright / Light Theme
st.markdown("""
    <style>
    /* Main body styling */
    .stApp {
        background-color: #f4f5f8;
        color: #1a1b26;
    }
    
    /* Premium white card styling with subtle shadow and border */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e1e4ed;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #1a1b26;
    }
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #565f89;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    
    /* Streamlit widgets modifications */
    div[data-testid="stSidebar"] {
        background-color: #1e1f29;
    }
    div[data-testid="stSidebar"] * {
        color: #a9b1d6 !important;
    }
    
    /* Header decoration */
    .header-container {
        padding: 10px 0px 20px 0px;
        border-bottom: 2px solid #e1e4ed;
        margin-bottom: 25px;
    }
    .header-sub {
        color: #ff007f;
        font-weight: 700;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .header-main {
        font-size: 36px;
        font-weight: 800;
        color: #1a1b26;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Load data helper
@st.cache_data
def load_data():
    # Attempt 1: Local relative path from root
    path1 = "Data/refined data/cleaned_reelgood.csv"
    if os.path.exists(path1):
        return pd.read_csv(path1)
        
    # Attempt 2: Local relative path from Code/ folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path2 = os.path.join(script_dir, "..", "Data", "refined data", "cleaned_reelgood.csv")
    if os.path.exists(path2):
        return pd.read_csv(path2)
        
    # Attempt 3: Root of virtual filesystem (for Stlite WebAssembly deployment)
    path3 = "cleaned_reelgood.csv"
    if os.path.exists(path3):
        return pd.read_csv(path3)
        
    # Attempt 4: Virtual filesystem inside script dir (Stlite default)
    path4 = os.path.join(script_dir, "cleaned_reelgood.csv")
    if os.path.exists(path4):
        return pd.read_csv(path4)
        
    # Fallback to the first path if none exist to trigger standard file not found error
    return pd.read_csv(path1)

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please run Code/clean_and_visualize.py first to generate the cleaned dataset.")
    st.stop()

# Deduplicate for Title-level analytics (Ratings, Release Year)
df_unique = df.drop_duplicates(subset=['Title', 'Type', 'Service'])

# HEADER (Indicate: Competitive Analysis of Streaming Marketplace)
st.markdown("""
    <div class="header-container">
        <div class="header-sub">Competitive Analysis of Streaming Marketplace</div>
        <h1 class="header-main">🎬 Streaming Catalog Analytics</h1>
    </div>
""", unsafe_allow_html=True)

# SIDEBAR FILTERS
st.sidebar.header("📊 Filter Controls")

# 1. Platform Filter
services = st.sidebar.multiselect(
    "Streaming Platforms",
    options=["Netflix", "Hulu", "HBO Max"],
    default=["Netflix", "Hulu", "HBO Max"]
)

# 2. Type Filter (Movies vs TV)
content_types = st.sidebar.multiselect(
    "Content Type",
    options=["movies", "tv"],
    default=["movies", "tv"],
    format_func=lambda x: "Movies" if x == "movies" else "TV Shows"
)

# 3. Release Year Slider
min_year = int(df_unique["Released Year"].min())
max_year = int(df_unique["Released Year"].max())
year_range = st.sidebar.slider(
    "Release Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(2000, max_year)
)

# 4. IMDb Rating Slider
rating_range = st.sidebar.slider(
    "IMDb Rating Range",
    min_value=0.0,
    max_value=10.0,
    value=(0.0, 10.0),
    step=0.1
)

# 5. Genre Filter
all_genres = sorted(df["Genre"].dropna().unique().tolist())
selected_genres = st.sidebar.multiselect(
    "Genres",
    options=all_genres,
    default=None,
    placeholder="All Genres"
)

# Apply filters
filtered_unique = df_unique[
    (df_unique["Service"].isin(services)) &
    (df_unique["Type"].isin(content_types)) &
    (df_unique["Released Year"].between(year_range[0], year_range[1])) &
    (df_unique["IMDB"].between(rating_range[0], rating_range[1]))
]

# Apply Genre Filter
if selected_genres:
    matching_titles = df[
        (df["Service"].isin(services)) &
        (df["Genre"].isin(selected_genres))
    ]["Title"].unique()
    filtered_unique = filtered_unique[filtered_unique["Title"].isin(matching_titles)]

# Colors mapping matching Tokyo Night Bright / Light palette
color_discrete_map = {
    'Netflix': '#ff007f',   # Tokyo Night Hot Pink
    'Hulu': '#00b4d8',      # Tokyo Night Cyan
    'HBO Max': '#7a5cff'    # Tokyo Night Purple
}

# METRICS ROW
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_titles = len(filtered_unique)
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{total_titles:,}</div><div class="metric-label">Filtered Titles</div></div>',
        unsafe_allow_html=True
    )
with col2:
    avg_rating = filtered_unique["IMDB"].mean()
    avg_str = f"{avg_rating:.2f}" if not pd.isna(avg_rating) else "N/A"
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{avg_str}</div><div class="metric-label">Avg IMDb Rating</div></div>',
        unsafe_allow_html=True
    )
with col3:
    movies_pct = (filtered_unique["Type"] == "movies").mean() * 100
    movies_pct_str = f"{movies_pct:.1f}%" if len(filtered_unique) > 0 else "N/A"
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{movies_pct_str}</div><div class="metric-label">% Movies Share</div></div>',
        unsafe_allow_html=True
    )
with col4:
    exclusive_pct = (filtered_unique["Exclusive Service"] == 1).mean() * 100
    excl_str = f"{exclusive_pct:.1f}%" if len(filtered_unique) > 0 else "N/A"
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{excl_str}</div><div class="metric-label">Exclusivity Rate</div></div>',
        unsafe_allow_html=True
    )

# CHARTS ROW 1: IMDb Ratings & Release Years (Relative Share)
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("⭐ IMDb Rating Share (Relative Distribution)")
    if not filtered_unique.empty:
        # Calculate IMDb distribution relative to each service catalog size
        imdb_dist = []
        for service in filtered_unique["Service"].unique():
            service_df = filtered_unique[filtered_unique["Service"] == service]
            total_service_titles = len(service_df)
            if total_service_titles > 0:
                counts, bins = np.histogram(service_df["IMDB"], bins=15, range=(0, 10))
                for i in range(len(counts)):
                    bin_label = f"{bins[i]:.1f}-{bins[i+1]:.1f}"
                    imdb_dist.append({
                        "Service": service,
                        "IMDb Bin": bin_label,
                        "bin_start": bins[i],
                        "Share of Catalog (%)": (counts[i] / total_service_titles) * 100
                    })
        df_imdb_dist = pd.DataFrame(imdb_dist).sort_values(by="bin_start")
        
        fig_imdb = px.bar(
            df_imdb_dist,
            x="IMDb Bin",
            y="Share of Catalog (%)",
            color="Service",
            barmode="group",
            color_discrete_map=color_discrete_map,
            template="plotly_white"
        )
        fig_imdb.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_imdb, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with chart_col2:
    st.subheader("📅 Release Year Share (Relative Distribution)")
    if not filtered_unique.empty:
        # Calculate Release Year distribution relative to each service catalog size
        year_dist = []
        for service in filtered_unique["Service"].unique():
            service_df = filtered_unique[filtered_unique["Service"] == service]
            total_service_titles = len(service_df)
            if total_service_titles > 0:
                counts = service_df["Released Year"].value_counts()
                for year, count in counts.items():
                    year_dist.append({
                        "Service": service,
                        "Released Year": year,
                        "Share of Catalog (%)": (count / total_service_titles) * 100
                    })
        df_year_dist = pd.DataFrame(year_dist).sort_values(by="Released Year")
        
        fig_year = px.line(
            df_year_dist,
            x="Released Year",
            y="Share of Catalog (%)",
            color="Service",
            color_discrete_map=color_discrete_map,
            template="plotly_white"
        )
        fig_year.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_year, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

# CHARTS ROW 2: Genres & Data Table
chart_col3, table_col = st.columns([1, 1.2])

with chart_col3:
    st.subheader("🏷️ Genre Share (Relative Distribution)")
    filtered_long = df[
        (df["Title"].isin(filtered_unique["Title"])) &
        (df["Service"].isin(services))
    ]
    if not filtered_long.empty:
        # Calculate Genre distribution relative to total service titles
        genre_dist = []
        for service in services:
            service_long = filtered_long[filtered_long["Service"] == service]
            total_service_titles = filtered_unique[filtered_unique["Service"] == service]["Title"].nunique()
            if total_service_titles > 0:
                counts = service_long["Genre"].value_counts()
                for genre, count in counts.items():
                    genre_dist.append({
                        "Service": service,
                        "Genre": genre,
                        "Share of Catalog (%)": (count / total_service_titles) * 100
                    })
        df_genre_dist = pd.DataFrame(genre_dist)
        
        # Sort genres by highest average share across selected services
        avg_genre_shares = df_genre_dist.groupby("Genre")["Share of Catalog (%)"].mean().sort_values(ascending=False).index[:15]
        df_genre_dist_top = df_genre_dist[df_genre_dist["Genre"].isin(avg_genre_shares)]
        
        fig_genre = px.bar(
            df_genre_dist_top,
            y="Genre",
            x="Share of Catalog (%)",
            color="Service",
            barmode="group",
            orientation="h",
            color_discrete_map=color_discrete_map,
            category_orders={"Genre": list(avg_genre_shares)},
            template="plotly_white"
        )
        fig_genre.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_genre, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with table_col:
    st.subheader("🔍 Catalog Explorer")
    search_query = st.text_input("Search titles:", "")
    
    display_df = filtered_unique[["Title", "Service", "Type", "IMDB", "Released Year", "Seasons"]].copy()
    display_df["Type"] = display_df["Type"].map({"movies": "Movie", "tv": "TV Show"})
    
    if search_query:
        display_df = display_df[display_df["Title"].str.contains(search_query, case=False, na=False)]
        
    st.dataframe(
        display_df.sort_values(by="IMDB", ascending=False),
        column_config={
            "Title": "Title",
            "Service": "Platform",
            "Type": "Format",
            "IMDB": st.column_config.NumberColumn("IMDb Rating", format="%.1f"),
            "Released Year": "Release Year",
            "Seasons": st.column_config.NumberColumn("Seasons", format="%d")
        },
        use_container_width=True,
        hide_index=True
    )
