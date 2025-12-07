import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import glob

# Plotly optionnel
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Configuration de la page
st.set_page_config(
    page_title="Dakar Auto Scraper",
    page_icon="car",
    layout="wide"
)

# === CSS GRIS ÉLÉGANT + TEXTE NOIR ===
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

    /* Sidebar gris anthracite */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #2d3436, #636e72);
        color: white;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label {
        color: white !important;
    }

    /* Cartes et conteneurs gris clair */
    .info-box, .stDataFrame, .streamlit-expander, .stMetric {
        background: rgba(240, 242, 246, 0.95);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 1px solid #ddd;
        color: #2d3436 !important;
    }

    /* Boutons gris élégants */
    .stButton>button {
        background: linear-gradient(135deg, #636e72, #2d3436);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2d3436, #1e1e1e);
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }

    /* Titres et textes en noir */
    h1, h2, h3, h4, .header-style, .subheader-style {
        color: #2d3436 !important;
        text-shadow: none;
        font-weight: 700;
    }
    p, li, span, label, .stMarkdown {
        color: #2d3436 !important;
        line-height: 1.7;
    }

    /* Tableau propre */
    .stDataFrame {
        background: white !important;
        border-radius: 12px;
        overflow: hidden;
    }

    /* Messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        background: rgba(240, 242, 246, 0.98);
        color: #2d3436;
        border-radius: 12px;
        border-left: 5px solid #636e72;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background: white;
        color: #2d3436;
        border: 1px solid #ccc;
        border-radius: 10px;
    }

    /* Cacher le menu Streamlit */
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown('<h1 style="text-align:center; font-size:4rem; color:#2d3436;">DAKAR AUTO SCRAPER</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-size:1.5rem; color:#636e72; font-weight:300;">Plateforme professionnelle d’extraction de données automobiles</p>', unsafe_allow_html=True)

# === MESSAGE D’ACCUEIL SIMPLIFIÉ ===
st.markdown("""
    <div class="info-box">
        <h2>Bienvenue !</h2>
        <p style="font-size:1.2rem;">
            Bienvenue sur <strong>Dakar Auto Scraper</strong> – votre outil professionnel pour extraire et analyser 
            les données véhicules du site <strong>Dakar-Auto.com</strong>, la première plateforme automobile du Sénégal.
        </p>
    </div>
""", unsafe_allow_html=True)

# === SIDEBAR ===
st.sidebar.image("https://img.icons8.com/fluency/96/000000/car.png", width=100)
st.sidebar.title("Menu")
menu_option = st.sidebar.radio(
    "Choisissez une option",
    ["Scraper les données", "Données pré-scrapées", "Dashboard", "Évaluation"],
    index=0
)

# === FONCTION DE SCRAPING (inchangée) ===
def scrape_data(num_pages):
    df = pd.DataFrame()
    progress_bar = st.progress(0)
    status_text = st.empty()

    for index in range(1, num_pages + 1):
        status_text.text(f"Scraping page {index}/{num_pages}...")
        progress_bar.progress(index / num_pages)

        url = f'https://dakar-auto.com/senegal/voitures-4?page={index}'
        try:
            res = get(url, timeout=15)
            soup = bs(res.content, 'html.parser')
            containers = soup.find_all('div', class_='listings-cards__list-item')

            data = []
            for c in containers:
                try:
                    title = c.find('h2', class_='listing-card__header__title').a.text.strip().split()
                    brand = title[0]
                    model = " ".join(title[1:-1])
                    year = title[-1]

                    attrs = c.find_all('li', class_='listing-card__attribute')
                    km = attrs[1].text.replace('km','').strip()
                    gearbox = attrs[2].text.strip()
                    fuel = attrs[3].text.strip()

                    owner = c.find('p', class_='time-author').a.text.replace('Par','').strip()
                    price = c.find('h3', class_='listing-card__header__price').text.replace('FCFA','').replace(' ','').strip()

                    data.append({
                        "brand": brand, "model": model, "year": year,
                        "kilometer": km, "fuel_type": fuel, "gearbox": gearbox,
                        "owner": owner, "price": price
                    })
                except:
                    continue

            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
        except Exception as e:
            st.error(f"Erreur page {index} : {e}")

    progress_bar.empty()
    status_text.empty()
    return df

# === OPTIONS DU MENU ===
if menu_option == "Scraper les données":
    st.header("Scraper les annonces voitures")
    col1, col2 = st.columns([2,1])
    with col1:
        pages = st.number_input("Nombre de pages à scraper", 1, 50, 3)
    with col2:
        st.metric("Estimé", f"~{pages * 25} annonces")

    if st.button("Lancer le scraping"):
        with st.spinner("Scraping en cours..."):
            data = scrape_data(pages)
        if not data.empty:
            st.success(f"{len(data)} annonces récupérées !")
            st.dataframe(data, use_container_width=True)

            csv = data.to_csv(index=False).encode()
            st.download_button(
                "Télécharger en CSV",
                data=csv,
                file_name=f"dakar_auto_{pd.Timestamp.now():%Y%m%d_%H%M}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Aucune donnée récupérée.")

elif menu_option == "Données pré-scrapées":
    st.header("Données déjà scrapées")
    if os.path.exists("data"):
        files = glob.glob("data/*.csv")
        if files:
            for f in files:
                name = os.path.basename(f)
                col1, col2, col3 = st.columns([4,1,1])
                col1.write(f"**{name}**")
                col2.write(f"{os.path.getsize(f)/1024:.1f} KB")
                with open(f, "rb") as file:
                    col3.download_button("Télécharger", file, name, mime="text/csv")
                with st.expander(f"Aperçu {name}"):
                    st.dataframe(pd.read_csv(f).head(10))
        else:
            st.info("Aucun fichier dans le dossier data/")
    else:
        st.error("Dossier 'data' manquant")

elif menu_option == "Dashboard":
    st.header("Dashboard")
    # (tu peux garder ou améliorer cette partie plus tard)
    st.info("Dashboard en cours de développement – revenez bientôt !")

elif menu_option == "Évaluation":
    st.header("Évaluez l’application")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Formulaire détaillé")
        if st.button("Ouvrir KoboToolbox"):
            st.markdown("<meta http-equiv='refresh' content='0; url=https://ee.kobotoolbox.org/x/uYmlZU5X'>", unsafe_allow_html=True)
    with col2:
        st.subheader("Formulaire rapide")
        if st.button("Ouvrir Google Forms"):
            st.markdown("<meta http-equiv='refresh' content='0; url=https://docs.google.com/forms/d/e/1FAIpQLSeL5dzKVxgxD-rOZqLLiDWmIE1dPhBjeeYcrEl3_EcTGeH2zw/viewform'>", unsafe_allow_html=True)

# === FOOTER ===
st.markdown("---")
st.markdown("""
    <div style="text-align:center; color:#2d3436; padding:1rem;">
        <p><strong>Dakar Auto Scraper</strong> • Outil professionnel • 2025</p>
    </div>
""", unsafe_allow_html=True)
