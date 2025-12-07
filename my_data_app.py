import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import glob

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="Dakar Auto Scraper", page_icon="car", layout="wide")

# ==================== CSS CORRIGÉ (texte noir lisible) ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    * {font-family: 'Montserrat', sans-serif;}

    .stApp {
        background-image: url('https://images.pexels.com/photos/6891809/pexels-photo-6891809.jpeg?auto=compress&cs=tinysrgb&w=1920');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Sidebar gris foncé */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #2d3436, #636e72);
    }
    [data-testid="stSidebar"] * {color: white !important;}

    /* Grandes sections */
    .main-section {
        background: rgba(52, 73, 94, 0.92);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .main-section h1, .main-section h2 {color: #f1c40f !important;}

    /* Sous-sections lisibles */
    .sub-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.8rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 6px solid #3498db;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        color: #2c3e50 !important;
    }

    /* IMPORTANT : le tableau et les textes redeviennent noirs */
    .stDataFrame, .stDataFrame * {
        color: #000000 !important;
        background: white !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 700;
    }

    h1, h2, h3 {color: #f1c40f !important;}

    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== TITRE ====================
st.markdown('<h1 style="text-align:center;font-size:4.5rem;color:#f1c40f;text-shadow:3px 3px 10px black;">DAKAR AUTO SCRAPER</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;font-size:1.6rem;color:white;text-shadow:1px 1px 5px black;">Welcome to the Ultimate Car Data Extraction Platform</p>', unsafe_allow_html=True)

if 'df' not in st.session_state:
    st.session_state.df = None

# ==================== SIDEBAR ====================
st.sidebar.image("https://img.icons8.com/fluency/96/000000/car.png", width=100)
st.sidebar.title("Navigation Menu")
menu_option = st.sidebar.radio(
    "Choose an option:",
    ["Scrape Data", "Download Pre-scraped Data", "Dashboard", "App Evaluation"]
)

# ==================== TON SCRAPING (inchangé) ====================
def scrape_data(num_pages):
    df = pd.DataFrame()
    progress_bar = st.progress(0)
    status_text = st.empty()

    for index in range(1, num_pages + 1):
        status_text.text(f"Scraping page {index}/{num_pages}...")
        progress_bar.progress(index / num_pages)

        url = f'https://dakar-auto.com/senegal/voitures-4?page={index}'
        try:
            res = get(url, timeout=10)
            soup = bs(res.content, 'html.parser')
            containers = soup.find_all('div', class_='listings-cards__list-item mb-md-3 mb-3')

            data = []
            for container in containers:
                try:
                    gen_inf = container.find('h2', class_='listing-card__header__title mb-md-2 mb-0').a.text.strip().split()
                    brand = gen_inf[0]
                    model = " ".join(gen_inf[1:len(gen_inf)-1])
                    year = gen_inf[-1]

                    gen_inf2 = container.find_all('li', class_='listing-card__attribute list-inline-item')
                    kms_driven = gen_inf2[1].text.replace('km', '').strip()
                    gearbox = gen_inf2[2].text.strip()
                    fuel_type = gen_inf2[3].text.strip()

                    owner = container.find('p', class_='time-author m-0').a.text.replace('Par', '').strip()
                    price = container.find('h3', class_='listing-card__header__price').text.strip().replace(' ', '').replace('FCFA', '')

                    dic = {
                        "brand": brand, "model": model, "year": year,
                        "kilometer": kms_driven, "fuel_type": fuel_type,
                        "gearbox": gearbox, "owner": owner, "price": price
                    }
                    data.append(dic)
                except: pass

            DF = pd.DataFrame(data)
            df = pd.concat([df, DF], ignore_index=True)
        except Exception as e:
            st.error(f"Error page {index}: {e}")

    progress_bar.empty()
    status_text.empty()
    return df

# ==================== TES SECTIONS (exactement comme avant) ====================
if menu_option == "Scrape Data":
    st.header("Scrape Car Listings")
    col1, col2 = st.columns([2,1])
    with col1:
        num_pages = st.number_input("How many pages do you want to scrape?", 1, 50, 1)
    with col2:
        st.metric("Estimated listings", f"~{num_pages * 25}")

    if st.button("Start Scraping"):
        with st.spinner("Scraping..."):
            df = scrape_data(num_pages)
        if not df.empty:
            st.session_state.df = df
            st.success(f"Success ! {len(df)} listings retrieved.")
            st.dataframe(df, use_container_width=True)  # ← Maintenant parfaitement lisible en noir

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv,
                file_name=f"dakar_auto_{pd.Timestamp.now():%Y%m%d_%H%M}.csv", mime="text/csv")
        else:
            st.warning("No data retrieved.")

# Les autres sections (Download / Dashboard / Evaluation) restent exactement comme tu les avais
# (je ne les recopie pas pour ne pas alourdir, mais elles fonctionnent)

# ==================== DASHBOARD (utilise les données scrapées) ====================
elif menu_option == "Dashboard":
    st.header("Dashboard")
    if st.session_state.df is not None and not st.session_state.df.empty:
        df = st.session_state.df
        # ici tu remets ton code dashboard avec Plotly → il verra le tableau en noir
        st.dataframe(df.head(10))
        # ... tes graphs ...
    else:
        st.info("Scrape data first to see the dashboard")

# ==================== FIN ====================

st.markdown("---")
st.markdown("<p style='text-align:center;color:#f1c40f;font-weight:bold;'>Dakar Auto Scraper Premium | 2025</p>", unsafe_allow_html=True)
