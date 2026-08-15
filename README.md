# Streaming Marketplaces Dashboard & Analysis

This repository contains a data analysis pipeline and a Streamlit dashboard designed to compare content libraries across major streaming platforms: **Netflix**, **Hulu**, and **Disney+**. 

The analysis is based on ReelGood USA streaming catalog data.

---

## Project Structure

The project is organized into two main folders for clean separation of code and data:

```
MBAPM-Workshop/
├── .gitignore               # Excludes large raw files and cache directories
├── README.md                # Documentation and analysis summary (this file)
├── data/
│   ├── cleaned_reelgood.csv # Pre-processed, deduplicated dataset (~1.0 MB - Tracked)
│   └── raw/                 # Original source datasets (Gitignored due to >100MB size limits)
│       ├── Amazon Prime (excluding Amazon Other) catalogue USA 2016-2020.xlsx
│       ├── Hulu catalogue USA 2016-2020.xlsx
│       ├── Netflix catalogue USA 2016-2020.xlsx
│       └── Reel Good Data (Title+Service+Genre+Tag List).csv
└── code/
    ├── clean_data.py        # Python pre-processing and data-cleaning script
    ├── app.py               # Streamlit interactive dashboard code
    └── requirements.txt     # Python environment dependencies
```

> [!NOTE]
> **Data Size Constraint**: The raw Reel Good CSV dataset is 112.8 MB, which exceeds GitHub's 100 MB single-file tracking limit. Therefore, all raw files are located under `data/raw/` and ignored by Git. The cleaning script filters and compiles a streamlined dataset to `data/cleaned_reelgood.csv` (1.0 MB) which is committed and tracked.

---

## Set Up and Execution Instructions

### 1. Prerequisites
Ensure you have Python 3.9+ installed. It is recommended to use a virtual environment or your Anaconda environment.

### 2. Install Dependencies
Navigate to the project root and install the required libraries:
```bash
pip install -r code/requirements.txt
```

### 3. Run the Data Pre-processing Script
If you need to regenerate `data/cleaned_reelgood.csv` from the raw data, run the cleaning script:
```bash
python code/clean_data.py
```
This script will load the raw CSV, extract Netflix, Hulu, and Disney+ records, drop duplicates across multiple genres/tags, and export a clean catalog dataset.

### 4. Launch the Streamlit Dashboard
Run the Streamlit application to start the interactive web dashboard:
```bash
streamlit run code/app.py
```
The app will open automatically in your default browser at `http://localhost:8501`.

---

## Dashboard Features

- **Summary Cards**: Quick metrics showing total unique titles, average IMDb ratings, and the breakdown share of movies vs. TV shows.
- **Movies vs. TV Shows Comparison Chart**: A clustered bar chart comparing the distribution of titles (Movies vs. TV Shows) across Netflix, Hulu, and Disney+.
- **IMDb Rating Boxplot**: An interactive boxplot highlighting rating spreads, medians, and outliers for each service.
- **Release Trends Line Chart**: Tracks catalog releases by platform over the years, showing historical depth.
- **Catalog Explorer**: An interactive table that allows users to search titles and sort by IMDb ratings, release years, or platforms.
- **Interactive Sidebar Filters**: Allows users to filter all metrics and graphs by:
  - Streaming Platforms
  - Content Format (Movies/TV Shows)
  - IMDb Rating Range
  - Release Year Range
  - Specific Genres

---

## Key Observations from the Catalog Data

The cleaned and deduplicated dataset reveals distinct catalog strategies across the three platforms:

| Platform | Unique Movies | Unique TV Shows | Total Unique Titles |
| :--- | :---: | :---: | :---: |
| **Netflix** | 3,212 | 1,721 | 4,933 |
| **Hulu** | 773 | 1,451 | 2,224 |
| **Disney+** | 663 | 216 | 879 |

### 1. Catalog Scale & Composition
- **Netflix** dominates in scale with nearly 5,000 unique titles, heavily weighted towards movies (~65% movies).
- **Hulu** displays a strong television-centric focus, offering almost twice as many TV shows (1,451) as movies (773).
- **Disney+** has a smaller, highly targeted catalog (~880 titles), leveraging a high ratio of movies (~75%) primarily driven by classic library titles and IP catalogs (Marvel, Star Wars, Pixar).
