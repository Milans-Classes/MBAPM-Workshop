# Streaming Marketplaces Data Analysis Report

This report presents findings from the cleaned ReelGood dataset, specifically focusing on the catalog distribution and content quality across three major streaming platforms: **Netflix**, **Hulu**, and **HBO Max**.

---

## 1. Data Cleaning & Preparation Summary
To isolate the major players and analyze them cleanly, the raw dataset was preprocessed using the following workflow:
* **Filtering & Casing:** Filtered the data to include `netflix`, `hulu_plus`, `hbo_max`, and `hbo`. Standardized names to `Netflix`, `Hulu`, and `HBO Max` (merging the legacy `hbo` service with `hbo_max`).
* **Handling Missing Values:** Excluded entries with missing IMDb ratings.
* **Deduplication:** Deduplicated titles at the service-level when evaluating ratings and release year distributions to prevent inflation from multi-genre tagging.
* **Refined Dataset Size:** The resulting refined dataset contains **24,998** rows of service-genre-tag combinations representing **9,299** unique titles.

---

## 2. Key Insights & Distributions

### A. Distribution of IMDb Ratings
The IMDb rating distribution reflects content quality across services.

![IMDb Ratings Distribution](file:///Users/milanmiric/Desktop/MBA%20PM%20-%20Intro%20Workshop/Code/images/imdb_distribution.png)

* **HBO Max** leads in catalog quality with a mean rating of **6.93**, reflecting its rich catalog of premium and critically acclaimed content.
* **Hulu** follows with a mean rating of **6.75**.
* **Netflix** has the lowest mean rating of **6.56**. This is a typical trait of platforms that prioritize catalog breadth and volume over curation.

### B. Distribution of Release Years
The release year distribution highlights differences in licensing strategy and library age.

![Release Year Distribution](file:///Users/milanmiric/Desktop/MBA%20PM%20-%20Intro%20Workshop/Code/images/release_year_distribution.png)

* **Netflix**'s catalog skewing heavily toward the late 2010s with a median release year of **2017**, showing its heavy investment in recent originals and recent licenses.
* **Hulu** also skews modern with a median release year of **2014**.
* **HBO Max** has a much wider distribution, extending far back into the 20th century with a median release year of **2006**, showing a strong library of classics and long-running legacy series.

### C. Distribution of Genres
The bar chart below outlines the occurrences of different genres across the platforms.

![Genre Distribution](file:///Users/milanmiric/Desktop/MBA%20PM%20-%20Intro%20Workshop/Code/images/genre_distribution.png)

* **Drama** and **Comedy** are the dominant genres across all services, with Drama having **4,652** occurrences and Comedy having **3,693** occurrences in the filtered dataset.
* **Netflix** dominates the **Documentary** space compared to competitors, while **HBO Max** has a strong relative presence in **Action & Adventure** and **Crime**.
