import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import glob

st.set_page_config(
    page_title="Dakar Auto Scraper",
    page_icon="🚗",
    layout="wide"
)

# ==================== FIX AFRICAN PREMIUM THEME ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    * {font-family: 'Poppins', sans-serif;}

    .app-bg {
        background: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.75)),
        url('https://cdn.pixabay.com/photo/2020/09/20/01/23/african-5586271_1280.jpg') center/cover fixed;
        min-height: 100vh;
        padding:20px;
    }

    [data-testid="stSidebar"] {
        background: #9b0058 !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    h1 {
        color: #ff69b4 !important;
        text-align:center;
        font-size:4rem;
        text-shadow: 3px 3px 10px black;
    }

    h2, h3 {
        color: #ffb6d6 !important;
        font-weight: 600;
    }

    .stButton>button {
        background: #ff4fa3 !important;
        color: white !important;
        border-radius: 12px;
        height: 3.3em;
        border: none;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 0 12px rgba(255, 70, 160, 0.7);
    }
    .stButton>button:hover {
        background: #ff79c6 !important;
        box-shadow: 0 0 18px rgba(255, 70, 160, 1);
    }

    .stDataFrame table, .stDataFrame td, .stDataFrame th {
        background-color: white !important;
        color: black !important;
        border: 1px solid #9b0058 !important;
    }

    .stDataFrame th {
        background-color: #9b0058 !important;
        color: white !important;
    }

    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# BACKGROUND CONTAINER
st.markdown("<div class='app-bg'>", unsafe_allow_html=True)

# ==================== TITLE ====================
st.markdown("<h1>DAKAR AUTO SCRAPER</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#ffe6f2; text-align:center; margin-top:-25px;'>Professional Vehicle Extraction – Dakar-Auto.com</h3>", unsafe_allow_html=True)
st.markdown("---")

if 'df' not in st.session_state:
    st.session_state.df = None

# ==================== SIDEBAR ====================
st.sidebar.image("https://img.icons8.com/fluency/96/car.png", width=110)
st.sidebar.markdown("<h2 style='text-align:center; color:white;'>Menu</h2>", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "",
    ["Scrape Data", "Download Pre-scraped Data", "Dashboard", "App Evaluation"]
)

# ==================== FIXED SCRAPER FUNCTION ====================
def scrape_data(pages):
    all_data = []
    progress = st.progress(0)
    status = st.empty()

    for p in range(1, pages + 1):
        status.text(f"Scraping page {p}/{pages}...")
        progress.progress(p / pages)

        url = f"https://dakar-auto.com/senegal/voitures-4?page={p}"

        try:
            response = get(url)
            soup = bs(response.text, "html.parser")

            cars = soup.find_all("div", class_="ads-list-details")

            for car in cars:
                title = car.find("h2").text.strip() if car.find("h2") else "N/A"
                price = car.find("span", class_="ads-price").text.strip() if car.find("span", class_="ads-price") else "N/A"
                location = car.find("span", class_="location").text.strip() if car.find("span", "location") else "N/A"

                all_data.append({
                    "Title": title,
                    "Price": price,
                    "Location": location
                })

        except Exception as e:
            st.error(f"Error scraping page {p}: {e}")

    return pd.DataFrame(all_data)


# ==================== SCRAPE DATA PAGE ====================
if menu == "Scrape Data":
    st.subheader("Scrape Dakar-Auto.com Cars")

    pages = st.number_input("Number of pages to scrape", 1, 20, 5)

    if st.button("Start Scraping"):
        df = scrape_data(pages)
        st.session_state.df = df

        st.success("Scraping Completed!")
        st.dataframe(df)

        df.to_csv("scraped_cars.csv", index=False)
        st.download_button(
            "Download CSV",
            data=df.to_csv().encode("utf-8"),
            file_name="cars_data.csv",
            mime="text/csv"
        )

# ==================== DOWNLOAD PAGE ====================
elif menu == "Download Pre-scraped Data":
    st.subheader("Download Previously Scraped Files")

    files = glob.glob("*.csv")
    if not files:
        st.warning("No files found.")
    else:
        for f in files:
            with open(f, "rb") as file:
                st.download_button(
                    label=f"Download {f}",
                    data=file,
                    file_name=f,
                    mime="text/csv"
                )

# ==================== DASHBOARD ====================
elif menu == "Dashboard":
    st.subheader("Data Summary Dashboard")

    if st.session_state.df is None:
        st.warning("You must scrape data first.")
    else:
        df = st.session_state.df

        st.write("### Total Cars Found:", len(df))
        st.write("### Sample Preview:")
        st.dataframe(df.head())

        st.write("### Price Distribution (Text Format - Needs Cleaning)")
        st.text(df["Price"].value_counts().head())

# ==================== APP EVALUATION ====================
elif menu == "App Evaluation":
    st.subheader("Rate This Application")
    note = st.slider("Your rating:", 1, 10, 8)
    st.write("Thank you for rating:", note)

# END BACKGROUND
st.markdown("</div>", unsafe_allow_html=True)
