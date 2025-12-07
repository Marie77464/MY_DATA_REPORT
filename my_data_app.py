# app.py → COPIE-COLLE ÇA EXACTEMENT (remplace tout ton fichier)

import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import glob

st.set_page_config(page_title="Dakar Auto Scraper", page_icon="car", layout="wide")

# ==================== CSS (tableau visible garanti) ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    * {font-family: 'Montserrat', sans-serif;}
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)),
                    url('https://images.pexels.com/photos/6891809/pexels-photo-6891809.jpeg?auto=compress&cs=tinysrgb&w=1920') center/cover fixed;
    }
    
    [data-testid="stSidebar"] {background: #2d3436;}
    [data-testid="stSidebar"] * {color: white !important;}
    
    h1 {color: #f1c40f !important; text-align:center; font-size:4.5rem; text-shadow: 3px 3px 10px black;}
    h2, h3 {color: #f1c40f !important;}
    
    .stButton>button {
        background: #e74c3c;
        color: white;
        border-radius: 12px;
        height: 3.5em;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    /* TABLEAU PARFAITEMENT VISIBLE */
    .stDataFrame table, .stDataFrame td, .stDataFrame th {
        background-color: white !important;
        color: black !important;
        border: 1px solid #2d3436 !important;
    }
    .stDataFrame th {background-color: #2d3436 !important; color: white !important;}
    
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== TITRE ====================
st.markdown("<h1>DAKAR AUTO SCRAPER</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#ecf0f1; text-align:center; margin-top:-30px;'>Extraction professionnelle des annonces Dakar-Auto.com</h3>", unsafe_allow_html=True)
st.markdown("---")

# Stockage des données
if 'df' not in st.session_state:
    st.session_state.df = None

# ==================== SIDEBAR ====================
st.sidebar.image("https://img.icons8.com/fluency/96/car.png", width=100)
st.sidebar.markdown("<h2 style='color:#f1c40f; text-align:center;'>Menu</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("", ["Scrape Data", "Download Pre-scraped Data", "Dashboard", "App Evaluation"])

# ==================== FONCTION SCRAPING CORRIGÉE (sans erreur de syntaxe) ====================
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
            soup = bs(r.content, 'html.parser')
            cards = soup.find_all('div', class_='listings-cards__list-item')

            for card in cards:
                try:
                    title = card.find('h2', class_='listing-card__header__title').a.text.strip().split()
                    brand = title[0]
                    model = " ".join(title[1:-1]) if len(title) > 2 else title[1]
                    year = title[-1]

                    attrs = card.find_all('li', class_='listing-card__attribute')
                    km = attrs[1].text.replace('km', '').strip() if len(attrs) > 1 else "N/A"
                    gearbox = attrs[2].text.strip() if len(attrs) > 2 else "N/A"
                    fuel = attrs[3].text.strip() if len(attrs) > 3 else "N/A"

                    price = card.find('h3', class_='listing-card__header__price').text
                    price = price.replace('FCFA', '').replace(' ', '').replace('\n', '').strip()

                    owner = card.find('p', class_='time-author').a.text.replace('Par', '').strip() if card.find('p', class_='time-author') else "N/A"

                    all_data.append({
                        "brand": brand,
                        "model": model,
                        "year": year,
                        "kilometer": km,
                        "fuel_type": fuel,
                        "gearbox": gearbox,
                        "owner": owner,
                        "price": price
                    })
                except:
                    continue  # on ignore les cartes cassées
        except Exception as e:
            st.error(f"Erreur réseau page {p} : {e}")

    progress.empty()
    status.empty()

    if all_data:
        df = pd.DataFrame(all_data)
        st.session_state.df = df
        st.success(f"{len(df)} annonces récupérées avec succès !")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="TÉLÉCHARGER LE CSV",
            data=csv,
            file_name=f"dakar_auto_{pd.Timestamp.now():%Y%m%d_%H%M}.csv",
            mime="text/csv"
        )
    else:
        st.warning("Aucune annonce trouvée.")

# ==================== MENU PRINCIPAL ====================
if menu == "Scrape Data":
    st.header("Scraper les annonces voitures")
    col1, col2 = st.columns([2,1])
    with col1:
        pages = st.number_input("Nombre de pages à scraper", min_value=1, max_value=50, value=3)
    with col2:
        st.metric("Annonces estimées", f"~{pages * 25}")

    if st.button("LANCER LE SCRAPING", type="primary"):
        scrape_data(pages)

elif menu == "Download Pre-scraped Data":
    st.header("Télécharger les données pré-scrapées")
    if os.path.exists("data"):
        files = glob.glob("data/*.csv")
        if files:
            for f in files:
                name = os.path.basename(f)
                c1, c2 = st.columns([3,1])
                c1.write(f"**{name}**")
                with open(f, "rb") as file:
                    c2.download_button("Télécharger", file, name, "text/csv")
        else:
            st.info("Aucun fichier dans le dossier data/")
    else:
        st.warning("Crée le dossier 'data' et mets-y tes CSV")

elif menu == "Dashboard":
    st.header("Dashboard")
    if st.session_state.df is not None and len(st.session_state.df) > 0:
        st.success("Données chargées ! Voici un aperçu :")
        st.dataframe(st.session_state.df, use_container_width=True)
    else:
        st.info("Scrape d'abord des données pour voir le dashboard")

elif menu == "App Evaluation":
    st.header("Évaluez l'application")
    st.write("Merci de nous aider à améliorer l’outil !")
    # Tu peux remettre tes liens ici

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("<p style='text-align:center; color:#f1c40f; font-size:1.3rem; font-weight:bold;'>Dakar Auto Scraper Premium © 2025</p>", unsafe_allow_html=True)
