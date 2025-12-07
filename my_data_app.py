import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import glob

# Configuration de la page
st.set_page_config(
    page_title="Dakar Auto Scraper",
    page_icon="🚗",
    layout="wide"
)

# CSS personnalisé pour rendre l'app plus jolie
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF3333;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stDownloadButton>button {
        width: 100%;
        background-color: #00C853;
        color: white;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: bold;
    }
    .header-style {
        font-size: 3rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subheader-style {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="header-style">🚗 MY DATA APP</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader-style">Web Scraping & Data Analysis Tool</p>', unsafe_allow_html=True)

# Description
st.markdown("""
    <div class="info-box">
    <h3>📊 About This App</h3>
    <p>This app performs webscraping of data from <strong>dakar-auto</strong> over multiple pages. 
    You can also download pre-scraped data from the app directly without scraping them.</p>
    
    <p><strong>🐍 Python libraries:</strong> base64, pandas, streamlit, requests, bs4</p>
    
    <p><strong>🔗 Data sources:</strong></p>
    <ul>
        <li>🚗 <a href="https://dakar-auto.com/senegal/voitures-4" target="_blank">Voitures</a></li>
        <li>🏍️ <a href="https://dakar-auto.com/senegal/motos-and-scooters-3" target="_blank">Motos & Scooters</a></li>
        <li>🔑 <a href="https://dakar-auto.com/senegal/location-de-voitures-19" target="_blank">Location de voitures</a></li>
    </ul>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/000000/car.png", width=100)
st.sidebar.title("📋 Menu")
st.sidebar.markdown("---")

menu_option = st.sidebar.radio(
    "Choisissez une option:",
    ["🔍 Scraper des données", "📥 Télécharger données pré-scrapées", "📊 Dashboard", "📝 Évaluation de l'app"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Astuce:** Commencez par scraper les données ou téléchargez les données existantes!")

# Fonction de scraping
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
            st.error(f"Erreur lors du scraping de la page {index}: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    return df

# Option 1: Scraper des données
if menu_option == "🔍 Scraper des données":
    st.header("🔍 Scraper des Annonces")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        num_pages = st.number_input(
            "Combien de pages voulez-vous scraper ?",
            min_value=1,
            max_value=50,
            value=1,
            step=1,
            help="Chaque page contient environ 20-30 annonces"
        )
    
    with col2:
        st.metric("Annonces estimées", f"~{num_pages * 25}")
    
    if st.button("🚀 Lancer le scraping", key="scrape_btn"):
        with st.spinner("🔄 Scraping en cours..."):
            df = scrape_data(num_pages)
        
        if not df.empty:
            st.success(f"✅ Scraping terminé ! {len(df)} annonces récupérées.")
            
            # Afficher les données
            st.subheader("📋 Aperçu des données")
            st.dataframe(df, use_container_width=True)
            
            # Statistiques rapides
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total annonces", len(df))
            with col2:
                st.metric("Marques uniques", df['brand'].nunique())
            with col3:
                st.metric("Prix moyen", f"{df['price'].str.replace(' ', '').astype(float).mean():,.0f} FCFA")
            with col4:
                st.metric("Année la plus récente", df['year'].max())
            
            # Télécharger
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Télécharger le CSV",
                data=csv,
                file_name=f"annonces_dakar_auto_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Aucune donnée n'a été récupérée.")

# Option 2: Télécharger données pré-scrapées
elif menu_option == "📥 Télécharger données pré-scrapées":
    st.header("📥 Données Pré-Scrapées (Non nettoyées)")
    
    data_folder = "data"
    
    if os.path.exists(data_folder):
        csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
        
        if csv_files:
            st.info(f"📁 {len(csv_files)} fichier(s) CSV disponible(s) dans le dossier 'data/'")
            
            for csv_file in csv_files:
                file_name = os.path.basename(csv_file)
                file_size = os.path.getsize(csv_file) / 1024  # en KB
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{file_name}**")
                with col2:
                    st.write(f"{file_size:.1f} KB")
                with col3:
                    with open(csv_file, "rb") as f:
                        st.download_button(
                            "⬇️ Télécharger",
                            data=f,
                            file_name=file_name,
                            mime="text/csv",
                            key=file_name
                        )
                
                # Aperçu
                with st.expander(f"👁️ Aperçu de {file_name}"):
                    df_preview = pd.read_csv(csv_file)
                    st.dataframe(df_preview.head(10), use_container_width=True)
                    st.caption(f"Affichage des 10 premières lignes sur {len(df_preview)} total")
                
                st.markdown("---")
        else:
            st.warning("⚠️ Aucun fichier CSV trouvé dans le dossier 'data/'")
    else:
        st.error("❌ Le dossier 'data/' n'existe pas. Veuillez créer ce dossier et y placer vos fichiers CSV.")

# Option 3: Dashboard
elif menu_option == "📊 Dashboard":
    st.header("📊 Dashboard des Données (Nettoyées)")
    
    data_folder = "data"
    
    if os.path.exists(data_folder):
        csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
        
        if csv_files:
            selected_file = st.selectbox("Choisissez un fichier à visualiser:", csv_files)
            
            if selected_file:
                df = pd.read_csv(selected_file)
                
                st.subheader("📈 Statistiques Générales")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total annonces", len(df))
                with col2:
                    if 'brand' in df.columns:
                        st.metric("Marques", df['brand'].nunique())
                with col3:
                    if 'price' in df.columns:
                        prices = pd.to_numeric(df['price'].astype(str).str.replace(' ', '').str.replace(',', ''), errors='coerce')
                        st.metric("Prix moyen", f"{prices.mean():,.0f} FCFA")
                with col4:
                    if 'year' in df.columns:
                        st.metric("Année moyenne", f"{pd.to_numeric(df['year'], errors='coerce').mean():.0f}")
                
                # Afficher le dataframe
                st.subheader("📋 Données")
                st.dataframe(df, use_container_width=True)
                
                # Graphiques
                if 'brand' in df.columns:
                    st.subheader("📊 Top 10 des Marques")
                    top_brands = df['brand'].value_counts().head(10)
                    st.bar_chart(top_brands)
                
                if 'fuel_type' in df.columns:
                    st.subheader("⛽ Répartition par Type de Carburant")
                    fuel_counts = df['fuel_type'].value_counts()
                    st.bar_chart(fuel_counts)
        else:
            st.warning("⚠️ Aucun fichier CSV trouvé dans le dossier 'data/'")
    else:
        st.error("❌ Le dossier 'data/' n'existe pas.")

# Option 4: Évaluation
elif menu_option == "📝 Évaluation de l'app":
    st.header("📝 Évaluez Notre Application")
    
    st.markdown("""
        Votre avis compte ! Aidez-nous à améliorer cette application en remplissant un formulaire d'évaluation.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 KoboToolbox")
        st.markdown("""
            Formulaire détaillé pour une évaluation complète de l'application.
        """)
        kobotoolbox_url = st.text_input(
            "URL KoboToolbox:",
            placeholder="https://ee.kobotoolbox.org/x/...",
            help="Entrez l'URL de votre formulaire KoboToolbox"
        )
        if st.button("🔗 Ouvrir KoboToolbox", key="kobo"):
            if kobotoolbox_url:
                st.markdown(f'<a href="{kobotoolbox_url}" target="_blank"><button style="background-color:#FF4B4B;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;">Accéder au formulaire KoboToolbox</button></a>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ Veuillez entrer l'URL du formulaire")
    
    with col2:
        st.subheader("📝 Google Forms")
        st.markdown("""
            Formulaire rapide pour partager votre expérience utilisateur.
        """)
        google_form_url = st.text_input(
            "URL Google Forms:",
            placeholder="https://forms.gle/...",
            help="Entrez l'URL de votre formulaire Google Forms"
        )
        if st.button("🔗 Ouvrir Google Forms", key="gforms"):
            if google_form_url:
                st.markdown(f'<a href="{google_form_url}" target="_blank"><button style="background-color:#4285F4;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;">Accéder au formulaire Google Forms</button></a>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ Veuillez entrer l'URL du formulaire")
    
    st.markdown("---")
    st.info("💡 Vos retours nous aident à améliorer constamment l'application. Merci pour votre contribution !")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Développé avec ❤️ using Streamlit | © 2024 Dakar Auto Scraper</p>
    </div>
""", unsafe_allow_html=True)
