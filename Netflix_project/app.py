import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from scipy.stats import chisquare

st.set_page_config(
    page_title="Netflix Content Analysis",
    page_icon="🎬",
    layout="wide"
)

# Paths that work on VS Code, GitHub and Streamlit Cloud
BASE = Path(r"C:\Users\David Chua\Desktop\fsds Projects\Netflix project\assets\netflix_titles_cleaned.csv").parent
DATA = BASE / "data" / "netflix_titles_cleaned.csv"
CERT = BASE / "assets" / "certificate.png"

@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\David Chua\Desktop\fsds Projects\Netflix project\assets\netflix_titles_cleaned.csv")

    df["country"] = df["country"].fillna("Unknown").str.split(",").str[0].str.strip()
    df["genre"] = df["listed_in"].fillna("Unknown").str.split(",").str[0].str.strip()
    df["rating"] = df["rating"].fillna("Unknown")

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

f = df[
    df["type"].isin(types) &
    df["release_year"].between(years[0], years[1])
]

# ---------------- Overview ----------------
if page == "Overview":

    st.title("🎬 Netflix Movies & TV Shows Analysis")
    st.write("Data Analyst Internship Project")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Titles", len(df))
    c2.metric("Movies", (df["type"] == "Movie").sum())
    c3.metric("TV Shows", (df["type"] == "TV Show").sum())

    st.subheader("Key Insights")

    st.write("• Movies dominate Netflix content.")
    st.write("• United States contributes the highest number of titles.")
    st.write("• TV-MA is the most common rating.")
    st.write("• Netflix content increased significantly after 2015.")

    st.dataframe(df.head(10), use_container_width=True)


# ---------------- Dashboard ----------------
elif page == "Dashboard":

    st.title("📊 Netflix Dashboard")

    c1, c2 = st.columns(2)

    c1.plotly_chart(
        px.bar(
            f["type"].value_counts(),
            title="Movies vs TV Shows"
        ),
        use_container_width=True
    )

    c2.plotly_chart(
        px.bar(
            f["country"].value_counts().head(10),
            title="Top 10 Countries"
        ),
        use_container_width=True
    )

    c3, c4 = st.columns(2)

    c3.plotly_chart(
        px.bar(
            f["rating"].value_counts(),
            title="Rating Distribution"
        ),
        use_container_width=True
    )

    c4.plotly_chart(
        px.histogram(
            f,
            x="release_year",
            title="Release Year Trend"
        ),
        use_container_width=True
    )

    st.plotly_chart(
        px.bar(
            f["genre"].value_counts().head(10),
            orientation="h",
            title="Top Genres"
        ),
        use_container_width=True
    )


# ---------------- Explorer ----------------
elif page == "Explorer":

    st.title("🔎 Netflix Data Explorer")

    search = st.text_input("Search title or director")

    if search:
        result = f[
            f["title"].str.contains(search, case=False, na=False) |
            f["director"].fillna("").str.contains(search, case=False, na=False)
        ]
    else:
        result = f

    st.write(f"**{len(result)} results found**")

    st.dataframe(
        result[
            ["title", "type", "director", "country",
             "release_year", "rating"]
        ],
        use_container_width=True
    )

    st.download_button(
        "⬇️ Download CSV",
        result.to_csv(index=False),
        "netflix_filtered.csv",
        "text/csv"
    )


# ---------------- Hypothesis Test ----------------
elif page == "Hypothesis Test":

    st.title("🧪 Hypothesis Testing")

    st.write(
        "**H₀:** Movies and TV Shows are equally distributed."
    )

    observed = df["type"].value_counts()

    if len(observed) == 2:

        statistic, p_value = chisquare(observed.values)

        c1, c2 = st.columns(2)

        c1.metric("Chi-Square", f"{statistic:.2f}")
        c2.metric("P-Value", f"{p_value:.2e}")

        if p_value < 0.05:
            st.success(
                "Reject H₀ — Movies and TV Shows are not equally distributed."
            )
        else:
            st.info("Fail to reject H₀.")

        st.plotly_chart(
            px.bar(
                observed,
                title="Observed Content Distribution"
            ),
            use_container_width=True
        )


# ---------------- Certificate ----------------
elif page == "Certificate":

    st.title("🎓 Internship Certificate")

    st.write(
        "ApexPlanet Software Pvt. Ltd. - Data Analytics Internship"
    )

    if CERT.exists():
        st.image(str(CERT), use_container_width=True)
    else:
        st.error("Certificate not found.")