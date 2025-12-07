import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import glob

# Check if plotly is available
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Dakar Auto Scraper",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS – Tout en rose + texte blanc
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

    * {font-family: 'Montserrat', sans-serif;}

    .stApp {
        background-image: url('https://images.pexels.com/photos/6891809/pexels-photo-6891809.jpeg?auto=compress&cs=tinysrgb&w=1920');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Sidebar – ROSE */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #FFB6D9, #FF69B4);
        backdrop-filter: blur(20px);
        box-shadow: 2px 0 20px rgba(0,0,0,0.5);
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: white !important;
        font-weight: 600;
    }

    /* Boutons – ROSE FONCÉ → PLUS FONCÉ au hover */
    .stButton>button {
        background: linear-gradient(135deg, #FF69B4, #FF1493);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        text-transform: uppercase;
        box-shadow: 0 6px 20px rgba(255,20,147,0.5);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #FF1493, #C71585);
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(255,20,147,0.7);
    }

    /* Boîte d’accueil & toutes les cartes – ROSE TRANSPARENT */
    .info-box, .stDataFrame, .streamlit-expander, .stMetric, div[data-testid="stMetricValue"] {
        background: rgba(255, 182, 217, 0.92) !important;
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(255, 105, 180, 0.4);
        border: 1px solid rgba(255,255,255,0.3);
        color: white !important;
    }

    h1, h2, h3, h4, .header-style {
        color: white !important;
        text-shadow: 3px 3px 8px rgba(0,0,0,0.8);
    }

    .subheader-style, p, li, span, label {
        color: white !important;
    }

    /* Texte général */
    .stMarkdown, p, li {
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    }

    /* Tableau */
    .stDataFrame {
        background: rgba(255, 105, 180, 0.3) !important;
    }

    /* Input & selectbox */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.2);
        color: white;
        border-radius: 10px;
    }

    /* Messages Streamlit */
    .stSuccess, .stWarning, .stInfo, .stError {
        background: rgba(255, 105, 180, 0.95);
        color: white;
        border-radius: 12px;
    }

    /* Supprimer le menu et footer Streamlit */
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="header-style">🚗 DAKAR AUTO SCRAPER</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader-style">Welcome to the Ultimate Car Data Extraction Platform</p>', unsafe_allow_html=True)

# Boîte d’accueil simplifiée (seulement la phrase de bienvenue)
st.markdown("""
    <div class="info-box">
    <h3>Welcome!</h3>
    <p>Bienvenue sur <strong>Dakar Auto Scraper</strong> – votre outil professionnel pour extraire et analyser les données véhicules du site <strong>Dakar-Auto.com</strong>, la première plateforme automobile du Sénégal !</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/000000/car.png", width=100)
st.sidebar.title("Menu")
st.sidebar.markdown("---")
menu_option = st.sidebar.radio(
    "Choisissez une option :",
    ["Scraper les données", "Données pré-scrapées", "Dashboard", "Évaluation de l’app"],
    index=0
)
st.sidebar.markdown("---")
st.sidebar.info("Commencez par scraper ou télécharger des données existantes !")

# ==================== LE RESTE DU CODE RESTE IDENTIQUE ====================

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
                   
                    gen_inf1 = container.find('ul', 'listing-card__attribute-list list-inline mb-0')
                    gen_inf2 = gen_inf1.find_all('li', 'listing-card__attribute list-inline-item')
                   
                    kms_driven = gen_inf2[1].text.replace('km', '').strip()
                    gearbox = gen_inf2[2].text.strip()
                    fuel_type = gen_inf2[3].text.strip()
                   
                    owner = "".join(container.find('p', class_='time-author m-0').a.text).replace('Par', '').strip()
                    price = "".join(container.find('h3', 'listing-card__header__price font-weight-bold text-uppercase mb-0').text.strip().split()).replace('FCFA', '')
                   
                    dic = {
                        "brand": brand,
                        "model": model,
                        "year": year,
                        "kilometer": kms_driven,
                        "fuel_type": fuel_type,
                        "gearbox": gearbox,
                        "owner": owner,
                        "price": price,
                    }
                    data.append(dic)
                except:
                    pass
           
            DF = pd.DataFrame(data)
            df = pd.concat([df, DF], axis=0).reset_index(drop=True)
        except Exception as e:
            st.error(f"Erreur page {index} : {str(e)}")
   
    progress_bar.empty()
    status_text.empty()
    return df

# Les 4 sections (Scrape Data / Download / Dashboard / Evaluation) restent exactement les mêmes que dans ton code original
# (je ne les recopie pas ici pour ne pas alourdir, mais tu peux les laisser telles quelles)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: white; text-shadow: 2px 2px 6px rgba(0,0,0,0.9); padding: 2rem;'>
        <p style='font-size:1.1rem; font-weight: 700; letter-spacing: 2px;'>
            Developed with passion • Dakar Auto Scraper Premium 2024
        </p>
    </div>
""", unsafe_allow_html=True)
