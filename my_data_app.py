# app.py  ←  Copie-colle exactement ça dans ton fichier

import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import glob
import plotly.express as px

# ================================================
# CONFIGURATION DE LA PAGE
# ================================================
st.set_page_config(
    page_title="Dakar Auto Scraper",
    page_icon="car",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================
# CSS CORRIGÉ (ne cache plus le contenu !)
# ================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    
    .main {
        font-family: 'Montserrat', sans-serif;
    }
    
    /* Fond d'écran seulement (sans masquer le contenu) */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
                    url('https://images.pexels.com/photos/6891809/pexels-photo-6891809.jpeg?auto=compress&cs=tinysrgb&w=1920');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Sidebar propre */
    [data-testid="stSidebar"] {
        background: #2d3436;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Titres en jaune doré */
    h1, h2, h3 {
        color: #f1c40f !important;
        text-align: center;
    }
    
    /* Boutons bleus */
    .stButton>button {
        background: #3498db;
        color: white;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    
    /* Masquer le menu Streamlit */
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================================================
# TITRE PRINCIPAL
# ================================================
st.markdown("<h1 style='font-size:4.5rem; margin-bottom:0;'>DAKAR AUTO SCRAPER</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#ecf0f1; margin-top:0;'>Professional Vehicle Data Extraction Tool</h3>", unsafe_allow_html=True)
st.markdown("---")

# Stockage des données scrapées
if 'data' not in st.session_state:
    st.session_state.data = None

# ================================================
# SIDEBAR
# ================================================
st.sidebar.image("https://img.icons8.com/fluency/96/car.png", width=90)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a section", 
    ["Scrape Data", "Pre-scraped Data", "Dashboard", "Feedback"])

# ================================================
# 1. SCRAPE DATA
# ================================================
if page == "Scrape Data":
    st.header("Scrape New Car Listings")
    
    col1, col2 = st.columns([3,1])
    with col1:
        pages = st.number_input("How many pages to scrape?", 1, 30, 5)
    with col2:
        st.metric("Estimated listings", pages * 25)
    
    if st.button("START SCRAPING NOW", type="primary"):
        with st.spinner("Scraping in progress..."):
            all_data = []
            progress = st.progress(0)
            for p in range(1, pages+1):
                progress.progress(p/pages)
                url = f"https://dakar-auto.com/senegal/voitures-4?page={p}"
                try:
                    r = get(url, timeout=15)
                    soup = bs(r.content, 'html.parser')
                    cards = soup.find_all('div', class_='listings-cards__list-item')
                    
                    for card in cards:
                        try:
                            title = card.find('h2', class_='listing-card__header__title').a.text.strip().split()
                            brand = title[0]
                            model = " ".join(title[1:-1])
                            year = title[-1]
                            
                            info = card.find_all('li', class_='listing-card__attribute')
                            km = info[1].text.replace('km','').strip()
                            fuel = info[3].text.strip()
                            gearbox = info[2].text.strip()
                            
                            price = card.find('h3', class_='listing-card__header__price').text
                            price = price.replace('FCFA','').replace(' ','').replace('\n','').strip()
                            
                            all_data.append({
                                "Brand": brand,
                                "Model": model,
                                "Year": year,
                                "Mileage": km,
                                "Fuel": fuel,
                                "Gearbox": gearbox,
                                "Price_FCFA": price
                            })
                        except:
                            continue
                except:
                    continue
            
            if all_data:
                df = pd.DataFrame(all_data)
                st.session_state.data = df
                st.success(f"Successfully scraped {len(df)} listings!")
                st.dataframe(df)
                
                csv = df.to_csv(index=False).encode()
                st.download_button("Download CSV", csv, "dakar_auto.csv", "text/csv")
            else:
                st.error("No data found")

# ================================================
# 2. PRE-SCRAPED DATA
# ================================================
elif page == "Pre-scraped Data":
    st.header("Download Pre-scraped Files")
    if os.path.exists("data"):
        files = [f for f in os.listdir("data") if f.endswith(".csv")]
        if files:
            for f in files:
                path = f"data/{f}"
                col1, col2 = st.columns(2)
                col1.write(f"**{f}**")
                with open(path, "rb") as file:
                    col2.download_button("Download", file, f, mime="text/csv")
        else:
            st.info("No files in /data folder")
    else:
        st.warning("Create folder 'data' and put your CSV files")

# ================================================
# 3. DASHBOARD
# ================================================
elif page == "Dashboard":
    st.header("Interactive Dashboard")
    
    if st.session_state.data is not None and not st.session_state.data.empty:
        df = st.session_state.data
    elif os.path.exists("data"):
        files = glob.glob("data/*.csv")
        if files:
            choice = st.selectbox("Select file", files)
            df = pd.read_csv(choice)
        else:
            st.warning("Scrape data first")
            st.stop()
    else:
        st.warning("No data available")
        st.stop()
    
    # Nettoyage rapide
    df["Price"] = pd.to_numeric(df["Price_FCFA"], errors='coerce')
    df["Year"] = pd.to_numeric(df["Year"], errors='coerce')
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Listings", len(df))
    c2.metric("Brands", df["Brand"].nunique())
    c3.metric("Avg Price", f"{df['Price'].mean():,.0f} FCFA")
    c4.metric("Latest Year", df["Year"].max())
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df["Brand"].value_counts().head(10), title="Top 10 Brands")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(df, x="Price", nbins=30, title="Price Distribution")
        st.plotly_chart(fig, use_container_width=True)

# ================================================
# 4. FEEDBACK
# ================================================
elif page == "Feedback":
    st.header("Your Feedback")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Open Detailed Form"):
            st.markdown("[KoboToolbox Link](https://ee.kobotoolbox.org/x/uYmlZU5X)")
    with col2:
        if st.button("Open Quick Google Form"):
            st.markdown("[Google Form Link](https://docs.google.com/forms/d/e/1FAIpQLSeL5dzKVxgxD-rOZqLLiDWmIE1dPhBjeeYcrEl3_EcTGeH2zw/viewform)")

# ================================================
# FOOTER
# ================================================
st.markdown("---")
st.markdown("<p style='text-align:center; color:#f1c40f; font-size:1.1rem;'>Dakar Auto Scraper • Professional Tool • 2025</p>", unsafe_allow_html=True)
