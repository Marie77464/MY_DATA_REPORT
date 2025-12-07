Aimport streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import glob
import plotly.express as px

# Config
st.set_page_config(page_title="Dakar Auto Scraper", page_icon="car", layout="wide")

# === CSS PROPRE & LISIBILE ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    * {font-family: 'Montserrat', sans-serif;}
    
    .stApp {
        background-image: url('https://images.pexels.com/photos/6891809/pexels-photo-6891809.jpeg?auto=compress&cs=tinysrgb&w=1920');
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* Sidebar - Gris foncé */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #2d3436, #636e72);
    }
    [data-testid="stSidebar"] * {color: white !important;}

    /* Grandes sections - Fond bleu pétrole doux */
    .main-section {
        background: rgba(52, 73, 94, 0.92);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        backdrop-filter: blur(10px);
    }
    .main-section h1, .main-section h2 {
        color: #f1c40f !important; /* Jaune doré pour les gros titres */
        text-align: center;
        font-weight: 700;
    }

    /* Sous-sections - Fond gris clair très lisible */
    .sub-section {
        background: rgba(236, 240, 245, 0.97);
        padding: 1.8rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 6px solid #3498db;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .sub-section h3, .sub-section p, .sub-section li {
        color: #2c3e50 !important;
        font-weight: 600;
    }

    /* Boutons */
    .stButton>button {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 700;
        box-shadow: 0 5px 15px rgba(52,152,219,0.4);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2980b9, #1abc9c);
        transform: translateY(-3px);
    }

    .stDataFrame, .streamlit-expander {
        background: white;
        border-radius: 12px;
        overflow: hidden;
    }

    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# === TITRE PRINCIPAL (reste en français comme demandé) ===
st.markdown('<h1 style="text-align:center; font-size:4.5rem; color:#f1c40f; text-shadow: 3px 3px 10px black;">DAKAR AUTO SCRAPER</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-size:1.6rem; color:white; text-shadow: 1px 1px 5px black;">Professional Vehicle Data Extraction from Dakar-Auto.com</p>', unsafe_allow_html=True)

# Session state pour garder les données scrapées
if 'df' not in st.session_state:
    st.session_state.df = None

# === SIDEBAR ===
st.sidebar.image("https://img.icons8.com/fluency/96/car.png", width=100)
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Scrape Data", "Pre-scraped Data", "Dashboard", "Feedback"])

# ==================== SCRAPE DATA ====================
if menu == "Scrape Data":
    st.markdown("<div class='main-section'>", unsafe_allow_html=True)
    st.header("Scrape New Listings")

    col1, col2 = st.columns([2,1])
    with col1:
        pages = st.number_input("Number of pages to scrape", 1, 50, 5)
    with col2:
        st.metric("Estimated listings", f"~{pages * 25}")

    if st.button("Start Scraping"):
        with st.spinner("Scraping in progress... Please wait"):
            df = pd.DataFrame()
            progress = st.progress(0)
            for i in range(1, pages + 1):
                progress.progress(i / pages)
                url = f"https://dakar-auto.com/senegal/voitures-4?page={i}"
                try:
                    r = get(url, timeout=15)
                    soup = bs(r.content, 'html.parser')
                    cards = soup.find_all('div', class_='listings-cards__list-item')

                    temp = []
                    for card in cards:
                        try:
                            title = card.find('h2', class_='listing-card__header__title').a.text.strip().split()
                            brand = title[0]
                            model = " ".join(title[1:-1])
                            year = title[-1]

                            attrs = card.find_all('li', class_='listing-card__attribute')
                            km = attrs[1].text.replace('km','').strip()
                            gearbox = attrs[2].text.strip()
                            fuel = attrs[3].text.strip()

                            price = card.find('h3', class_='listing-card__header__price').text
                            price = price.replace('FCFA','').replace(' ','').strip()

                            owner = card.find('p', class_='time-author').a.text.replace('Par','').strip()

                            temp.append({
                                "Brand": brand,
                                "Model": model,
                                "Year": year,
                                "Mileage (km)": km,
                                "Fuel": fuel,
                                "Gearbox": gearbox,
                                "Price (FCFA)": price,
                                "Seller": owner
                            })
                        except: continue
                    df = pd.concat([df, pd.DataFrame(temp)], ignore_index=True)
                except: pass

            progress.empty()
            if not df.empty:
                st.session_state.df = df  # Sauvegarde pour le dashboard
                st.success(f"Successfully scraped {len(df)} listings!")
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False).encode()
                st.download_button(
                    "Download CSV",
                    data=csv,
                    file_name=f"dakar_auto_{pd.Timestamp.now():%Y%m%d_%H%M}.csv",
                    mime="text/csv"
                )
            else:
                st.error("No data found.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== PRE-SCRAPED DATA ====================
elif menu == "Pre-scraped Data":
    st.markdown("<div class='main-section'>", unsafe_allow_html=True)
    st.header("Download Pre-scraped Datasets")
    if os.path.exists("data"):
        files = glob.glob("data/*.csv")
        if files:
            for f in files:
                name = os.path.basename(f)
                col1, col2, col3 = st.columns([5,1,1])
                col1.write(f"**{name}**")
                col2.write(f"{os.path.getsize(f)/1024:.1f} KB")
                with open(f,"rb") as file:
                    col3.download_button("Download", file, name, mime="text/csv")
                with st.expander(f"Preview {name}"):
                    st.dataframe(pd.read_csv(f).head(10))
        else:
            st.info("No files in data folder")
    else:
        st.warning("Create a 'data' folder and add your CSV files")
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== DASHBOARD (AUTOMATIQUE) ====================
elif menu == "Dashboard":
    st.markdown("<div class='main-section'>", unsafe_allow_html=True)
    st.header("Interactive Dashboard")

    # Charger les données : d'abord celles scrapées, sinon un fichier
    df = st.session_state.df
    if df is None or df.empty:
        if os.path.exists("data"):
            files = glob.glob("data/*.csv")
            if files:
                choice = st.selectbox("Select a dataset", files)
                df = pd.read_csv(choice)
            else:
                st.warning("No data available. Please scrape first or add CSV files.")
                st.stop()
        else:
            st.warning("No data. Scrape first.")
            st.stop()

    # Nettoyage rapide pour les graphs
    df_plot = df.copy()
    df_plot["Price (FCFA)"] = pd.to_numeric(df_plot["Price (FCFA)"], errors='coerce')
    df_plot["Year"] = pd.to_numeric(df_plot["Year"], errors='coerce')
    df_plot = df_plot.dropna(subset=["Price (FCFA)", "Year"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Listings", len(df))
    col2.metric("Unique Brands", df["Brand"].nunique())
    col3.metric("Average Price", f"{df_plot['Price (FCFA)'].mean():,.0f} FCFA")
    col4.metric("Newest Year", df["Year"].max())

    st.markdown("<div class='sub-section'>", unsafe_allow_html=True)
    st.subheader("Top 10 Brands")
    top10 = df["Brand"].value_counts().head(10)
    fig1 = px.bar(x=top10.index, y=top10.values, color=top10.values,
                  color_continuous_scale="Blues", labels={"x":"Brand", "y":"Count"})
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='sub-section'>", unsafe_allow_html=True)
        st.subheader("Price Distribution")
        fig2 = px.histogram(df_plot, x="Price (FCFA)", nbins=30, color_discrete_sequence=["#3498db"])
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='sub-section'>", unsafe_allow_html=True)
        st.subheader("Fuel Type")
        fuel = df["Fuel"].value_counts()
        fig3 = px.pie(values=fuel.values, names=fuel.index, color_discrete_sequence=px.colors.sequential.Blues)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sub-section'>", unsafe_allow_html=True)
    st.subheader("Average Price by Brand (Top 10)")
    avg_price = df_plot.groupby("Brand")["Price (FCFA)"].mean().sort_values(ascending=False).head(10)
    fig4 = px.bar(x=avg_price.index, y=avg_price.values, color=avg_price.values,
                  color_continuous_scale="Viridis")
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==================== FEEDBACK ====================
elif menu == "Feedback":
    st.markdown("<div class='main-section'>", unsafe_allow_html=True)
    st.header("Your Feedback Matters")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Detailed Form")
        if st.button("Open KoboToolbox"):
            st.markdown("<script>window.open('https://ee.kobotoolbox.org/x/uYmlZU5X', '_blank')</script>", unsafe_allow_html=True)
    with col2:
        st.subheader("Quick Form")
        if st.button("Open Google Form"):
            st.markdown("<script>window.open('https://docs.google.com/forms/d/e/1FAIpQLSeL5dzKVxgxD-rOZqLLiDWmIE1dPhBjeeYcrEl3_EcTGeH2zw/viewform', '_blank')</script>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align:center; padding:2rem; color:#f1c40f; font-weight:700;'>
    Dakar Auto Scraper © 2025 | Professional Tool for Senegal Automotive Market
</div>
""", unsafe_allow_html=True)import streamlit as st
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

