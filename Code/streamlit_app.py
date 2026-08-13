import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="Streaming Marketplace Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme customization
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #1c2130;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2d3748;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #ffffff;
    }
    .metric-label {
        font-size: 14px;
        color: #a0aec0;
    }
    </style>
""", unsafe_allow_html=True)

# Load data helper
@st.cache_data
def load_data():
    path = "Data/refined data/cleaned_reelgood.csv"
    if not os.path.exists(path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "..", "Data", "refined data", "cleaned_reelgood.csv")
    return pd.read_csv(path)

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please run Code/clean_and_visualize.py first to generate the cleaned dataset.")
    st.stop()

# Deduplicate for Title-level analytics (Ratings, Release Year)
df_unique = df.drop_duplicates(subset=['Title', 'Type', 'Service'])

# TITLE & HEADER
st.title("🎬 Streaming Marketplace Catalog Dashboard")
st.markdown("Analyze catalogue distributions and IMDb ratings for **Netflix, Hulu, and HBO Max**.")

# SIDEBAR FILTERS
st.sidebar.header("📊 Filter Content")

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

# 5. Genre Filter (from long format)
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

# Apply Genre Filter (we check matching Titles in the main long-format DataFrame)
if selected_genres:
    matching_titles = df[
        (df["Service"].isin(services)) &
        (df["Genre"].isin(selected_genres))
    ]["Title"].unique()
    filtered_unique = filtered_unique[filtered_unique["Title"].isin(matching_titles)]

# Colors mapping matching branding
color_discrete_map = {
    'Netflix': '#E50914',
    'Hulu': '#3DBB3E',
    'HBO Max': '#9933FF'
}

# METRICS ROW
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_titles = len(filtered_unique)
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{total_titles:,}</div><div class="metric-label">Total Titles</div></div>',
        unsafe_allow_html=True
    )
with col2:
    avg_rating = filtered_unique["IMDB"].mean()
    avg_str = f"{avg_rating:.2f}" if not pd.isna(avg_rating) else "N/A"
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{avg_str}</div><div class="metric-label">Average IMDb Rating</div></div>',
        unsafe_allow_html=True
    )
with col3:
    movies_pct = (filtered_unique["Type"] == "movies").mean() * 100
    movies_pct_str = f"{movies_pct:.1f}%" if len(filtered_unique) > 0 else "N/A"
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{movies_pct_str}</div><div class="metric-label">% Movies</div></div>',
        unsafe_allow_html=True
    )
with col4:
    exclusive_pct = (filtered_unique["Exclusive Service"] == 1).mean() * 100
    excl_str = f"{exclusive_pct:.1f}%" if len(filtered_unique) > 0 else "N/A"
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{excl_str}</div><div class="metric-label">Exclusivity Rate</div></div>',
        unsafe_allow_html=True
    )

# CHARTS ROW 1: IMDb Ratings & Release Years
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("⭐ IMDb Rating Distribution")
    if not filtered_unique.empty:
        fig_imdb = px.histogram(
            filtered_unique,
            x="IMDB",
            color="Service",
            barmode="stack",
            nbins=20,
            color_discrete_map=color_discrete_map,
            labels={"IMDB": "IMDb Rating", "count": "Count"},
            template="plotly_dark"
        )
        fig_imdb.update_layout(margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_imdb, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with chart_col2:
    st.subheader("📅 Release Year Trend")
    if not filtered_unique.empty:
        # Group to find count of releases per year and service
        releases = filtered_unique.groupby(["Released Year", "Service"]).size().reset_index(name="Count")
        fig_year = px.line(
            releases,
            x="Released Year",
            y="Count",
            color="Service",
            color_discrete_map=color_discrete_map,
            labels={"Released Year": "Year", "Count": "Titles Added"},
            template="plotly_dark"
        )
        fig_year.update_layout(margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_year, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

# CHARTS ROW 2: Genres & Data Table
chart_col3, table_col = st.columns([1, 1.2])

with chart_col3:
    st.subheader("🏷️ Genre Distribution")
    # We pull genre listings from the full DataFrame based on matching unique title indices
    filtered_long = df[
        (df["Title"].isin(filtered_unique["Title"])) &
        (df["Service"].isin(services))
    ]
    if not filtered_long.empty:
        genre_dist = filtered_long.groupby(["Genre", "Service"]).size().reset_index(name="Count")
        genre_totals = filtered_long["Genre"].value_counts().index[:15]  # Top 15 genres
        genre_dist_top = genre_dist[genre_dist["Genre"].isin(genre_totals)]
        
        fig_genre = px.bar(
            genre_dist_top,
            y="Genre",
            x="Count",
            color="Service",
            barmode="stack",
            orientation="h",
            color_discrete_map=color_discrete_map,
            category_orders={"Genre": list(genre_totals)},
            template="plotly_dark"
        )
        fig_genre.update_layout(margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
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
