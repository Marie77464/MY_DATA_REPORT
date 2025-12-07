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

# ==================== AFRICAN PREMIUM THEME ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    * {font-family: 'Poppins', sans-serif;}

    .stApp {
        background: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.75)),
        url('https://cdn.pixabay.com/photo/2020/03/10/17/15/auto-4925619_1280.jpg') center/cover fixed;
    }

    [data-testid="stSidebar"] {
        background: #9b0058;
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

    /* TABLE THEME */
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

# ==================== SCRAPER FUNCTION ====================
def scrape_data(pages):
    all_data = []
    progress = st.progress(0)
    status = st.empty()

    for p in range(1, pages + 1):
        status.text(f"Scraping page {p}/{pages}...")
        progress.progress(p / pages)

        url = f"https://dakar-auto.com/senegal/voitures-4?page={p}"

        try:
            r = get(url, timeout=15)
            soup = bs(r.content, "html.parser")
            cards = soup.find_all("div", class_="listings-cards__list-item")

            for card in cards:
                try:
                    title = card.find("h2", class_="listing-card__header__title").a.text.strip().split()
                    brand = title[0]
                    model = " ".join(title[1:-1]) if len(title) > 2 else title[1]
                    year = title[-1]

                    attrs = card.find_all("li", class_="listing-card__attribute")
                    km = attrs[1].text.replace("km", "").strip() if len(attrs) > 1 else "N/A"
                    gearbox = attrs[2].text.strip() if len(attrs) > 2 else "N/A"
                    fuel = attrs[3].text.strip() if len(attrs) > 3 else "N/A"

                    price = card.find("h3", class_="listing-card__header__price").text
                    price = price.replace("FCFA", "").replace(" ", "").replace("\n", "").strip()

                    owner = card.find("p", class_="time-author").a.text.replace("Par", "").strip() if card.find("p", class_="time-author") else "N/A"

                    all_data.append({
                        "brand": brand,
                        "model": model,
                        "year": year,
                        "kilometers": km,
                        "fuel_type": fuel,
                        "gearbox": gearbox,
                        "owner": owner,
                        "price": price
                    })
                except:
                    continue

        except Exception as e:
            st.error(f"Network error page {p} : {e}")

    progress.empty()
    status.empty()

    if all_data:
        df = pd.DataFrame(all_data)
        st.session_state.df = df

        st.success(f"{len(df)} listings successfully extracted!")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="DOWNLOAD CSV",
            data=csv,
            file_name=f"dakar_auto_{pd.Timestamp.now():%Y%m%d_%H%M}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data found.")

# ==================== MAIN MENU ====================
if menu == "Scrape Data":
    st.header("Vehicle Scraper")
    col1, col2 = st.columns([2, 1])

    with col1:
        pages = st.number_input("Number of pages to scrape", 1, 50, 3)

    with col2:
        st.metric("Estimated listings", f"~{pages * 25}")

    if st.button("START SCRAPING"):
        scrape_data(pages)

elif menu == "Download Pre-scraped Data":
    st.header("Download Pre-scraped Files")
    if os.path.exists("data"):
        files = glob.glob("data/*.csv")
        if files:
            for f in files:
                n = os.path.basename(f)
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{n}**")
                with open(f, "rb") as file:
                    c2.download_button("Download", file, n, "text/csv")
        else:
            st.info("No CSV files found.")
    else:
        st.warning("Create a folder named 'data' and add CSV files in it.")

elif menu == "Dashboard":
    st.header("Dashboard")
    if st.session_state.df is not None:
        st.dataframe(st.session_state.df, use_container_width=True)
    else:
        st.info("You must scrape data first.")

elif menu == "App Evaluation":
    st.header("Application Feedback")
    st.write("Thank you for helping us improve this tool!")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#ffb6d6; font-size:1.3rem;'>Dakar Auto Scraper Premium © 2025</p>",
    unsafe_allow_html=True
)
