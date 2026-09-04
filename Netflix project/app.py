import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Netflix Analysis",
    page_icon="🎬",
    layout="wide"
)

BASE = Path(__file__).parent
DATA = BASE / "data" / "netflix_titles_cleaned.csv"
CERT = BASE / "assets" / "certificate.png"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA)

    df["country"] = df["country"].fillna("Unknown")
    df["rating"] = df["rating"].fillna("Unknown")
    df["listed_in"] = df["listed_in"].fillna("Unknown")
    df["director"] = df["director"].fillna("Unknown")

    return df


df = load_data()

st.sidebar.title("🎬 Netflix Analysis")

page = st.sidebar.radio(
    "Select Page",
    ["Overview", "Dashboard", "Explorer", "Hypothesis Test", "Certificate"]
)

types = st.sidebar.multiselect(
    "Content Type",
    df["type"].dropna().unique(),
    default=df["type"].dropna().unique()
)

min_year = int(df["release_year"].min())
max_year = int(df["release_year"].max())

years = st.sidebar.slider(
    "Release Year",
    min_year,
    max_year,
    (2015, max_year)
)

filtered = df[
    df["type"].isin(types) &
    df["release_year"].between(years[0], years[1])
]


# ================= OVERVIEW =================
if page == "Overview":

    st.title("🎬 Netflix Movies & TV Shows Analysis")

    st.write("Data Analyst Internship Project")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Titles", len(df))
    c2.metric("Movies", (df["type"] == "Movie").sum())
    c3.metric("TV Shows", (df["type"] == "TV Show").sum())

    st.subheader("📌 Key Insights")

    st.write("• Movies dominate Netflix content.")
    st.write("• United States contributes the highest number of titles.")
    st.write("• TV-MA is the most common rating.")
    st.write("• Netflix content increased significantly after 2015.")

    st.subheader("Sample Data")
    st.dataframe(df.head(10), use_container_width=True)


# ================= DASHBOARD =================
elif page == "Dashboard":

    st.title("📊 Netflix Dashboard")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Movies vs TV Shows")
        st.bar_chart(filtered["type"].value_counts())

    with c2:
        st.subheader("Top 10 Countries")
        st.bar_chart(filtered["country"].value_counts().head(10))

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Ratings")
        st.bar_chart(filtered["rating"].value_counts())

    with c4:
        st.subheader("Release Year")
        st.line_chart(
            filtered["release_year"].value_counts().sort_index()
        )

    st.subheader("Top Genres")

    genres = (
        filtered["listed_in"]
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .head(10)
    )

    st.bar_chart(genres)


# ================= EXPLORER =================
elif page == "Explorer":

    st.title("🔎 Netflix Data Explorer")

    search = st.text_input(
        "Search by title or director"
    )

    result = filtered

    if search:
        result = filtered[
            filtered["title"].str.contains(
                search, case=False, na=False
            )
            |
            filtered["director"].str.contains(
                search, case=False, na=False
            )
        ]

    st.write(f"**{len(result)} results found**")

    columns = [
        "title",
        "type",
        "director",
        "country",
        "release_year",
        "rating"
    ]

    st.dataframe(
        result[columns],
        use_container_width=True
    )

    st.download_button(
        "⬇️ Download CSV",
        result.to_csv(index=False),
        "netflix_filtered.csv",
        "text/csv"
    )


# ================= HYPOTHESIS =================
elif page == "Hypothesis Test":

    st.title("🧪 Hypothesis Testing")

    st.write(
        "**H₀:** Movies and TV Shows are equally distributed."
    )

    movie_count = (df["type"] == "Movie").sum()
    tv_count = (df["type"] == "TV Show").sum()

    total = movie_count + tv_count
    expected = total / 2

    chi_square = (
        (movie_count - expected) ** 2 / expected
        + (tv_count - expected) ** 2 / expected
    )

    st.metric("Chi-Square Statistic", f"{chi_square:.2f}")

    st.write(f"Movies: **{movie_count}**")
    st.write(f"TV Shows: **{tv_count}**")

    if movie_count != tv_count:
        st.success(
            "Reject H₀ — Movies and TV Shows are not equally distributed."
        )
    else:
        st.info(
            "Fail to reject H₀ — both content types have equal counts."
        )

    st.subheader("Observed Counts")

    st.bar_chart(
        df["type"].value_counts()
    )


# ================= CERTIFICATE =================
elif page == "Certificate":

    st.title("🎓 Internship Certificate")

    st.write(
        "ApexPlanet Software Pvt. Ltd. - Data Analytics Internship"
    )

    if CERT.exists():
        st.image(
            str(CERT),
            use_container_width=True
        )
    else:
        st.error(
            "Certificate not found. "
            "Please put certificate.png inside the assets folder."
        )
