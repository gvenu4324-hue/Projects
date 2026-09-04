import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from scipy.stats import chisquare

# ---------------- Page Settings ----------------

st.set_page_config(
    page_title="Netflix Content Analysis",
    page_icon="🎬",
    layout="wide"
)

# ---------------- Paths ----------------
# Works on VS Code, GitHub and Streamlit Cloud

BASE = Path(__file__).parent

DATA = BASE / "data" / "netflix_titles_cleaned.csv"
CERT = BASE / "assets" / "certificate.png"


# ---------------- Load Data ----------------

@st.cache_data
def load_data():

    df = pd.read_csv(DATA)

    df["country"] = (
        df["country"]
        .fillna("Unknown")
        .str.split(",")
        .str[0]
        .str.strip()
    )

    df["genre"] = (
        df["listed_in"]
        .fillna("Unknown")
        .str.split(",")
        .str[0]
        .str.strip()
    )

    df["rating"] = df["rating"].fillna("Unknown")

    df["director"] = df["director"].fillna("Unknown")

    return df


# Load dataset
df = load_data()


# ---------------- Sidebar ----------------

st.sidebar.title("🎬 Netflix Analysis")

page = st.sidebar.radio(
    "Select Page",
    [
        "Overview",
        "Dashboard",
        "Explorer",
        "Hypothesis Test",
        "Certificate"
    ]
)


# ---------------- Filters ----------------

types = st.sidebar.multiselect(
    "Content Type",
    df["type"].dropna().unique(),
    default=df["type"].dropna().unique()
)

min_year = int(df["release_year"].min())
max_year = int(df["release_year"].max())

default_start = max(2015, min_year)

years = st.sidebar.slider(
    "Release Year",
    min_year,
    max_year,
    (default_start, max_year)
)


# Apply filters
f = df[
    df["type"].isin(types)
    & df["release_year"].between(years[0], years[1])
]


# ==================================================
# OVERVIEW
# ==================================================

if page == "Overview":

    st.title("🎬 Netflix Movies & TV Shows Analysis")

    st.subheader("Created by Yeturi Venu Gopal")

    st.write("Data Analyst Internship Project")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Titles",
        len(df)
    )

    c2.metric(
        "Movies",
        (df["type"] == "Movie").sum()
    )

    c3.metric(
        "TV Shows",
        (df["type"] == "TV Show").sum()
    )

    st.subheader("📌 Key Insights")

    st.write("• Movies dominate Netflix content.")

    st.write(
        "• United States contributes the highest number of titles."
    )

    st.write(
        "• TV-MA is the most common rating."
    )

    st.write(
        "• Netflix content increased significantly after 2015."
    )

    st.subheader("📋 Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )


# ==================================================
# DASHBOARD
# ==================================================

elif page == "Dashboard":

    st.title("📊 Netflix Dashboard")

    c1, c2 = st.columns(2)

    # Movies vs TV Shows
    type_data = f["type"].value_counts()

    fig1 = px.bar(
        x=type_data.index,
        y=type_data.values,
        labels={
            "x": "Content Type",
            "y": "Number of Titles"
        },
        title="Movies vs TV Shows"
    )

    c1.plotly_chart(
        fig1,
        use_container_width=True
    )


    # Top Countries
    country_data = f["country"].value_counts().head(10)

    fig2 = px.bar(
        x=country_data.index,
        y=country_data.values,
        labels={
            "x": "Country",
            "y": "Number of Titles"
        },
        title="Top 10 Countries"
    )

    c2.plotly_chart(
        fig2,
        use_container_width=True
    )


    c3, c4 = st.columns(2)


    # Rating Distribution
    rating_data = f["rating"].value_counts()

    fig3 = px.bar(
        x=rating_data.index,
        y=rating_data.values,
        labels={
            "x": "Rating",
            "y": "Number of Titles"
        },
        title="Rating Distribution"
    )

    c3.plotly_chart(
        fig3,
        use_container_width=True
    )


    # Release Year
    fig4 = px.histogram(
        f,
        x="release_year",
        nbins=30,
        title="Release Year Trend",
        labels={
            "release_year": "Release Year"
        }
    )

    c4.plotly_chart(
        fig4,
        use_container_width=True
    )


    # Top Genres
    genre_data = f["genre"].value_counts().head(10)

    fig5 = px.bar(
        x=genre_data.values,
        y=genre_data.index,
        orientation="h",
        labels={
            "x": "Number of Titles",
            "y": "Genre"
        },
        title="Top 10 Genres"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )


# ==================================================
# EXPLORER
# ==================================================

elif page == "Explorer":

    st.title("🔎 Netflix Data Explorer")

    search = st.text_input(
        "Search title or director"
    )


    if search:

        result = f[
            f["title"].str.contains(
                search,
                case=False,
                na=False
            )
            |
            f["director"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    else:

        result = f


    st.write(
        f"**{len(result)} results found**"
    )


    st.dataframe(
        result[
            [
                "title",
                "type",
                "director",
                "country",
                "release_year",
                "rating"
            ]
        ],
        use_container_width=True
    )


    st.download_button(
        "⬇️ Download CSV",
        result.to_csv(index=False),
        "netflix_filtered.csv",
        "text/csv"
    )


# ==================================================
# HYPOTHESIS TEST
# ==================================================

elif page == "Hypothesis Test":

    st.title("🧪 Hypothesis Testing")

    st.write(
        "**H₀:** Movies and TV Shows are equally distributed."
    )

    st.write(
        "**H₁:** Movies and TV Shows are not equally distributed."
    )


    observed = df["type"].value_counts()


    if len(observed) == 2:

        statistic, p_value = chisquare(
            observed.values
        )


        c1, c2 = st.columns(2)


        c1.metric(
            "Chi-Square",
            f"{statistic:.2f}"
        )


        c2.metric(
            "P-Value",
            f"{p_value:.2e}"
        )


        if p_value < 0.05:

            st.success(
                "Reject H₀ — Movies and TV Shows are not equally distributed."
            )

        else:

            st.info(
                "Fail to reject H₀."
            )


        fig6 = px.bar(
            x=observed.index,
            y=observed.values,
            labels={
                "x": "Content Type",
                "y": "Number of Titles"
            },
            title="Observed Content Distribution"
        )


        st.plotly_chart(
            fig6,
            use_container_width=True
        )


# ==================================================
# CERTIFICATE
# ==================================================

elif page == "Certificate":

    st.title("🎓 Internship Certificate")

    st.write(
        "ApexPlanet Software Pvt. Ltd. - Data Analytics Internship"
    )


    if CERT.exists():

        st.image(
            str(CERT),
            caption="Internship Certificate",
            use_container_width=True
        )

    else:

        st.error(
            "Certificate not found. Please check that the file is located at:"
        )

        st.code(
            "assets/certificate.png"
        )
